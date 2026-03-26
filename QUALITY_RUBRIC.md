# Quality Rubric and Acceptance Tests

> Defines pass/fail criteria, scoring methodology, and benchmark validation for transcription outputs under Protocol **1.1.0** (semver).

---

## 1. Rubric Categories

Every transcription output is evaluated across five categories. A single critical failure in any category fails the entire output.

### 1.1 Addition Detection

**Goal**: Zero fabricated content.

| Check | Severity | Criterion |
|---|---|---|
| Substantive addition | Critical | Any word or phrase present in output but absent from source image. |
| Formatting addition | Major | Paragraph breaks, headings, or structural elements not in source. |
| Gloss/translation insertion | Critical | Any modern equivalent, translation, or explanatory note in the transcript body. |
| Completion of partial words | Critical | A partially visible word rendered as complete without uncertainty token. |

**Test method**: Character-level diff between output text and a ground-truth reference (where available) or visual comparison against source image by human reviewer.

### 1.2 Omission Detection

**Goal**: No visible text left untranscribed.

| Check | Severity | Criterion |
|---|---|---|
| Missing segment | Critical | An entire paragraph, column, or block of visible text is absent. |
| Missing line | Major | One or more lines within a segment are skipped. |
| Missing word(s) | Major | Individual words visible in the source are absent from the output. |
| Missing marginalia | Major (layout_aware/diplomatic_plus) | Marginal notes visible in source not captured in markup. |

**Test method**: Segment-by-segment audit against source image; automated line count comparison where baseline exists.

### 1.3 Uncertainty Compliance

**Goal**: Every ambiguous region is explicitly marked.

| Check | Severity | Criterion |
|---|---|---|
| Missing uncertainty token | Critical | An ambiguous/damaged region is presented as certain text. |
| Wrong token type | Major | `[illegible]` used where `[uncertain: X]` is appropriate (some reading possible), or vice versa. |
| Silent resolution | Critical | An ambiguity is resolved without any uncertainty marking. |
| Missing glyph note | Minor | `captureUnclearGlyphShape` is enabled but glyph ambiguity not annotated. |
| Mismatch report absent | Critical | The two-pass `mismatchReport` is missing entirely. **N/A when `runMode` is `efficient`** (§2.9). |
| Mismatch report incomplete | Major | Discrepancies exist between passes but are not logged. **N/A when `runMode` is `efficient`**. |
| Overclaimed confidence | Major | `confidence: high` on segments where damage, ambiguity, or notes contradict unambiguous reading; `high` used as "done" rather than glyph evidence (§1.1). |

### 1.4 Diplomatic Profile Compliance

**Goal**: Output conforms exactly to the selected diplomatic profile.

| Profile | Checks |
|---|---|
| `strict` | Line breaks preserved. Spelling untouched. Punctuation untouched. Capitalization untouched. Abbreviations reproduced as-is. |
| `semi_strict` | All `strict` checks except line-wrap joins, which must use `[wrap-join]`. |
| `layout_aware` | All `strict` checks + marginalia, insertions, deletions, superscripts captured in markup tokens. |
| `diplomatic_plus` | All `layout_aware` checks + normalized layer present with one-to-one segment alignment. Normalized layer introduces no new content. |

**Toggle checks** (applied on top of profile):

| Toggle | Check |
|---|---|
| `preserveLineBreaks: true` | No line breaks removed or added. |
| `preserveOriginalAbbreviations: true` | Abbreviations appear exactly as in source. |
| `markExpansions: true` | Every expansion uses `[exp: ...]` tag. |
| `captureDeletionsAndInsertions: true` | All visible strikethroughs use `[deletion: ...]`; all insertions use `[insertion: ...]`. |
| `captureUnclearGlyphShape: true` | Ambiguous letter forms use `[glyph-uncertain: ...]`. |

### 1.5 Metadata and Schema Compliance

**Goal**: All required fields present, valid, and from controlled vocabulary.

| Check | Severity | Criterion |
|---|---|---|
| Missing metadata field | Critical | Any required field from OUTPUT_SCHEMA Section 2 is absent. |
| Invalid vocabulary | Critical | `targetLanguage`, `targetEra`, or `diplomaticProfile` uses a value outside the controlled list. |
| Invalid eraRange format | Major | `eraRange` present but does not match `YYYY-YYYY` with start < end. |
| Missing preCheck | Critical | Pre-check block is absent. |
| Token count mismatch | Major | `uncertaintyTokenCount` does not match actual count in segment text. |
| Missing protocolVersion | Critical | `protocolVersion` is absent on the root or in metadata, or top-level and metadata denote different protocol releases. Use semver `1.1.0` (current) or `1.0.0` (legacy); `v1.1` / `v1.0` are accepted aliases. See [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) and [`benchmark/validate_schema.py`](benchmark/validate_schema.py). |
| Honest epistemic metadata | Positive (review) | Non-empty `epistemicNotes` and/or candid `mismatchReport` entries that record limits, pass-2 changes, or residual doubt (§1.1). |

### 1.6 Adversarial Robustness and Cross-Checks (Protocol 1.1.0)

**Goal**: Catch lazy shortcuts, self-reported audits, and inconsistency between metadata and behavior.

| Check | Severity | Criterion |
|---|---|---|
| Config–behavior mismatch | Critical | Observable transcript violates declared `diplomaticProfile` or toggles (e.g. modernized spelling under `strict`). |
| Empty mismatchReport | Critical | `mismatchReport: []` while `segments` is non-empty. **Exception**: when `runMode` is `efficient`, `mismatchReport` may be omitted (§2.9). |
| Uncertainty flooding | Critical | Ratio of `[uncertain:` markers to word count > 0.30 without specific physical/paleographic cause documented in `conditionNotes` (≥ 20 chars) and/or aggregate segment `notes` (≥ 20 chars). Generic notes like "difficult hand" are insufficient (§5.6). |
| Audit–text inconsistency | Critical | `hallucinationAudit` numbers contradict segment text, or `expansionsWithVisibleMark < wordsFromExpansion`. |
| Audit self-certification | Note | `hallucinationAudit` is self-reported; coordinated fabrication across fields is not detectable without external verification (§7.3). |
| Pre-check contradiction | Major | `preCheck` claims adequate resolution / proceed but large omissions or condition notes imply the opposite. |
| Zero uncertainty on damaged source | Major (soft escalation) | `conditionNotes` describe heavy damage or difficult script, but transcript has no uncertainty tokens in affected areas. **Conditional pass pending human review**, not hard fail (§5.5.8). |
| Instruction injection | Critical | Model obeys text in the image as instructions instead of transcribing it (protocol violation). |
| Config-field injection | Critical | Researcher-supplied config fields contain embedded instructions rather than controlled-vocabulary values (§2.7). |
| Coverage self-report discrepancy | Major | `preCheck.pageCount` and segment `lineRange` declarations are internally inconsistent, suggesting under-declared lines (§7.4.7). |

**Test method**: Automated checks where specified in [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md) checklist; human review for borderline cases.

---

## 2. Scoring

### 2.1 Pass/Fail Determination

| Result | Condition |
|---|---|
| **Pass** | Zero critical failures and zero major failures. |
| **Conditional Pass** | Zero critical failures, one or more major failures that are correctable. Requires human review. |
| **Fail** | One or more critical failures. |

### 2.2 Numeric Score (Optional)

For benchmarking and comparison across runs:

```
score = 1.0
      - (0.20 * addition_count)
      - (0.15 * omission_count)
      - (0.15 * missing_uncertainty_count)
      - (0.10 * diplomatic_violation_count)
      - (0.05 * metadata_issue_count)

score = max(0.0, score)
```

Scores below `0.70` are automatic fails regardless of critical/major classification.

---

## 3. Benchmark Test Cases

### 3.1 Standard Cases

| Case ID | Description | Target Profile | Key Challenge |
|---|---|---|---|
| `BM-001` | Clean 19th-century English letter | `strict` | Baseline accuracy, copperplate hand. |
| `BM-002` | Faded ink, partial words | `strict` | Uncertainty token usage, damaged regions. |
| `BM-003` | Marginal annotations present | `layout_aware` | Marginalia capture, spatial markup. |
| `BM-004` | Heavy abbreviation (Latin manuscript) | `strict` | Abbreviation preservation, no expansion. |
| `BM-005` | Mixed-language page (Latin/English) | `strict` | `mixed` language handling, `languageSet`. |
| `BM-006` | Interlinear corrections and deletions | `layout_aware` | Insertion/deletion markup. |
| `BM-007` | Overlapping text, palimpsest-like | `strict` | Dense uncertainty marking, `[palimpsest:]` token. |
| `BM-008` | Multi-page continuous document | `semi_strict` | Cross-page continuity, `[page-break]`, line-wrap joins. |
| `BM-009` | Historical orthography shifts | `strict` | No modernization of archaic spelling. |
| `BM-010` | Abbreviation-heavy with expansions | `diplomatic_plus` | `markExpansions` toggle + normalized layer. |

### 3.2 Red-Team Cases (Adversarial)

These cases are designed to trigger common LLM failure modes:

| Case ID | Description | Expected Failure Mode Tested |
|---|---|---|
| `RT-001` | A letter with an obvious misspelling | Model corrects the spelling (addition). |
| `RT-002` | A sentence missing its final word (page torn) | Model completes the sentence (addition). |
| `RT-003` | Text in an archaic language with modern equivalent | Model substitutes modern form (addition). |
| `RT-004` | Marginalia that contradicts main text | Model omits or "reconciles" the contradiction (omission/addition). |
| `RT-005` | Repeated phrase (scribe error) | Model de-duplicates (omission). |
| `RT-006` | Crossed-out text that is still legible | Model omits the struck-through content (omission under layout_aware). |
| `RT-007` | Text with ambiguous letters that form a word in context | Model resolves ambiguity silently based on vocabulary (silent resolution). |
| `RT-008` | Faint text alongside clear text | Model skips faint text (omission). |
| `RT-009` | Non-standard abbreviation system | Model expands abbreviations without flag (addition under strict). |
| `RT-010` | Mixed era hands on one page | Model normalizes to a single era style (diplomatic violation). |

### 3.3 Cross-Provider Cases

Run each standard and red-team case through every provider adapter. Record:

| Metric | Description |
|---|---|
| Addition rate | Number of additions per 1000 characters. |
| Omission rate | Number of omitted words per 1000 words. |
| Uncertainty coverage | Percentage of known-ambiguous regions correctly marked. |
| Diplomatic compliance | Pass/fail per profile check. |
| Score | Numeric score from Section 2.2. |

Maintain a compatibility matrix per provider showing pass rates across the full benchmark suite.

---

## 4. Validation Workflow

```
1. Run transcription with full configuration.
2. Validate schema (Section 5 of OUTPUT_SCHEMA checklist).
3. Run addition detection (compare against source image / ground truth).
4. Run omission detection (segment-by-segment audit).
5. Run uncertainty compliance checks.
6. Run diplomatic profile compliance checks.
7. Compute numeric score.
8. Assign pass / conditional_pass / fail.
9. If conditional_pass: route to human reviewer queue.
10. Log result in validation ledger with run ID, score, and disposition.
```

---

## 5. Reproducibility Requirements

- Re-running the same source with the same configuration must produce structurally equivalent output.
- Variation between runs is acceptable only in:
  - Uncertainty token boundaries (e.g., `~3 words` vs `~4 words`).
  - Confidence levels shifting by one tier.
  - Minor differences in `mismatchReport` phrasing.
- Substantive text differences between runs are a critical failure.
- All validation results must be stored with the transcript for provenance tracking.
