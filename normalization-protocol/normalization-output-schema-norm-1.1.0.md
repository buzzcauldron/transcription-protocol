# Normalization Output Schema

> **Document file:** `normalization-output-schema-norm-1.1.0.md` · Standalone artifact for [normalization-addon-protocol-norm-1.1.0.md](normalization-addon-protocol-norm-1.1.0.md) (`norm-1.1.0`).  
> **Not** part of `transcriptionOutput` — validated by [`benchmark/validate_normalization.py`](../benchmark/validate_normalization.py), not `validate_schema.py`.

## Relationship to diplomatic output

`normalizationOutput` is **derivative only**. The `source` fields record provenance **from** this file **to** the diplomatic `transcriptionOutput` that was edited—not the other way around. The schema encodes **forward** lineage (diplomatic → normalized) only. This add-on defines **no** valid pipeline from `normalizedText` back to diplomatic segment text. See [normalization-addon-protocol-norm-1.1.0.md §1.1](normalization-addon-protocol-norm-1.1.0.md).

---

## 1. Top-level structure

```yaml
normalizationOutput:
  normalizationProtocolVersion: "norm-1.1.0"
  source:
    sourcePageId: "string"
    sourceProtocolVersion: "1.1.0"     # diplomatic protocol semver
    sourceSchemaRevision: null         # optional; mirrors diplomatic metadata.schemaRevision
    sourceTranscriptionHash: null      # optional SHA-256 of canonical diplomatic YAML/JSON
  normalizationPolicy:
    editorialLevel: "mechanical" | "conservative_editorial" | "scholarly_editorial"
    orthographyTarget: "string"
    abbreviationHandling: "string"
    lineBreakHandling: "preserve" | "reflow_to_spaces" | "other"
    registerNotes: "string or null"
  metadata:
    modelId: "string"
    timestamp: "ISO-8601 UTC"
    notes: "string or null"
  normalizedSegments:
    - segmentId: 1
      diplomaticText: "verbatim copy of segments[segmentId-1].text for this id"
      normalizedText: "string"
      alignmentNotes: "string or null"
```

---

## 2. Field rules

| Field | Rule |
|-------|------|
| `normalizationProtocolVersion` | Must match a version defined in [normalization-addon-protocol-norm-1.1.0.md](normalization-addon-protocol-norm-1.1.0.md). Current: `norm-1.1.0`. Legacy `norm-1.0.0` may still appear in older files. |
| `source.sourcePageId` | Must match the diplomatic transcript’s `metadata.sourcePageId`. |
| `source.sourceProtocolVersion` | Diplomatic `protocolVersion` (semver or legacy alias) of the source transcript. |
| `normalizationPolicy` | Required object; all keys above must be present (`null` allowed only where noted). |
| `normalizationPolicy.orthographyTarget` | Describes target spelling or script norms **within the document language(s)** only; must not encode translation into another language ([normalization-addon-protocol-norm-1.1.0.md §1.2](normalization-addon-protocol-norm-1.1.0.md)). |
| `normalizationPolicy.editorialLevel` | **Required** when `normalizationProtocolVersion` is `norm-1.1.0`. Omit on legacy `norm-1.0.0`. When present: one of `mechanical`, `conservative_editorial`, `scholarly_editorial` — see [normalization-addon-protocol-norm-1.1.0.md §2](normalization-addon-protocol-norm-1.1.0.md). |
| `normalizedSegments` | Ordered list; each item must include `segmentId`, `diplomaticText`, `normalizedText`. |

### Segment rules

| Field | Rule |
|-------|------|
| `segmentId` | Integer matching `segments[].segmentId` in the diplomatic transcript. |
| `diplomaticText` | **Must exactly equal** the `text` field of the corresponding diplomatic segment (string equality after same normalization as validator: exact). |
| `normalizedText` | Derivative only; **same natural language(s) as the diplomatic segment** — translation is invalid ([normalization-addon-protocol-norm-1.1.0.md §1.2](normalization-addon-protocol-norm-1.1.0.md), §5). Must obey [normalization-addon-protocol-norm-1.1.0.md §5](normalization-addon-protocol-norm-1.1.0.md) for the declared `editorialLevel`. |
| `alignmentNotes` | Optional; **required** when policy choices need justification (e.g. picking one branch of `[uncertain: A / B]` at `conservative_editorial` or `scholarly_editorial`, or documenting scholarly choices at `scholarly_editorial`). |

---

## 3. Full example

```yaml
normalizationOutput:
  normalizationProtocolVersion: "norm-1.1.0"
  source:
    sourcePageId: "KB27-344-8773"
    sourceProtocolVersion: "1.1.0"
    sourceSchemaRevision: null
    sourceTranscriptionHash: null
  normalizationPolicy:
    editorialLevel: "conservative_editorial"
    orthographyTarget: "Classical Latin lemmas for expanded forms; diplomatic spelling retained where unexpanded"
    abbreviationHandling: "Expand only where diplomatic uses [exp: ...] with visible suspension"
    lineBreakHandling: "reflow_to_spaces"
    registerNotes: null
  metadata:
    modelId: "claude-4-opus-20260301"
    timestamp: "2026-03-26T12:00:00Z"
    notes: null
  normalizedSegments:
    - segmentId: 1
      diplomaticText: |
        venit et defendit
      normalizedText: "venit et defendit"
      alignmentNotes: null
    - segmentId: 2
      diplomaticText: |
        [uncertain: sub / super] iudice
      normalizedText: "[uncertain: sub / super] iudice"
      alignmentNotes: "Ambiguity retained in normalized layer per normalization-addon-protocol §2 Level B"
```

---

## 4. Validation checklist

- [ ] `normalizationProtocolVersion` present and supported.
- [ ] `source.sourcePageId` and `source.sourceProtocolVersion` present.
- [ ] `normalizationPolicy` complete (all required keys, including `editorialLevel`).
- [ ] Every in-scope `segmentId` from the diplomatic transcript has exactly one row.
- [ ] Each `diplomaticText` equals the diplomatic segment `text` (when validator is run with `--transcript`).
- [ ] No `normalizedText` introduces content absent from diplomatic evidence (manual review; automated checks are limited).
- [ ] **No translation:** `normalizedText` does not render the segment in a different natural language than the diplomatic line (add-on §1.2, §5.7).
- [ ] `metadata.timestamp` valid ISO 8601.

---

## 5. Embedding vs standalone file

- **Standalone file** — Recommended: one YAML file per page containing only `normalizationOutput`.
- **Pipeline packaging** — Downstream tools may bundle diplomatic + normalization outputs; this schema does **not** require merging into `transcriptionOutput`.
