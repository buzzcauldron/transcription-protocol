"""Red-team regression tests for stress evaluators and prompt/GT firewalls.

Guards against:
- Ground-truth leakage into model prompts
- Accidental GT drift without review
- Scoring games via normalization, reordering, or uncertain-token branch choice
- Evaluator regressions that would inflate accuracy over time
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

import yaml

from benchmark.ground_truth import (
    DEED_WHITE_GT,
    DONNE_GT,
    JOHNSON_GT,
    KB27_GT,
    LINCOLN_GT_P1,
    LINCOLN_GT_P2,
    LOVEJOY_GT,
    MEDIEVAL_GT,
)
from benchmark._eval_core import word_diff_tolerant, tokenize_for_tolerant_scoring
from benchmark.prompt_builder import build_zones
from benchmark.stress_gate import gates_from_raw
from benchmark.stress_metrics import run_evaluator

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "benchmark" / "manifest.yaml"

# Distinctive GT phrases — must never appear in prompts sent to models.
_GT_PHRASES = [
    "Londinia Dominus Rex per Johannem",
    "iacitiram multiplice",
    "honorable fauor that yr lp",
    "poorest seruant I: Donne",
    "calling forth one accusing murmer",
    "peperit iniquitatem. Lacum",
    "two Indian Deeds for the President's approval",
    "pardon of J S Waring of Md has issued",
    "removed the Post Master at Joliet",
]

# SHA-256 prefixes lock GT strings; update deliberately if scholarly GT changes.
_GT_INTEGRITY = {
    "KB27": ("8be1df047cc6a89c", 249),
    "DONNE": ("e17ace1ebedb68f8", 179),
    "LINCOLN_P1": ("33b748cb9c0d2949", 250),
    "LINCOLN_P2": ("fc81222b1161a4e8", 240),
    "MEDIEVAL": ("df3fda0cc4c577be", 100),
}

# Known-good blind KB27 transcript (modernized spellings). Bounds catch evaluator drift.
_KB27_BLIND_MODERNIZED = (
    "Londonia Dominus Rex per Johannem de Lincoln qui sequitur pro eo optulit se quarto die "
    "versus Magistrum Robertum de Thresk de placito quare cum de iure et secundum legem et "
    "consuetudinem regni Regis nunc Anglie omnia terras et tenementa et redditus ac "
    "advocationes ecclesiasticarum et aliorum beneficiorum ecclesiasticarum quorumcumque "
    "que de domino Rege tenentur in capite sine licencia Regis alienata in manum Regis capi "
    "et penes Regem remanere debeant predictus Robertus ius corone et Regie dignitatis Regis "
    "iniens enervare se in ecclesiam de Northflete vacantem et ad Regis donacionem spectantem "
    "ratione alienacionis advocationis ecclesie illius que quidem advocacio de domino Rege "
    "tenetur in capite sine licencia Regis per Johannem Archiepiscopum Cantuarie facte et "
    "quam etiam advocationem ea de causa in manum suam capi fecit Rex vi et armis est "
    "ingressus et sic in eadem ad huc se tenet et quam pluries bullas et brevia domino Regi "
    "et regno Regis preiudiciales infra idem regnum detulit et in dies deferre fecit et "
    "diversos processus super eiusdem bullis et litteris per callidas machinationes infra "
    "idem regnum prosequitur sum effectum in Regis contempto et iacturam multiplicem ac "
    "iurium corone et Regie dignitatis Regis predictorum exheredationem manifestam et contra "
    "pacem Regis Et ipse non venit et preceptum fuit vicecomiti sicut pluries quod caperet "
    "eum etc Et vicecomites retornavit quod non est inventus etc ideo preceptum est "
    "vicecomiti sicut pluries quod capiat eum si inventus etc Et salvo etc Ita quod habeant "
    "corpus eius coram domino Rege a die Pasche in xv dies ubicumque etc"
)


def _seg(text: str, *, page: int = 1, segment_id: int = 1) -> dict:
    return {"segmentId": segment_id, "pageNumber": page, "text": text}


def _lincoln_segments() -> list[dict]:
    return [
        _seg(LINCOLN_GT_P1, page=1, segment_id=1),
        _seg(LINCOLN_GT_P2, page=2, segment_id=2),
    ]


def _minimal_yaml(segment_text: str, *, page: int = 1) -> str:
    return f"""transcriptionOutput:
  protocolVersion: "1.1.0"
  metadata:
    sourcePageId: "redteam"
    modelId: "test"
    timestamp: "2026-06-10T12:00:00Z"
    protocolVersion: "1.1.0"
    targetLanguage: "lat-Latn"
    languageSet: []
    targetEra: "medieval"
    diplomaticProfile: "layout_aware"
    normalizationMode: "diplomatic"
    runMode: "standard"
  preCheck:
    resolutionAdequate: true
    orientationCorrect: true
    pageBoundariesVisible: true
    pageCount: 1
    scriptIdentified: "test"
    scriptMatchesConfig: true
    conditionNotes: null
    proceedDecision: "proceed"
    abortReason: null
  segments:
    - segmentId: 1
      pageNumber: {page}
      lineRange: "1"
      position: "body"
      text: |
        {segment_text}
      confidence: "medium"
      uncertaintyTokenCount: 0
      notes: null
  mismatchReport:
    - mismatchId: 1
      segmentId: 1
      pass1Reading: "x"
      pass2Reading: "x"
      resolution: "pass2 confirms final text; no edit"
      resolved: true
  hallucinationAudit:
    totalWords: 10
    wordsGroundedInGlyphs: 10
    wordsFromExpansion: 0
    expansionsWithVisibleMark: 0
    normalizationReversals: 0
    formulaSubstitutionsDetected: 0
    auditPass: true
"""


class TestGroundTruthIntegrity(unittest.TestCase):
    def test_gt_checksums_unchanged(self) -> None:
        blobs = {
            "KB27": KB27_GT,
            "DONNE": DONNE_GT,
            "LINCOLN_P1": LINCOLN_GT_P1,
            "LINCOLN_P2": LINCOLN_GT_P2,
            "MEDIEVAL": MEDIEVAL_GT,
        }
        for key, text in blobs.items():
            prefix, word_count = _GT_INTEGRITY[key]
            digest = hashlib.sha256(text.encode()).hexdigest()[:16]
            self.assertEqual(digest, prefix, f"{key} GT changed — update checksum after review")
            self.assertEqual(len(text.split()), word_count, f"{key} word count drift")


class TestPromptFirewall(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    def test_no_gt_phrases_in_prompts(self) -> None:
        for case_id, case in self.manifest["cases"].items():
            system, user = build_zones(case["prompt"])
            blob = (system + user).lower()
            for phrase in _GT_PHRASES:
                with self.subTest(case=case_id, phrase=phrase[:32]):
                    self.assertNotIn(phrase.lower(), blob)

    def test_no_evaluation_hints_in_script_notes(self) -> None:
        forbidden = ("scored against", "page-xml gt", "ground truth", "ground-truth")
        for case_id, case in self.manifest["cases"].items():
            notes = str((case.get("prompt") or {}).get("scriptNotesOptional", "")).lower()
            for hint in forbidden:
                with self.subTest(case=case_id, hint=hint):
                    self.assertNotIn(hint, notes)


class TestModernTolerantScoring(unittest.TestCase):
    def test_illegible_absorbs_gt_word_without_omit(self) -> None:
        gt = ["the", "president", "has", "approved"]
        tr = tokenize_for_tolerant_scoring("the [illegible] has approved")
        diff = word_diff_tolerant(gt, tr)
        self.assertEqual(diff.omissions, [])
        self.assertEqual(diff.wildcard_matches, 1)
        self.assertEqual(diff.substantive_matches, 3)

    def test_all_illegible_is_gaming(self) -> None:
        r = run_evaluator("modern_deed", [_seg("[illegible] " * 40)])
        self.assertEqual(r["disposition"], "FAIL")
        self.assertIn("uncertainty_gaming", r["critical_flags"])

    def test_modern_evaluators_pass_on_gt(self) -> None:
        for ev, gt in [
            ("modern_lovejoy", LOVEJOY_GT),
            ("modern_johnson", JOHNSON_GT),
            ("modern_deed", DEED_WHITE_GT),
        ]:
            with self.subTest(evaluator=ev):
                r = run_evaluator(ev, [_seg(gt)])
                self.assertEqual(r["accuracy_percent"], 100.0)
                self.assertEqual(r["disposition"], "PASS")


class TestPerfectSelfMatch(unittest.TestCase):
    def test_all_evaluators_pass_on_gt(self) -> None:
        cases = [
            ("lincoln", _lincoln_segments()),
            ("medieval", [_seg(MEDIEVAL_GT)]),
            ("legal", [_seg(KB27_GT)]),
            ("earlymodern", [_seg(DONNE_GT)]),
            ("modern_lovejoy", [_seg(LOVEJOY_GT)]),
            ("modern_johnson", [_seg(JOHNSON_GT)]),
            ("modern_deed", [_seg(DEED_WHITE_GT)]),
        ]
        for evaluator, segments in cases:
            with self.subTest(evaluator=evaluator):
                r = run_evaluator(evaluator, segments)
                self.assertEqual(r["accuracy_percent"], 100.0)
                self.assertEqual(r["addition_count"], 0)
                self.assertEqual(r["omission_count"], 0)
                self.assertEqual(r["disposition"], "PASS")


class TestNormalizationBoundaries(unittest.TestCase):
    def test_legal_ignores_case_and_punctuation(self) -> None:
        r = run_evaluator("legal", [_seg(KB27_GT.upper())])
        self.assertEqual(r["disposition"], "PASS")

    def test_legal_penalizes_substitutions(self) -> None:
        mutated = KB27_GT.replace("Londinia", "Londonia", 1)
        r = run_evaluator("legal", [_seg(mutated)])
        self.assertGreater(r["addition_count"], 0)
        self.assertGreater(r["omission_count"], 0)
        self.assertEqual(r["disposition"], "FAIL")

    def test_earlymodern_accepts_line_break_hyphen_join(self) -> None:
        for text in (DONNE_GT, DONNE_GT.replace("ap=prehension", "apprehension")):
            with self.subTest(text="eq" if "=" in text else "expanded"):
                r = run_evaluator("earlymodern", [_seg(text)])
                self.assertEqual(r["disposition"], "PASS")


class TestAdversarialInputs(unittest.TestCase):
    def test_empty_transcript_fails(self) -> None:
        for evaluator in ("lincoln", "medieval", "legal", "earlymodern"):
            with self.subTest(evaluator=evaluator):
                r = run_evaluator(evaluator, [_seg("")])
                self.assertEqual(r["disposition"], "FAIL")
                self.assertGreater(r["omission_count"], 0)

    def test_garbage_transcript_fails(self) -> None:
        r = run_evaluator("legal", [_seg("foo bar baz " * 30)])
        self.assertEqual(r["disposition"], "FAIL")
        self.assertGreater(r["addition_count"], 0)

    def test_hallucination_snippet_fails(self) -> None:
        r = run_evaluator(
            "legal",
            [_seg("Lond Unus Rex et Johannes de Lincolnia qui sequitur pro eo")],
        )
        self.assertEqual(r["disposition"], "FAIL")
        self.assertLess(r["accuracy_percent"], 5.0)

    def test_word_reorder_within_segment_fails(self) -> None:
        words = KB27_GT.split()
        half = len(words) // 2
        shuffled = " ".join(words[half:] + words[:half])
        r = run_evaluator("legal", [_seg(shuffled)])
        self.assertEqual(r["disposition"], "FAIL")
        self.assertLess(r["accuracy_percent"], 60.0)

    def test_cross_evaluator_mismatch_fails(self) -> None:
        r = run_evaluator("lincoln", [_seg(KB27_GT)])
        self.assertEqual(r["disposition"], "FAIL")
        self.assertLess(r["accuracy_percent"], 5.0)


class TestUncertainTokenGaming(unittest.TestCase):
    """First-branch uncertain readings are scored; wrong branch must not pass."""

    def test_lucky_uncertain_branch_passes(self) -> None:
        text = KB27_GT.replace("brevas", "[uncertain: brevas / brevia]")
        r = run_evaluator("legal", [_seg(text)])
        self.assertEqual(r["addition_count"], 0)
        self.assertEqual(r["omission_count"], 0)

    def test_wrong_uncertain_branch_fails(self) -> None:
        text = KB27_GT.replace("brevas", "[uncertain: brevia / brevas]")
        r = run_evaluator("legal", [_seg(text)])
        self.assertGreater(r["addition_count"], 0)
        self.assertGreater(r["omission_count"], 0)


class TestBlindRegressionBounds(unittest.TestCase):
    """Pin expected scoring for a strong but imperfect blind transcript."""

    def test_kb27_blind_modernized_within_bounds(self) -> None:
        r = run_evaluator("legal", [_seg(_KB27_BLIND_MODERNIZED)])
        self.assertGreaterEqual(r["accuracy_percent"], 92.0)
        self.assertLessEqual(r["accuracy_percent"], 96.0)
        self.assertGreaterEqual(r["addition_count"], 10)
        self.assertLessEqual(r["addition_count"], 20)
        self.assertEqual(r["disposition"], "FAIL")


class TestDispositionInvariants(unittest.TestCase):
    def test_any_addition_is_fail(self) -> None:
        text = KB27_GT + " extraword"
        r = run_evaluator("legal", [_seg(text)])
        self.assertGreater(r["addition_count"], 0)
        self.assertEqual(r["disposition"], "FAIL")
        self.assertIn("substantive_additions", r["critical_flags"])

    def test_minor_omissions_conditional_pass(self) -> None:
        words = KB27_GT.split()
        truncated = " ".join(words[:-2])
        r = run_evaluator("legal", [_seg(truncated)])
        self.assertEqual(r["omission_count"], 2)
        self.assertEqual(r["disposition"], "CONDITIONAL_PASS")


class TestExpansionFirewall(unittest.TestCase):
    def test_diplomatic_yaml_blocked_for_medieval(self) -> None:
        yaml_text = _minimal_yaml("& peperit iniquitatem").replace(
            'diplomaticProfile: "layout_aware"',
            'diplomaticProfile: "strict"',
        )
        yaml_text = yaml_text.replace(
            "targetLanguage: \"lat-Latn\"",
            "targetLanguage: \"lat-Latn\"\n    diplomaticToggles:\n      preserveOriginalAbbreviations: true",
        )
        g = gates_from_raw(yaml_text, "medieval")
        self.assertEqual(g["disposition"], "FAIL")
        self.assertIn("expansion firewall", g["notes"])
        self.assertEqual(g["addition_count"], "—")

    def test_expansion_mode_scores_medieval(self) -> None:
        yaml_text = _minimal_yaml(MEDIEVAL_GT).replace(
            'diplomaticProfile: "layout_aware"',
            'diplomaticProfile: "strict"',
        )
        yaml_text = yaml_text.replace(
            "targetLanguage: \"lat-Latn\"",
            "targetLanguage: \"lat-Latn\"\n    diplomaticToggles:\n      preserveOriginalAbbreviations: false",
        )
        g = gates_from_raw(yaml_text, "medieval")
        self.assertTrue(g["schema_ok"])
        self.assertEqual(g["disposition"], "PASS")


class TestGateIntegration(unittest.TestCase):
    def test_gates_from_raw_legal_perfect_pass(self) -> None:
        g = gates_from_raw(_minimal_yaml(KB27_GT), "legal")
        self.assertTrue(g["schema_ok"])
        self.assertEqual(g["disposition"], "PASS")
        self.assertEqual(g["addition_count"], 0)

    def test_schema_failure_overrides_good_text(self) -> None:
        broken = _minimal_yaml(KB27_GT).replace("auditPass: true", "auditPass: false")
        g = gates_from_raw(broken, "legal")
        self.assertFalse(g["schema_ok"])
        self.assertEqual(g["disposition"], "FAIL")


if __name__ == "__main__":
    unittest.main()
