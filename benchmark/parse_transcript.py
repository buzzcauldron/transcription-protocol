"""Extract YAML from model responses (handles markdown fences and preamble)."""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple

import yaml

_FENCE = re.compile(r"^```(?:yaml)?\s*\n(.*?)\n```\s*$", re.DOTALL | re.MULTILINE)


def extract_yaml_text(raw: str) -> str:
    raw = raw.strip()
    m = _FENCE.search(raw)
    if m:
        return m.group(1).strip()
    # First line starting with transcriptionOutput
    if "transcriptionOutput:" in raw:
        idx = raw.index("transcriptionOutput:")
        return raw[idx:].strip()
    return raw


def parse_transcription_yaml(raw: str) -> Tuple[Dict[str, Any] | None, str | None]:
    """
    Parse model output into a dict. Returns (data, error_message).
    Root may be transcriptionOutput or full document containing it.
    """
    text = extract_yaml_text(raw)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"
    if data is None:
        return None, "Empty YAML"
    if not isinstance(data, dict):
        return None, "Root must be a mapping"
    return data, None


def get_transcription_root(data: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str | None]:
    """Normalize to the inner transcriptionOutput mapping."""
    if "transcriptionOutput" in data:
        inner = data["transcriptionOutput"]
        if isinstance(inner, dict):
            return inner, None
        return None, "transcriptionOutput must be a mapping"
    # Some models emit metadata/segments at top level
    if "metadata" in data and "segments" in data:
        return data, None
    return None, "Missing transcriptionOutput or top-level metadata/segments"
