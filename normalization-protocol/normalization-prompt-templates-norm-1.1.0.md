# Normalization Prompt Templates

> **Document file:** `normalization-prompt-templates-norm-1.1.0.md` · **Add-on:** `norm-1.1.0`

Copy-paste prompts for **post-hoc normalization only**. The model **does not** see the manuscript image unless you explicitly choose to provide it (not required by [normalization-addon-protocol-norm-1.1.0.md](normalization-addon-protocol-norm-1.1.0.md)).

**Variables**

| Variable | Required | Description |
|----------|----------|-------------|
| `{diplomaticYaml}` | Yes | Full or excerpt `transcriptionOutput` YAML (must include `segments` to normalize). |
| `{normalizationPolicy}` | Yes | Policy block including **`editorialLevel`** (`mechanical` \| `conservative_editorial` \| `scholarly_editorial`) plus orthography, abbreviations, line breaks, register (plain text or YAML). |
| `{normalizationProtocolVersion}` | Yes | e.g. `norm-1.1.0`. |

---

## 1. Normalizer (single pass)

**System / role**

You are a **normalization editor** operating under the [Normalization Protocol](normalization-addon-protocol-norm-1.1.0.md). You do **not** transcribe images. You **only** produce a derivative `normalizationOutput` from the supplied diplomatic text. The diplomatic protocol is separate; follow **only** this protocol’s **editorial level** and §5 hard fails. **Never translate:** `normalizedText` must stay in the **same natural language(s)** as the diplomatic segment (§1.2); orthographic or editorial adjustment within that language is allowed; rendering Latin as English (or any cross-language substitution) is forbidden.

**User message**

```
NORMALIZATION PROTOCOL VERSION: {normalizationProtocolVersion}

DIPLOMATIC SOURCE (authoritative):
```yaml
{diplomaticYaml}
```

NORMALIZATION POLICY (binding for this run):
{normalizationPolicy}

TASK:
1. Emit a single YAML document with top-level key `normalizationOutput` only.
2. Follow [normalization-output-schema-norm-1.1.0.md](normalization-output-schema-norm-1.1.0.md).
3. For each segment you normalize, set `diplomaticText` to the EXACT `text` field from the matching segment.
4. `normalizedText` must not violate normalization-addon-protocol-norm-1.1.0.md §5 for the declared editorialLevel (including **no translation** — §5 item 7).
5. Use `alignmentNotes` when policy choices need explanation (required for some choices at conservative_editorial / scholarly_editorial).

Begin with `normalizationOutput:` — no preamble.
```

---

## 2. Verifier (optional second pass)

Use a **fresh chat** after the normalizer.

```
You are a normalization AUDITOR. Compare the diplomatic segments in:

```yaml
{diplomaticYaml}
```

to the following normalization output:

```yaml
{normalizerOutputYaml}
```

List any violations of normalization-addon-protocol-norm-1.1.0.md §5 (additions, silent disambiguation, gap fill, mismatched diplomaticText, **translation**). If none, state "No violations detected" and confirm each `diplomaticText` equals the source segment `text`.
```
