# Stress testing with Cursor models (no terminal API keys)

Use this when you want **several models from the Cursor UI** (Chat or Agent) on the **same manuscript images and prompt**, then score outputs with the same **schema + ground-truth gates** as [`stress_run.py`](stress_run.py).

## 1. Images

For **BM-001** (Lincoln letter), download or use the two LoC IIIF URLs from [`manifest.yaml`](manifest.yaml) under `cases.BM-001.image_urls`. After a normal run, files also appear under `benchmark/images/BM-001/page_1.jpg` and `page_2.jpg`.

## 2. Prompt

Use the transcriber rules from [`PROMPT_TEMPLATES.md`](../PROMPT_TEMPLATES.md) and the **CONFIGURATION** block from `manifest.yaml` → `cases.BM-001.prompt` (language, era, diplomatic profile, `sourcePageId`, etc.). Include the **OUTPUT FORMAT** section so the model emits valid YAML (`transcriptionOutput`, `metadata`, `preCheck`, `segments`, `mismatchReport`).

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

## Notes

- Cursor model names and vision support depend on your plan; the methodology matches the automated harness: **same inputs + same gates**.
- If a saved file starts with `ERROR:` (from a failed API run), replay treats it as a failed row.
