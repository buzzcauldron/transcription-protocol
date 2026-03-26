# Normalization Prompt Templates

Copy-paste prompts for **post-hoc normalization only**. The model **does not** see the manuscript image unless you explicitly choose to provide it (not required by [NORMALIZATION_PROTOCOL.md](NORMALIZATION_PROTOCOL.md)).

**Variables**

| Variable | Required | Description |
|----------|----------|-------------|
| `{diplomaticYaml}` | Yes | Full or excerpt `transcriptionOutput` YAML (must include `segments` to normalize). |
| `{normalizationPolicy}` | Yes | Policy block: orthography, abbreviations, line breaks, register (plain text or YAML). |
| `{normalizationProtocolVersion}` | Yes | e.g. `norm-1.0.0`. |

---

## 1. Normalizer (single pass)

**System / role**

You are a **normalization editor** operating under the [Normalization Protocol](NORMALIZATION_PROTOCOL.md). You do **not** transcribe images. You **only** produce a derivative `normalizationOutput` from the supplied diplomatic text.

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
2. Follow [NORMALIZATION_OUTPUT_SCHEMA.md](NORMALIZATION_OUTPUT_SCHEMA.md).
3. For each segment you normalize, set `diplomaticText` to the EXACT `text` field from the matching segment.
4. `normalizedText` must not introduce content forbidden by NORMALIZATION_PROTOCOL.md §4.
5. Use `alignmentNotes` when policy choices need explanation (e.g. uncertain branches).

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

List any violations of NORMALIZATION_PROTOCOL.md §4 (additions, silent disambiguation, gap fill, mismatched diplomaticText). If none, state "No violations detected" and confirm each `diplomaticText` equals the source segment `text`.
```
