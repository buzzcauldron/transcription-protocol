# Post-hoc normalization (add-on)

This folder defines a **separate** protocol for producing a **normalized / searchable text layer** from an existing **diplomatic** transcript. It does **not** replace or modify the [Academic Handwriting Transcription Protocol](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md): transcription remains a no-addition, diplomatic-first product validated by [`benchmark/validate_schema.py`](../benchmark/validate_schema.py).

## When to use this

- You already have a compliant `transcriptionOutput` (or export) from the main protocol.
- You want a **second step**—same or different model, same or different session—that applies explicit spelling, expansion, and register rules **only** as a derivative of that transcript.
- You want artifacts and prompts that **do not** change the core transcription prompts, skill, or schema defaults.

## What this is not

- Not a license to “fix” or modernize the diplomatic layer during the initial image-to-text pass.
- Not merged into `validate_schema.py`; optional validation lives in [`benchmark/validate_normalization.py`](../benchmark/validate_normalization.py).

## Documents

| Document | Role |
|----------|------|
| [NORMALIZATION_PROTOCOL.md](NORMALIZATION_PROTOCOL.md) | Rules: hierarchy of truth, hard fails, policies. |
| [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md) | Standalone `normalizationOutput` shape and checklist. |
| [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md) | Copy-paste normalizer-only prompts. |

## Versioning

The add-on uses its own **`normalizationProtocolVersion`** (e.g. `norm-1.0.0`), distinct from `transcriptionOutput.protocolVersion` in the main protocol.
