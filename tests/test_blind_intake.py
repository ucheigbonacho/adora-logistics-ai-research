"""Structural intake checks using unit-test fixtures only, not field evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from validation.blind_intake import validate

class BlindIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "reviewed.jsonl"
        self.row = {
            "id": "BLIND-001", "experiment_id": "Q1-E01",
            "input": {"utterance": "Could you suggest a detour around the highway closure?"},
            "expected": "route_proposal_requested", "reviewer": "TEST-REVIEWER",
            "reviewed_at": "test-date", "reference": "test-reference",
            "ontology_version": "draft-v0.1", "source_reference": "test-source",
            "review_method": "test-method", "approval_reference": "test-approval",
            "review_verified": True,
        }
    def check(self, row):
        self.path.write_text(json.dumps(row), encoding="utf-8")
        return validate(self.path)
    def test_valid_structure(self):
        self.assertTrue(self.check(self.row)["passes_structural_checks"])
    def test_reject_development_overlap(self):
        row = dict(self.row, input={"utterance": "road closed ahead"})
        self.assertFalse(self.check(row)["passes_structural_checks"])
    def test_reject_missing_approval(self):
        self.assertFalse(self.check(dict(self.row, approval_reference=""))["passes_structural_checks"])
    def test_reject_unverified_flag(self):
        self.assertFalse(self.check(dict(self.row, review_verified=False))["passes_structural_checks"])
    def test_does_not_mutate_input(self):
        original = json.dumps(self.row)
        self.path.write_text(original, encoding="utf-8")
        validate(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), original)
