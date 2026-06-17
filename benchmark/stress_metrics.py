"""Ground-truth comparison for stress tests (evaluator types from manifest)."""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, List, Set, Union

from ._eval_core import (
    WILDCARD,
    disposition,
    normalize_for_comparison,
    rubric_score,
    tokenize_for_tolerant_scoring,
    word_diff,
    word_diff_tolerant,
)
from .ground_truth import (
    DEED_WHITE_GT,
    DONNE_GT,
    JOHNSON_GT,
    KB27_GT,
    LINCOLN_GT_P1,
    LINCOLN_GT_P2,
    LONDON_CW_1854_GT,
    LOVEJOY_GT,
    MEDIEVAL_GT,
    expand_medieval,
    normalize_medieval_latin,
)

MODERN_GT_BY_EVALUATOR = {
    "modern_lovejoy": LOVEJOY_GT,
    "modern_johnson": JOHNSON_GT,
    "modern_deed": DEED_WHITE_GT,
}

# Wildcard-aligned words above this share of GT without substantive coverage → gaming.
_MODERN_WILDCARD_CEILING = 0.15

# Evaluators whose ground truth is expanded (full words); protocol §2.4.1 firewall applies.
EXPANDED_GT_EVALUATORS: Set[str] = {"medieval", "legal"}


def _strip_combining_marks(text: str) -> str:
    """Remove Unicode combining marks (macrons, tildes) from diplomatic residue."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _prepare_expanded_latin(text: str) -> str:
    """Normalize transcription toward expanded Latin before comparison to expanded GT."""
    text = normalize_for_comparison(text)
    text = _strip_combining_marks(text)
    return expand_medieval(text)


def _normalize_loose(text: str) -> str:
    """Case/punctuation-insensitive normalization for word-level scoring.

    Strips uncertainty/markup tokens, joins line-break hyphenation (``=``),
    drops paragraph marks and punctuation, lowercases, and collapses whitespace.
    Used by the legal and early-modern evaluators where the only meaningful
    signal is the word sequence, not capitalization or pointing.
    """
    text = normalize_for_comparison(text)
    text = text.replace("=", "")
    text = text.lower()
    text = re.sub(r"[¶.,:;()\"']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
    gt_norm = normalize_medieval_latin(_prepare_expanded_latin(MEDIEVAL_GT))
    tr_norm = normalize_medieval_latin(_prepare_expanded_latin(raw))
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


def evaluate_legal(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """KB27.335 King's Bench plea roll (c.1340 legal anglicana), expanded PAGE-XML GT."""
    tr = _normalize_loose(_prepare_expanded_latin(_text_from_segments(segments)))
    gt = _normalize_loose(_prepare_expanded_latin(KB27_GT))
    matches, adds, omits = word_diff(gt, tr)
    total_gt = len(gt.split())
    accuracy = (matches / total_gt * 100) if total_gt else 0.0
    score = rubric_score(len(adds), len(omits))
    disp, crit, major = disposition(len(adds), len(omits))
    return {
        "evaluator": "legal",
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


def _modern_tr_tokens(text: str) -> List[Union[str, object]]:
    tokens = tokenize_for_tolerant_scoring(text)
    out: List[Union[str, object]] = []
    for tok in tokens:
        if tok is WILDCARD:
            out.append(WILDCARD)
            continue
        clean = re.sub(r"[¶.,:;()\"']", " ", str(tok).lower())
        for word in clean.split():
            if word:
                out.append(word)
    return out


def _evaluate_modern(segments: List[Dict[str, Any]], gt: str, evaluator: str) -> Dict[str, Any]:
    """19th-c. English correspondence/deeds; tolerant of honest damage tokens."""
    gt_words = _normalize_loose(gt).split()
    tr_tokens = _modern_tr_tokens(_text_from_segments(segments))
    diff = word_diff_tolerant(gt_words, tr_tokens)
    total_gt = len(gt_words)
    accuracy = (diff.matches / total_gt * 100) if total_gt else 0.0
    score = rubric_score(len(diff.additions), len(diff.omissions))
    disp, crit, major = disposition(len(diff.additions), len(diff.omissions))
    if total_gt and diff.wildcard_matches / total_gt > _MODERN_WILDCARD_CEILING:
        crit = list(crit) + ["uncertainty_gaming"]
        disp = "FAIL"
    if total_gt and diff.substantive_matches == 0 and diff.wildcard_matches > 0:
        crit = list(crit) + ["uncertainty_gaming"]
        disp = "FAIL"
    return {
        "evaluator": evaluator,
        "matches": diff.matches,
        "substantive_matches": diff.substantive_matches,
        "wildcard_matches": diff.wildcard_matches,
        "additions": diff.additions,
        "omissions": diff.omissions,
        "addition_count": len(diff.additions),
        "omission_count": len(diff.omissions),
        "ground_truth_words": total_gt,
        "accuracy_percent": round(accuracy, 2),
        "score": round(score, 4),
        "disposition": disp,
        "critical_flags": crit,
        "major_flags": major,
    }


def evaluate_modern_lovejoy(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _evaluate_modern(segments, LOVEJOY_GT, "modern_lovejoy")


def evaluate_modern_johnson(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _evaluate_modern(segments, JOHNSON_GT, "modern_johnson")


def evaluate_modern_deed(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _evaluate_modern(segments, DEED_WHITE_GT, "modern_deed")


def evaluate_london_cw_1854(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """London, Canada West, 3 Sep 1854 Scottish emigrant letter — researcher's partial GT."""
    return _evaluate_modern(segments, LONDON_CW_1854_GT, "london_cw_1854")


def evaluate_earlymodern(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Donne -> Egerton letter (1602 secretary hand), EMMO diplomatic, body only."""
    tr = _normalize_loose(_text_from_segments(segments))
    gt = _normalize_loose(DONNE_GT)
    matches, adds, omits = word_diff(gt, tr)
    total_gt = len(gt.split())
    accuracy = (matches / total_gt * 100) if total_gt else 0.0
    score = rubric_score(len(adds), len(omits))
    disp, crit, major = disposition(len(adds), len(omits))
    return {
        "evaluator": "earlymodern",
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
    "legal": evaluate_legal,
    "earlymodern": evaluate_earlymodern,
    "modern_lovejoy": evaluate_modern_lovejoy,
    "modern_johnson": evaluate_modern_johnson,
    "modern_deed": evaluate_modern_deed,
    "london_cw_1854": evaluate_london_cw_1854,
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
