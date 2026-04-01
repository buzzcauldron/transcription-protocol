# Changelog

> **Document:** `CHANGELOG.md` · Tracks **Academic Handwriting Transcription Protocol** releases (repo [`VERSION`](VERSION)).

All notable changes to the **Academic Handwriting Transcription Protocol** use [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`). The machine-readable `protocolVersion` field in transcripts uses the same scheme; legacy outputs may still use the `v1.x` prefix (see [transcription-output-schema-v1.1.0.md](transcription-output-schema-v1.1.0.md)).

## [1.1.0] — 2026-03-26

### Normalization — document language only (2026-03-28)

- [normalization-addon-protocol-norm-1.1.0.md](normalization-protocol/normalization-addon-protocol-norm-1.1.0.md) **§1.2** and **§5** item 7: normalization **never** translates into another language; `orthographyTarget` is intra-language only. README, schema checklist, skill workflow, and normalizer prompts updated accordingly.

### Documentation layout (filenames)

- Core specs use **descriptive, versioned filenames** at repo root (e.g. `diplomatic-transcription-protocol-v1.1.0.md`, `transcription-output-schema-v1.1.0.md`, `quality-rubric-v1.1.0.md`, `prompt-templates-v1.1.0.md`). Each file states **protocol 1.1.0** in its header.
- **`ADVERSARIAL_LIMITS.md` removed** — content merged into **§6** of [`quality-rubric-v1.1.0.md`](quality-rubric-v1.1.0.md).
- Normalization add-on docs renamed under [`normalization-protocol/`](normalization-protocol/README.md) (e.g. `normalization-addon-protocol-norm-1.1.0.md`).

### Added

- Formal **semantic versioning** for `protocolVersion`: canonical values `1.0.0` and `1.1.0`; `v1.0` and `v1.1` accepted as legacy aliases (validator maps aliases to canonical semver).
- **`runMode`** (`standard` | `efficient`) with efficient-mode constraints on diplomatic profiles and optional omission of `mismatchReport`.
- **`metadata.epistemicNotes`** and conservative epistemic stance (protocol §1.1).
- **`metadata.schemaRevision`** for companion-document revision tracking (protocol §9).

### Changed

- Mismatch-report and uncertainty rules aligned with two-pass verification for standard mode (protocol §5.2, §5.6).

### Phase 1 revision (2026-03-31) — same protocol semver `1.1.0`

Per **Phase 1** adoption (no protocol semver bump; spec filenames unchanged):

- **Core uncertainty tokens `[crop]` and `[crop: description]`** (protocol §3): mark text truncated by image edge, binding, or scan — distinct from `[gap]` (physical absence) and `[illegible]` (unreadable ink). Documented in [diplomatic-transcription-protocol-v1.1.0.md](diplomatic-transcription-protocol-v1.1.0.md), [prompt-templates-v1.1.0.md](prompt-templates-v1.1.0.md), [skill/SKILL.md](skill/SKILL.md), and [quality-rubric-v1.1.0.md](quality-rubric-v1.1.0.md) §1.3.
- **Skill routing (protocol §2.9):** when marginalia, clerk indexing, or layout markup requires profile tokens, use **`runMode: standard`** with **`layout_aware`** / **`diplomatic_plus`** as appropriate — not **`efficient`** with those profiles. Document routing in **`metadata.scriptNotes`** or **`metadata.epistemicNotes`**.
- **Long-s (U+017F) / scribal forms:** prompt and skill guidance not to modernize **ſ** or archaic spelling in Latin-alphabet hands.
- **`benchmark/validate_schema.py`:** efficient-mode forbidden-token scan allows **`[crop]`** as a core token (comment in source). Unit tests: `tests/test_validate_schema_crop.py`.
- **Optional stress case `BM-CROP`** in [benchmark/manifest.yaml](benchmark/manifest.yaml); notes in [benchmark/test-results/BM-CROP.md](benchmark/test-results/BM-CROP.md) and [benchmark/images/README.md](benchmark/images/README.md).
- **Pre-check vs metadata:** protocol §4, [skill/SKILL.md](skill/SKILL.md), [prompt-templates-v1.1.0.md](prompt-templates-v1.1.0.md), and [benchmark/prompt_builder.py](benchmark/prompt_builder.py) — when visible script/language/era **does not** match declared `targetLanguage` / `targetEra`, align metadata with the image or set `scriptMatchesConfig: false` and document; no fixed “medieval Latin” requirement. Regression: [`tests/test_validate_schema_precheck.py`](tests/test_validate_schema_precheck.py).

### Documentation & tooling

- **§2.9:** Explicit **when not to use `efficient` mode** guidance (heavy abbreviation, complex layout, caret insertions, multi-page/palimpsest needs).
- **`benchmark/validate_schema.py`:** When `runMode` is `efficient`, segment `text` must not contain standard-only tokens (`[exp: …]`, `[wrap-join]`, `[deletion: …]`, `[insertion: …]`, `[marginalia: …]`, `[superscript: …]`, `[page-break]`, `[palimpsest: …]`, `[line-end-hyphen]`; protocol §2.9, §3). Core tokens include `[crop]` / `[crop: …]` (Phase 1).

### Repository tooling — 2026-03-27

- **`benchmark/validate_schema.py`:** `validate_transcription_output` returns `(ok, errors, warnings)`. When `metadata.diplomaticToggles.markExpansions` is `true`, the number of `[exp:` openings in concatenated segment text must equal `hallucinationAudit.wordsFromExpansion` and `hallucinationAudit.expansionsWithVisibleMark` (protocol §7.3 audit–text consistency).
- **Soft escalation warnings (non-failing):** multiline body segments, `preCheck.conditionNotes` matching damage/abbreviation/difficulty heuristics, and zero `[uncertain]` / `[illegible]` / `[glyph-uncertain]` tokens together emit a §7.3–§7.4 suspected-overconfidence warning (surfaced in [`benchmark/stress_gate.py`](benchmark/stress_gate.py) notes).
- **Protocol §2.4:** Guidance on consistent treatment of scribal `&c` when `markExpansions` is `true`.

## [1.0.0] — initial release

- Core transcription rules: no addition, uncertainty tokens, diplomatic profiles, segments, pre-check, YAML output shape as documented in companion specs.

---

## Repository add-ons (separate from transcript `protocolVersion`)

### `norm-1.1.0` normalization add-on — 2026-03-26

- **Editorial levels** as the primary control: `normalizationPolicy.editorialLevel` is `mechanical` \| `conservative_editorial` \| `scholarly_editorial` ([normalization-addon-protocol-norm-1.1.0.md](normalization-protocol/normalization-addon-protocol-norm-1.1.0.md) §2). Diplomatic transcription rules are not duplicated in the normalization docs.
- **One-way dependency** ([normalization-addon-protocol-norm-1.1.0.md](normalization-protocol/normalization-addon-protocol-norm-1.1.0.md) §1.1): editorial normalization may only follow diplomatic `transcriptionOutput`; no valid protocol path from `normalizationOutput` / `normalizedText` back to diplomatic transcription.
- Schema and examples updated in [`normalization-protocol/normalization-output-schema-norm-1.1.0.md`](normalization-protocol/normalization-output-schema-norm-1.1.0.md); prompts in [`normalization-protocol/normalization-prompt-templates-norm-1.1.0.md`](normalization-protocol/normalization-prompt-templates-norm-1.1.0.md).
- [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) accepts both add-on versions; **`norm-1.1.0` requires `editorialLevel`** in policy; **`norm-1.0.0` does not** (legacy). New work should use `norm-1.1.0`.

### `norm-1.0.0` normalization add-on — 2026-03-26

- Initial [`normalization-protocol/`](normalization-protocol/README.md): post-hoc **derivative** normalization from existing diplomatic `transcriptionOutput`; superseded for new work by **`norm-1.1.0`** (editorial levels).
- Optional validator [`benchmark/validate_normalization.py`](benchmark/validate_normalization.py) (does not change [`benchmark/validate_schema.py`](benchmark/validate_schema.py)).
