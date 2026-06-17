"""Provider adapter layer for Protocol 1.2.0 (see skill/PROVIDER_ADAPTERS.md).

Shared canonical JSON schemas, provider-specific prompt hardening, and Gemini
schema transforms. Used by benchmark/transcription_harness.py, benchmark/providers.py,
and transcriber-shell LLM adapters (via vendored import).
"""

from __future__ import annotations

from typing import Literal

ProviderName = Literal["anthropic", "openai", "gemini", "claude", "mistral"]

# ---------------------------------------------------------------------------
# Canonical output schema (intersection-safe; see PROVIDER_ADAPTERS.md §2)
# ---------------------------------------------------------------------------

CANONICAL_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["preCheck", "segments", "mismatchReport", "metadata"],
    "properties": {
        "preCheck": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "imageQuality",
                "scriptIdentification",
                "scriptMatchesConfig",
                "conditionNotes",
            ],
            "properties": {
                "imageQuality": {"type": "string"},
                "scriptIdentification": {"type": "string"},
                "scriptMatchesConfig": {"type": "boolean"},
                "conditionNotes": {"type": "string"},
            },
        },
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["segmentId", "lineRange", "text", "confidence", "notes"],
                "properties": {
                    "segmentId": {"type": "string"},
                    "lineRange": {"type": "string"},
                    "text": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "notes": {"type": ["string", "null"]},
                },
            },
        },
        "mismatchReport": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["segmentId", "pass1Reading", "pass2Finding", "resolution"],
                "properties": {
                    "segmentId": {"type": "string"},
                    "pass1Reading": {"type": "string"},
                    "pass2Finding": {"type": "string"},
                    "resolution": {"type": "string"},
                },
            },
        },
        "metadata": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "sourcePageId",
                "protocolVersion",
                "targetLanguage",
                "targetEra",
                "diplomaticProfile",
                "normalizationMode",
                "runMode",
                "englishHandwritingModality",
                "epistemicNotes",
            ],
            "properties": {
                "sourcePageId": {"type": "string"},
                "protocolVersion": {"type": "string"},
                "targetLanguage": {"type": "string"},
                "targetEra": {"type": "string"},
                "diplomaticProfile": {
                    "type": "string",
                    "enum": ["strict", "semi_strict", "layout_aware", "diplomatic_plus"],
                },
                "normalizationMode": {
                    "type": "string",
                    "enum": ["diplomatic", "normalized"],
                },
                "runMode": {"type": "string", "enum": ["standard", "efficient"]},
                "englishHandwritingModality": {"type": ["string", "null"]},
                "epistemicNotes": {"type": ["string", "null"]},
            },
        },
    },
}

VERIFIER_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "sourcePageId",
        "transcriptionAccepted",
        "additions",
        "omissions",
        "missingUncertainty",
        "diplomaticViolations",
        "overallAssessment",
        "notes",
    ],
    "properties": {
        "sourcePageId": {"type": "string"},
        "transcriptionAccepted": {"type": "boolean"},
        "additions": {"type": "array", "items": {"type": "string"}},
        "omissions": {"type": "array", "items": {"type": "string"}},
        "missingUncertainty": {"type": "array", "items": {"type": "string"}},
        "diplomaticViolations": {"type": "array", "items": {"type": "string"}},
        "overallAssessment": {
            "type": "string",
            "enum": ["pass", "fail", "conditional_pass"],
        },
        "notes": {"type": "string"},
    },
}

GPT_HARDENING = """
GPT-SPECIFIC HARDENING (do not relax the shared prohibitions):
- A grammatical, plausible sentence is NOT evidence. Faded/clipped/ambiguous word \
=> emit an uncertainty token, never the most likely word. Fluent prose is a FAILURE \
if any token is unsupported by glyphs.
- Per-word decision rule: glyph unambiguous -> transcribe; two readings -> \
[uncertain: X / Y]; unreadable -> [illegible]; edge cutoff -> [crop]. No "best guess" branch.
- Do not normalize archaic spelling or long-s to make a line scan."""

CLAUDE_HARDENING = """
CLAUDE-SPECIFIC HARDENING:
- Begin output with the transcript. Do not narrate method or confidence policy first.
- The >30% uncertainty gate (§ABS 11) is a hard ceiling, not a target. Near it => you are \
over-marking; re-read and commit to glyph-supported readings.
- One uncertainty token per genuinely ambiguous span, not per word in a hard line."""

VERIFIER_HEADER = """You are an academic transcription verifier under the Academic \
Handwriting Transcription Protocol 1.2.0. You are given the source image and a \
transcription produced by another agent. Audit it; do NOT re-transcribe or correct."""

VERIFIER_CHECKS = """
PERFORM ALL CHECKS:
A. ADDITION CHECK — list any transcription text NOT visible in the image.
B. OMISSION CHECK — list any visible image text MISSING from the transcription.
C. UNCERTAINTY CHECK — list regions presented as certain that are actually ambiguous.
D. DIPLOMATIC COMPLIANCE — list violations of the active diplomatic profile.
E. METADATA CHECK — confirm required fields and a present mismatchReport.
Emit the verificationReport per schema. Zero issues => empty arrays, overallAssessment 'pass'."""


def normalize_provider(provider: str) -> str:
    p = (provider or "").strip().lower()
    if p in ("anthropic", "claude"):
        return "anthropic"
    if p in ("openai", "gpt", "chatgpt"):
        return "openai"
    if p in ("gemini", "google"):
        return "gemini"
    return p


def augment_system_for_provider(system: str, provider: str) -> str:
    """Append provider-specific hardening to the shared systemRules zone."""
    p = normalize_provider(provider)
    if p == "anthropic":
        return system + CLAUDE_HARDENING
    if p in ("openai", "gemini", "mistral"):
        return system + GPT_HARDENING
    return system


def openai_system_role(provider: str) -> str:
    """OpenAI Chat Completions role for systemRules (developer preferred for GPT-5.x)."""
    return "developer" if normalize_provider(provider) == "openai" else "system"


def gemini_schema_transform(schema: dict) -> dict:
    """Transform canonical JSON Schema into Gemini OpenAPI-3 dialect."""
    type_map = {
        "object": "OBJECT",
        "array": "ARRAY",
        "string": "STRING",
        "boolean": "BOOLEAN",
        "integer": "INTEGER",
        "number": "NUMBER",
    }

    def conv(node: dict) -> dict:
        out: dict = {}
        t = node.get("type")
        if isinstance(t, list):
            non_null = [x for x in t if x != "null"][0]
            out["type"] = type_map[non_null]
            out["nullable"] = "null" in t
        elif isinstance(t, str):
            out["type"] = type_map[t]
        if "enum" in node:
            out["enum"] = node["enum"]
        if node.get("type") == "object" or (
            isinstance(t, list) and "object" in t
        ):
            props = {k: conv(v) for k, v in node.get("properties", {}).items()}
            out["properties"] = props
            if node.get("required"):
                out["required"] = node["required"]
            out["propertyOrdering"] = list(props.keys())
        if node.get("type") == "array" or (isinstance(t, list) and "array" in t):
            out["items"] = conv(node["items"])
        return out

    return conv(schema)
