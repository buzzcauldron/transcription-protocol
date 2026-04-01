"""Validator tests: efficient mode allows [crop]; standard-only tokens still forbidden."""

from __future__ import annotations

import unittest

from benchmark.validate_schema import validate_transcription_output


def _minimal_efficient_root(segment_text: str) -> dict:
    return {
        "protocolVersion": "1.1.0",
        "metadata": {
            "sourcePageId": "test-page",
            "modelId": "test-model",
            "timestamp": "2026-03-31T12:00:00Z",
            "protocolVersion": "1.1.0",
            "targetLanguage": "eng-Latn",
            "languageSet": [],
            "targetEra": "nineteenth_century",
            "diplomaticProfile": "strict",
            "normalizationMode": "diplomatic",
            "runMode": "efficient",
        },
        "preCheck": {
            "resolutionAdequate": True,
            "orientationCorrect": True,
            "pageBoundariesVisible": True,
            "pageCount": 1,
            "scriptIdentified": "test",
            "scriptMatchesConfig": True,
            "conditionNotes": None,
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


class EfficientCropTokenTests(unittest.TestCase):
    def test_crop_allowed_in_efficient_mode(self) -> None:
        ok, errors, _warnings = validate_transcription_output(
            _minimal_efficient_root(
                "The witness depo[crop] further stated that the deed was sealed."
            )
        )
        self.assertTrue(ok, msg="; ".join(errors))

    def test_crop_description_allowed_in_efficient_mode(self) -> None:
        ok, errors, _warnings = validate_transcription_output(
            _minimal_efficient_root(
                "In witneſs whereof [crop: binding edge] the party has set his hand."
            )
        )
        self.assertTrue(ok, msg="; ".join(errors))

    def test_marginalia_still_forbidden_in_efficient_mode(self) -> None:
        ok, errors, _warnings = validate_transcription_output(
            _minimal_efficient_root(
                'Main text. [marginalia: left margin: "see roll 12"]'
            )
        )
        self.assertFalse(ok)
        self.assertTrue(any("marginalia" in e.lower() for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
