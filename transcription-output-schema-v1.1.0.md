# Output Schema Specification

> **Document file:** `transcription-output-schema-v1.1.0.md` · **Protocol:** **1.1.0** (semver; matches repo [`VERSION`](../VERSION)) — Required structure of every diplomatic `transcriptionOutput`.

---

## 1. Top-Level Structure

Every transcription output is a single document (JSON or structured markdown) containing the blocks below. All blocks are required unless marked optional.

The **`segments`** array holds the **full diplomatic transcription** of the page or run (body text in reading order, including uncertainty tokens). Other top-level keys supply metadata, pre-check, the Pass 2 verification trail (`mismatchReport`, optional `pass2Summary`), and `hallucinationAudit` — process and provenance around that text, not a substitute for it (see protocol §5.2.1).

```
transcriptionOutput:
  protocolVersion: "1.1.0"
  metadata: { ... }
  preCheck: { ... }
  segments: [ ... ]
  mismatchReport: [ ... ]
  pass2Summary: { ... }             # optional shorthand for clean runs (see protocol §5.2)
  hallucinationAudit: { ... }
  normalizedLayer: [ ... ]          # only when normalizationMode is "normalized"
```

---

## 2. Metadata Block

All fields are required. Values must use the controlled vocabulary defined in the protocol.

```
metadata:
  sourcePageId: "string"            # unique page identifier
  modelId: "string"                 # model name and version (e.g., "claude-4-opus-20260301")
  timestamp: "ISO-8601"             # UTC timestamp of transcription run
  protocolVersion: "1.1.0"          # must match top-level (same protocol); legacy v1.0/v1.1 aliases OK
  targetLanguage: "eng-Latn"        # controlled code
  languageSet: []                   # populated only if targetLanguage is "mixed"
  targetEra: "nineteenth_century"   # canonical tag
  eraRange: "1820-1860"            # optional refinement, null if not used
  diplomaticProfile: "strict"       # one of: strict, semi_strict, layout_aware, diplomatic_plus
  diplomaticToggles:
    preserveLineBreaks: true
    preserveOriginalAbbreviations: true
    markExpansions: false
    captureDeletionsAndInsertions: false
    captureUnclearGlyphShape: true
  normalizationMode: "diplomatic"   # "diplomatic" or "normalized"
  runMode: "standard"               # "standard" or "efficient" (protocol §2.9)
  mixedContent:
    mixedLanguage: false
    mixedEra: false
  scriptNotes: "string or null"     # optional paleographic notes from researcher
  englishHandwritingModality: "copperplate" | null   # optional; only when targetLanguage is eng-Latn (or English in mixed)
  epistemicNotes: "string or null"  # optional: run-level limits, residual doubt, unverified regions (protocol §1.1)
  schemaRevision: "string or null"  # optional: companion-doc revision date (e.g. "2026-03-26") per protocol §9
```

### Validation Rules

| Field | Rule |
|---|---|
| `protocolVersion` (top-level and metadata) | Must denote the **same protocol** (semver `1.1.0` current; `1.0.0` legacy). Strings `v1.1` / `v1.0` are accepted aliases and compare equal to `1.1.0` / `1.0.0`. |
| `targetLanguage` | Must be from controlled vocabulary or valid ISO 639-3 + script pattern. |
| `epistemicNotes` | Optional. If present, must be a non-empty string or `null`. Summarizes honest limits of the transcript. |
| `schemaRevision` | Optional. Date string (e.g. `"2026-03-26"`) recording companion-doc version. |
| `englishHandwritingModality` | If present, must be one of the tags in protocol §2.8, or `null`. Omit or `null` when `targetLanguage` is not English. |
| `targetEra` | Must be one of the six canonical tags. |
| `eraRange` | If present, must match `YYYY-YYYY` format with start < end. |
| `diplomaticProfile` | Must be one of four defined profiles. |
| `diplomaticToggles` | Toggle values must be boolean. Overrides must be compatible with the selected profile. |
| `normalizationMode` | Must be `diplomatic` or `normalized`. |
| `runMode` | Must be `standard` or `efficient`. Default: `standard`. If `efficient`, `diplomaticProfile` must not be `layout_aware` or `diplomatic_plus` (§2.9). |
| `sourcePageId` | Must be non-empty string. |
| `modelId` | Must be non-empty string. |
| `timestamp` | Must be valid ISO 8601. |

---

## 3. Pre-Check Block

Required. Captures the image quality assessment performed before transcription.

```
preCheck:
  resolutionAdequate: true/false
  orientationCorrect: true/false
  pageBoundariesVisible: true/false
  pageCount: N
  scriptIdentified: "string"       # e.g., "copperplate cursive"
  scriptMatchesConfig: true/false
  conditionNotes: "string or null"  # damage, staining, fading
  proceedDecision: "proceed" / "abort"
  proceedOverride: true/false       # optional; true when researcher overrides a failed pre-check (§4.1)
  abortReason: "string or null"     # only if proceedDecision is "abort"
```

If `proceedDecision` is `abort`, the `segments` array must be empty and the output must explain why in `abortReason`.

When `proceedOverride` is `true`, the run is classified as **reduced validity** — downstream consumers should treat the output as provisional.

---

## 4. Segments Array

Required. One entry per transcribed segment (paragraph, column block, or natural division).

```
segments:
  - segmentId: 1
    pageNumber: 1
    lineRange: "1-8"                # line numbers within the page
    position: "body"                # one of: body, header, footer, margin_left,
                                    #   margin_right, margin_top, margin_bottom,
                                    #   interlinear, footnote
    text: |
      The verbatim transcribed text
      with line breaks preserved per profile rules.
    confidence: "high"              # one of: high, medium, low
    uncertaintyTokenCount: 0        # count of uncertainty tokens in this segment
    notes: "string or null"         # optional segment-level notes
```

### Segment Validation Rules

| Rule | Description |
|---|---|
| Non-empty text | Every segment must contain at least one character or uncertainty token. |
| Valid confidence | Must be `high`, `medium`, or `low`. |
| Consistent lineRange | `lineRange` must not overlap with other segments on the same page. |
| Token count accuracy | `uncertaintyTokenCount` must equal the actual number of uncertainty tokens in `text`. |
| Position vocabulary | Must be from the allowed position set. |

---

## 5. Mismatch Report

Required when `runMode` is `standard` (the default). Documents the two-pass self-check. **`mismatchReport` must not** be an empty array when `segments` is non-empty—each segment must be accounted for with either a discrepancy or an explicit Pass 2 confirmation.

**Efficient mode:** When `runMode` is `efficient`, `mismatchReport` may be omitted or `null` (Pass 2 is not required; see protocol §2.9).

There are two legal entry types:
1. **Discrepancy** — Pass 2 changed a reading (`pass1Reading` ≠ `pass2Reading`).
2. **Confirmation** — Pass 2 verified with no edits: `resolution: "pass2 confirms final text; no edit"`.

A confirm-only report is **valid** when no edits occurred. An all-"confirmed" report when real edits **did** occur is dishonest and violates §1.1.

```
mismatchReport:
  - mismatchId: 1
    segmentId: 3
    pass1Reading: "the compleat works"
    pass2Reading: "the [uncertain: compleat / complete] works"
    resolution: "adopted pass2 reading with uncertainty token"
    resolved: true
```

When Pass 2 confirms Pass 1 for a segment with no edits, still emit an entry, e.g. `resolution: "pass2 confirms final text; no change"`.

### Alternative: `pass2Summary` (optional shorthand)

For clean runs with many segments, a single run-level `pass2Summary` may replace per-segment confirmation boilerplate:

```
pass2Summary:
  segmentsReviewed: 40
  segmentsAltered: 0
  note: "Pass 2 complete; all segments verified, no edits."
```

When `pass2Summary` is present and `segmentsAltered` is 0, per-segment confirmation entries are optional. When `segmentsAltered` > 0, each altered segment **must** appear in `mismatchReport` as a discrepancy entry.

### Optional: layout reading order

For `layout_aware` / `diplomatic_plus`, metadata may include:

```
readingOrderNotes: "Main text column first; margin_left bottom to top; interlinear insertions after host line"
```

---

## 6. Normalized Layer (Optional)

Required only when `normalizationMode` is `normalized`. Provides a searchable normalized version aligned one-to-one with the diplomatic segments.

```
normalizedLayer:
  - segmentId: 1
    diplomaticText: "ye olde shoppe"
    normalizedText: "the old shop"
    alignmentNotes: "ye → the; olde → old; shoppe → shop"
```

### Normalized Layer Rules

| Rule | Description |
|---|---|
| One-to-one alignment | Every segment in `segments` must have a corresponding entry in `normalizedLayer`. |
| Diplomatic text match | `diplomaticText` must exactly match the `text` field of the corresponding segment. |
| No additions | `normalizedText` must not introduce content absent from the diplomatic text. |

---

## 6b. Hallucination Audit Block

Required. The model must perform a self-audit and record results. See protocol §7.3.

```
hallucinationAudit:
  totalWords: 250
  wordsGroundedInGlyphs: 247
  wordsFromExpansion: 85            # expansion-events, not output words
  expansionsWithVisibleMark: 85
  normalizationReversals: 0
  formulaSubstitutionsDetected: 0
  auditPass: true                   # convenience boolean; true only when all checks pass
  checks:                           # recommended structured breakdown
    glyphGrounding: { pass: true, anomalies: 0 }
    expansionJustification: { pass: true, anomalies: 0 }
    normalizationCheck: { pass: true, anomalies: 0 }
    formulaCheck: { pass: true, anomalies: 0 }
    confidenceCalibration: { pass: true, anomalies: 0 }
```

### Audit Validation Rules

| Rule | Description |
|---|---|
| `wordsFromExpansion` ≤ `expansionsWithVisibleMark` | If expansions exceed visible marks, the run fails regardless of `auditPass`. |
| `[exp:` count vs audit (when `markExpansions` is true) | Count of `[exp:` openings in concatenated `segments[].text` must equal `wordsFromExpansion` and `expansionsWithVisibleMark` (protocol §7.3; [`validate_schema.py`](benchmark/validate_schema.py)). |
| `totalWords` consistency | Should approximate the whitespace-delimited word count across all segment text. |
| `checks` block | Optional but recommended. When present, `auditPass` must equal logical AND of all check `pass` values. |

**Limitation:** The audit is self-reported by the same model. It catches careless self-contradiction but cannot catch coordinated fabrication. External verification is required for high-stakes runs.

---

## 7. Full Example

```yaml
transcriptionOutput:
  protocolVersion: "1.1.0"
  metadata:
    sourcePageId: "MS-1234-folio-12r"
    modelId: "claude-4-opus-20260301"
    timestamp: "2026-03-20T14:30:00Z"
    protocolVersion: "1.1.0"
    targetLanguage: "eng-Latn"
    languageSet: []
    targetEra: "nineteenth_century"
    eraRange: "1840-1860"
    diplomaticProfile: "strict"
    diplomaticToggles:
      preserveLineBreaks: true
      preserveOriginalAbbreviations: true
      markExpansions: false
      captureDeletionsAndInsertions: false
      captureUnclearGlyphShape: true
    normalizationMode: "diplomatic"
    runMode: "standard"
    mixedContent:
      mixedLanguage: false
      mixedEra: false
    scriptNotes: "cursive copperplate, consistent hand"
    englishHandwritingModality: "copperplate"
    epistemicNotes: null
    schemaRevision: null
  preCheck:
    resolutionAdequate: true
    orientationCorrect: true
    pageBoundariesVisible: true
    pageCount: 1
    scriptIdentified: "copperplate cursive"
    scriptMatchesConfig: true
    conditionNotes: "slight foxing in lower right corner"
    proceedDecision: "proceed"
    proceedOverride: false
    abortReason: null
  segments:
    - segmentId: 1
      pageNumber: 1
      lineRange: "1-6"
      position: "body"
      text: |
        Dear Sir,
        I write to you on the subject of the
        [uncertain: proposed / postponed] meeting which
        was to take place on the 14th of this
        month. I regret to inform you that
        [illegible: ~3 words] will not be possible.
      confidence: "medium"
      uncertaintyTokenCount: 2
      notes: "foxing affects lower portion"
    - segmentId: 2
      pageNumber: 1
      lineRange: "7-10"
      position: "body"
      text: |
        Your humble servant,
        [uncertain: J. Hartley / J. Hartly]
      confidence: "medium"
      uncertaintyTokenCount: 1
      notes: null
  mismatchReport:
    - mismatchId: 1
      segmentId: 1
      pass1Reading: "proposed meeting"
      pass2Reading: "[uncertain: proposed / postponed] meeting"
      resolution: "adopted pass2 with uncertainty token — second letter could be 'ro' or 'os'"
      resolved: true
    - mismatchId: 2
      segmentId: 2
      pass1Reading: "J. Hartley"
      pass2Reading: "[uncertain: J. Hartley / J. Hartly]"
      resolution: "pass2 confirms final text; no edit"
      resolved: true
  hallucinationAudit:
    totalWords: 42
    wordsGroundedInGlyphs: 40
    wordsFromExpansion: 0
    expansionsWithVisibleMark: 0
    normalizationReversals: 0
    formulaSubstitutionsDetected: 0
    auditPass: true
    checks:
      glyphGrounding: { pass: true, anomalies: 0 }
      expansionJustification: { pass: true, anomalies: 0 }
      normalizationCheck: { pass: true, anomalies: 0 }
      formulaCheck: { pass: true, anomalies: 0 }
      confidenceCalibration: { pass: true, anomalies: 0 }
  normalizedLayer: null
```

---

## 8. Schema Validation Checklist

Use this checklist to validate any output programmatically or by inspection:

- [ ] `protocolVersion` (top-level and metadata) present, same protocol (`1.1.0` or `1.0.0`, or legacy aliases `v1.1` / `v1.0`).
- [ ] All metadata fields present and use controlled vocabulary.
- [ ] `preCheck` block present with all fields.
- [ ] If `proceedDecision` is `abort`, segments array is empty.
- [ ] At least one segment present (unless aborted).
- [ ] Every segment has `segmentId`, `pageNumber`, `lineRange`, `position`, `text`, `confidence`.
- [ ] `uncertaintyTokenCount` matches actual token count in segment text.
- [ ] No line range overlaps within the same page.
- [ ] `mismatchReport` present; **non-empty** when `segments` is non-empty (protocol §5.2), unless `pass2Summary` is present with `segmentsAltered: 0`. **Exception**: when `runMode` is `efficient`, `mismatchReport` may be omitted.
- [ ] `runMode` is `standard` or `efficient`; if `efficient`, `diplomaticProfile` is not `layout_aware` or `diplomatic_plus` (§2.9).
- [ ] Uncertainty token density not above protocol threshold unless justified in notes (protocol §5.6).
- [ ] `epistemicNotes` if non-null is substantive (protocol §1.1).
- [ ] `hallucinationAudit` present with consistent numeric fields; `wordsFromExpansion` ≤ `expansionsWithVisibleMark`; if `markExpansions` is true, `[exp:` count in segment text matches both expansion audit integers.
- [ ] If structured `checks` block present, `auditPass` matches logical AND of all check `pass` values.
- [ ] `proceedOverride` if `true`: override documented in `conditionNotes` (§4.1).
- [ ] If `normalizationMode` is `normalized`, `normalizedLayer` is present with one-to-one alignment.
- [ ] `normalizedLayer` entries do not introduce new content.
