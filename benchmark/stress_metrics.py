"""Ground-truth comparison for stress tests (evaluator types from manifest)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from ._eval_core import (
    disposition,
    normalize_for_comparison,
    rubric_score,
    word_diff,
)
from .ground_truth import (
    LINCOLN_GT_P1,
    LINCOLN_GT_P2,
    MEDIEVAL_GT,
    expand_medieval,
    normalize_medieval_latin,
)


def _sorted_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        segments,
        key=lambda s: (int(s.get("pageNumber", 0)), int(s.get("segmentId", 0))),
    )


def _text_from_segments(segments: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for seg in _sorted_segments(segments):
        t = seg.get("text")
        if t:
            parts.append(str(t))
    return "\n".join(parts)


def evaluate_lincoln(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_page: dict[int, list] = defaultdict(list)
    for seg in segments:
        try:
            pn = int(seg.get("pageNumber", 0))
        except (TypeError, ValueError):
            pn = 1
        by_page[pn].append(seg)
    p1_segs = sorted(by_page.get(1, []), key=lambda s: int(s.get("segmentId", 0)))
    p2_segs = sorted(by_page.get(2, []), key=lambda s: int(s.get("segmentId", 0)))
    t1 = "\n".join(str(s.get("text", "")) for s in p1_segs)
    t2 = "\n".join(str(s.get("text", "")) for s in p2_segs)
    tr_p1 = normalize_for_comparison(t1)
    tr_p2 = normalize_for_comparison(t2)
    tr_full = (tr_p1 + " " + tr_p2).strip()
    gt_p1 = normalize_for_comparison(LINCOLN_GT_P1)
    gt_p2 = normalize_for_comparison(LINCOLN_GT_P2)
    gt_full = (gt_p1 + " " + gt_p2).strip()
    matches, adds, omits = word_diff(gt_full, tr_full)
    total_gt = len(gt_full.split())
    accuracy = (matches / total_gt * 100) if total_gt else 0.0
    score = rubric_score(len(adds), len(omits))
    disp, crit, major = disposition(len(adds), len(omits))
    return {
        "evaluator": "lincoln",
        "matches": matches,
        "additions": adds,
        "omissions": omits,
        "addition_count": len(adds),
        "omission_count": len(omits),
        "ground_truth_words": total_gt,
        "accuracy_percent": round(accuracy, 2),
        "score": round(score, 4),
        "disposition": disp,
        "critical_flags": crit,
        "major_flags": major,
    }


def evaluate_medieval(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw = _text_from_segments(segments)
    tr_expanded = expand_medieval(raw)
    gt_norm = normalize_medieval_latin(MEDIEVAL_GT)
    tr_norm = normalize_medieval_latin(tr_expanded)
    matches, adds, omits = word_diff(gt_norm, tr_norm)
    total_gt = len(gt_norm.split())
    accuracy = (matches / total_gt * 100) if total_gt else 0.0
    score = rubric_score(len(adds), len(omits))
    disp, crit, major = disposition(len(adds), len(omits))
    return {
        "evaluator": "medieval",
        "matches": matches,
        "additions": adds,
        "omissions": omits,
        "addition_count": len(adds),
        "omission_count": len(omits),
        "ground_truth_words": total_gt,
        "accuracy_percent": round(accuracy, 2),
        "score": round(score, 4),
        "disposition": disp,
        "critical_flags": crit,
        "major_flags": major,
    }


EVALUATORS = {
    "lincoln": evaluate_lincoln,
    "medieval": evaluate_medieval,
}


def run_evaluator(evaluator_name: str, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    fn = EVALUATORS.get(evaluator_name)
    if not fn:
        return {"error": f"unknown evaluator: {evaluator_name}"}
    return fn(segments)


def file_to_base64(path: str) -> Tuple[str, str]:
    """Return (base64_str, media_type guess)."""
    from pathlib import Path

    p = Path(path)
    suf = p.suffix.lower()
    mt = "image/jpeg"
    if suf == ".png":
        mt = "image/png"
    elif suf == ".webp":
        mt = "image/webp"
    data = p.read_bytes()
    return base64.standard_b64encode(data).decode("ascii"), mt
