"""Unit tests for benchmark/transcription_harness.py (no API calls)."""

from __future__ import annotations

import unittest

from benchmark.transcription_harness import (
    addition_rate,
    compute_metrics,
    divergence,
    render_report,
    run_mock,
)


class TestTranscriptionHarness(unittest.TestCase):
    def test_flooding_gate_trips_on_dense_uncertainty(self):
        transcript = {
            "segments": [
                {
                    "segmentId": "s1",
                    "lineRange": "1",
                    "text": "[uncertain: a] [uncertain: b] [uncertain: c] sure",
                    "confidence": "low",
                    "notes": None,
                }
            ]
        }
        m = compute_metrics("claude", transcript)
        self.assertTrue(m.flooding_gate_tripped)
        self.assertGreater(m.uncertain_word_rate, 0.30)

    def test_addition_rate_per_100_words(self):
        transcript = {
            "segments": [
                {
                    "segmentId": "s1",
                    "lineRange": "1",
                    "text": "one two three four",
                    "confidence": "high",
                    "notes": None,
                }
            ]
        }
        verification = {
            "additions": ["ghost word"],
            "omissions": [],
            "missingUncertainty": [],
            "diplomaticViolations": [],
            "overallAssessment": "conditional_pass",
        }
        rate = addition_rate(verification, transcript)
        self.assertEqual(rate["addition_count"], 1)
        self.assertEqual(rate["additions_per_100w"], 25.0)

    def test_divergence_detects_provider_split(self):
        a = {
            "segments": [
                {"segmentId": "s1", "text": "alpha beta gamma", "confidence": "high", "notes": None}
            ]
        }
        b = {
            "segments": [
                {"segmentId": "s1", "text": "alpha beta delta", "confidence": "high", "notes": None}
            ]
        }
        d = divergence(a, b)
        self.assertLess(d["overall_similarity"], 1.0)
        self.assertIn("s1", d["per_segment"])

    def test_render_report_includes_sections(self):
        transcript = {
            "segments": [
                {"segmentId": "s1", "text": "hello world", "confidence": "high", "notes": None}
            ]
        }
        result = {
            "metrics": {"openai": compute_metrics("openai", transcript).__dict__},
            "addition_rates": {},
            "divergence": {},
            "errors": {},
        }
        md = render_report(result)
        self.assertIn("Uncertainty / flooding", md)
        self.assertIn("openai", md)

    def test_run_mock_smoke(self):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            run_mock()
        out = buf.getvalue()
        self.assertIn("claude", out)
        self.assertIn("openai", out)


if __name__ == "__main__":
    unittest.main()
