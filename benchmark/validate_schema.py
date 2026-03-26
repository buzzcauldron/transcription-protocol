"""Minimal schema gate aligned with OUTPUT_SCHEMA.md and QUALITY_RUBRIC §1.5.

protocolVersion accepts semver (1.0.0, 1.1.0) and legacy v1.0 / v1.1 aliases.
"""

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
# Semantic versioning (MAJOR.MINOR.PATCH). Legacy `v1.x` strings remain accepted as aliases.
PROTOCOL_VERSION_ALIASES: Dict[str, str] = {
    "1.0.0": "1.0.0",
    "1.1.0": "1.1.0",
    "v1.0": "1.0.0",
    "v1.1": "1.1.0",
}
VALID_PROTOCOL_VERSIONS = tuple(PROTOCOL_VERSION_ALIASES.keys())


def _canonical_protocol_version(pv: Any) -> str | None:
    if pv is None or not isinstance(pv, str):
        return None
    return PROTOCOL_VERSION_ALIASES.get(pv)
VALID_RUN_MODES = ("standard", "efficient")
EFFICIENT_INCOMPATIBLE_PROFILES = ("layout_aware", "diplomatic_plus")
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

# Protocol §2.9 / §3: extended & special tokens must not appear in segment text when runMode is efficient.
_EFFICIENT_FORBIDDEN_TOKEN_CHECKS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\[exp:", re.IGNORECASE), "[exp: …]"),
    (re.compile(r"\[wrap-join\]", re.IGNORECASE), "[wrap-join]"),
    (re.compile(r"\[deletion:", re.IGNORECASE), "[deletion: …]"),
    (re.compile(r"\[insertion:", re.IGNORECASE), "[insertion: …]"),
    (re.compile(r"\[marginalia:", re.IGNORECASE), "[marginalia: …]"),
    (re.compile(r"\[superscript:", re.IGNORECASE), "[superscript: …]"),
    (re.compile(r"\[page-break\]", re.IGNORECASE), "[page-break]"),
    (re.compile(r"\[palimpsest:", re.IGNORECASE), "[palimpsest: …]"),
    (re.compile(r"\[line-end-hyphen\]", re.IGNORECASE), "[line-end-hyphen]"),
)


def _efficient_forbidden_tokens_in_text(text: str) -> List[str]:
    """Return human-readable token labels found in text (standard-only tokens)."""
    found: List[str] = []
    seen: set[str] = set()
    for pat, label in _EFFICIENT_FORBIDDEN_TOKEN_CHECKS:
        if pat.search(text) and label not in seen:
            found.append(label)
            seen.add(label)
    return found


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
        f"(>{UNCERTAINTY_FLOOD_THRESHOLD:.0%}); document the specific physical/paleographic "
        f"cause in conditionNotes (>=20 chars) or segment notes (aggregate >=20 chars)"
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
    canon_pv = _canonical_protocol_version(pv)
    if canon_pv is None:
        errors.append(
            f"protocolVersion must be one of {sorted(VALID_PROTOCOL_VERSIONS)}, got {pv!r}"
        )

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
        if "schemaRevision" in meta:
            sr = meta.get("schemaRevision")
            if sr is not None and not isinstance(sr, str):
                errors.append("schemaRevision must be null or a date string (protocol §9)")
        rm = meta.get("runMode")
        if rm is not None and rm not in VALID_RUN_MODES:
            errors.append(f"runMode must be one of {VALID_RUN_MODES}, got {rm!r}")
        if rm == "efficient":
            dp = meta.get("diplomaticProfile")
            if dp in EFFICIENT_INCOMPATIBLE_PROFILES:
                errors.append(
                    f"runMode 'efficient' is incompatible with diplomaticProfile "
                    f"'{dp}' (requires profile-specific tokens; protocol §2.9)"
                )
        mpv = meta.get("protocolVersion")
        canon_mpv = _canonical_protocol_version(mpv)
        if canon_mpv is None:
            errors.append(
                f"metadata.protocolVersion must be one of {sorted(VALID_PROTOCOL_VERSIONS)}, "
                f"got {mpv!r}"
            )
        if canon_pv is not None and canon_mpv is not None and canon_pv != canon_mpv:
            errors.append(
                "metadata.protocolVersion must denote the same protocol as "
                "transcriptionOutput.protocolVersion (e.g. v1.1 and 1.1.0 are equivalent)"
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
        if "proceedOverride" in pre:
            po = pre.get("proceedOverride")
            if po is True:
                cn = pre.get("conditionNotes")
                if (
                    not cn
                    or not isinstance(cn, str)
                    or len(cn.strip()) < MIN_CONDITION_NOTES_LEN
                ):
                    errors.append(
                        "proceedOverride is true but conditionNotes does not document the override reason "
                        f"(protocol §4.1; require >= {MIN_CONDITION_NOTES_LEN} chars, same threshold as §5.6)"
                    )
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

    run_mode = (meta or {}).get("runMode", "standard") if isinstance(meta, dict) else "standard"
    is_efficient = run_mode == "efficient"

    if is_efficient and isinstance(segs, list):
        for i, seg in enumerate(segs):
            if not isinstance(seg, dict):
                continue
            t = seg.get("text")
            if not isinstance(t, str):
                continue
            forbidden = _efficient_forbidden_tokens_in_text(t)
            if forbidden:
                errors.append(
                    f"segment {i} text contains standard-only token(s) "
                    f"{', '.join(forbidden)} but runMode is efficient (protocol §2.9, §3)"
                )

    mr = root.get("mismatchReport")
    p2s_early = root.get("pass2Summary")
    pass2_clean = isinstance(p2s_early, dict) and p2s_early.get("segmentsAltered") == 0

    if mr is None:
        # Standard mode: Pass 2 / mismatchReport only when there is body text to verify (§5.2, §7.4.6).
        # Aborted runs (empty segments) need not include mismatchReport.
        # Omission is allowed when pass2Summary has segmentsAltered: 0 (clean pass-2 shorthand; protocol §5.2).
        if (
            not is_efficient
            and isinstance(segs, list)
            and len(segs) > 0
            and not pass2_clean
        ):
            errors.append(
                "mismatchReport is required when segments is non-empty (protocol 1.1.0 §5.2), "
                "unless pass2Summary is present with segmentsAltered: 0"
            )
    elif not isinstance(mr, list):
        errors.append("mismatchReport must be a list")
    elif (
        isinstance(segs, list)
        and len(segs) > 0
        and isinstance(mr, list)
        and len(mr) == 0
        and not is_efficient
    ):
        if not pass2_clean:
            errors.append(
                "mismatchReport must not be empty when segments is non-empty "
                "(protocol 1.1.0 §5.2) unless pass2Summary is present with segmentsAltered: 0"
            )

    p2s = root.get("pass2Summary")
    if isinstance(p2s, dict):
        sr = p2s.get("segmentsReviewed")
        sa = p2s.get("segmentsAltered")
        if sr is not None and not isinstance(sr, int):
            errors.append("pass2Summary.segmentsReviewed must be an integer")
        if sa is not None and not isinstance(sa, int):
            errors.append("pass2Summary.segmentsAltered must be an integer")
        if isinstance(sa, int) and sa > 0:
            if not isinstance(mr, list):
                errors.append(
                    "pass2Summary.segmentsAltered > 0 requires mismatchReport listing each altered segment "
                    "(protocol §5.2)"
                )
            else:
                altered_ids = {
                    e.get("segmentId")
                    for e in mr
                    if isinstance(e, dict) and e.get("segmentId") is not None
                }
                if len(altered_ids) < sa:
                    errors.append(
                        f"pass2Summary.segmentsAltered is {sa} but mismatchReport "
                        f"only covers {len(altered_ids)} segment(s)"
                    )

    audit = root.get("hallucinationAudit")
    if audit is None:
        errors.append(
            "hallucinationAudit is required (protocol §7.4 item 5; hard fail if absent)"
        )
    elif not isinstance(audit, dict):
        errors.append("hallucinationAudit must be an object")
    else:
        ap = audit.get("auditPass")
        checks = audit.get("checks")
        check_pass_bools: list[bool] = []
        if isinstance(checks, dict):
            for ck_name, ck_val in checks.items():
                if not isinstance(ck_val, dict) or "pass" not in ck_val:
                    continue
                pv = ck_val.get("pass")
                if pv is True:
                    check_pass_bools.append(True)
                elif pv is False:
                    check_pass_bools.append(False)
                else:
                    errors.append(
                        f"hallucinationAudit.checks.{ck_name}.pass must be boolean true or false"
                    )
        if check_pass_bools:
            expected_audit_pass = all(check_pass_bools)
            if ap is not expected_audit_pass:
                errors.append(
                    "hallucinationAudit.auditPass must equal the logical AND of "
                    "checks.*.pass (OUTPUT_SCHEMA §6b; protocol §7.3)"
                )
        if ap is not True:
            errors.append(
                "hallucinationAudit.auditPass must be true (protocol §7.4 item 5; "
                "false or missing is a hard fail)"
            )
        wfe = audit.get("wordsFromExpansion")
        ewm = audit.get("expansionsWithVisibleMark")
        if (
            isinstance(wfe, (int, float))
            and isinstance(ewm, (int, float))
            and ewm < wfe
        ):
            errors.append(
                f"hallucinationAudit: expansionsWithVisibleMark ({ewm}) < "
                f"wordsFromExpansion ({wfe}) — expansion without visible mark (§7.3)"
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
