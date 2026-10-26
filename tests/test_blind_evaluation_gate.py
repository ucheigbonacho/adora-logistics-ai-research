import json
import tempfile
import unittest
from pathlib import Path
from validation.evaluate_blind import evaluate_blind

class BlindEvaluationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "cases.jsonl"
        self.case = {"id": "BLIND-T1", "experiment_id": "Q1-E01",
                     "input": {"utterance": "Could you recommend a detour for this delivery?"},
                     "expected": "route_proposal_requested",
                     "reviewer": "UNIT-TEST-ONLY", "reviewed_at": "UNIT-TEST",
                     "reference": "UNIT-TEST", "ontology_version": "draft-v0.1",
                     "source_reference": "UNIT-TEST", "review_method": "UNIT-TEST",
                     "approval_reference": "UNIT-TEST", "review_verified": True}

    def write(self, case):
        self.path.write_text(json.dumps(case), encoding="utf-8")

    def test_rejects_unverified(self):
        self.write(dict(self.case, review_verified=False))
        result = evaluate_blind(self.path)
        self.assertEqual(result["status"], "REJECTED_PRECHECK")
        self.assertIsNone(result["evaluation"])

    def test_rejects_development_overlap(self):
        self.write(dict(self.case, input={"utterance": "alternate route"}))
        self.assertEqual(evaluate_blind(self.path)["status"], "REJECTED_PRECHECK")

    def test_scoring_does_not_change_input(self):
        self.write(self.case)
        before = self.path.read_bytes()
        result = evaluate_blind(self.path)
        self.assertEqual(result["status"], "STRUCTURALLY_ACCEPTED_NOT_AUTHENTICATED")
        self.assertEqual(result["evaluation"]["total"], 1)
        self.assertEqual(self.path.read_bytes(), before)
