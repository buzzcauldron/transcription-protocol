# Normalization Protocol

> **Version `norm-1.1.0`** — Post-hoc **editorial** normalization of diplomatic transcripts.

This document defines **only** the normalization add-on: **editorial levels**, derivative rules, and the `normalizationOutput` artifact. It does **not** define diplomatic transcription. The [Academic Handwriting Transcription Protocol](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md) remains the sole specification for `transcriptionOutput`; `normalizationProtocolVersion` is **not** the same field as `transcriptionOutput.protocolVersion`.

---

## 1. Separation from diplomatic transcription

| Concern | Where it lives |
|--------|----------------|
| Image-to-text, uncertainty tokens, Pass 2, `hallucinationAudit`, `runMode`, profiles | **Diplomatic protocol only** — not repeated here. |
| Turning an **existing** diplomatic transcript into a searchable / editorially styled layer | **This document** (`norm-*`). |

Normalization **never** replaces re-reading the manuscript for diplomatic purposes. Optional image access during normalization **must not** introduce wording that is not already licensed by the diplomatic segment text and its tokens (§5).

### 1.1 One-way dependency

**Valid pipeline:** manuscript → diplomatic `transcriptionOutput` → optional `normalizationOutput`.

Editorial normalization is **strictly downstream** of an existing diplomatic transcript. This add-on defines **no** procedure to produce or “recover” diplomatic `transcriptionOutput` from `normalizationOutput`, nor to treat `normalizedText` as the input to a new diplomatic pass. **Reverse derivation is out of scope and not valid** under this protocol.

`normalizedText` is **not** admissible as primary evidence for readings. For protocol-defined, image-grounded transcription, only diplomatic `segments[].text` (and the manuscript image) holds that authority.

---

## 2. Editorial levels (required choice)

Every normalization run **must** declare exactly one **editorial level** in `normalizationPolicy.editorialLevel`. Levels are ordered from **least** to **most** interpretive. Higher levels **do not** relax §5 hard fails.

### Level A — `mechanical`

**Permitted:** Whitespace normalization, Unicode normalization, line-break reflow per `lineBreakHandling`, trivial punctuation spacing where the diplomatic string unambiguously allows it.

**Not permitted:** Lexical expansion of abbreviations, resolving `[uncertain: A / B]` to a single reading, emending spelling, “completing” legal formulas, or adding proper nouns not present in the diplomatic string.

**Typical use:** Search indexing while preserving diplomatic wording and all bracket tokens verbatim.

### Level B — `conservative_editorial`

**Permitted:** Everything in **mechanical**, plus orthographic or register adjustments **explicitly licensed** by the diplomatic layer—chiefly expansions already marked with `[exp: …]` when `abbreviationHandling` says to realize those expansions in full, and orthography per `orthographyTarget` **without** inventing words that are not licensed by the diplomatic line.

**Not permitted:** Guessed expansions where diplomatic has no `[exp:]` and no other explicit license; silent collapse of `[uncertain:]`; gap fill; formula completion from paleographic “typicality.”

**Typical use:** Readable Latin/English that stays mechanically tied to what the diplomatic transcript already encodes.

### Level C — `scholarly_editorial`

**Permitted:** Everything in **conservative_editorial**, plus **documented** interpretive choices in `alignmentNotes` where policy requires choosing among alternatives **only** for spans the diplomatic text already constrains (e.g. retaining both branches in `normalizedText`, or recording why a conservative merge is impossible).

**Still not permitted:** §5 hard fails—no new content for `[gap:]` / `[illegible:]` without explicit scholarly conjecture markers **and** a clear statement that the conjecture is **not** in the diplomatic layer; no invented names or formulas.

**Typical use:** Human-reviewed or team-reviewed editorial layer; outputs should be treated as **provisional** unless a separate verification step says otherwise (record in `metadata.notes`).

---

## 3. Inputs

1. **Diplomatic source** — A `transcriptionOutput` (or export) whose `segments[].text` is treated as **read-only** evidence. Structural validity is defined by [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md); this add-on does not re-validate the full diplomatic protocol beyond what the optional transcript cross-check needs.

2. **Normalization policy** — Must include `editorialLevel` (§2) and the fields in [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md).

Optional **image access** must not introduce content not licensed by the diplomatic text and tokens (§5).

---

## 4. Hierarchy of truth (derivative layer)

| Layer | Authority |
|--------|-----------|
| Diplomatic `segments[].text` | **Supreme** for what was read from the page (produced under the diplomatic protocol). |
| Bracket tokens in that text | **Binding** for normalization: `normalizedText` must not silently remove uncertainty or gap marking appropriate to the chosen **editorial level**. |
| `normalizedText` | **Derivative** only; must obey §2 and §5. |

If policy and diplomatic evidence conflict, **diplomatic evidence wins** (normalize less, not more).

---

## 5. Hard fails (normalization output invalid)

A `normalizationOutput` is **invalid** if any of the following hold:

1. **Addition** — `normalizedText` introduces lexical content not licensed by the diplomatic string and its tokens for the declared **editorial level** (§2).

2. **Silent disambiguation** — An `[uncertain: A / B]` is collapsed to a single reading without `alignmentNotes` (and, for `scholarly_editorial`, without meeting the level’s documentation rules).

3. **Gap fill** — Material appears for `[gap:]`, `[illegible:]`, or similar without preserving the same uncertainty structure **or** an explicit conjecture convention **and** a statement that the conjecture is not in the diplomatic layer.

4. **Diplomatic mismatch** — `diplomaticText` does not **exactly** match the corresponding diplomatic segment `text` (see schema).

5. **Missing alignment** — Any in-scope diplomatic segment lacks exactly one normalized row.

6. **Missing or invalid editorial level** — For `norm-1.1.0`, `normalizationPolicy.editorialLevel` is **required** and must be one of `mechanical`, `conservative_editorial`, `scholarly_editorial`. Legacy `norm-1.0.0` artifacts may omit it; if present, the same enum applies.

---

## 6. Policy block (required)

See [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md). The policy **must** name:

- **`editorialLevel`** — §2.
- **`orthographyTarget`** — Target orthography or `none` / `unchanged` for mechanical-only runs.
- **`abbreviationHandling`** — How `[exp:]` and abbreviations are realized; `none` for **mechanical**.
- **`lineBreakHandling`** — `preserve` | `reflow_to_spaces` | `other`.
- **`registerNotes`** — Optional register; may be `null`.

---

## 7. Relationship to embedded `normalizedLayer`

The diplomatic [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md) allows an optional embedded `normalizedLayer` on a single `transcriptionOutput`. That is one **combined** workflow. This add-on defines a **standalone** `normalizationOutput` file—same **editorial-level** ideas apply if you embed or split.

---

## 8. Versioning

- **`normalizationProtocolVersion`** — e.g. `norm-1.1.0`. Bumped when **this** add-on’s rules or schema change.
- **Source transcript** — Record `source.sourceProtocolVersion` for traceability only; it refers to the diplomatic protocol, not this add-on.

---

## References

- [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md)
- [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)
- Validator: [`benchmark/validate_normalization.py`](../benchmark/validate_normalization.py)
