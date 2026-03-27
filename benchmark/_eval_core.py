"""
Shared word-level comparison helpers for benchmark and stress tests.
Aligned with benchmark/evaluate.py and quality-rubric addition/omission logic.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import List, Tuple

TOKEN_PATTERN = re.compile(
    r"\[(?:illegible|uncertain|gap|damaged|glyph-uncertain|"
    r"deletion|insertion|marginalia|superscript|exp|wrap-join)[^]]*\]"
)


def strip_tokens(text: str) -> str:
    def replace_token(m):
        tok = m.group(0)
        if tok.startswith("[uncertain:"):
            inner = tok[len("[uncertain:") :].rstrip("]").strip()
            return inner.split("/")[0].strip()
        if tok.startswith("[deletion:"):
            return ""
        if tok.startswith("[insertion:"):
            inner = tok[len("[insertion:") :].rstrip("]").strip()
            return inner
        if tok.startswith("[marginalia:"):
            return ""
        if tok.startswith("[exp:"):
            inner = tok[len("[exp:") :].rstrip("]").strip()
            return inner
        if tok == "[wrap-join]":
            return ""
        return ""

    return TOKEN_PATTERN.sub(replace_token, text)


def normalize_for_comparison(text: str) -> str:
    text = strip_tokens(text)
    text = text.replace("=\n", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_diff(ground_truth: str, transcription: str) -> Tuple[int, List[str], List[str]]:
    gt_words = ground_truth.split()
    tr_words = transcription.split()
    sm = SequenceMatcher(None, gt_words, tr_words)
    additions: List[str] = []
    omissions: List[str] = []
    matches = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            matches += i2 - i1
        elif op == "insert":
            additions.extend(tr_words[j1:j2])
        elif op == "delete":
            omissions.extend(gt_words[i1:i2])
        elif op == "replace":
            omissions.extend(gt_words[i1:i2])
            additions.extend(tr_words[j1:j2])
    return matches, additions, omissions


def rubric_score(addition_count: int, omission_count: int) -> float:
    score = 1.0 - 0.20 * addition_count - 0.15 * omission_count
    return max(0.0, score)


def disposition(
    addition_count: int, omission_count: int
) -> Tuple[str, List[str], List[str]]:
    critical: List[str] = []
    major: List[str] = []
    if addition_count > 0:
        critical.append("substantive_additions")
    if omission_count > 3:
        critical.append("significant_omissions")
    elif omission_count > 0:
        major.append("minor_omissions")
    if critical:
        return "FAIL", critical, major
    if major:
        return "CONDITIONAL_PASS", critical, major
    return "PASS", critical, major
