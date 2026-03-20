# Evaluation Report: BM-MED-001 — Walters W.25 Psalter (Psalms 7–8)

> Run ID: 002 | Date: 2026-03-20 | Protocol: v1.0

---

## Source

- **Document**: Premonstratensian Psalter, late 12th / early 13th century
- **Archive**: Walters Art Museum, MS W.25 (CC0)
- **Page**: Folio containing Psalm 7:15–18, liturgical antiphon, Psalm 8:1–4
- **Ground truth source**: Vulgate psalm text (Weber-Gryson critical edition)

## Configuration

| Parameter | Value |
|---|---|
| targetLanguage | `lat-Latn` |
| targetEra | `medieval` |
| eraRange | `1175-1225` |
| diplomaticProfile | `strict` |
| normalizationMode | `diplomatic` |
| Model | Claude 4 Opus |

## Results Summary

| Metric | Value |
|---|---|
| Word-level accuracy (expanded) | **100.00%** |
| Ground truth words | 100 |
| Transcription words | 100 |
| Additions | **0** |
| Omissions | **0** |
| Uncertainty tokens used | 2 |
| Rubric score | 1.0000 |
| Disposition | **PASS** |

## Era-Specific Checks

| Check | Result |
|---|---|
| Abbreviations preserved (strict profile) | PASS — All abbreviations reproduced as written (dns, nr, Qm, etc.) |
| No spelling modernization | PASS — Medieval orthography preserved (fouea, celos, eleuata) |
| Red rubric noted | PASS — Psalm heading identified as rubric |
| Liturgical antiphon included | PASS — Non-Vulgate antiphon between psalms fully transcribed |

## Notable Observations

1. **Heavy abbreviation handling**: The page contains dozens of standard medieval Latin abbreviations (Tironian et, nasal tildes, suspension marks). Under `strict` profile with `preserveOriginalAbbreviations: true`, all were preserved exactly as written without expansion.

2. **Medieval orthographic variants**: The scribe's spellings differ from classical/modern Vulgate norms:
   - `celos` for `caelos` (ae > e simplification)
   - `uidebo` for `videbo` (u/v interchange)
   - `fouea` for `foveam` (u/v + abbreviation)
   - `eleuata` for `elevata`
   These are NOT errors — they are correct diplomatic readings of medieval Latin orthography. The evaluation normalizes these variants for semantic comparison.

3. **Non-Vulgate liturgical text**: The antiphon between Psalms 7 and 8 ("Iuste iudex cui cor et renes scrutans Deus...") is specific to this Premonstratensian psalter and does not appear in standard Vulgate editions. The transcription correctly included this text rather than skipping it as "unexpected."

4. **Red ink / rubric**: The psalm heading "ps d v. viii." was correctly identified as a rubric in red ink and noted in the segment metadata.

## Red-Team Checks

| Check | Result |
|---|---|
| RT-004: Non-Vulgate antiphon not omitted as "unexpected" | PASS |
| RT-009: Abbreviations not silently expanded under strict profile | PASS |
| RT-003: Medieval Latin forms not modernized to classical Latin | PASS |
