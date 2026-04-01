# BM-CROP (optional benchmark case)

**Purpose:** Exercise protocol **§3** **`[crop]`** / **`[crop: …]`** for lines truncated by **binding, gutter, or scan frame** — distinct from **`[gap]`** (physical absence) and **`[illegible]`** (unreadable ink in frame).

**Image:** Not committed. Place a public-domain manuscript or deed scan with a visible spine or cropped edge at `benchmark/images/BM-CROP/page.jpg` and run `benchmark/stress_run.py` with `--include-optional` (or the project’s equivalent) for model matrix testing after `validate_transcription_output` passes.

**Schema:** Use `protocolVersion` **1.1.0**; efficient mode allows `[crop]` in segment text (see `benchmark/validate_schema.py` and `tests/test_validate_schema_crop.py`).
