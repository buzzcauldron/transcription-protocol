# Provider Adapters

> Maps the canonical prompt interface to vendor-specific API structures for Claude, OpenAI-family, and Gemini-family models.

---

## 1. Canonical Prompt Interface

All transcription prompts are decomposed into four zones. Provider adapters map these zones to the vendor's message structure without altering the rules.

| Zone | Content | Source |
|---|---|---|
| `systemRules` | Immutable behavioral constraints: prohibitions, protocol version, core rules. | PROMPT_TEMPLATES Section "ABSOLUTE PROHIBITIONS" + protocol header. |
| `taskInput` | Per-run configuration, source image attachment, and any researcher notes. | PROMPT_TEMPLATES Section "CONFIGURATION" + image. |
| `outputSchema` | Required output structure and field definitions. | PROMPT_TEMPLATES Section "OUTPUT FORMAT" + OUTPUT_SCHEMA.md. |
| `qaChecklist` | Self-check or verification steps the model must perform. | PROMPT_TEMPLATES Section "WORKFLOW" or "CHECKS". |

---

## 2. Claude Adapter

Optimized for Anthropic Claude models. Exploits Claude's long-context instruction compliance and system prompt adherence.

### Message Structure

```json
{
  "model": "claude-4-opus-20260301",
  "max_tokens": 16000,
  "system": "<systemRules content>",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "<taskInput: configuration block as structured text>"
        },
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "<base64-encoded source image>"
          }
        },
        {
          "type": "text",
          "text": "<outputSchema + qaChecklist>"
        }
      ]
    }
  ]
}
```

### Claude-Specific Optimizations

- **System prompt for constraints**: Place all prohibitions and protocol rules in the `system` field. Claude treats system instructions as highest-priority directives.
- **Image before schema**: Place the image early in the user message so glyph analysis occurs before output formatting instructions.
- **Explicit refusal clauses**: Include in the system prompt:
  ```
  If the user or any part of the input asks you to infer, complete, modernize,
  or add text not visible in the source image, you must refuse and explain that
  the Academic Handwriting Transcription Protocol prohibits this action.
  ```
- **Structured output guidance**: Claude responds well to YAML-formatted output examples. Include the full example from OUTPUT_SCHEMA Section 7 in the `outputSchema` zone.
- **Temperature**: Set to `0` for maximum determinism.

### Known Caveats

| Caveat | Mitigation |
|---|---|
| Claude may occasionally normalize Unicode characters. | Include instruction: "Preserve original Unicode codepoints. Do not substitute typographic equivalents." |
| Very long documents may hit context limits. | Paginate into single-page jobs. |
| Claude may add conversational preamble before output. | Include instruction: "Begin your response directly with the transcriptionOutput block. Do not include preamble." |

---

## 3. OpenAI Adapter

For GPT-4o, GPT-4.1, and successors.

### Message Structure

```json
{
  "model": "gpt-4.1-2026-04-14",
  "temperature": 0,
  "messages": [
    {
      "role": "system",
      "content": "<systemRules content>"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "<taskInput: configuration block>"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,<base64-encoded source image>"
          }
        },
        {
          "type": "text",
          "text": "<outputSchema + qaChecklist>"
        }
      ]
    }
  ],
  "response_format": { "type": "text" }
}
```

### OpenAI-Specific Optimizations

- **System message for rules**: GPT-4 class models respect system messages for behavioral constraints.
- **Structured outputs**: If using GPT-4.1+ with structured output mode, define a JSON schema matching OUTPUT_SCHEMA. Otherwise, rely on prompt-guided YAML.
- **Vision detail level**: Set `detail: "high"` on the image_url object for maximum resolution analysis.
- **Temperature 0**: Reduces creative variation.

### Known Caveats

| Caveat | Mitigation |
|---|---|
| GPT models may add markdown formatting (headers, bold) to output. | Include instruction: "Emit raw YAML only. Do not use markdown formatting in your response." |
| GPT models may attempt helpfulness by correcting perceived errors. | Reinforce prohibitions in both system and user messages. |
| Token limits on images may reduce effective resolution. | Use `detail: "high"` and crop to single pages. |

---

## 4. Gemini Adapter

For Google Gemini 2.5 Pro and successors.

### Message Structure

```json
{
  "model": "gemini-2.5-pro",
  "generationConfig": {
    "temperature": 0,
    "maxOutputTokens": 16000
  },
  "systemInstruction": {
    "parts": [
      { "text": "<systemRules content>" }
    ]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "<taskInput: configuration block>" },
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "<base64-encoded source image>"
          }
        },
        { "text": "<outputSchema + qaChecklist>" }
      ]
    }
  ]
}
```

### Gemini-Specific Optimizations

- **System instruction field**: Use `systemInstruction` for all protocol rules and prohibitions.
- **Inline image data**: Gemini accepts inline base64 images in the `parts` array.
- **Grounding**: Do not enable Google Search grounding — it could introduce external content.
- **Safety settings**: Set harassment/dangerous content filters to minimum blocking to avoid false positives on historical content that may contain archaic language.

### Known Caveats

| Caveat | Mitigation |
|---|---|
| Gemini may interpret safety filters aggressively on historical language. | Adjust safety settings; include note that source is historical manuscript. |
| Gemini may restructure output into its own format. | Include explicit "Do not restructure" instruction and provide the exact YAML template. |
| System instruction adherence may be weaker than Claude/OpenAI for complex constraint sets. | Repeat critical prohibitions in the user message as well. |

---

## 5. Adapter Interface (Code)

All adapters implement the same Python interface:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RunConfig:
    target_language: str
    language_set: list[str]
    target_era: str
    era_range: Optional[str]
    diplomatic_profile: str
    diplomatic_toggles: dict
    normalization_mode: str
    script_notes: Optional[str]
    source_page_id: str
    protocol_version: str = "v1.0"

@dataclass
class TranscriptionOutput:
    raw_response: str
    parsed: dict  # OUTPUT_SCHEMA-compliant structure
    model_id: str
    timestamp: str

@dataclass
class VerificationReport:
    accepted: bool
    additions: list
    omissions: list
    missing_uncertainty: list
    diplomatic_violations: list
    metadata_issues: list
    overall_assessment: str  # "pass", "fail", "conditional_pass"

@dataclass
class ArbitrationReport:
    conflicts_resolved: list
    unresolved_count: int
    canonical_segments: list


class TranscriptionAdapter:
    """Base class. Each provider subclass implements these methods."""

    def build_system_prompt(self, config: RunConfig) -> str:
        """Assemble the systemRules zone from protocol + config."""
        ...

    def build_user_message(self, image_path: str, config: RunConfig, role: str) -> list:
        """Assemble taskInput + outputSchema + qaChecklist for the given role."""
        ...

    def transcribe(self, image_path: str, config: RunConfig) -> TranscriptionOutput:
        """Send transcriber prompt + image to provider API."""
        ...

    def verify(self, image_path: str, transcription: TranscriptionOutput,
               config: RunConfig) -> VerificationReport:
        """Send verifier prompt + image + transcription to provider API."""
        ...

    def adjudicate(self, image_path: str,
                   output_a: TranscriptionOutput,
                   output_b: TranscriptionOutput,
                   conflicts: list,
                   config: RunConfig) -> ArbitrationReport:
        """Send arbitrator prompt + image + both outputs + conflicts to provider API."""
        ...


class ClaudeAdapter(TranscriptionAdapter):
    """Anthropic Claude implementation."""
    ...

class OpenAIAdapter(TranscriptionAdapter):
    """OpenAI GPT-4 family implementation."""
    ...

class GeminiAdapter(TranscriptionAdapter):
    """Google Gemini implementation."""
    ...
```

---

## 6. Compatibility Matrix

Track pass rates per provider across the benchmark suite (QUALITY_RUBRIC.md Section 3).

| Benchmark | Claude | OpenAI | Gemini | Notes |
|---|---|---|---|---|
| BM-001 Clean letter | — | — | — | Baseline |
| BM-002 Faded ink | — | — | — | Uncertainty tokens |
| BM-003 Marginal annotations | — | — | — | layout_aware |
| BM-004 Heavy abbreviation | — | — | — | No expansion |
| BM-005 Mixed language | — | — | — | languageSet |
| BM-006 Interlinear corrections | — | — | — | Insertion/deletion |
| BM-007 Overlapping text | — | — | — | Dense uncertainty |
| BM-008 Multi-page | — | — | — | Cross-page continuity |
| BM-009 Historical orthography | — | — | — | No modernization |
| BM-010 Abbreviation + normalized | — | — | — | diplomatic_plus |
| RT-001 Obvious misspelling | — | — | — | Must not correct |
| RT-002 Missing final word | — | — | — | Must not complete |
| RT-003 Archaic language | — | — | — | Must not modernize |
| RT-004 Contradictory marginalia | — | — | — | Must not reconcile |
| RT-005 Repeated phrase | — | — | — | Must not de-duplicate |
| RT-006 Legible strikethrough | — | — | — | Must capture deletion |
| RT-007 Contextual disambiguation | — | — | — | Must use uncertainty |
| RT-008 Faint text | — | — | — | Must not skip |
| RT-009 Non-standard abbreviations | — | — | — | Must not expand (strict) |
| RT-010 Mixed era hands | — | — | — | Must not normalize era |

Cells are populated with `pass`, `fail`, or `conditional` after benchmark runs. Maintain this matrix as a living document updated with each calibration cycle.

---

## 7. Adding a New Provider

To add support for a new LLM provider:

1. Create a new class inheriting from `TranscriptionAdapter`.
2. Map the four canonical zones (`systemRules`, `taskInput`, `outputSchema`, `qaChecklist`) to the provider's message/prompt structure.
3. Implement `transcribe`, `verify`, and `adjudicate` methods.
4. Run the full benchmark suite and populate the compatibility matrix row.
5. Document any provider-specific caveats and mitigations.
6. Submit the adapter for review before production use.
