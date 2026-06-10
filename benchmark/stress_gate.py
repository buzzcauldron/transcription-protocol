"""Parse, schema-check, and ground-truth-evaluate raw transcriber output (shared by stress_run and stress_replay)."""

from __future__ import annotations

from typing import Any, Dict

from .parse_transcript import get_transcription_root, parse_transcription_yaml
from .stress_metrics import EXPANDED_GT_EVALUATORS, run_evaluator
from .validate_schema import validate_transcription_output


def _preserve_original_abbreviations(root_out: dict) -> bool | None:
    """Return metadata toggle value, or None if toggles are missing."""
    meta = root_out.get("metadata") or {}
    toggles = meta.get("diplomaticToggles")
    if not isinstance(toggles, dict):
        return None
    val = toggles.get("preserveOriginalAbbreviations")
    if val is None:
        return None
    return bool(val)


def gates_from_raw(raw: str, evaluator: str) -> Dict[str, Any]:
    """
    Run YAML parse, schema gate, and evaluator metrics on raw model text.

    Returns a dict suitable for one matrix row (without case / model columns):
    schema_ok, addition_count, omission_count, disposition, score, notes.
    """
    notes_parts: list[str] = []
    schema_ok = False
    addition_count: Any = "—"
    omission_count: Any = "—"
    disposition = "FAIL"
    score: Any = "—"

    data, err = parse_transcription_yaml(raw)
    if err:
        notes_parts.append(err)
        return {
            "schema_ok": False,
            "addition_count": "—",
            "omission_count": "—",
            "disposition": "FAIL",
            "score": "—",
            "notes": " ".join(notes_parts),
        }

    root_out, rerr = get_transcription_root(data)
    if rerr:
        notes_parts.append(rerr)
        return {
            "schema_ok": False,
            "addition_count": "—",
            "omission_count": "—",
            "disposition": "FAIL",
            "score": "—",
            "notes": " ".join(notes_parts),
        }

    schema_ok, schema_errors, schema_warnings = validate_transcription_output(root_out)
    if not schema_ok:
        notes_parts.append("; ".join(schema_errors[:5]))
        if len(schema_errors) > 5:
            notes_parts.append(f"(+{len(schema_errors) - 5} more)")
    if schema_warnings:
        notes_parts.append("Warnings: " + "; ".join(schema_warnings))

    expansion_blocked = False
    if evaluator in EXPANDED_GT_EVALUATORS:
        preserve_abbrevs = _preserve_original_abbreviations(root_out)
        if preserve_abbrevs is True:
            notes_parts.append(
                "expansion firewall (protocol §2.4.1): diplomatic output "
                "(preserveOriginalAbbreviations: true) cannot be scored against expanded GT"
            )
            expansion_blocked = True

    segs = root_out.get("segments") or []
    if not isinstance(segs, list):
        segs = []
    if expansion_blocked:
        disposition = "FAIL"
    else:
        metrics = run_evaluator(evaluator, segs)
        if metrics.get("error"):
            notes_parts.append(metrics["error"])
            disposition = "FAIL"
        else:
            addition_count = metrics.get("addition_count", "")
            omission_count = metrics.get("omission_count", "")
            disposition = metrics.get("disposition", "")
            score = metrics.get("score", "")
            accuracy_percent = metrics.get("accuracy_percent", "")
            if not schema_ok:
                disposition = "FAIL"

    return {
        "schema_ok": schema_ok,
        "accuracy_percent": accuracy_percent,
        "addition_count": addition_count,
        "omission_count": omission_count,
        "disposition": disposition,
        "score": score,
        "notes": " ".join(notes_parts).strip() or "—",
    }
