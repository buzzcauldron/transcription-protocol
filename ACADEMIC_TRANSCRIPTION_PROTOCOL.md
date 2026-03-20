# Academic Handwriting Transcription Protocol

> Version 1.0 — Strict no-addition transcription standard for LLM-assisted manuscript work.

---

## 1. Governing Principle

**Transcribe only what is visibly present on the page.**

- Never add, infer, complete, paraphrase, modernize, or normalize any text.
- Never silently resolve ambiguity. All uncertainty must be explicitly marked.
- The transcriber's role is reproduction, not interpretation.

---

## 2. Required Run Configuration

Every transcription run must declare the following parameters before work begins. Outputs missing any required field fail validation.

### 2.1 Target Language

`targetLanguage` — controlled code using ISO 639-3 plus optional script tag.

| Code | Description |
|---|---|
| `eng-Latn` | English, Latin script |
| `lat-Latn` | Latin, Latin script |
| `fra-Latn` | French, Latin script |
| `deu-Latn` | German, Latin script |
| `deu-Kurrentschrift` | German, Kurrent script |
| `spa-Latn` | Spanish, Latin script |
| `ita-Latn` | Italian, Latin script |
| `por-Latn` | Portuguese, Latin script |
| `nld-Latn` | Dutch, Latin script |
| `ell-Grek` | Greek, Greek script |
| `ara-Arab` | Arabic, Arabic script |
| `ota-Arab` | Ottoman Turkish, Arabic script |
| `heb-Hebr` | Hebrew, Hebrew script |
| `rus-Cyrl` | Russian, Cyrillic script |
| `zho-Hani` | Chinese, Han characters |
| `jpn-Jpan` | Japanese, mixed script |
| `kor-Hang` | Korean, Hangul script |
| `san-Deva` | Sanskrit, Devanagari script |
| `mixed` | Multiple languages on page (requires `languageSet` array) |

For unlisted languages, use the ISO 639-3 code with a hyphenated script identifier.

When `targetLanguage` is `mixed`, supply a `languageSet` array:

```
languageSet: ["lat-Latn", "eng-Latn", "ell-Grek"]
```

**Constraint**: `targetLanguage` guides glyph decoding only. It must never authorize inferred wording, vocabulary completion, or grammatical correction.

### 2.2 Target Era

`targetEra` — canonical tag identifying the handwriting period/style.

| Tag | Approximate Scope |
|---|---|
| `medieval` | Before 1500 |
| `early_modern` | 1500–1700 |
| `enlightenment` | 1700–1800 |
| `nineteenth_century` | 1800–1900 |
| `twentieth_century` | 1900–2000 |
| `contemporary` | 2000–present |

Optional refinement: `eraRange` (e.g., `1600-1699`) for tighter paleographic calibration.

**Constraint**: `targetEra` is a decoding hint only. It must never justify filling gaps, correcting perceived spelling errors, or resolving abbreviations based on period conventions unless the glyph evidence supports exactly one reading.

### 2.3 Diplomatic Profile

`diplomaticProfile` — required selection governing fidelity level.

| Profile | Behavior |
|---|---|
| `strict` | Preserve original spelling, punctuation, capitalization, abbreviations, and line breaks exactly as seen. |
| `semi_strict` | Preserve all glyph content and spelling. Allow explicit line-wrap joining with marker `[wrap-join]` retained in output. |
| `layout_aware` | Strict diplomatic plus spatial cues: marginalia, insertions, deletions, and superscripts encoded in markup (see Section 5). |
| `diplomatic_plus` | Strict diplomatic transcript plus a parallel normalized layer for searchability, with one-to-one segment alignment. |

### 2.4 Diplomatic Toggles

`diplomaticToggles` — optional overrides, bounded by profile.

| Toggle | Default | Notes |
|---|---|---|
| `preserveLineBreaks` | `true` | `false` only allowed in `semi_strict` or above. |
| `preserveOriginalAbbreviations` | `true` | When `true`, abbreviations are reproduced as-is. |
| `markExpansions` | `false` | When `true`, expanded abbreviations use `[exp: ...]` tags. Only meaningful if `preserveOriginalAbbreviations` is `true`. |
| `captureDeletionsAndInsertions` | `false` (`true` in `layout_aware`, `diplomatic_plus`) | Encode strikethroughs, carets, and interlinear additions. |
| `captureUnclearGlyphShape` | `true` | Emit `[glyph-uncertain: description]` for ambiguous letter forms. |

### 2.5 Normalization Mode

`normalizationMode` — controls whether a secondary normalized view is produced.

| Value | Behavior |
|---|---|
| `diplomatic` | Only the verbatim diplomatic transcript is produced (default). |
| `normalized` | A parallel normalized layer is generated alongside the diplomatic transcript, aligned segment-by-segment. |

The diplomatic transcript is always the authoritative record.

---

## 3. Uncertainty Tokens

When any portion of the source is unclear, damaged, or ambiguous, use exactly these tokens. Never improvise alternatives or silently skip content.

| Token | Meaning | Usage |
|---|---|---|
| `[illegible]` | Character(s) cannot be read at all. | `The [illegible] stood by the door.` |
| `[illegible: ~N chars]` | Illegible region with estimated extent. | `[illegible: ~12 chars]` |
| `[illegible: ~N words]` | Illegible region estimated in words. | `[illegible: ~3 words]` |
| `[uncertain: X]` | Best reading, but confidence is low. | `The [uncertain: magistrate] spoke.` |
| `[uncertain: X / Y]` | Two or more plausible readings. | `[uncertain: their / there]` |
| `[gap]` | Physical gap, tear, or missing section. | `...the treaty of [gap] was signed...` |
| `[gap: description]` | Gap with physical description. | `[gap: torn corner, ~2 lines missing]` |
| `[damaged: description]` | Visible but physically compromised text. | `[damaged: ink smear over 3 words]` |
| `[glyph-uncertain: description]` | Individual letter form is ambiguous. | `[glyph-uncertain: could be 'a' or 'o']` |
| `[exp: expanded]` | Abbreviation expansion (only if `markExpansions` is `true`). | `S[exp: anc]t[exp: us]` |
| `[wrap-join]` | Line-wrap join point (only in `semi_strict`+). | `con-[wrap-join]tinued` |
| `[deletion: text]` | Struck-through or crossed-out text (only in `layout_aware`+). | `[deletion: previously written word]` |
| `[insertion: text]` | Interlinear or marginal insertion (only in `layout_aware`+). | `[insertion: added above line: "very"]` |
| `[marginalia: text]` | Marginal note (only in `layout_aware`+). | `[marginalia: left margin: "cf. p.42"]` |
| `[superscript: text]` | Superscripted text (only in `layout_aware`+). | `[superscript: e]` |

---

## 4. Pre-Transcription Checklist

Before transcribing, the model must assess the source image and report:

1. **Resolution adequacy**: Is the image resolution sufficient to distinguish individual characters?
2. **Orientation**: Is the page correctly oriented (not rotated/inverted)?
3. **Page boundaries**: Are all edges of the written area visible?
4. **Page count**: How many pages are in this submission?
5. **Script identification**: What script/hand is used? Does it match `targetLanguage` and `targetEra`?
6. **Condition notes**: Any damage, staining, fading, or obstruction that will affect transcription.

If the image fails checks 1–3, the model must report the failure and request a better scan rather than proceeding with degraded accuracy.

---

## 5. Transcription Workflow

### 5.1 Segment-by-Segment Processing

Divide the page into segments (by paragraph, column, or natural divisions). Transcribe each segment independently to reduce omission and drift.

For each segment:
1. Identify the segment boundaries on the page.
2. Transcribe character by character, word by word.
3. Mark every uncertain or illegible region with the appropriate token.
4. Apply the selected `diplomaticProfile` and `diplomaticToggles`.
5. Record a confidence level for the segment: `high`, `medium`, or `low`.

### 5.2 Two-Pass Self-Check

After completing the initial transcription:

**Pass 2 — Verification sweep:**
1. Re-read each segment against the source image.
2. Compare Pass 1 output to the image, word by word.
3. Flag any discrepancies found between Pass 1 and the re-read.
4. Report all discrepancies in a `mismatchReport` block, even if they are resolved.
5. Produce the final text incorporating corrections.

The `mismatchReport` must always be present, even if empty:

```
mismatchReport:
  - segment: 3
    pass1: "the compleat works"
    pass2: "the [uncertain: compleat / complete] works"
    resolution: "adopted pass2 reading with uncertainty token"
```

### 5.3 Forbidden Actions

The following actions are strictly prohibited regardless of configuration:

- Completing partially visible words based on context or vocabulary.
- Correcting perceived spelling, grammar, or punctuation errors in the source.
- Inserting modern equivalents, translations, or glosses into the transcript body.
- Omitting text (even if repetitive, trivial, or apparently erroneous).
- Reordering text to match "expected" reading order unless the source layout is unambiguous.
- Adding paragraph breaks, headings, or formatting not present in the source.
- Summarizing or condensing any portion of the text.

### 5.4 Latin Normalization Bias (Critical for Medieval Documents)

**WARNING**: LLMs trained on Latin corpora will silently normalize scribal spellings to classical or standardized forms. This is the single most common failure mode in blind testing (observed WER 6% in benchmark BM-005). You MUST resist this tendency.

**Observed failure patterns** (from blind benchmark on 14th-century legal hand):

| What the scribe wrote | What the LLM produced | Error type |
|---|---|---|
| `ecclesticarum` | `ecclesiasticarum` | Spelling normalization |
| `quoruscumque` | `quorumcumque` | Spelling normalization |
| `iacitiram` | `iacturam` | Spelling normalization |
| `lettris` | `litteris` | Spelling normalization |
| `corporus` | `corpus` | Spelling normalization |
| `preiudicialies` | `preiudiciales` | Spelling normalization |
| `dignitatus` | `dignitatis` | Spelling normalization |
| `brevas` | `brevia` | Spelling normalization |
| `tenementibus` | `tenementa` | Case ending on abbreviation |
| `sedem` | `secundum` | Rejected unusual reading |

**Rules to prevent this**:

1. **Prefer the visually unusual reading.** If the glyph evidence supports a non-standard spelling (e.g., `ecclesticarum` rather than `ecclesiasticarum`), transcribe the non-standard form. Scribal spellings are data, not errors.
2. **Do not second-guess case endings.** When expanding an abbreviation, the specific case ending visible in the manuscript (even a single visible letter) overrides what Latin grammar "should" require.
3. **When in doubt, use uncertainty tokens.** If a reading looks unusual but the visual evidence supports it, prefer `[uncertain: unusual_form]` over silently normalizing to the expected form.
4. **Never reject a reading because it seems grammatically wrong.** Scribes made errors, used dialectal forms, and employed non-standard abbreviation practices. All of these are evidence that must be preserved.
5. **Abbreviation expansion must follow the specific scribe's practice, not classical norms.** If a scribe abbreviates in a way that expands to a non-classical form, that expansion is correct for this manuscript.

---

## 6. Output Requirements

Every transcription output must include the fields defined in [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md). At minimum:

- Run configuration metadata (`targetLanguage`, `targetEra`, `diplomaticProfile`, active toggles).
- Page and line indexing for every transcribed line.
- Per-segment confidence (`high`, `medium`, `low`).
- Provenance record (model identifier, timestamp, source page ID).
- The `mismatchReport` from the two-pass check.
- A `mixedContent` flag if the document contains multiple languages or era-inconsistent hands.

---

## 7. Quality Gate

Outputs are evaluated against the rubric defined in [QUALITY_RUBRIC.md](QUALITY_RUBRIC.md). An output fails if any of the following are true:

- Any text is present in the output that is not visible in the source image (fabricated addition).
- Any `[illegible]`, `[uncertain: ...]`, or `[gap]` token is missing where the source is ambiguous.
- The `mismatchReport` is absent.
- Required metadata fields are missing or contain values outside the controlled vocabulary.
- The `diplomaticProfile` compliance checks fail (e.g., line breaks removed under `strict`).

---

## 8. Versioning and Reproducibility

- Every transcript must record the protocol version used (this document: `v1.0`).
- Re-running the same source with the same configuration must produce structurally equivalent output.
- Any deviation between runs must be confined to uncertainty tokens and confidence scores, not substantive text changes.

---

## References

- Prompt templates: [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)
- Output schema: [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md)
- Quality rubric: [QUALITY_RUBRIC.md](QUALITY_RUBRIC.md)
- Framework plan: [framework/FRAMEWORK_PLAN.md](framework/FRAMEWORK_PLAN.md)
- Agent Skill: [skill/SKILL.md](skill/SKILL.md)
- Provider adapters: [skill/PROVIDER_ADAPTERS.md](skill/PROVIDER_ADAPTERS.md)
