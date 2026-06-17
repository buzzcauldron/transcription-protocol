# Stress testing with Cursor models (no terminal API keys)

Use this when you want **several models from the Cursor UI** (Chat or Agent) on the **same manuscript images and prompt**, then score outputs with the same **schema + ground-truth gates** as [`stress_run.py`](stress_run.py).

## 1. Images

For **BM-001** (Lincoln letter), download or use the two LoC IIIF URLs from [`manifest.yaml`](manifest.yaml) under `cases.BM-001.image_urls`. After a normal run, files also appear under `benchmark/images/BM-001/page_1.jpg` and `page_2.jpg`.

## 2. Prompt

Use the transcriber rules from [`prompt-templates.md`](../prompt-templates.md) and the **CONFIGURATION** block from `manifest.yaml` → `cases.BM-001.prompt` (language, era, diplomatic profile, `sourcePageId`, etc.). Include the **OUTPUT FORMAT** section so the model emits valid YAML (`transcriptionOutput`, `metadata`, `preCheck`, `segments`, `mismatchReport`).

The same text is assembled in code by [`prompt_builder.py`](prompt_builder.py) (`SYSTEM_RULES` + `build_user_text`).

## 3. One run per model

For each model you want in the matrix:

1. Start a **new chat** (avoids cross-talk).
2. Set the **Cursor model** in the picker.
3. **Attach** both page images.
4. Paste the full prompt. Use the **lowest temperature** the UI allows.
5. Copy the **entire** assistant reply (including YAML).

## 4. Save raw responses

For each run, create a folder and file:

`benchmark/test-results/stress/BM-001/<short-label>/response.txt`

Use a short folder name (`gpt-4o`, `claude-opus`, etc.). Optionally add `meta.json` next to it so the report shows a friendly label:

```json
{
  "modelKey": "cursor-gpt",
  "modelId": "gpt-4o",
  "caseId": "BM-001"
}
```

If `meta.json` is missing, the folder name is used as the model column.

## 5. Score locally (replay)

From the repository root:

```bash
python -m benchmark.stress_replay
# or
python -m benchmark.stress_run --replay
```

This reads every `response.txt` under `benchmark/test-results/stress/<case>/...`, runs parse + schema validation + [`stress_metrics`](stress_metrics.py) for the case’s `evaluator` in the manifest, and writes:

- `benchmark/test-results/stress/stress_report.md`
- `benchmark/test-results/stress/stress_results.json`

**Dependencies:** `pyyaml` only (same as [`requirements-stress.txt`](../requirements-stress.txt) without the API SDKs). Install with `pip install pyyaml` if needed.

## Claude Code CLI

To use the **same manifest + prompt zones** with the **`claude`** terminal command (Claude Code), see [`CLAUDE_CLI.md`](CLAUDE_CLI.md).

## Anti-cheating (required for blind runs)

The harness is designed so models cannot score well by shortcutting:

1. **No ground truth in the prompt** — use only `manifest.yaml` `prompt` fields and images. Never paste LOC crowd `.txt` transcripts, Basler/EMMO/PAGE-XML text, or prior `response.txt` files into the chat.
2. **Additions are always fatal** — disposition fails on any substantive word not in GT, regardless of accuracy %.
3. **`[illegible]` is not a free pass** — on `modern_*` cases, one damage token can absorb one GT word without an omission penalty; flooding (>15% wildcards) triggers `uncertainty_gaming` and fails. Use tokens only where glyphs are actually missing — not to skip readable text.
4. **Expansion mode for expanded GT** — `BM-MED-001` and `BM-KB27` must emit `preserveOriginalAbbreviations: false`; diplomatic abbreviations against expanded GT are not scored (expansion firewall).
5. **Schema gaming fails the row** — invented `segments[].position` values, empty `mismatchReport` with segments present, or self-certified `hallucinationAudit` without matching segment text still fail validation before GT is applied.

Regression checks: `python3 -m unittest discover -s tests -p 'test_*.py'`

## Notes

- Cursor model names and vision support depend on your plan; the methodology matches the automated harness: **same inputs + same gates**.
- If a saved file starts with `ERROR:` (from a failed API run), replay treats it as a failed row.
