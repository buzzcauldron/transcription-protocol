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
- **Using `[illegible]` or `[gap]` to avoid attempting a difficult reading.** See Section 5.5.

### 5.4 Latin Normalization Bias (Failure Mode A)

**WARNING**: LLMs trained on Latin corpora will silently normalize scribal spellings to classical or standardized forms. This was the dominant failure mode in blind testing (observed WER 6% in benchmark BM-005). You MUST resist this tendency.

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

### 5.5 Illegibility Bail-Out (Failure Mode B)

**WARNING**: Some LLMs will abuse `[illegible]` and `[gap]` tokens to avoid attempting difficult readings. This is equally as harmful as normalization — it produces a technically "safe" output that is useless to researchers. In blind testing, one model marked ~90% of a fully legible 14-line plea roll as `[gap: remainder of document heavily abbreviated and illegible at current resolution]` while only attempting 3 lines.

**This is a protocol violation.** Text that is abbreviated is not illegible. Text that requires paleographic skill to read is not illegible. Text in a difficult hand is not illegible.

**Definitions**:

- **`[illegible]`** means the ink is physically absent, smeared beyond recognition, or the letterforms are damaged to the point where no reading is possible even with magnification. It does NOT mean "I am not confident" or "this is heavily abbreviated."
- **`[gap]`** means there is a physical hole, tear, or missing portion of the writing surface. It does NOT mean "the rest of the page is hard to read."
- **`[uncertain: X]`** is the correct token when you CAN propose a reading but lack confidence. This is what should be used for difficult abbreviations, ambiguous minims, and unfamiliar letterforms.

**Rules to prevent illegibility bail-out**:

1. **Every line of visible text must be attempted.** You may not skip lines or mark entire sections as `[gap]` unless there is a physical gap in the writing surface.
2. **Abbreviated words are readable, not illegible.** Standard medieval abbreviation marks (suspensions, contractions, superscript letters, tironian et, nasal bars) have deterministic or near-deterministic expansions. Attempt the expansion. If uncertain, use `[uncertain: expansion]`.
3. **Use `[uncertain]` not `[illegible]` for difficult readings.** If you can see letterforms but are unsure what they say, that is `[uncertain: best_guess]`, not `[illegible]`.
4. **`[illegible]` requires a physical cause.** Every use of `[illegible]` must correspond to a specific physical condition: ink fading, smearing, staining, water damage, binding obstruction, or torn parchment. If you cannot name the physical cause, you probably mean `[uncertain]`.
5. **`[gap]` requires physical absence.** `[gap]` means parchment is missing, torn, or cut away. It never means "I stopped transcribing here."
6. **Coverage threshold.** If the image shows N lines of text, the transcription must contain attempted readings for all N lines. An output that attempts fewer than 90% of visible lines is automatically invalid.
7. **Maximum consecutive `[illegible]` span.** No more than approximately one line of continuous text may be marked `[illegible]` unless the physical cause is documented (e.g., `[damaged: ink smear across lines 5-7]`). If you find yourself marking multiple consecutive words as `[illegible]`, you are likely bailing out rather than reading.

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

## 7. Anti-Hallucination Gates

Hallucination — producing text not grounded in visible glyphs — is the worst-case failure. A hallucinated transcription is worse than no transcription: it contaminates the scholarly record with fabricated evidence. Every rule below is a hard gate. Any single violation invalidates the entire output.

### 7.1 The Grounding Rule

**Every character in the output must be traceable to a visible mark on the page.**

- If you cannot point to the specific ink stroke(s) that produced a character, that character must not appear in the output.
- "I know this word should be here because of context" is hallucination.
- "This abbreviation usually expands to X" is only valid if the abbreviation mark itself is visible. If the mark is absent or ambiguous, use `[uncertain]`.

### 7.2 Five Forms of Hallucination

All five are protocol violations of equal severity.

| Form | Description | Example |
|---|---|---|
| **Content fabrication** | Words inserted that have no corresponding glyphs on the page. | Adding a word to complete a sentence that "makes sense." |
| **Normalization substitution** | Replacing what the scribe wrote with a "correct" classical/standard form. | `ecclesticarum` → `ecclesiasticarum`. The scribe wrote the first form; the second is fabricated. |
| **Formula injection** | Inserting expected legal/liturgical/literary formulae instead of reading what is present. | Writing `secundum legem` because that's the standard formula, when the scribe wrote `sedem legem`. |
| **Expansion fabrication** | Expanding an abbreviation to a word the scribe did not intend, based on what the word "should" be. | Expanding `ten'` as `tenementa` when visible case markers indicate `tenementibus`. |
| **Metadata fabrication** | Inventing document identifiers, dates, or provenance not visible on the page or provided by the user. | Assigning a shelfmark the model "recognizes" rather than using only what is given or visible. |

### 7.3 Self-Audit Checklist (Mandatory)

After completing the transcription and before emitting output, the model must perform this audit. The audit results must be recorded in the output under `hallucinationAudit`.

For every word in the transcription, verify:

1. **Glyph grounding**: Can I identify the ink strokes on the page that produce this word? If no → remove or mark `[uncertain]`.
2. **Expansion justification**: If this word is an expanded abbreviation, can I identify the specific abbreviation mark (bar, suspension, superscript, symbol) that I am expanding? If no → revert to the abbreviated form or mark `[uncertain]`.
3. **Normalization check**: Is this word spelled differently from what I see on the page? Did I "clean up" a scribal form? If yes → revert to the scribal form.
4. **Formula check**: Did I write this word because it is the expected next word in a known formula, or because I read it from the page? If the former → re-examine the page and correct.
5. **Confidence calibration**: Am I claiming `high` confidence on a segment where I used contextual knowledge to resolve ambiguity? If yes → downgrade to `medium` or `low`.

```yaml
hallucinationAudit:
  totalWords: 250
  wordsGroundedInGlyphs: 247
  wordsFromExpansion: 85
  expansionsWithVisibleMark: 85
  normalizationReversals: 0
  formulaSubstitutionsDetected: 0
  auditPass: true
```

### 7.4 Hard Fail Conditions

The output is **automatically invalid** if ANY of the following are true:

1. **Any word appears in the output that has no corresponding glyph group on the page.** This includes words added "for sense," words from expected formulae, and words from the model's knowledge of the text.
2. **Any scribal spelling has been silently replaced** with a classical, standard, or "correct" form without an `[uncertain]` token.
3. **Any abbreviation has been expanded without a visible abbreviation mark** (suspension, contraction bar, superscript, or recognized symbol) justifying the expansion.
4. **Metadata fields contain values not provided by the user or visible on the page.** The model must never invent shelfmarks, folio numbers, dates, or repository names.
5. **The `hallucinationAudit` block is absent or reports `auditPass: false`.**
6. **The `mismatchReport` is absent.**
7. **Coverage is below 90%** of visible text lines.
8. **`[illegible]` or `[gap]` is used without a documented physical cause** (see Section 5.5).

### 7.5 Severity Hierarchy

When errors conflict, this hierarchy determines disposition:

1. **Hallucination** (worst) — any fabricated content invalidates the entire output, regardless of overall accuracy.
2. **Silent normalization** — substituting "correct" forms is a form of hallucination and is treated as such.
3. **Omission via bail-out** — marking readable text as `[illegible]` produces an incomplete but non-toxic output. Bad, but less bad than fabrication.
4. **Genuine misreading** — reading the wrong glyph when the correct one was difficult. This is a normal transcription error, not a protocol violation, provided the misreading was not caused by normalization bias.

**In all cases: an honest `[uncertain]` is better than a confident wrong answer. An honest `[uncertain]` is also better than a cowardly `[illegible]`.**

---

## 8. Quality Gate

Outputs are evaluated against the rubric defined in [QUALITY_RUBRIC.md](QUALITY_RUBRIC.md), subject to the hard fail conditions in Section 7.4. An output that passes the anti-hallucination gates is then evaluated for:

- Per-segment confidence calibration.
- Uncertainty token placement (tokens present where source is ambiguous).
- Diplomatic profile compliance (line breaks, abbreviation handling, layout markup).
- Metadata completeness.

---

## 9. Versioning and Reproducibility

- Every transcript must record the protocol version used (this document: `v1.1`).
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
