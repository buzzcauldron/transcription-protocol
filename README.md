# Academic Handwriting Transcription Protocol

A strict no-addition transcription system for LLM-assisted manuscript work, built for academic researchers who need extreme fidelity to handwritten source material.

**Core guarantee**: the model will never add, infer, complete, or modernize text. Every ambiguity is explicitly marked. Every output is auditable.

---

## Quick Start

There are three ways to use this protocol, from simplest to most automated.

### Option A: Copy-Paste into Any Chat Interface

No installation required. Works with Claude, ChatGPT, Gemini, or any LLM that accepts image uploads.

1. Open [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md) and copy the **Transcriber Prompt** (Section 1).
2. Fill in the configuration variables at the top:
   - `{targetLanguage}` — e.g., `eng-Latn` for English, `lat-Latn` for Latin ([full list](ACADEMIC_TRANSCRIPTION_PROTOCOL.md#21-target-language))
   - `{targetEra}` — e.g., `medieval`, `early_modern`, `nineteenth_century` ([full list](ACADEMIC_TRANSCRIPTION_PROTOCOL.md#22-target-era))
   - `{diplomaticProfile}` — start with `strict` ([options explained below](#diplomatic-profiles))
   - `{normalizationMode}` — use `diplomatic` unless you need a searchable modernized layer
   - `{sourcePageId}` — any identifier for your page (e.g., `MS-1234-folio-5r`)
3. Paste the filled-in prompt into your chat, attach the manuscript image, and send.
4. For verification, open a **new chat session** and paste the **Verifier Prompt** (Section 2) along with the same image and the transcription output.

### Option B: Install as a Cursor Agent Skill

For repeated use inside Cursor IDE:

```bash
# Clone into your personal skills directory
git clone https://github.com/buzzcauldron/transcription-protocol.git \
  ~/.cursor/skills/academic-transcription
```

The skill auto-activates when you mention transcription, paleography, or manuscript work. Attach a manuscript image and the agent will follow the protocol automatically.

### Option C: Build an Automated Pipeline

For batch processing with programmatic quality control:

1. Review [framework/FRAMEWORK_PLAN.md](framework/FRAMEWORK_PLAN.md) for the full pipeline architecture.
2. Implement the adapter interface from [skill/PROVIDER_ADAPTERS.md](skill/PROVIDER_ADAPTERS.md) for your chosen LLM provider(s).
3. The pipeline runs dual independent transcriptions, diffs them, adjudicates conflicts, validates outputs against the quality rubric, and exports researcher-ready packages.

---

## Configuration Reference

### Target Language

Use ISO 639-3 codes with a script tag. Common values:

| Code | Language |
|---|---|
| `eng-Latn` | English |
| `lat-Latn` | Latin |
| `fra-Latn` | French |
| `deu-Latn` | German (Latin script) |
| `deu-Kurrentschrift` | German (Kurrent script) |
| `ell-Grek` | Greek |
| `ara-Arab` | Arabic |
| `heb-Hebr` | Hebrew |
| `mixed` | Multiple languages (add `languageSet` array) |

For unlisted languages, use the ISO 639-3 code with a hyphenated script identifier.

### Target Era

| Tag | Approximate Range |
|---|---|
| `medieval` | Before 1500 |
| `early_modern` | 1500--1700 |
| `enlightenment` | 1700--1800 |
| `nineteenth_century` | 1800--1900 |
| `twentieth_century` | 1900--2000 |
| `contemporary` | 2000--present |

Add `eraRange` (e.g., `1600-1699`) for tighter paleographic calibration. The era guides glyph decoding only -- it never authorizes inferred wording.

### Diplomatic Profiles

Choose how faithfully the output mirrors the physical page:

| Profile | Use When |
|---|---|
| **`strict`** | You need exact reproduction: every spelling, abbreviation, line break, and punctuation mark as-is. Default choice for most scholarly work. |
| **`semi_strict`** | You want strict content but line-wrap joins are acceptable (marked with `[wrap-join]`). Good for continuous-text reading. |
| **`layout_aware`** | You need spatial information: marginalia, interlinear insertions, deletions, and superscripts captured in markup. Best for codicological analysis. |
| **`diplomatic_plus`** | You need both: a strict diplomatic transcript plus a parallel normalized/searchable layer aligned segment-by-segment. Best for digital editions. |

### Diplomatic Toggles

Fine-tune behavior within your chosen profile:

| Toggle | Default | Effect |
|---|---|---|
| `preserveLineBreaks` | `true` | Keep original line breaks |
| `preserveOriginalAbbreviations` | `true` | Reproduce abbreviations as-is |
| `markExpansions` | `false` | Tag expanded abbreviations with `[exp: ...]` |
| `captureDeletionsAndInsertions` | profile-dependent | Encode strikethroughs and interlinear additions |
| `captureUnclearGlyphShape` | `true` | Note ambiguous letter forms with `[glyph-uncertain: ...]` |

---

## How Uncertainty Is Marked

The protocol uses a fixed set of tokens. The model cannot improvise alternatives or silently skip unclear text.

| Token | Meaning |
|---|---|
| `[illegible]` | Cannot be read at all |
| `[illegible: ~N chars]` | Illegible with estimated extent |
| `[uncertain: X]` | Best reading, low confidence |
| `[uncertain: X / Y]` | Two or more plausible readings |
| `[gap]` | Physical gap or tear |
| `[damaged: description]` | Visible but compromised text |

---

## Benchmark Results

Tested against real manuscripts with established scholarly transcriptions:

| Document | Era | Language | Accuracy | Additions | Result |
|---|---|---|---|---|---|
| Lincoln letter (1837) | 19th century | `eng-Latn` | 99.80% | **0** | CONDITIONAL_PASS |
| Walters W.25 Psalter (~1200) | Medieval | `lat-Latn` | 100% | **0** | PASS |
| Donne letter (1602) | Early modern | `eng-Latn` | 100% | **0** | PASS |

Zero fabricated additions across all test cases. Full results in [`benchmark/test-results/`](benchmark/test-results/).

---

## Repository Structure

```
ACADEMIC_TRANSCRIPTION_PROTOCOL.md   Core protocol and rules
PROMPT_TEMPLATES.md                  Copy-paste prompts for chat/API use
OUTPUT_SCHEMA.md                     Required output structure
QUALITY_RUBRIC.md                    Pass/fail rubric and benchmark cases

framework/
  FRAMEWORK_PLAN.md                  Automated pipeline architecture

skill/
  SKILL.md                           Cursor Agent Skill (Claude-optimized)
  PROVIDER_ADAPTERS.md               Claude / OpenAI / Gemini API adapters

benchmark/
  evaluate.py                        Evaluation scripts
  evaluate_all.py
  ground-truth-*.md                  Known transcriptions for comparison
  test-results/                      Transcription outputs and reports
```

---

## Worked Example

Here is a typical output for a 19th-century English letter under `strict` profile:

```yaml
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
```

The model preserved original spelling, flagged ambiguous words with `[uncertain: ...]`, and marked unreadable text with `[illegible: ...]` -- adding nothing.

---

## License

Protocol documents and evaluation scripts are available for academic and non-commercial use. Benchmark source images are public domain (Library of Congress, Walters Art Museum CC0, Folger Shakespeare Library CC BY-SA 4.0).
