"""
Shared word-level comparison helpers for benchmark and stress tests.
Aligned with benchmark/evaluate.py and quality-rubric addition/omission logic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Tuple, Union

# Sentinel: transcription token that absorbs one GT word without add/omit penalty.
WILDCARD = object()

DAMAGE_TOKEN_PATTERN = re.compile(
    r"\[(?:illegible|gap|damaged|glyph-uncertain|crop)(?::[^\]]*)?\]",
    re.IGNORECASE,
)

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


def tokenize_for_tolerant_scoring(text: str) -> List[Union[str, object]]:
    """Tokenize transcription text; damage tokens become WILDCARD sentinels."""
    text = text.replace("=\n", "")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.findall(r"\[[^\]]+\]|[^\s\[]+", text)
    tokens: List[Union[str, object]] = []
    for part in parts:
        if DAMAGE_TOKEN_PATTERN.fullmatch(part):
            tokens.append(WILDCARD)
            continue
        if part.startswith("[uncertain:"):
            inner = part[len("[uncertain:") :].rstrip("]").strip()
            tokens.append(inner.split("/")[0].strip())
            continue
        if part.startswith("[deletion:") or part.startswith("[marginalia:"):
            continue
        if part.startswith("[insertion:"):
            inner = part[len("[insertion:") :].rstrip("]").strip()
            tokens.append(inner)
            continue
        if part.startswith("[exp:"):
            inner = part[len("[exp:") :].rstrip("]").strip()
            tokens.append(inner)
            continue
        if part == "[wrap-join]":
            continue
        if part.startswith("["):
            continue
        tokens.append(part)
    return tokens


@dataclass
class TolerantDiffResult:
    matches: int
    substantive_matches: int
    wildcard_matches: int
    additions: List[str]
    omissions: List[str]


def word_diff_tolerant(
    gt_words: List[str], tr_tokens: List[Union[str, object]]
) -> TolerantDiffResult:
    """Align TR to GT; WILDCARD tokens absorb a GT word without add/omit penalty."""
    n, m = len(gt_words), len(tr_tokens)
    neg_inf = -10**9
    dp = [[neg_inf] * (m + 1) for _ in range(n + 1)]
    back: List[List[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0

    for i in range(n + 1):
        for j in range(m + 1):
            base = dp[i][j]
            if base == neg_inf:
                continue
            if i < n and j < m and tr_tokens[j] is WILDCARD:
                score = base + 2
                if score >= dp[i + 1][j + 1]:
                    dp[i + 1][j + 1] = score
                    back[i + 1][j + 1] = "W"
            if (
                i < n
                and j < m
                and tr_tokens[j] is not WILDCARD
                and gt_words[i] == tr_tokens[j]
            ):
                score = base + 3
                if score >= dp[i + 1][j + 1]:
                    dp[i + 1][j + 1] = score
                    back[i + 1][j + 1] = "M"
            if i < n:
                score = base - 1
                if score >= dp[i + 1][j]:
                    dp[i + 1][j] = score
                    back[i + 1][j] = "O"
            if j < m:
                score = base - (1 if tr_tokens[j] is WILDCARD else 2)
                if score >= dp[i][j + 1]:
                    dp[i][j + 1] = score
                    back[i][j + 1] = "A"

    additions: List[str] = []
    omissions: List[str] = []
    substantive_matches = 0
    wildcard_matches = 0
    i, j = n, m
    while i > 0 or j > 0:
        op = back[i][j]
        if op is None:
            if i > 0:
                omissions.append(gt_words[i - 1])
                i -= 1
            elif j > 0:
                tok = tr_tokens[j - 1]
                additions.append("[illegible]" if tok is WILDCARD else str(tok))
                j -= 1
            else:
                break
            continue
        if op == "W":
            wildcard_matches += 1
            i -= 1
            j -= 1
        elif op == "M":
            substantive_matches += 1
            i -= 1
            j -= 1
        elif op == "O":
            omissions.append(gt_words[i - 1])
            i -= 1
        elif op == "A":
            tok = tr_tokens[j - 1]
            additions.append("[illegible]" if tok is WILDCARD else str(tok))
            j -= 1

    omissions.reverse()
    additions.reverse()
    matches = substantive_matches + wildcard_matches
    return TolerantDiffResult(
        matches=matches,
        substantive_matches=substantive_matches,
        wildcard_matches=wildcard_matches,
        additions=additions,
        omissions=omissions,
    )


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
