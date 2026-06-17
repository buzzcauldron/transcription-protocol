"""Tests for Protocol 1.2.0 provider adapter layer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.provider_adapters import (  # noqa: E402
    CANONICAL_SCHEMA,
    augment_system_for_provider,
    gemini_schema_transform,
    normalize_provider,
    openai_system_role,
)
from benchmark.transcription_harness import compute_metrics, run_mock  # noqa: E402


def test_normalize_provider_aliases():
    assert normalize_provider("claude") == "anthropic"
    assert normalize_provider("gpt") == "openai"
    assert normalize_provider("google") == "gemini"


def test_augment_system_appends_hardening():
    base = "SHARED RULES"
    assert "GPT-SPECIFIC" in augment_system_for_provider(base, "openai")
    assert "CLAUDE-SPECIFIC" in augment_system_for_provider(base, "anthropic")
    assert augment_system_for_provider(base, "openai") != augment_system_for_provider(base, "anthropic")


def test_openai_system_role():
    assert openai_system_role("openai") == "developer"
    assert openai_system_role("anthropic") == "system"


def test_gemini_schema_transform_uppercases_types():
    out = gemini_schema_transform(CANONICAL_SCHEMA)
    assert out["type"] == "OBJECT"
    assert "segments" in out["properties"]
    assert out["properties"]["segments"]["type"] == "ARRAY"


def test_harness_mock_flooding_and_additions(capsys):
    run_mock()
    out = capsys.readouterr().out
    assert "TRIPPED" in out
    assert "additions" in out.lower()


def test_harness_cli_mock():
    proc = subprocess.run(
        [sys.executable, "-m", "benchmark.transcription_harness", "--mock"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Cross-Provider Transcription Comparison" in proc.stdout


def test_compute_metrics_empty_segments():
    m = compute_metrics("test", {"segments": []})
    assert m.total_words == 1  # guard divisor
    assert m.flooding_gate_tripped is False
