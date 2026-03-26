#!/usr/bin/env python3
"""
Score saved stress-test responses (no API keys).

Scans --output-dir/<case>/<run>/response.txt and applies the same gates as stress_run.

Usage (from repository root):
  python -m benchmark.stress_replay
  python -m benchmark.stress_replay --cases BM-001
  python -m benchmark.stress_run --replay
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .stress_common import load_manifest, repo_root, write_report_md
from .stress_gate import gates_from_raw


def _model_label(run_dir: Path) -> str:
    meta = run_dir / "meta.json"
    if meta.exists():
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
            mk = m.get("modelKey", run_dir.name)
            mid = m.get("modelId", "?")
            return f"{mk} ({mid})"
        except (json.JSONDecodeError, OSError):
            pass
    return run_dir.name


def run_replay(
    manifest_path: Path,
    output_dir: Path,
    cases: list[str] | None,
    include_optional: bool,
) -> int:
    manifest = load_manifest(manifest_path)
    cases_cfg = manifest.get("cases") or {}

    case_ids = list(cases_cfg.keys())
    if cases:
        case_ids = [c for c in cases if c in cases_cfg]
        unknown = set(cases) - set(cases_cfg.keys())
        if unknown:
            print(f"Unknown cases: {unknown}", file=sys.stderr)
            return 1

    case_ids = [
        c
        for c in case_ids
        if not (cases_cfg[c].get("optional") and not include_optional)
    ]

    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows: list[dict[str, Any]] = []

    for case_id in case_ids:
        evaluator = cases_cfg[case_id].get("evaluator", "lincoln")
        case_path = output_dir / case_id
        if not case_path.is_dir():
            print(f"No saved runs under {case_path}", file=sys.stderr)
            continue
        for sub in sorted(case_path.iterdir()):
            if not sub.is_dir():
                continue
            resp_path = sub / "response.txt"
            if not resp_path.exists():
                continue
            raw = resp_path.read_text(encoding="utf-8")
            if raw.startswith("ERROR:"):
                rows.append(
                    {
                        "case": case_id,
                        "model": _model_label(sub),
                        "schema_ok": False,
                        "addition_count": "—",
                        "omission_count": "—",
                        "disposition": "FAIL",
                        "score": "—",
                        "notes": raw.strip(),
                    }
                )
                continue
            g = gates_from_raw(raw, evaluator)
            rows.append(
                {
                    "case": case_id,
                    "model": _model_label(sub),
                    **g,
                }
            )

    report_path = output_dir / "stress_report.md"
    write_report_md(report_path, rows, started)
    results_path = output_dir / "stress_results.json"
    results_path.write_text(
        json.dumps({"generated": started, "rows": rows}, indent=2),
        encoding="utf-8",
    )
    print(f"Replay: scored {len(rows)} response(s)")
    print(f"Report written: {report_path}")
    print(f"JSON written: {results_path}")
    return 0


def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(
        description="Score saved stress test response.txt files (no API calls)"
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=root / "benchmark" / "manifest.yaml",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=root / "benchmark" / "test-results" / "stress",
    )
    ap.add_argument("--cases", nargs="*", default=None)
    ap.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional manifest cases (e.g. BM-MED-001)",
    )
    args = ap.parse_args()
    return run_replay(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        cases=args.cases,
        include_optional=args.include_optional,
    )


if __name__ == "__main__":
    raise SystemExit(main())
