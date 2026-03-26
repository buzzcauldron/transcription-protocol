# Normalization Protocol

> **Version `norm-1.0.0`** — Post-hoc derivative normalization of diplomatic transcripts.

This protocol governs **only** the production of a **normalized layer** from an existing diplomatic output. It is **downstream** of the [Academic Handwriting Transcription Protocol](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md) and must not be conflated with `transcriptionOutput.protocolVersion`.

---

## 1. Scope

**In scope:** Transforming diplomatic segment text into an explicitly policy-driven normalized form (searchability, consistent orthography, expanded abbreviations per policy), with **segment-aligned** provenance.

**Out of scope:** Re-reading the manuscript image, changing diplomatic segment `text`, or bypassing the main protocol’s anti-hallucination gates. Normalization runs **do not** replace a diplomatic transcription pass.

---

## 2. Inputs

A normalization run **must** take as authoritative input:

1. **Diplomatic source** — A complete `transcriptionOutput` document (or equivalent export) that **already conforms** to [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md) for the diplomatic body, **or** a researcher-approved subset that preserves every `segmentId` and verbatim `text` to be normalized.

2. **Normalization policy** — Declared rules for this run (see §5), recorded in the output so results are reproducible.

Optional: **image access** for disambiguation is **not** allowed to introduce content that is not already licensed by the diplomatic text and its uncertainty tokens (see §4).

---

## 3. Hierarchy of truth

| Layer | Authority |
|--------|-----------|
| Diplomatic `segments[].text` | **Supreme** for what was read from the page. |
| Uncertainty tokens (`[uncertain:]`, `[illegible:]`, `[gap:]`, `[exp:]`, etc.) | **Binding**: normalized text **must not** collapse a bracketed alternative into a single “correct” reading **without** reflecting that ambiguity in `normalizedText` (e.g. retain parallel options, repeat tokens, or document the constraint in `alignmentNotes`). |
| `normalizedText` | **Derivative** only: no words, morphemes, or expansions that are not justified by §4. |

If diplomatic text and policy appear to conflict, **policy yields** to diplomatic evidence (you may normalize *less*, not *more*, than the source licenses).

---

## 4. Hard fails (normalization output invalid)

A `normalizationOutput` is **invalid** if any of the following hold:

1. **Addition** — `normalizedText` introduces proper lexical content not licensed by the diplomatic string and its tokens (including sensible expansions only where `diplomaticToggles` / diplomatic profile explicitly allowed marked expansions).

2. **Silent disambiguation** — An `[uncertain: A / B]` (or equivalent) is resolved to a single modern form without recording the choice basis in `alignmentNotes` **or** preserving ambiguity in the normalized string per policy.

3. **Gap fill** — Material appears in `normalizedText` for regions marked `[gap:]`, `[illegible:]`, or similar **without** the same uncertainty structure or an explicit scholarly conjecture marker **and** a statement that the conjecture is **not** in the diplomatic layer.

4. **Diplomatic mismatch** — `diplomaticText` in a normalized segment row does not **exactly** match the corresponding diplomatic segment `text` for that `segmentId` (see [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md)).

5. **Missing alignment** — Any diplomatic segment included in scope lacks a corresponding normalized row (one-to-one for in-scope segments).

---

## 5. Normalization policy (required declaration)

The output **must** include a `normalizationPolicy` block (see schema) that makes explicit at minimum:

- **Orthography target** — e.g. classical Latin, regency English spelling, modern editorial convention (name the standard or house style).
- **Abbreviation handling** — e.g. expand only where `[exp:]` appears in diplomatic; or expand all suspensions per a named paleographic convention.
- **Line breaks / whitespace** — preserve, reflow for search, or normalize to spaces.
- **Register** — e.g. retain historical morphology vs. normalize to lemma forms (only where licensed by source).

Policies may be **conservative** (minimal change) or **aggressive** (maximal readability); aggressive policies **still** cannot violate §4.

---

## 6. Relationship to in-run `normalizedLayer`

The main protocol allows `normalizationMode: normalized` and an embedded `normalizedLayer` inside a single `transcriptionOutput` ([OUTPUT_SCHEMA.md §6](../OUTPUT_SCHEMA.md)). That is one **combined** workflow.

This add-on defines a **standalone** `normalizationOutput` for users who complete diplomatic transcription first and normalize later—possibly with a different tool or model. The **segment-level alignment rules** (`diplomaticText` snapshot, `normalizedText`, `alignmentNotes`) are conceptually aligned with OUTPUT_SCHEMA §6 but live in a **separate document** validated separately.

---

## 7. Versioning

- **`normalizationProtocolVersion`** — Semver prefixed conventionally with `norm-` (e.g. `norm-1.0.0`). Bumped when rules or schema of **this** add-on change.
- **Source transcript** — Record `source.protocolVersion` (diplomatic) and optional `schemaRevision` for traceability.

---

## References

- [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md)
- [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)
- [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md) (diplomatic + optional embedded normalized layer)
- Validator: [`benchmark/validate_normalization.py`](../benchmark/validate_normalization.py)
