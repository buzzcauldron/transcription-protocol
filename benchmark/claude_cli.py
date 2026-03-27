#!/usr/bin/env python3
"""Prepare (and optionally run) a Claude Code CLI transcription using manifest + prompt_builder.

Requires: Claude Code (`claude` on PATH, e.g. ~/.local/bin/claude).
Images: resolved the same way as stress_run (download BM-001 from LoC IIIF or use local paths).

Usage (from repository root):
  python -m benchmark.claude_cli --case BM-001
  python -m benchmark.claude_cli --case BM-001 --exec   # runs claude -p (non-interactive)

Writes:
  benchmark/test-results/claude-cli/<case>/system.txt
  benchmark/test-results/claude-cli/<case>/user.txt
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .prompt_builder import build_zones
from .stress_common import load_manifest, repo_root
from .stress_run import ensure_images


def main() -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(
        description="Build system/user prompts for Claude Code CLI protocol test"
    )
    ap.add_argument("--case", default="BM-001", help="Case ID from manifest.yaml")
    ap.add_argument(
        "--manifest",
        type=Path,
        default=root / "benchmark" / "manifest.yaml",
    )
    ap.add_argument(
        "--exec",
        action="store_true",
        help="Run `claude -p` with the built prompts (non-interactive)",
    )
    ap.add_argument(
        "--claude-bin",
        default=None,
        help="Path to claude executable (default: shutil.which('claude'))",
    )
    args = ap.parse_args()

    data = load_manifest(args.manifest)
    cases = data.get("cases") or {}
    if args.case not in cases:
        print(f"Unknown case {args.case!r}. Known: {list(cases.keys())}", file=sys.stderr)
        return 1

    case_cfg = cases[args.case]
    prompt_cfg = dict(case_cfg.get("prompt") or {})
    # Ensure runMode present for prompt_builder
    if "runMode" not in prompt_cfg:
        prompt_cfg["runMode"] = "standard"

    try:
        image_paths = ensure_images(args.case, case_cfg, root)
    except Exception as e:
        print(f"Image resolution failed: {e}", file=sys.stderr)
        return 1

    multi_note = None
    if len(image_paths) > 1:
        multi_note = f"{len(image_paths)} pages attached — transcribe all; use [page-break] between pages if required by profile."

    system, user = build_zones(prompt_cfg, multi_page_note=multi_note)

    # Claude Code often resolves @/absolute/path for file inclusion; include both forms.
    abs_lines = "\n".join(f"- @{p}" for p in image_paths)
    user += f"""

---
MANUSCRIPT IMAGES (vision required — transcribe from these files):
{abs_lines}

If your environment does not auto-load paths above, open this folder and attach the same images manually.
"""

    out_dir = root / "benchmark" / "test-results" / "claude-cli" / args.case
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "system.txt").write_text(system, encoding="utf-8")
    (out_dir / "user.txt").write_text(user, encoding="utf-8")

    print(f"Wrote:\n  {out_dir / 'system.txt'}\n  {out_dir / 'user.txt'}\n")
    print("Images:")
    for p in image_paths:
        print(f"  {p}")

    claude_bin = args.claude_bin or shutil.which("claude")
    if not claude_bin:
        claude_bin = str(Path.home() / ".local" / "bin" / "claude")
    if not Path(claude_bin).is_file():
        print(
            "\n`claude` not found. Install Claude Code or pass --claude-bin PATH.\n"
            "See benchmark/CLAUDE_CLI.md",
            file=sys.stderr,
        )
        return 0 if not args.exec else 1

    cmd = [
        claude_bin,
        "-p",
        "--add-dir",
        str(root),
        "--append-system-prompt",
        system,
        user,
    ]
    print("\nExample (run manually):")
    print(
        "  claude -p --add-dir \"$(pwd)\" "
        f'--append-system-prompt "$(cat {out_dir / "system.txt"})" '
        f' "$(cat {out_dir / "user.txt"})"'
    )

    if args.exec:
        print("\nRunning claude -p ...\n")
        r = subprocess.run(cmd, cwd=str(root))
        return int(r.returncode)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
