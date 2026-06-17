"""Build transcriber system + user text from prompt-templates.md § 1 (Transcriber Prompt).

System rules are loaded directly from prompt-templates.md so benchmark tests
validate the same prompt text that is distributed to users.  The CONFIGURATION
block and YAML output schema are still generated dynamically (they depend on
per-run manifest values).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_system_rules(protocol_version: str = "1.2.0") -> str:
    """Extract system rules from § 1 of prompt-templates.md.

    Strips the CONFIGURATION block (generated dynamically by build_user_text)
    and the OUTPUT FORMAT section (replaced by the detailed YAML schema).
    Appends the two final emit-format lines that are not in the md template.
    """
    md_path = _REPO_ROOT / "prompt-templates.md"
    text = md_path.read_text(encoding="utf-8")

    m = re.search(r"## 1\. Transcriber Prompt\b.*?````\n(.*?)````", text, re.DOTALL)
    if not m:
        raise FileNotFoundError(
            f"Section '## 1. Transcriber Prompt' not found in {md_path}"
        )
    block = m.group(1)

    # Header = everything before CONFIGURATION:
    cfg_start = block.index("\nCONFIGURATION:")
    header = block[:cfg_start].strip()

    # Rules = CONFIDENCE AND HONESTY … last sentence before OUTPUT FORMAT:
    rules_start = block.index("\nCONFIDENCE AND HONESTY")
    out_start = block.find("\nOUTPUT FORMAT:")
    rules = block[rules_start:out_start].strip()

    combined = header + "\n\n" + rules

    # Substitute static placeholder; leave config-dependent ones as descriptive text
    combined = combined.replace("{protocolVersion}", protocol_version)
    combined = re.sub(r"\{targetLanguage\}", "<configured language/script>", combined)
    combined = re.sub(r"\{targetEra\}", "<configured era>", combined)
    combined = re.sub(r"\{diplomaticProfile\}", "<configured profile>", combined)
    combined = re.sub(r"\{[a-zA-Z]+\}", "", combined)

    combined += (
        "\n\nBegin your response with the YAML document. "
        "Do not include conversational preamble before the YAML.\n"
        "Emit raw YAML only in the transcriptionOutput structure — "
        "do not wrap in markdown code fences unless unavoidable."
    )
    return combined


# Loaded once at import time; shared across all calls in a process.
SYSTEM_RULES = _load_system_rules()

# Efficient mode: same rules — the md's EFFICIENT MODE section covers it.
SYSTEM_RULES_EFFICIENT = SYSTEM_RULES


def _render_toggles(prompt_cfg: Dict[str, Any]) -> str:
    """Build the diplomaticToggles YAML block from actual config values.

    The schema template used to hardcode ``preserveOriginalAbbreviations: true``.
    That caused models to echo ``true`` in their output metadata even when the
    configuration said ``false``, because the output-schema example dominated
    over the configuration block.  This function renders the *real* values from
    the config so the model sees a consistent, binding example.
    """
    defaults: Dict[str, Any] = {
        "preserveLineBreaks": True,
        "preserveOriginalAbbreviations": True,
        "markExpansions": False,
        "captureDeletionsAndInsertions": False,
        "captureUnclearGlyphShape": True,
    }
    raw = prompt_cfg.get("diplomaticToggles", {})
    if isinstance(raw, str):
        try:
            parsed: Dict[str, Any] = json.loads(raw)
        except Exception:
            parsed = {}
    elif isinstance(raw, dict):
        parsed = dict(raw)
    else:
        parsed = {}
    merged = {**defaults, **parsed}
    lines = ["    diplomaticToggles:"]
    for k, v in merged.items():
        lines.append(f"      {k}: {str(v).lower()}")
    return "\n".join(lines)

_SCHEMA_USER_PREFIX = """
OUTPUT FORMAT (required — follow exactly; all fields mandatory unless noted):

BINDING RULE — diplomaticToggles: The toggle values shown below come directly
from your CONFIGURATION block above.  You MUST echo them back exactly as shown;
do NOT substitute protocol defaults.

If preserveOriginalAbbreviations is TRUE (diplomatic mode): your transcription
MUST preserve every abbreviation mark exactly as it appears in the manuscript.
Unicode combining diacritics (U+0305 macron, U+0303 tilde, superscript letters,
suspension strokes, etc.) MUST be retained verbatim.  Do NOT expand any
abbreviation — not even common ones like ẽt → et, p̃ → per, q̃d → quod.
Expansion is a HARD PROTOCOL VIOLATION when preserveOriginalAbbreviations is true.

If preserveOriginalAbbreviations is FALSE (normalized mode): your transcription
MUST contain only fully expanded words — no Unicode combining diacritics
(U+0305 macron, U+0303 tilde, etc.), no superscript abbreviation letters.

transcriptionOutput:
  protocolVersion: "{pv}"
  metadata:
    sourcePageId: "<from configuration>"
    modelId: "<provider model id you are running under>"
    timestamp: "<ISO-8601 UTC>"
    protocolVersion: "{pv}"
    targetLanguage: "<from configuration>"
    languageSet: []
    targetEra: "<from configuration>"
    eraRange: "<from configuration or null>"
    diplomaticProfile: "<from configuration>"
"""

# _SCHEMA_USER_SUFFIX_TAIL is appended after the dynamically-rendered toggle block.
_SCHEMA_USER_SUFFIX_TAIL = """    normalizationMode: "<from configuration>"
    runMode: "<from configuration, default standard>"
    mixedContent: { mixedLanguage: false, mixedEra: false }
    scriptNotes: null
    englishHandwritingModality: null   # or protocol §2.8 tag when targetLanguage is eng-Latn
    epistemicNotes: null   # optional; run-level limits and residual uncertainty (protocol §1.1)
    schemaRevision: null   # optional; companion-doc revision date (protocol §9)
  preCheck:
    resolutionAdequate: true/false
    orientationCorrect: true/false
    pageBoundariesVisible: true/false
    pageCount: <integer>
    scriptIdentified: "string"
    scriptMatchesConfig: true/false
    conditionNotes: null
    proceedDecision: "proceed" | "abort"
    proceedOverride: false   # true when researcher overrides failed pre-check (§4.1)
    abortReason: null
  segments:
    - segmentId: 1
      pageNumber: 1
      lineRange: "1-10"
      position: "body"
      text: |
        <verbatim transcription>
      confidence: "medium"   # default typical; use "high" only for unambiguous stretches, "low" when difficult (§1.1)
      uncertaintyTokenCount: <integer matching token count in text>
      notes: null
  # If Pass 2 found NO changes across any segment, use the compact shorthand:
  pass2Summary:
    segmentsReviewed: <integer — total segments reviewed>
    segmentsAltered: 0
    notes: "Pass 2 complete. All readings confirmed; no edits made."
  mismatchReport: null   # set to null only when pass2Summary.segmentsAltered is 0
  # If Pass 2 changed ANY segment, set mismatchReport to a list and omit pass2Summary:
  # mismatchReport:
  #   - mismatchId: 1
  #     segmentId: 1
  #     pass1Reading: "<prior draft reading>"
  #     pass2Reading: "<corrected reading after pass 2>"
  #     resolution: "<explanation of change>"
  #     resolved: true
  hallucinationAudit:
    totalWords: <integer approx. word count across segments>
    wordsGroundedInGlyphs: <integer>
    wordsFromExpansion: <integer>
    expansionsWithVisibleMark: <integer>   # must be >= wordsFromExpansion (§7.3)
    normalizationReversals: 0
    formulaSubstitutionsDetected: 0
    auditPass: true   # must be true — false is a hard fail (§7.4)
"""

_SCHEMA_USER_PREFIX_EFFICIENT = """
OUTPUT FORMAT (required — follow exactly; all fields mandatory unless noted):

BINDING RULE — diplomaticToggles: Echo your CONFIGURATION toggle values exactly
into your output metadata.  Do NOT substitute defaults.
If preserveOriginalAbbreviations is TRUE: retain all abbreviation marks verbatim
(macrons, tildes, superscripts) — do NOT expand any abbreviation.
If preserveOriginalAbbreviations is FALSE: expand all abbreviations fully.

transcriptionOutput:
  protocolVersion: "{pv}"
  metadata:
    sourcePageId: "<from configuration>"
    modelId: "<provider model id you are running under>"
    timestamp: "<ISO-8601 UTC>"
    protocolVersion: "{pv}"
    targetLanguage: "<from configuration>"
    languageSet: []
    targetEra: "<from configuration>"
    eraRange: "<from configuration or null>"
    diplomaticProfile: "<strict or semi_strict only; not layout_aware or diplomatic_plus>"
"""

_SCHEMA_USER_SUFFIX_TAIL_EFFICIENT = """    normalizationMode: "<from configuration>"
    runMode: "efficient"
    mixedContent: { mixedLanguage: false, mixedEra: false }
    scriptNotes: null
    englishHandwritingModality: null
    epistemicNotes: null
    schemaRevision: null
  preCheck:
    resolutionAdequate: true/false
    orientationCorrect: true/false
    pageBoundariesVisible: true/false
    pageCount: <integer>
    scriptIdentified: "string"
    scriptMatchesConfig: true/false
    conditionNotes: null
    proceedDecision: "proceed" | "abort"
    proceedOverride: false
    abortReason: null
  segments:
    - segmentId: 1
      pageNumber: 1
      lineRange: "1-10"
      position: "body"
      text: |
        <verbatim transcription>
      confidence: "medium"
      uncertaintyTokenCount: <integer matching token count in text>
      notes: null
  mismatchReport: null   # efficient mode: omit or null (no Pass 2)
  hallucinationAudit:
    totalWords: <integer approx. word count across segments>
    wordsGroundedInGlyphs: <integer>
    wordsFromExpansion: <integer>
    expansionsWithVisibleMark: <integer>
    normalizationReversals: 0
    formulaSubstitutionsDetected: 0
    auditPass: true   # must be true (§7.4)
"""


def _run_mode_from_cfg(prompt_cfg: Dict[str, Any]) -> str:
    cfg = {k: (v if v is not None else "") for k, v in prompt_cfg.items()}
    rm = str(cfg.get("runMode", "standard") or "standard").strip()
    return rm if rm else "standard"


def build_user_text(prompt_cfg: Dict[str, Any], multi_page_note: str | None = None) -> str:
    cfg = {k: (v if v is not None else "") for k, v in prompt_cfg.items()}
    parts = [
        "CONFIGURATION:",
        f"- Target language/script: {cfg.get('targetLanguage', '')}",
        f"- Language set (if mixed): {cfg.get('languageSet', '[]')}",
        f"- Target era: {cfg.get('targetEra', '')}",
        f"- Era range: {cfg.get('eraRange', '')}",
        f"- Diplomatic profile: {cfg.get('diplomaticProfile', '')}",
        f"- Diplomatic toggles: {cfg.get('diplomaticToggles', '{}')}",
        f"- Normalization mode: {cfg.get('normalizationMode', '')}",
        f"- Script notes: {cfg.get('scriptNotesOptional', '')}",
        f"- English handwriting modality (eng-Latn only): {cfg.get('englishHandwritingModality', '')}",
        f"- Epistemic notes (optional metadata): {cfg.get('epistemicNotesOptional', '')}",
        f"- Run mode: {cfg.get('runMode', 'standard')}",
        f"- Source page ID: {cfg.get('sourcePageId', '')}",
        f"- Protocol version: {cfg.get('protocolVersion', '1.1.0')}",
    ]
    if multi_page_note:
        parts.append(f"- Note: {multi_page_note}")
    pv = str(cfg.get("protocolVersion", "1.2.0") or "1.2.0")
    rm = _run_mode_from_cfg(prompt_cfg)
    toggle_block = _render_toggles(prompt_cfg)
    if rm == "efficient":
        schema = (_SCHEMA_USER_PREFIX_EFFICIENT + toggle_block + _SCHEMA_USER_SUFFIX_TAIL_EFFICIENT).replace("{pv}", pv)
    else:
        schema = (_SCHEMA_USER_PREFIX + toggle_block + _SCHEMA_USER_SUFFIX_TAIL).replace("{pv}", pv)
    parts.append(schema)
    return "\n".join(parts)


def build_zones(prompt_cfg: Dict[str, Any], multi_page_note: str | None = None) -> tuple[str, str]:
    """Return (system_rules, user_text)."""
    rm = _run_mode_from_cfg(prompt_cfg)
    system = SYSTEM_RULES_EFFICIENT if rm == "efficient" else SYSTEM_RULES
    return system, build_user_text(prompt_cfg, multi_page_note)
