"""Shared paths, manifest loading, and report writing for stress tools."""

from __future__ import annotations

from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_env_file(root: Path | None = None) -> None:
    """Load ``root/.env`` into ``os.environ`` when ``python-dotenv`` is installed.

    No-op if the file is missing or the package is not installed (set keys in the shell instead).
    """
    r = root or repo_root()
    env_path = r / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env_path, override=False)


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
