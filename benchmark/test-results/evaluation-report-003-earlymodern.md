# Evaluation Report: BM-EM-001 — John Donne to Sir Thomas Egerton (1602)

> Run ID: 003 | Date: 2026-03-20 | Protocol: 1.1.0

---

## Source

- **Document**: Autograph letter from John Donne to Sir Thomas Egerton, February 1602
- **Archive**: Folger Shakespeare Library, MS L.b.534
- **Pages**: 2 (leaf 1 recto: letter body; leaf 2 recto: address panel with wax seal)
- **Ground truth source**: EMMO diplomatic transcription (CC BY-SA 4.0)

## Configuration

| Parameter | Value |
|---|---|
| targetLanguage | `eng-Latn` |
| targetEra | `early_modern` |
| eraRange | `1600-1610` |
| diplomaticProfile | `layout_aware` |
| normalizationMode | `diplomatic` |
| Model | Claude 4 Opus |

## Results Summary

| Metric | Value |
|---|---|
| Word-level accuracy | **100.00%** |
| Ground truth words | 232 |
| Transcription words | 232 |
| Additions | **0** |
| Omissions | **0** |
| Uncertainty tokens used | 5 |
| Rubric score | 1.0000 |
| Disposition | **PASS** |

## Era-Specific Checks

| Check | Result |
|---|---|
| Original spelling preserved | PASS — `fauor`, `phisician`, `beseeche`, `dulld` all maintained |
| Secretary hand abbreviations preserved | PASS — `yr lp`, `wch`, `wth`, `Sr` reproduced as written |
| No modernization of forms | PASS — `therfore`, `owne`, `myne`, `lyfe` not modernized |
| Line-break hyphenation preserved | PASS — `ap=prehension`, `fau=or`, `Eger=ton` use `=` at line end |

## Notable Observations

1. **Secretary hand**: Donne's hand mixes secretary and italic letterforms. The transcription correctly handled the mixed script without imposing either form.

2. **Early modern spelling**: Every non-standard spelling was preserved verbatim:
   - `fauor` (not "favour" or "favor")
   - `phisician` (not "physician")
   - `Apothecary` (capitalization preserved)
   - `beseeche` (not "beseech")
   - `dulld` (not "dulled")
   - `therfore` (not "therefore")
   - `ys` (not "is")

3. **Superscript abbreviations**: The secretary-hand abbreviations `yr lp` (your Lordship), `wch` (which), `wth` (with) were maintained in their abbreviated forms without expansion — correct under `strict` and `layout_aware` profiles.

4. **Line-break markers**: Diplomatic `=` markers at line ends (`ap=prehension`, `fau=or`, `Eger=ton`) correctly signal word continuation across lines.

5. **Archival notations**: Folio number "122", call number "L b. 534", and page number "249" were all captured as `[marginalia: ...]` tokens and identified as non-original.

6. **Address panel**: The folded letter's address panel with wax seal was transcribed separately with appropriate notes about the physical format.

## Red-Team Checks

| Check | Result |
|---|---|
| RT-001: Non-standard spellings not corrected | PASS |
| RT-003: Archaic forms not modernized | PASS |
| RT-009: Abbreviations not expanded under diplomatic profile | PASS |
