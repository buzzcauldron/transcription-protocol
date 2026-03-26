#!/usr/bin/env python3
"""
Multi-model stress test: run transcriber prompt + gate checks (schema + ground truth).

Usage (from repository root):
  python -m benchmark.stress_run
  python -m benchmark.stress_run --cases BM-001 --models anthropic openai
  python -m benchmark.stress_run --include-optional
  python -m benchmark.stress_run --replay

Requires API keys in the environment for selected providers (not for --replay).
Loads repo-root ``.env`` when present (see ``.env.example``; requires ``python-dotenv`` from requirements-stress.txt).
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import certifi
except ImportError:
    certifi = None

from .prompt_builder import build_zones
from .providers import PROVIDERS
from .stress_common import load_env_file, load_manifest, repo_root, write_report_md
from .stress_gate import gates_from_raw


def _download(url: str, dest: Path) -> None:
    ctx = ssl.create_default_context(cafile=certifi.where() if certifi else None)
    req = urllib.request.Request(url, headers={"User-Agent": "transcription-protocol-stress/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        dest.write_bytes(resp.read())


def ensure_images(case_id: str, case_cfg: dict, root: Path) -> list[str]:
    """Return absolute paths to image files (download URL list if needed)."""
    urls = case_cfg.get("image_urls") or []
    rel_paths = case_cfg.get("image_paths") or []
    out: list[str] = []
    if urls:
        dest_dir = root / "benchmark" / "images" / case_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        for i, url in enumerate(urls):
            dest = dest_dir / f"page_{i + 1}.jpg"
            if not dest.exists():
                print(f"  Downloading: {url}")
                _download(url, dest)
            out.append(str(dest.resolve()))
    for rp in rel_paths:
        p = (root / rp).resolve()
        if p.exists():
            out.append(str(p))
        elif not urls:
            raise FileNotFoundError(
                f"Missing image for {case_id}: expected {p} (see benchmark/images/README.md)"
            )
    return out


def main() -> int:
    root = repo_root()
    load_env_file(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    ap = argparse.ArgumentParser(description="Multi-model transcription protocol stress test")
    ap.add_argument(
        "--manifest",
        type=Path,
        default=root / "benchmark" / "manifest.yaml",
        help="Path to manifest.yaml",
    )
    ap.add_argument(
        "--cases",
        nargs="*",
        default=None,
        help="Case IDs (default: all non-optional)",
    )
    ap.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Model keys from manifest (default: all)",
    )
    ap.add_argument(
        "--include-optional",
        action="store_true",
        help="Include cases marked optional: true (e.g. BM-MED-001 with local image)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve images and exit without calling APIs",
    )
    ap.add_argument(
        "--replay",
        action="store_true",
        help="Score saved response.txt under --output-dir only (no API calls); see benchmark/CURSOR_STRESS.md",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=root / "benchmark" / "test-results" / "stress",
        help="Raw responses and report output directory",
    )
    args = ap.parse_args()

    if args.replay:
        from .stress_replay import run_replay

        return run_replay(
            manifest_path=args.manifest,
            output_dir=args.output_dir,
            cases=args.cases,
            include_optional=args.include_optional,
        )

    manifest = load_manifest(args.manifest)
    cases_cfg = manifest.get("cases") or {}
    models_cfg = manifest.get("models") or {}

    case_ids = list(cases_cfg.keys())
    if args.cases:
        case_ids = [c for c in args.cases if c in cases_cfg]
        unknown = set(args.cases) - set(cases_cfg.keys())
        if unknown:
            print(f"Unknown cases: {unknown}", file=sys.stderr)
            return 1

    model_keys = list(models_cfg.keys())
    if args.models:
        model_keys = [m for m in args.models if m in models_cfg]
        unk = set(args.models) - set(models_cfg.keys())
        if unk:
            print(f"Unknown model keys: {unk}", file=sys.stderr)
            return 1

    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows: list[dict] = []
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        for case_id in case_ids:
            case_cfg = cases_cfg[case_id]
            if case_cfg.get("optional") and not args.include_optional:
                print(f"[dry-run] skip optional {case_id}")
                continue
            n_urls = len(case_cfg.get("image_urls") or [])
            rels = case_cfg.get("image_paths") or []
            print(
                f"[dry-run] {case_id}: would use {n_urls} URL(s), "
                f"paths={rels}, models={model_keys}"
            )
        report_path = args.output_dir / "stress_report.md"
        write_report_md(report_path, [], started)
        results_path = args.output_dir / "stress_results.json"
        results_path.write_text(json.dumps({"generated": started, "rows": []}, indent=2), encoding="utf-8")
        print(f"(empty matrix) Report written: {report_path}")
        print(f"JSON written: {results_path}")
        return 0

    for case_id in case_ids:
        case_cfg = cases_cfg[case_id]
        if case_cfg.get("optional") and not args.include_optional:
            print(f"Skip optional case {case_id} (use --include-optional)")
            continue

        try:
            image_paths = ensure_images(case_id, case_cfg, root)
        except FileNotFoundError as e:
            print(f"Skip {case_id}: {e}")
            continue

        if not image_paths:
            print(f"Skip {case_id}: no images resolved")
            continue

        prompt_cfg = dict(case_cfg.get("prompt") or {})
        multi = len(image_paths) > 1
        note = (
            f"{len(image_paths)} pages — one segments list covering all visible body text in reading order."
            if multi
            else None
        )
        system, user_text = build_zones(prompt_cfg, multi_page_note=note)

        evaluator = case_cfg.get("evaluator", "lincoln")

        for mk in model_keys:
            mc = models_cfg[mk]
            provider = mc.get("provider")
            model_name = mc.get("model")
            fn = PROVIDERS.get(provider or "")
            if not fn:
                print(f"Skip model {mk}: unknown provider {provider}")
                continue

            out_dir = args.output_dir / case_id / mk
            out_dir.mkdir(parents=True, exist_ok=True)
            raw_path = out_dir / "response.txt"
            meta_path = out_dir / "meta.json"

            notes_parts: list[str] = []
            schema_ok = False
            addition_count = ""
            omission_count = ""
            disposition = ""
            score = ""

            try:
                raw = fn(system, user_text, image_paths, model_name)
            except Exception as e:
                notes_parts.append(f"API error: {e}")
                rows.append(
                    {
                        "case": case_id,
                        "model": f"{mk} ({model_name})",
                        "schema_ok": False,
                        "addition_count": "—",
                        "omission_count": "—",
                        "disposition": "FAIL",
                        "score": "—",
                        "notes": " ".join(notes_parts),
                    }
                )
                raw_path.write_text(f"ERROR: {e}", encoding="utf-8")
                continue

            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(
                json.dumps(
                    {
                        "caseId": case_id,
                        "modelKey": mk,
                        "provider": provider,
                        "modelId": model_name,
                        "started": started,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            g = gates_from_raw(raw, evaluator)
            rows.append(
                {
                    "case": case_id,
                    "model": f"{mk} ({model_name})",
                    **g,
                }
            )

    report_path = args.output_dir / "stress_report.md"
    write_report_md(report_path, rows, started)
    results_path = args.output_dir / "stress_results.json"
    results_path.write_text(json.dumps({"generated": started, "rows": rows}, indent=2), encoding="utf-8")
    print(f"Report written: {report_path}")
    print(f"JSON written: {results_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
