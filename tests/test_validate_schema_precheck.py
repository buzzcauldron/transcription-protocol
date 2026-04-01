"""Validator tests: preCheck.scriptMatchesConfig and conditionNotes (metadata vs image guidance)."""

from __future__ import annotations

import unittest

from benchmark.validate_schema import validate_transcription_output


def _minimal_efficient_root(
    *,
    script_matches_config: bool,
    condition_notes: str | None,
    target_language: str = "eng-Latn",
    target_era: str = "nineteenth_century",
    segment_text: str = "Witness the deed [crop].",
) -> dict:
    return {
        "protocolVersion": "1.1.0",
        "metadata": {
            "sourcePageId": "test-page",
            "modelId": "test-model",
            "timestamp": "2026-03-31T12:00:00Z",
            "protocolVersion": "1.1.0",
            "targetLanguage": target_language,
            "languageSet": [],
            "targetEra": target_era,
            "diplomaticProfile": "strict",
            "normalizationMode": "diplomatic",
            "runMode": "efficient",
        },
        "preCheck": {
            "resolutionAdequate": True,
            "orientationCorrect": True,
            "pageBoundariesVisible": True,
            "pageCount": 1,
            "scriptIdentified": "English legal hand",
            "scriptMatchesConfig": script_matches_config,
            "conditionNotes": condition_notes,
            "proceedDecision": "proceed",
            "abortReason": None,
        },
        "segments": [
            {
                "segmentId": 1,
                "pageNumber": 1,
                "lineRange": "1",
                "position": "body",
                "text": segment_text,
                "confidence": "medium",
                "uncertaintyTokenCount": 1,
            }
        ],
        "mismatchReport": None,
        "hallucinationAudit": {
            "totalWords": 10,
            "wordsGroundedInGlyphs": 10,
            "wordsFromExpansion": 0,
            "expansionsWithVisibleMark": 0,
            "normalizationReversals": 0,
            "formulaSubstitutionsDetected": 0,
            "auditPass": True,
        },
    }


class PrecheckMetadataTests(unittest.TestCase):
    def test_script_matches_config_false_with_notes_passes(self) -> None:
        """Researcher YAML disagrees with image; flag + document — must still validate."""
        ok, errors, _warnings = validate_transcription_output(
            _minimal_efficient_root(
                script_matches_config=False,
                condition_notes=(
                    "scriptMatchesConfig false: metadata had medieval Latin but page is "
                    "nineteenth-century English per scriptIdentified."
                ),
            )
        )
        self.assertTrue(ok, msg="; ".join(errors))

    def test_script_matches_config_true_passes(self) -> None:
        ok, errors, _warnings = validate_transcription_output(
            _minimal_efficient_root(
                script_matches_config=True,
                condition_notes=None,
            )
        )
        self.assertTrue(ok, msg="; ".join(errors))


if __name__ == "__main__":
    unittest.main()
