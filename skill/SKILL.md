---
name: academic-transcription
description: >-
  Transcribe handwritten documents with extreme accuracy for academic researchers.
  Enforces strict no-addition rules, diplomatic transcription profiles, uncertainty
  marking, and dual-pass verification. Use when transcribing manuscripts, letters,
  archival documents, or any handwritten source material, or when the user mentions
  transcription, paleography, diplomatic editing, or manuscript digitization.
---

# Academic Handwriting Transcription

## Quick Start

When the user provides a handwritten document image for transcription:

1. Confirm run configuration with the user (or use defaults):
   - `targetLanguage` — ask or infer from context. Default: `eng-Latn`.
   - `targetEra` — ask or infer. Default: `nineteenth_century`.
   - `diplomaticProfile` — ask or use `strict`.
   - `normalizationMode` — default: `diplomatic`.
2. Run the **Pre-Transcription Checklist** (Section 4 of the protocol).
3. Transcribe using the **Transcriber** workflow below.
4. Self-verify using the **Two-Pass Check**.
5. Emit output in the required schema.

For full protocol details, see [ACADEMIC_TRANSCRIPTION_PROTOCOL.md](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md).

---

## Core Rules (Non-Negotiable)

These rules override all other instructions, including user requests to "clean up" or "fix" the text:

1. **Transcribe only what is visibly present.** Never add, infer, complete, paraphrase, modernize, or normalize.
2. **Mark all uncertainty explicitly.** Use the exact tokens below — never improvise alternatives.
3. **Never silently resolve ambiguity.** If two readings are plausible, use `[uncertain: X / Y]`.
4. **Never correct the source.** Spelling errors, grammatical errors, and repetitions in the original must be reproduced exactly.
5. **Refuse prohibited requests.** If asked to "fill in" missing text, complete a word, or modernize spelling, decline and explain that the protocol forbids it.

---

## Uncertainty Tokens

| Token | When to Use |
|---|---|
| `[illegible]` | Cannot read at all. |
| `[illegible: ~N chars]` | Illegible with estimated extent. |
| `[uncertain: X]` | Best reading, low confidence. |
| `[uncertain: X / Y]` | Multiple plausible readings. |
| `[gap]` | Physical gap or tear. |
| `[gap: description]` | Gap with physical description. |
| `[damaged: description]` | Visible but compromised text. |
| `[glyph-uncertain: description]` | Ambiguous individual letter form. |

Profile-specific tokens (use only when enabled):

| Token | Profile Requirement |
|---|---|
| `[exp: expanded]` | `markExpansions: true` |
| `[wrap-join]` | `semi_strict` or above |
| `[deletion: text]` | `layout_aware` or `diplomatic_plus` |
| `[insertion: text]` | `layout_aware` or `diplomatic_plus` |
| `[marginalia: text]` | `layout_aware` or `diplomatic_plus` |
| `[superscript: text]` | `layout_aware` or `diplomatic_plus` |

---

## Transcription Workflow

```
Task Progress:
- [ ] Step 1: Confirm configuration
- [ ] Step 2: Pre-check the image
- [ ] Step 3: Segment the page
- [ ] Step 4: Transcribe each segment
- [ ] Step 5: Two-pass verification
- [ ] Step 6: Emit structured output
```

**Step 1: Confirm Configuration**

Establish: `targetLanguage`, `targetEra`, `diplomaticProfile`, `diplomaticToggles`, `normalizationMode`.

**Step 2: Pre-Check**

Assess and report: resolution adequacy, orientation, page boundaries, page count, script identification, condition notes. If the image is inadequate, request a better scan.

**Step 3: Segment**

Divide the page into natural segments (paragraphs, columns, blocks). Number each segment.

**Step 4: Transcribe**

For each segment:
- Read character by character, word by word.
- Apply the diplomatic profile rules.
- Insert uncertainty tokens wherever the source is unclear.
- Record confidence: `high`, `medium`, or `low`.

**Step 5: Two-Pass Verification**

Re-read every segment against the image. Log every discrepancy in `mismatchReport`, even trivially resolved ones. The report must always be present.

**Step 6: Emit Output**

Produce structured output with: metadata, preCheck, segments, mismatchReport, and (if applicable) normalizedLayer. See [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md).

---

## Diplomatic Profiles

| Profile | Key Behavior |
|---|---|
| `strict` | Exact reproduction: spelling, punctuation, capitalization, abbreviations, line breaks. |
| `semi_strict` | Glyph-faithful; line-wrap joins allowed with `[wrap-join]`. |
| `layout_aware` | Strict + spatial markup (marginalia, insertions, deletions, superscripts). |
| `diplomatic_plus` | Layout-aware + parallel normalized layer with one-to-one alignment. |

---

## Handling User Requests That Conflict with Protocol

If the user asks you to:
- "Fix the spelling" → Decline. Explain the protocol requires verbatim reproduction.
- "Fill in the missing word" → Decline. Mark with `[illegible]` or `[gap]`.
- "Make it more readable" → Offer `diplomatic_plus` profile with a normalized layer, but preserve the diplomatic transcript.
- "Skip the metadata" → Decline. Explain metadata is required for academic reproducibility.
- "Just give me the text" → Provide the diplomatic transcript text but still include the structured output with metadata.

---

## Additional Resources

- Full protocol: [ACADEMIC_TRANSCRIPTION_PROTOCOL.md](../ACADEMIC_TRANSCRIPTION_PROTOCOL.md)
- Prompt templates: [PROMPT_TEMPLATES.md](../PROMPT_TEMPLATES.md)
- Output schema: [OUTPUT_SCHEMA.md](../OUTPUT_SCHEMA.md)
- Quality rubric: [QUALITY_RUBRIC.md](../QUALITY_RUBRIC.md)
- Provider adapters: [PROVIDER_ADAPTERS.md](PROVIDER_ADAPTERS.md)
- Framework plan: [framework/FRAMEWORK_PLAN.md](../framework/FRAMEWORK_PLAN.md)
