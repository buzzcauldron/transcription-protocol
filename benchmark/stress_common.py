"""Shared paths, manifest loading, and report writing for stress tools."""

from __future__ import annotations

from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_manifest(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_report_md(
    path: Path,
    rows: list[dict],
    started: str,
) -> None:
    lines = [
        "# Stress test compatibility matrix",
        "",
        f"Generated: {started} (UTC)",
        "",
        "| Case | Model | Schema OK | Additions | Omissions | Disposition | Score | Notes |",
        "|------|-------|-----------|-----------|------------|-------------|-------|-------|",
    ]
    for r in rows:
        notes = (r.get("notes") or "").replace("|", "\\|")
        lines.append(
            f"| {r.get('case', '')} | {r.get('model', '')} | {r.get('schema_ok', '')} | "
            f"{r.get('addition_count', '')} | {r.get('omission_count', '')} | "
            f"{r.get('disposition', '')} | {r.get('score', '')} | {notes} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
