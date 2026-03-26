"""Minimal schema gate aligned with OUTPUT_SCHEMA.md and QUALITY_RUBRIC §1.5."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

UNCERTAIN_PATTERN = re.compile(r"\[uncertain:", re.IGNORECASE)
# Whitespace-delimited words (rough, for density check)
WORD_PATTERN = re.compile(r"\S+")

VALID_LANGUAGES_PREFIXES = (
    "eng-",
    "lat-",
    "fra-",
    "deu-",
    "spa-",
    "ita-",
    "por-",
    "nld-",
    "ell-",
    "ara-",
    "ota-",
    "heb-",
    "rus-",
    "zho-",
    "jpn-",
    "kor-",
    "san-",
)
VALID_ERAS = (
    "medieval",
    "early_modern",
    "enlightenment",
    "nineteenth_century",
    "twentieth_century",
    "contemporary",
)
VALID_PROFILES = ("strict", "semi_strict", "layout_aware", "diplomatic_plus")
ENGLISH_HANDWRITING_MODALITY = (
    "unspecified",
    "insular_anglicana",
    "court_chancery",
    "secretary",
    "italic",
    "round_hand",
    "copperplate",
    "spencerian",
    "palmer_business",
    "school_cursive",
    "mixed_english_hands",
)
VALID_CONFIDENCE = ("high", "medium", "low")
VALID_POSITION = (
    "body",
    "header",
    "footer",
    "margin_left",
    "margin_right",
    "margin_top",
    "margin_bottom",
    "interlinear",
    "footnote",
)

UNCERTAINTY_FLOOD_THRESHOLD = 0.30
MIN_CONDITION_NOTES_LEN = 20
# Aggregate length of segment `notes` — same threshold spirit as conditionNotes (§5.6 / §1.1 carve-out).
MIN_SEGMENT_NOTES_AGGREGATE_LEN = 20


def _concat_segment_texts(segs: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for seg in segs:
        if isinstance(seg, dict) and seg.get("text"):
            parts.append(str(seg["text"]))
    return "\n".join(parts)


def _aggregate_segment_notes_len(segs: List[Dict[str, Any]]) -> int:
    total = 0
    for seg in segs:
        if not isinstance(seg, dict):
            continue
        n = seg.get("notes")
        if n is not None and isinstance(n, str):
            total += len(n.strip())
    return total


def _uncertainty_flood_error(
    full_text: str,
    pre: Dict[str, Any] | None,
    segments: List[Dict[str, Any]] | None,
) -> str | None:
    """Protocol §5.6: too many [uncertain: tokens vs words; carve-out when documented."""
    if not full_text.strip():
        return None
    words = WORD_PATTERN.findall(full_text)
    n_words = len(words)
    if n_words == 0:
        return None
    n_unc = len(UNCERTAIN_PATTERN.findall(full_text))
    ratio = n_unc / n_words
    if ratio <= UNCERTAINTY_FLOOD_THRESHOLD:
        return None
    cn = (pre or {}).get("conditionNotes")
    long_condition_notes = (
        cn is not None
        and isinstance(cn, str)
        and len(cn.strip()) >= MIN_CONDITION_NOTES_LEN
    )
    long_segment_notes = (
        segments is not None
        and _aggregate_segment_notes_len(segments) >= MIN_SEGMENT_NOTES_AGGREGATE_LEN
    )
    if long_condition_notes or long_segment_notes:
        return None
    return (
        f"uncertainty flooding: {n_unc} [uncertain: markers vs ~{n_words} tokens "
        f"(>{UNCERTAINTY_FLOOD_THRESHOLD:.0%}); expand conditionNotes or segment notes, "
        f"or reduce spurious uncertainty"
    )


def _req(d: Dict[str, Any], key: str, errors: List[str]) -> Any:
    """Field must be present; `null` is allowed (OUTPUT_SCHEMA uses null for several keys)."""
    if key not in d:
        errors.append(f"missing required field: {key}")
        return None
    return d[key]


def validate_transcription_output(root: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    pv = root.get("protocolVersion")
    if pv != "v1.0":
        errors.append(f"protocolVersion must be v1.0, got {pv!r}")

    meta = root.get("metadata")
    if not isinstance(meta, dict):
        errors.append("metadata must be an object")
    else:
        for k in (
            "sourcePageId",
            "modelId",
            "timestamp",
            "protocolVersion",
            "targetLanguage",
            "languageSet",
            "targetEra",
            "diplomaticProfile",
            "normalizationMode",
        ):
            _req(meta, k, errors)
        tl = meta.get("targetLanguage")
        if tl and tl != "mixed" and not any(
            tl.startswith(p) for p in VALID_LANGUAGES_PREFIXES
        ):
            if not (len(tl) >= 7 and "-" in tl):
                errors.append(f"targetLanguage may be invalid: {tl!r}")
        te = meta.get("targetEra")
        if te and te not in VALID_ERAS:
            errors.append(f"targetEra not in controlled list: {te!r}")
        dp = meta.get("diplomaticProfile")
        if dp and dp not in VALID_PROFILES:
            errors.append(f"diplomaticProfile invalid: {dp!r}")
        nm = meta.get("normalizationMode")
        if nm and nm not in ("diplomatic", "normalized"):
            errors.append(f"normalizationMode must be diplomatic or normalized: {nm!r}")
        toggles = meta.get("diplomaticToggles")
        if toggles is not None and not isinstance(toggles, dict):
            errors.append("diplomaticToggles must be an object")
        mixed = meta.get("mixedContent")
        if mixed is not None and not isinstance(mixed, dict):
            errors.append("mixedContent must be an object")
        ehm = meta.get("englishHandwritingModality")
        if ehm is not None and ehm not in ENGLISH_HANDWRITING_MODALITY:
            errors.append(
                f"englishHandwritingModality invalid: {ehm!r} (see protocol §2.8)"
            )
        if ehm is not None and tl and not str(tl).startswith("eng") and tl != "mixed":
            errors.append(
                "englishHandwritingModality should be null when targetLanguage is not English"
            )
        if "epistemicNotes" in meta:
            en = meta.get("epistemicNotes")
            if en is not None and (
                not isinstance(en, str) or len(en.strip()) == 0
            ):
                errors.append(
                    "epistemicNotes must be null or a non-empty string (protocol §1.1)"
                )

    pre = root.get("preCheck")
    if not isinstance(pre, dict):
        errors.append("preCheck must be an object")
    else:
        for k in (
            "resolutionAdequate",
            "orientationCorrect",
            "pageBoundariesVisible",
            "pageCount",
            "scriptIdentified",
            "scriptMatchesConfig",
            "conditionNotes",
            "proceedDecision",
            "abortReason",
        ):
            _req(pre, k, errors)
        if pre.get("proceedDecision") == "abort":
            segs = root.get("segments")
            if segs not in ([], None):
                errors.append("segments must be empty when proceedDecision is abort")

    segs = root.get("segments")
    if not isinstance(segs, list):
        errors.append("segments must be a list")
    elif pre and pre.get("proceedDecision") == "proceed" and len(segs) == 0:
        errors.append("segments empty but proceedDecision is proceed")

    if isinstance(segs, list):
        for i, seg in enumerate(segs):
            if not isinstance(seg, dict):
                errors.append(f"segment {i} must be an object")
                continue
            for k in (
                "segmentId",
                "pageNumber",
                "lineRange",
                "position",
                "text",
                "confidence",
                "uncertaintyTokenCount",
            ):
                _req(seg, k, errors)
            if seg.get("confidence") not in VALID_CONFIDENCE:
                errors.append(f"segment {i} confidence invalid")
            if seg.get("position") not in VALID_POSITION:
                errors.append(f"segment {i} position invalid")

    mr = root.get("mismatchReport")
    if mr is None:
        errors.append("mismatchReport is required (list; non-empty when segments exist per v1.1)")
    elif not isinstance(mr, list):
        errors.append("mismatchReport must be a list")
    elif (
        isinstance(segs, list)
        and len(segs) > 0
        and isinstance(mr, list)
        and len(mr) == 0
    ):
        errors.append(
            "mismatchReport must not be empty when segments is non-empty (protocol v1.1 §5.2)"
        )

    if isinstance(segs, list) and segs:
        flood_err = _uncertainty_flood_error(
            _concat_segment_texts(segs),
            pre if isinstance(pre, dict) else None,
            segs,
        )
        if flood_err:
            errors.append(flood_err)

    ok = len(errors) == 0
    return ok, errors
