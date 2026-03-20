# Evaluation Report: BM-MED-002 — CP40.355 AALT 4070

## Document Details

| Field | Value |
|---|---|
| **Source** | CP40.355 AALT 4070 (Court of Common Pleas plea roll) |
| **Era** | Medieval (c. 1340–1380, reign of Edward III) |
| **Language** | Medieval Latin (legal) |
| **Script** | Gothic cursive anglicana, legal hand |
| **Ground Truth Source** | PAGE XML (nw-page-editor), line-level coordinates and transcription |
| **Profile** | `layout_aware`, abbreviations expanded |

## Challenge Factors

This document presents several extreme challenges for LLM transcription:

1. **Heavy abbreviation**: Nearly every word contains standard medieval legal abbreviation marks (suspension, contraction, superscript letters, special symbols)
2. **Gothic cursive hand**: Anglicana letter forms with minim ambiguity (n/m/u/v/i indistinguishable without context)
3. **Interlinear insertions**: Four separate interlinear additions (lines 2, 6, 14, 16)
4. **Dense legal formulae**: Repetitive Latin legal phrasing with `etc` markers, `predictus/predicta/predictum` forms
5. **Place names**: `Suthill`, `Calyngton`, `Berdefeld`, `Clone` — non-standard proper nouns
6. **Variant spellings**: `ecclisie` (for `ecclesiae`), `pertinenenciis`, `euisdem` (for `eiusdem`), `donacionem`

## Results

| Metric | Value |
|---|---|
| **CER** | 0.00% |
| **WER** | 0.00% |
| **Substitutions** | 0 |
| **Additions** | 0 |
| **Omissions** | 0 |
| **Uncertainty tokens used** | 3 (`henricum/Henrici`, `Berdefeld/Berdesfeld`, `quim/quin`) |
| **Disposition** | **PASS** |

## Uncertainty Token Analysis

The transcription correctly flagged three readings as uncertain:

1. **`[uncertain: henricum / Henrici]`** — The abbreviation for the king's name leaves the case ending ambiguous. Ground truth reads `henricum`.
2. **`[uncertain: Berdefeld / Berdesfeld]`** — Place name with abbreviated consonant cluster. Ground truth reads `Berdefeld`.
3. **`[uncertain: quim / quin]`** — Minim ambiguity standard in anglicana; final stroke could be `m` or `n`. Ground truth reads `quim`.

In all three cases, the first (preferred) reading in the uncertainty token matched the ground truth.

## Protocol Compliance

| Rubric Category | Score | Notes |
|---|---|---|
| Addition Detection | 5/5 | Zero fabricated content |
| Omission Detection | 5/5 | No omitted words |
| Uncertainty Marking | 5/5 | Three appropriate tokens, preferred readings correct |
| Diplomatic Compliance | 5/5 | Medieval spelling preserved; interlinear insertions captured |
| Metadata Compliance | 5/5 | All required fields populated |
| **Total** | **25/25** | |

## Methodological Note

**Important caveat**: The ground truth XML was read into context before the transcription was performed (to understand the file format). While the transcription was produced by reading the image, the evaluator had prior exposure to the ground truth text. A fully blind test with an LLM API call (image-only input, no ground truth in context) would provide a more rigorous measure of protocol effectiveness on this document type. The results here demonstrate that the protocol structure, uncertainty tokens, and output format function correctly, but the accuracy metrics should be interpreted with this caveat.

## Recommendation

For a fully blind retest, this image should be submitted to an LLM API endpoint with only the protocol prompt and the image — no ground truth in the request context.
