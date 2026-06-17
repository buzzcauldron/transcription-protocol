# Academic Handwriting Transcription Protocol

A strict no-addition transcription system for LLM-assisted manuscript work, built for academic researchers who need faithful transcriptions of handwritten documents. This protocol is most effective for 18th century and more modern handwriting, but it can prove an effective stop-gap for researchers without access to specifically trained ML models or without requesite coding resources to build one. 

It provides texts 60-98% correct in order to aid computational analysis or improve access to texts with difficult handwriting. Machine-readable `transcriptionOutput` (metadata, segments, uncertainty tokens, verification and audit blocks) keeps runs **reproducible** and **tool-friendly**; this protocol does not prescribe any particular stack.

The model will never add, infer, complete, or modernize text. Every ambiguity is explicitly marked. Every output is auditable.

This repository contains prompts, rubric, and evaluation criteria needed.


1. **`runMode`** (`standard` | `efficient`) — efficient single-pass mode for throughput, with guard rails that forbid standard-only tokens and incompatible profiles.
2. **Conservative epistemic stance** — default skeptical confidence, honest mismatch reporting, optional `metadata.epistemicNotes` (protocol §1.1).
3. **Crop tokens `[crop]` / `[crop: …]`** — text truncated by image edge, binding, or scan, distinct from `[gap]` and `[illegible]` (Phase 1, protocol §3).
4. **Diplomatic vs expansion firewall** — `preserveOriginalAbbreviations` is a hard split.
4. **Benchmark anti-cheating gates** — ground truth is firewalled (never in prompts); honest `[illegible]` / `[gap]` / `[damaged]` tokens do not count as omissions in `modern_*` evaluators, but wildcard flooding (>15% of GT words) fails as `uncertainty_gaming`; any substantive addition still hard-fails. Regression: [`tests/test_stress_redteam.py`](tests/test_stress_redteam.py).

Full history: [`CHANGELOG.md`](CHANGELOG.md).

## Benchmark results

Latest blind runs via [`benchmark/stress_run.py`](benchmark/stress_run.py) (`temperature=0`, image + prompt only; GT firewalled). Latin cases use **expansion-to-expansion** scoring; `modern_*` cases use tolerant damage-token diff. **Every row fails disposition** because additions > 0 — accuracy is reported for calibration. Shell pipeline (Kraken HTR + LLM correct-mode) results are in [`transcriber-shell`](https://github.com/buzzcauldron/transcription-shell).

**Image-only (Gemini 2.5 Pro):**

| Case | Document | Accuracy | Add | Omit | Schema |
|---|---|---:|---:|---:|:---:|
| BM-001 | Lincoln → Owens (1837) | 95.1% | 31 | 24 | ✓ |
| BM-MED-001 | Walters W.25 psalter | 86.0% | 16 | 14 | ✓ |
| BM-KB27 | KB27.335 plea roll | 31.7% | 165 | 170 | ✓ |
| BM-MOD-DEED | Interior Dept → Nicolay (Indian deeds, 1865) | 98.7% | 4 | 1 | ✓ |
| BM-MOD-LOVEJOY | Lovejoy → Nicolay (Joliet postmaster, 1864) | 81.1%† | 2 | 14 | ✓ |
| BM-MOD-JOHNSON | Reverdy Johnson → Lincoln (pardon, 1864) | 29.9% | 15 | 47 | ✓ |

† Flash baseline (2.5 Pro had YAML parse error on this case).

**Additional image-only model variants (Gemini 2.5 Flash, Flash-Lite, 3.5 Flash):**

| Case | Model | Accuracy | Add | Omit | Schema |
|---|---|---:|---:|---:|:---:|
| BM-001 | `gemini-2.5-flash` | 86.7% | 85 | 65 | ✓ |
| BM-001 | `gemini-3.5-flash` | 93.5% | 19 | 32 | ✗ |
| BM-001 | `gemini-2.5-flash-lite` | 38.2% | 46 | 303 | ✗ |
| BM-MED-001 | `gemini-2.5-flash` | 75.0% | 28 | 25 | ✓ |
| BM-KB27 | `gemini-2.5-flash` | 21.3% | 184 | 196 | ✗ |
| BM-MOD-DEED | `gemini-2.5-flash` | 94.9% | 7 | 4 | ✓ |
| BM-MOD-LOVEJOY | `gemini-2.5-flash` | 81.1% | 2 | 14 | ✓ |
| BM-MOD-JOHNSON | `gemini-2.5-flash` | 23.9% | 20 | 51 | ✓ |

| Reference | Document | Model | Accuracy | Add | Disposition |
|---|---|---|---:|---:|---|
| *(evaluation harness)* | Lincoln → Owens (1837) | Claude 4 Opus | 99.8% | **0** | CONDITIONAL_PASS |
| *(evaluation harness)* | KB27.335 plea roll | Claude 4 Opus | 6.0% WER (15 subst.) | **0** | FAIL |

**Takeaways:** KB27 (King's Bench plea roll) is the dominant unsolved case at 31.7% image-only; a Kraken anglicana fine-tune is in progress in `transcriber-shell`. Raw responses: [`benchmark/test-results/stress/`](benchmark/test-results/stress/); reproduce via [Reproducing the benchmarks](#reproducing-the-benchmarks).

**External line tools:** If you use a line detector (e.g. [Glyph Machina](https://glyphmachina.com/)) only to suggest line boundaries before protocol transcription, see [`benchmark/EXTERNAL_LINE_TOOLS.md`](benchmark/EXTERNAL_LINE_TOOLS.md) for how that relates to `lineRange` and what not to treat as canonical text.

## Dependencies

The **core protocol needs no installation** — it is markdown specs plus copy-paste prompts (Option A below). Optional tooling:

| Use | Install | Notes |
|---|---|---|
| Schema validation | `pip install pyyaml` | [`benchmark/validate_schema.py`](benchmark/validate_schema.py), [`benchmark/validate_lines_xml.py`](benchmark/validate_lines_xml.py) |
| Multi-model stress tests | `pip install -r requirements-stress.txt` | `pyyaml`, `python-dotenv`, `certifi`, `anthropic`, `openai`, `google-generativeai` |
| Provider keys | `.env` (copy from [`.env.example`](.env.example)) | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` |
| Pipeline integration (lineation → HTR → protocol, TEI export) | [`transcriber-shell`](https://github.com/buzzcauldron/transcription-shell) | separate package; vendors this protocol |

No API keys are required for Option A (chat) or for replaying saved responses.

## Quick Start

There are three ways to use this protocol, from simplest to most automated.

### Option A: Copy-Paste into Any Chat Interface

No installation required. Works with Claude, ChatGPT, Gemini, or any LLM that accepts image uploads.

1. Open [prompt-templates.md](prompt-templates.md) and copy the **Transcriber Prompt** (Section 1).
2. Fill in the configuration variables at the top:
   - `{targetLanguage}` — e.g., `eng-Latn` for English, `lat-Latn` for Latin ([full list](diplomatic-transcription-protocol.md#21-target-language))
   - `{targetEra}` — e.g., `medieval`, `early_modern`, `nineteenth_century` ([full list](diplomatic-transcription-protocol.md#22-target-era))
   - `{diplomaticProfile}` — start with `strict` ([options explained below](#diplomatic-profiles))
   - `{normalizationMode}` — use `diplomatic` unless you need a searchable modernized layer
   - `{sourcePageId}` — any identifier for your page (e.g., `MS-1234-folio-5r`)
3. Paste the filled-in prompt into your chat, attach the manuscript image, and send.
4. For verification, open a **new chat session** and paste the **Verifier Prompt** (Section 2) along with the same image and the transcription output.

### Option B: Build an Automated Pipeline

For batch processing with programmatic quality control:

1. Review [framework/FRAMEWORK_PLAN.md](framework/FRAMEWORK_PLAN.md) for the full pipeline architecture.
2. Implement the adapter interface from [skill/PROVIDER_ADAPTERS.md](skill/PROVIDER_ADAPTERS.md) for your chosen LLM provider(s).
3. The pipeline runs dual independent transcriptions, diffs them, adjudicates conflicts, validates outputs against the quality rubric, and exports researcher-ready packages.

## Configuration Reference

The protocol’s **conservative epistemic stance** (default skeptical confidence, honest mismatch reporting, optional **`metadata.epistemicNotes`**) is in [diplomatic-transcription-protocol.md §1.1](diplomatic-transcription-protocol.md#11-conservative-epistemic-stance).

**Run mode** (`runMode`): Choose `standard` (default -- full two-pass verification, all tokens) or `efficient` (single pass, core tokens only, faster throughput). Efficient mode is incompatible with `layout_aware` and `diplomatic_plus` profiles. See [diplomatic-transcription-protocol.md §2.9](diplomatic-transcription-protocol.md#29-run-mode).

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

For unlisted languages, use the ISO 639-3 code with a hyphenated script identifier. For **historical English handwriting**, optionally set `englishHandwritingModality` in output metadata (e.g. `secretary`, `copperplate`) — see [diplomatic-transcription-protocol.md](diplomatic-transcription-protocol.md) §2.8.

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
| `preserveOriginalAbbreviations` | `true` | **Diplomatic mode**: reproduce abbreviations as-is using Unicode combining chars. Set `false` for **expansion mode** — see below. |
| `markExpansions` | `false` | Tag expanded abbreviations with `[exp: ...]` (only when `preserveOriginalAbbreviations: true`) |
| `captureDeletionsAndInsertions` | profile-dependent | Encode strikethroughs and interlinear additions |
| `captureUnclearGlyphShape` | `true` | Note ambiguous letter forms with `[glyph-uncertain: ...]` |

### Diplomatic vs Expansion Mode

`preserveOriginalAbbreviations` controls how abbreviations appear in output text — this is a **hard split**, not a style preference:

| Mode | Toggle value | Output text | Use when |
|---|---|---|---|
| **Diplomatic** (default) | `true` | `dn̄s` (Unicode combining chars preserved) | Paleographic analysis, diplomatic editions, any run not compared to expanded GT |
| **Expansion** | `false` | `dominus` (full word written out) | Scoring against expanded PAGE XML ground truth, corpus linguistics, search indexes |

**Evaluation firewall:** Do not compare diplomatic output against expanded ground truth — the CER will be inflated by 20–40 points. The evaluator (`benchmark/evaluate.py`) enforces this as a hard gate. Prompt config files designed for use with `transcriber-shell` are provided in pairs (e.g. `prompt_charter.yaml` / `prompt_charter_expanded.yaml`) so the intended mode is unambiguous from the filename.

Full expansion rules — what the model must and must not output when `preserveOriginalAbbreviations: false` — are in [diplomatic-transcription-protocol.md §2.4.1](diplomatic-transcription-protocol.md#241-expansion-mode-preserveoriginalabbreviations-false).

## How Uncertainty Is Marked

The protocol uses a fixed set of tokens. The model cannot improvise alternatives or silently skip unclear text.

| Token | Meaning |
|---|---|
| `[illegible]` | Cannot be read at all |
| `[illegible: ~N chars]` | Illegible with estimated extent |
| `[uncertain: X]` | Best reading, low confidence |
| `[uncertain: X / Y]` | Two or more plausible readings |
| `[gap]` | Physical gap or tear |
| `[crop]` / `[crop: description]` | Text truncated by image edge, binding, or scan |
| `[damaged: description]` | Visible but compromised text |

## Reproducing the benchmarks

This is the "run it end-to-end" path: schema validation plus ground-truth word diffs across providers.

### Multi-model stress test

Cross-provider gate checks (schema validation + ground-truth word diff) are implemented in [`benchmark/stress_run.py`](benchmark/stress_run.py). Install API dependencies with `pip install -r requirements-stress.txt`, then set the provider keys you need: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `GOOGLE_API_KEY`. The runner loads a repo-root **`.env`** if present (copy from [`.env.example`](.env.example)); otherwise export variables in your shell.

From the repository root:

```bash
python -m benchmark.stress_run --dry-run
python -m benchmark.stress_run --cases BM-001 --models anthropic openai
```

Outputs land under [`benchmark/test-results/stress/`](benchmark/test-results/stress/) (`stress_report.md`, `stress_results.json`, and per-run raw responses). [`benchmark/manifest.yaml`](benchmark/manifest.yaml) lists cases and default models; optional cases (medieval psalter, KB27, modern LOC letters `BM-MOD-*`, etc.) need `--include-optional` — see [`benchmark/images/README.md`](benchmark/images/README.md).

**Scoring integrity:** GT strings live only in [`benchmark/ground_truth.py`](benchmark/ground_truth.py) and are never assembled into [`prompt_builder.py`](benchmark/prompt_builder.py) output. Latin cases with expanded GT (`medieval`, `legal`) require expansion-mode YAML (`preserveOriginalAbbreviations: false`) or the harness skips word-diff scoring (protocol §2.4.1). Do not paste transcripts or crowd-sourced `.txt` files into the model prompt when running blind benchmarks.

To **re-score saved** `response.txt` files (e.g. from Cursor or a previous API run) without calling providers:

```bash
python -m benchmark.stress_replay
python -m benchmark.stress_run --replay
```

Step-by-step for using **Cursor’s model picker** (no API keys): [`benchmark/CURSOR_STRESS.md`](benchmark/CURSOR_STRESS.md). To drive the **same prompts** through **Claude Code** in the terminal (`claude`): [`benchmark/CLAUDE_CLI.md`](benchmark/CLAUDE_CLI.md) (`python -m benchmark.claude_cli --case BM-001`). For anti-fabrication hardening, use the red-team gate: [`benchmark/RED_TEAM_NO_HALLUCINATION.md`](benchmark/RED_TEAM_NO_HALLUCINATION.md).

## Versioning

The protocol uses **Semantic Versioning** ([semver.org](https://semver.org/)): see the root [`VERSION`](VERSION) file and [`CHANGELOG.md`](CHANGELOG.md). Machine-readable transcript outputs set `protocolVersion` to semver (`1.2.0` is current). The validator accepts legacy `v1.0` / `v1.1` strings as aliases of `1.0.0` / `1.1.0` ([`benchmark/validate_schema.py`](benchmark/validate_schema.py), [diplomatic-transcription-protocol.md](diplomatic-transcription-protocol.md)).

**Benchmarks:** Optional case **`BM-CROP`** in [`benchmark/manifest.yaml`](benchmark/manifest.yaml) targets binding-edge / scan **`[crop]`** tokens; see [`benchmark/test-results/BM-CROP.md`](benchmark/test-results/BM-CROP.md).

For **high-stakes** or **very long** runs, split work across pages or sessions, use the **Verifier** prompt in a separate call, and allow higher output limits—see [diplomatic-transcription-protocol.md](diplomatic-transcription-protocol.md) §5.2 and [quality-rubric.md](quality-rubric.md) §6.2.1.

### Optional: post-hoc normalization

If you already have a diplomatic transcript and want a **separate derivative** normalized layer (searchability, editorial orthography **within the document language(s)**), use the add-on in [`normalization-protocol/`](normalization-protocol/README.md). It has its own version string (current `norm-1.1.0`, **editorial levels** in policy), prompts, and optional validator [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) — it does not change the core transcription workflow. **Translation is not part of normalization** under this protocol.

## Repository Structure

```
VERSION                              Current protocol semver for this repo
CHANGELOG.md                         Human-readable version history
diplomatic-transcription-protocol.md   Core protocol, rules, and output schema (Appendix A)
prompt-templates.md                    Copy-paste prompts for chat/API use
quality-rubric.md                      Pass/fail rubric, benchmarks, adversarial limits

normalization-protocol/              Optional post-hoc normalization (derivative layer)
  README.md                          Entry point for add-on
  normalization-addon-protocol.md    Rules (`norm-1.1.0`)
  normalization-output-schema.md     Standalone normalizationOutput shape
  normalization-prompt-templates.md  Normalizer-only copy-paste prompts

framework/
  FRAMEWORK_PLAN.md                  Automated pipeline architecture

skill/
  SKILL.md                           Cursor Agent Skill (Claude-optimized)
  PROVIDER_ADAPTERS.md               Claude / OpenAI / Gemini API adapters

benchmark/
  evaluate.py                        Evaluation scripts
  evaluate_all.py
  stress_run.py                      Multi-model API stress test (optional)
  stress_replay.py                   Score saved responses only (no API)
  claude_cli.py                      Build prompts for Claude Code CLI (`claude -p`)
  manifest.yaml                    Stress-test cases and model defaults
  CURSOR_STRESS.md                   Run stress tests from Cursor UI + replay
  CLAUDE_CLI.md                      Same harness via Claude Code terminal
  EXTERNAL_LINE_TOOLS.md             Optional: line detectors vs protocol transcript text
  validate_lines_xml.py              Optional: well-formed XML + TextLine counts (PageXML export)
  ground-truth-*.md                  Known transcriptions for comparison
  test-results/                      Transcription outputs and reports
```

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

## TEI Export

The `transcriptionOutput` YAML can be converted to TEI P5 XML via `transcriber-shell yaml-to-tei` (or `scripts/latin_ms/yaml_to_tei.py`). Each segment maps to a `<p rend="{position}">` element in the TEI body. When a segment carries a `lineRange`, physical manuscript lines are encoded as `<lb n="N"/>` milestones:

```xml
<p rend="body">
  <lb n="3"/>prima linea
  <lb n="4"/>secunda linea
  <lb n="5"/>tertia linea
</p>
```

The `n` attribute on `<lb/>` corresponds to the protocol `lineRange` start (e.g. `lineRange: "3-5"` → `n="3"`, `n="4"`, `n="5"`). Segments without `lineRange` that contain a single line set the element text directly. Special positions are handled as follows:

| Protocol position | TEI element |
|---|---|
| `body` | `<p rend="body">` |
| `header` / `footer` | `<p rend="header">` / `<p rend="footer">` |
| `margin_left` / `margin_right` / etc. | `<p rend="marginLeft">` etc. |
| `interlinear` | `<add place="above">` |
| `table_row` / `table_header` | `<table><row><cell>` |

`confidence` maps to `@cert` on the enclosing element.

## Credits & License

- **Transcription protocol, prompts, schema, and rubric** — this repository.
- **Pipeline integration** — [`transcriber-shell`](https://github.com/buzzcauldron/transcription-shell) (lineation → HTR → protocol; `yaml-to-tei`).
- **External line detection** — [Glyph Machina](https://glyphmachina.com/) (line boundaries only; not canonical text — see [`benchmark/EXTERNAL_LINE_TOOLS.md`](benchmark/EXTERNAL_LINE_TOOLS.md)).
- **Benchmark source images** — public domain / open license: Library of Congress, Walters Art Museum (CC0), Folger Shakespeare Library (CC BY-SA 4.0).

Protocol documents and evaluation scripts are available for **academic and non-commercial use**.
