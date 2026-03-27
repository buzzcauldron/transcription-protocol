# Post-hoc normalization (add-on)

> **Add-on version:** `norm-1.1.0` (see document filenames below).

This folder defines a **separate** protocol for producing a **normalized / searchable text layer** from an existing **diplomatic** transcript. It does **not** replace or modify the [Academic Handwriting Transcription Protocol](../diplomatic-transcription-protocol-v1.1.0.md): transcription remains a no-addition, diplomatic-first product validated by [`benchmark/validate_schema.py`](../benchmark/validate_schema.py).

## Editorial levels (core control)

Normalization is governed by **`normalizationPolicy.editorialLevel`** — not by re-stating diplomatic rules:

| Level | Name | Summary |
|-------|------|---------|
| A | `mechanical` | Whitespace, Unicode, line reflow; no lexical expansion. |
| B | `conservative_editorial` | Mechanical plus orthography/expansion **only** where the diplomatic text already licenses it (e.g. `[exp: …]`). |
| C | `scholarly_editorial` | Conservative plus **documented** interpretive choices in `alignmentNotes` where policy requires; still no §5 hard fails. |

See [normalization-addon-protocol-norm-1.1.0.md §2](normalization-addon-protocol-norm-1.1.0.md).

## When to use this

- You already have a compliant `transcriptionOutput` (or export) from the main protocol.
- You want a **second step**—same or different model, same or different session—that applies an explicit **editorial level** and policy fields **only** as a derivative of that transcript.
- You want artifacts and prompts that **do not** change the core transcription prompts, skill, or schema defaults.

## What this is not

- Not **translation** — `normalizedText` stays in the **document language(s)** as the diplomatic transcript; switching to another language is out of scope and invalid (see [normalization-addon-protocol-norm-1.1.0.md §1.2](normalization-addon-protocol-norm-1.1.0.md)).
- Not a license to “fix” or modernize the diplomatic layer during the initial image-to-text pass.
- Not a path to reconstruct or derive diplomatic `transcriptionOutput` from normalized text; the workflow is **one-way** (diplomatic → normalization only). See [normalization-addon-protocol-norm-1.1.0.md §1.1](normalization-addon-protocol-norm-1.1.0.md).
- Not merged into `validate_schema.py`; optional validation lives in [`benchmark/validate_normalization.py`](../benchmark/validate_normalization.py).

## Documents

| Document | Role |
|----------|------|
| [normalization-addon-protocol-norm-1.1.0.md](normalization-addon-protocol-norm-1.1.0.md) | One-way dependency (§1.1), editorial levels (§2), hierarchy of truth, hard fails, policy fields. |
| [normalization-output-schema-norm-1.1.0.md](normalization-output-schema-norm-1.1.0.md) | Standalone `normalizationOutput` shape and checklist. |
| [normalization-prompt-templates-norm-1.1.0.md](normalization-prompt-templates-norm-1.1.0.md) | Copy-paste normalizer-only prompts. |

## Versioning

The add-on uses its own **`normalizationProtocolVersion`** (current: **`norm-1.1.0`**; legacy **`norm-1.0.0`**), distinct from `transcriptionOutput.protocolVersion` in the main protocol.
