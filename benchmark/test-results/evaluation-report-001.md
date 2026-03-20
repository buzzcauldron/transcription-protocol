# Evaluation Report: BM-001 — Lincoln-Owens Letter

> Run ID: 001 | Date: 2026-03-20 | Protocol: v1.0

---

## Source

- **Document**: Letter, Abraham Lincoln to Mary S. Owens, 16 August 1837
- **Archive**: Library of Congress (mcc.030)
- **Pages**: 2
- **Ground truth source**: Roy P. Basler, ed., *The Collected Works of Abraham Lincoln* (Rutgers, 1953), 1:94-95; Papers of Abraham Lincoln digital edition

## Configuration

| Parameter | Value |
|---|---|
| targetLanguage | `eng-Latn` |
| targetEra | `nineteenth_century` |
| eraRange | `1830-1840` |
| diplomaticProfile | `layout_aware` |
| normalizationMode | `diplomatic` |
| Model | Claude 4 Opus |

## Results Summary

| Metric | Value |
|---|---|
| Word-level accuracy | **99.80%** |
| Ground truth words | 490 |
| Transcription words | 489 |
| Matching words | 489 |
| Additions | **0** |
| Omissions | **1** ("for") |
| Addition rate | 0.00 / 1000 words |
| Omission rate | 2.04 / 1000 words |
| Uncertainty tokens used | 6 |
| Rubric score | 0.8500 |
| Disposition | **CONDITIONAL_PASS** |

## Rubric Category Breakdown

### 1. Addition Detection — PASS

Zero fabricated additions. No spelling corrections, no word completions, no modernization. The core no-addition requirement is fully met.

### 2. Omission Detection — CONDITIONAL (1 word)

One word omitted: **"for"** in the phrase "And for the purpose of making the" (segment 6, page 1). This word falls directly on a horizontal fold crease that partially obscures the ink. The mismatch report documents this discrepancy — Pass 1 included "for", Pass 2 dropped it, and the more conservative reading was adopted. This is a physical damage case appropriate for human review.

### 3. Uncertainty Compliance — PASS

Six uncertainty tokens used across the transcription:
- 4 `[uncertain: ...]` tokens at fold crease locations on page 1 (segment 7)
- 1 `[uncertain: ...]` on the word "sister" near the close (segment 14)
- 1 `[marginalia: ...]` with uncertainty on archival notation (segment 16)

The fold-damaged regions are appropriately flagged. No ambiguous regions were presented as definitive without tokens.

### 4. Diplomatic Profile Compliance — PASS

- Line breaks preserved throughout.
- Original spelling preserved (including "murmer" not corrected to "murmur"; "any thing" not joined to "anything").
- One deletion captured: `[deletion: anxi]` where Lincoln crossed out a false start before "anxious" (page 2, segment 10).
- Archival marginalia captured with `[marginalia: ...]` tokens (segments 1 and 16).

### 5. Metadata and Schema Compliance — PASS

All required fields present. Controlled vocabulary used correctly. Pre-check block complete. Mismatch report present with 3 documented discrepancies.

## Notable Observations

1. **"think you of you"** — The transcription correctly reproduces this apparent scribal error verbatim (segment 3), without correction. This is exactly the protocol-compliant behavior.

2. **"murmer"** — Lincoln's original spelling is preserved, not silently corrected to "murmur". Protocol compliance confirmed.

3. **"any thing"** — Lincoln's two-word form is preserved, not modernized to "anything". Protocol compliance confirmed.

4. **Fold crease handling** — The horizontal fold across the lower third of page 1 is the source of all uncertainty. The protocol correctly flagged these regions rather than silently guessing.

5. **Deletion capture** — The crossed-out false start before "anxious" on page 2 was captured with `[deletion: anxi]`, demonstrating `layout_aware` profile compliance.

## Disposition Rationale

**CONDITIONAL_PASS** — Zero critical failures (no additions, no silent resolutions). One major failure: a single-word omission at a physical damage point. This is correctly routed to the human review queue per the framework.

The omitted word "for" should be re-examined by a human reviewer against the original manuscript or higher-resolution scan. If confirmed present, the word should be restored with a note about the fold crease.

## Benchmark Classification

This result maps to test case **BM-001** (Clean 19th-century English letter) with the complication of a fold crease (approaching **BM-002** territory — faded/damaged regions).

| Red-team check | Result |
|---|---|
| RT-001: Did not correct "murmer" to "murmur" | PASS |
| RT-005: Did not de-duplicate "think you of you" | PASS |
| RT-009: Did not expand abbreviations | PASS |
| RT-007: Did not silently resolve fold-obscured text | PASS |
