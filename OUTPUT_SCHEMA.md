# Output Schema Specification

> Defines the required structure of every transcription output under the Academic Handwriting Transcription Protocol v1.0.

---

## 1. Top-Level Structure

Every transcription output is a single document (JSON or structured markdown) containing the blocks below. All blocks are required unless marked optional.

```
transcriptionOutput:
  protocolVersion: "v1.0"
  metadata: { ... }
  preCheck: { ... }
  segments: [ ... ]
  mismatchReport: [ ... ]
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
  protocolVersion: "v1.0"
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
  mixedContent:
    mixedLanguage: false
    mixedEra: false
  scriptNotes: "string or null"     # optional paleographic notes from researcher
  englishHandwritingModality: "copperplate" | null   # optional; only when targetLanguage is eng-Latn (or English in mixed)
  epistemicNotes: "string or null"  # optional: run-level limits, residual doubt, unverified regions (protocol §1.1)
```

### Validation Rules

| Field | Rule |
|---|---|
| `targetLanguage` | Must be from controlled vocabulary or valid ISO 639-3 + script pattern. |
| `epistemicNotes` | Optional. If present, must be a non-empty string or `null`. Summarizes honest limits of the transcript. |
| `englishHandwritingModality` | If present, must be one of the tags in protocol §2.8, or `null`. Omit or `null` when `targetLanguage` is not English. |
| `targetEra` | Must be one of the six canonical tags. |
| `eraRange` | If present, must match `YYYY-YYYY` format with start < end. |
| `diplomaticProfile` | Must be one of four defined profiles. |
| `diplomaticToggles` | Toggle values must be boolean. Overrides must be compatible with the selected profile. |
| `normalizationMode` | Must be `diplomatic` or `normalized`. |
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
  abortReason: "string or null"     # only if proceedDecision is "abort"
```

If `proceedDecision` is `abort`, the `segments` array must be empty and the output must explain why in `abortReason`.

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

Required. Documents the two-pass self-check. **Protocol v1.1:** `mismatchReport` **must not** be an empty array when `segments` is non-empty—each segment must be accounted for with either a discrepancy between pass readings or an explicit Pass 2 confirmation (see [ACADEMIC_TRANSCRIPTION_PROTOCOL.md](ACADEMIC_TRANSCRIPTION_PROTOCOL.md) Section 5.2).

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

## 7. Full Example

```yaml
transcriptionOutput:
  protocolVersion: "v1.0"
  metadata:
    sourcePageId: "MS-1234-folio-12r"
    modelId: "claude-4-opus-20260301"
    timestamp: "2026-03-20T14:30:00Z"
    protocolVersion: "v1.0"
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
    mixedContent:
      mixedLanguage: false
      mixedEra: false
    scriptNotes: "cursive copperplate, consistent hand"
    englishHandwritingModality: "copperplate"
    epistemicNotes: null
  preCheck:
    resolutionAdequate: true
    orientationCorrect: true
    pageBoundariesVisible: true
    pageCount: 1
    scriptIdentified: "copperplate cursive"
    scriptMatchesConfig: true
    conditionNotes: "slight foxing in lower right corner"
    proceedDecision: "proceed"
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
  normalizedLayer: null
```

---

## 8. Schema Validation Checklist

Use this checklist to validate any output programmatically or by inspection:

- [ ] `protocolVersion` present and matches `v1.0`.
- [ ] All metadata fields present and use controlled vocabulary.
- [ ] `preCheck` block present with all fields.
- [ ] If `proceedDecision` is `abort`, segments array is empty.
- [ ] At least one segment present (unless aborted).
- [ ] Every segment has `segmentId`, `pageNumber`, `lineRange`, `position`, `text`, `confidence`.
- [ ] `uncertaintyTokenCount` matches actual token count in segment text.
- [ ] No line range overlaps within the same page.
- [ ] `mismatchReport` present; **non-empty** when `segments` is non-empty (v1.1).
- [ ] Uncertainty token density not above protocol threshold unless justified in notes (v1.1).
- [ ] `epistemicNotes` if non-null is substantive (protocol §1.1).
- [ ] `hallucinationAudit` numeric fields consistent with segment text when present (v1.1 cross-check).
- [ ] If `normalizationMode` is `normalized`, `normalizedLayer` is present with one-to-one alignment.
- [ ] `normalizedLayer` entries do not introduce new content.
