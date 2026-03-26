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

## [1.0.0] — initial release

- Core transcription rules: no addition, uncertainty tokens, diplomatic profiles, segments, pre-check, YAML output shape as documented in companion specs.

---

## Repository add-ons (separate from transcript `protocolVersion`)

### `norm-1.0.0` normalization add-on — 2026-03-26

- New [`normalization-protocol/`](normalization-protocol/README.md): post-hoc **derivative** normalization from existing diplomatic `transcriptionOutput`; own `normalizationProtocolVersion` (`norm-1.0.0`), prompts, and [`NORMALIZATION_OUTPUT_SCHEMA.md`](normalization-protocol/NORMALIZATION_OUTPUT_SCHEMA.md).
- Optional validator [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) (does not change [`benchmark/validate_schema.py`](benchmark/validate_schema.py)).
