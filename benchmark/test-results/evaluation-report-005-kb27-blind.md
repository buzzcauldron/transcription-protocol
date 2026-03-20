# Evaluation Report: BM-005 — KB27.335 AALT 0235 (BLIND TEST)

## Document Details

| Field | Value |
|---|---|
| **Source** | KB27.335 AALT 0235 (King's Bench plea roll) |
| **Era** | Medieval (c. 1340–1380) |
| **Language** | Medieval Latin (legal) |
| **Script** | Gothic cursive anglicana, legal hand |
| **Ground Truth** | PAGE XML (nw-page-editor) |
| **Test Type** | **BLIND** — ground truth not seen before transcription |

## Results

| Metric | Value |
|---|---|
| **CER** | 1.82% (29 edits / 1596 chars) |
| **WER** | 6.00% (15 edits / 250 words) |
| **Additions** | 0 |
| **Omissions** | 0 |
| **Substitutions** | 15 |
| **Disposition** | **FAIL** (WER > 5%) |

## Error Analysis

All 15 errors are **substitutions** — no words were added or omitted. Every error falls into the same pattern: the LLM silently normalized scribal Latin to classical/standard forms.

### Spelling Normalization (10 errors)
| Ground Truth | Transcription | Error |
|---|---|---|
| `ecclesticarum` | `ecclesiasticarum` | Normalized to classical spelling |
| `quoruscumque` | `quorumcumque` | Normalized to classical spelling |
| `iacitiram` | `iacturam` | Normalized to classical spelling |
| `lettris` | `litteris` | Normalized to classical spelling |
| `corporus` | `corpus` | Normalized to classical spelling |
| `preiudicialies` | `preiudiciales` | Normalized to classical spelling |
| `dignitatus` | `dignitatis` | Normalized to classical spelling |
| `brevas` | `brevia` | Normalized to classical declension |
| `Londinia` | `Londonia` | Wrong vowel in toponym |
| `Lincoln` | `Lincolnia` | Added suffix not present |

### Abbreviation Expansion Errors (3 errors)
| Ground Truth | Transcription | Error |
|---|---|---|
| `tenementibus` | `tenementa` | Wrong case ending on expansion |
| `Rege` | `Regem` | Wrong case ending on expansion |
| `advocato` | `advocacio` | Wrong expansion |

### Reading Rejection (2 errors)
| Ground Truth | Transcription | Error |
|---|---|---|
| `sedem` | `secundum` | Rejected unusual reading, substituted expected legal formula |
| `multiplice` | `multiplicem` | Changed case ending to "correct" Latin |

## Key Finding

**The dominant failure mode is Latin normalization bias.** The LLM's training on Latin corpora causes it to silently "correct" scribal spellings to classical forms. This produces zero additions and zero omissions — the word count is exactly right — but 6% of words are silently altered.

This is especially insidious because:
1. The output *looks* correct to anyone not comparing character-by-character
2. The "corrections" are plausible Latin
3. No uncertainty tokens are emitted because the model is *confident* in its normalization

## Protocol Response

Based on this blind test, the protocol has been updated with:
1. A new **Section 5.4: Latin Normalization Bias** with a concrete error table
2. Anti-normalization rules requiring the model to prefer visually unusual readings
3. A self-check step in the two-pass verification specifically targeting normalization
4. The SKILL.md has been updated with the same warnings and made platform-agnostic
