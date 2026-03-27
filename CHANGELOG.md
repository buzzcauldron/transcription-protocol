# Changelog

All notable changes to the **Academic Handwriting Transcription Protocol** use [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`). The machine-readable `protocolVersion` field in transcripts uses the same scheme; legacy outputs may still use the `v1.x` prefix (see [OUTPUT_SCHEMA.md](OUTPUT_SCHEMA.md)).

## [1.1.0] — 2026-03-26

### Added

- Formal **semantic versioning** for `protocolVersion`: canonical values `1.0.0` and `1.1.0`; `v1.0` and `v1.1` accepted as legacy aliases (validator maps aliases to canonical semver).
- **`runMode`** (`standard` | `efficient`) with efficient-mode constraints on diplomatic profiles and optional omission of `mismatchReport`.
- **`metadata.epistemicNotes`** and conservative epistemic stance (protocol §1.1).
- **`metadata.schemaRevision`** for companion-document revision tracking (protocol §9).

### Changed

- Mismatch-report and uncertainty rules aligned with two-pass verification for standard mode (protocol §5.2, §5.6).

### Documentation & tooling

- **§2.9:** Explicit **when not to use `efficient` mode** guidance (heavy abbreviation, complex layout, caret insertions, multi-page/palimpsest needs).
- **`benchmark/validate_schema.py`:** When `runMode` is `efficient`, segment `text` must not contain standard-only tokens (`[exp: …]`, `[wrap-join]`, `[deletion: …]`, `[insertion: …]`, `[marginalia: …]`, `[superscript: …]`, `[page-break]`, `[palimpsest: …]`, `[line-end-hyphen]`; protocol §2.9, §3).

### Repository tooling — 2026-03-27

- **`benchmark/validate_schema.py`:** `validate_transcription_output` returns `(ok, errors, warnings)`. When `metadata.diplomaticToggles.markExpansions` is `true`, the number of `[exp:` openings in concatenated segment text must equal `hallucinationAudit.wordsFromExpansion` and `hallucinationAudit.expansionsWithVisibleMark` (protocol §7.3 audit–text consistency).
- **Soft escalation warnings (non-failing):** multiline body segments, `preCheck.conditionNotes` matching damage/abbreviation/difficulty heuristics, and zero `[uncertain]` / `[illegible]` / `[glyph-uncertain]` tokens together emit a §7.3–§7.4 suspected-overconfidence warning (surfaced in [`benchmark/stress_gate.py`](benchmark/stress_gate.py) notes).
- **Protocol §2.4:** Guidance on consistent treatment of scribal `&c` when `markExpansions` is `true`.

## [1.0.0] — initial release

- Core transcription rules: no addition, uncertainty tokens, diplomatic profiles, segments, pre-check, YAML output shape as documented in companion specs.

---

## Repository add-ons (separate from transcript `protocolVersion`)

### `norm-1.1.0` normalization add-on — 2026-03-26

- **Editorial levels** as the primary control: `normalizationPolicy.editorialLevel` is `mechanical` \| `conservative_editorial` \| `scholarly_editorial` ([NORMALIZATION_PROTOCOL.md](normalization-protocol/NORMALIZATION_PROTOCOL.md) §2). Diplomatic transcription rules are not duplicated in the normalization docs.
- **One-way dependency** ([NORMALIZATION_PROTOCOL.md](normalization-protocol/NORMALIZATION_PROTOCOL.md) §1.1): editorial normalization may only follow diplomatic `transcriptionOutput`; no valid protocol path from `normalizationOutput` / `normalizedText` back to diplomatic transcription.
- Schema and examples updated in [`normalization-protocol/NORMALIZATION_OUTPUT_SCHEMA.md`](normalization-protocol/NORMALIZATION_OUTPUT_SCHEMA.md); prompts in [`PROMPT_TEMPLATES.md`](normalization-protocol/PROMPT_TEMPLATES.md).
- [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) accepts both add-on versions; **`norm-1.1.0` requires `editorialLevel`** in policy; **`norm-1.0.0` does not** (legacy). New work should use `norm-1.1.0`.

### `norm-1.0.0` normalization add-on — 2026-03-26

- Initial [`normalization-protocol/`](normalization-protocol/README.md): post-hoc **derivative** normalization from existing diplomatic `transcriptionOutput`; superseded for new work by **`norm-1.1.0`** (editorial levels).
- Optional validator [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) (does not change [`benchmark/validate_schema.py`](benchmark/validate_schema.py)).
