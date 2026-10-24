import json
import tempfile
import unittest
from pathlib import Path

from validation.reviewed_reference import evaluate_reviewed_cases


def sample(**changes):
    case = {"id": "review-1", "experiment_id": "Q2-E01",
            "input": {"available": True, "equipment_match": False,
                      "hours_left": 8, "hours_needed": 3},
            "expected": "resource_constraint_reject",
            "reviewer": "test-reviewer-only", "reviewed_at": "test-date",
            "reference": "test-reference-only"}
    case.update(changes)
    return case


class ReviewedReferenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "reviewed.jsonl"

    def run_cases(self, cases):
        self.path.write_text("\n".join(json.dumps(c) for c in cases), encoding="utf-8")
        return evaluate_reviewed_cases(self.path)

    def test_match(self):
        result = self.run_cases([sample()])
        self.assertEqual((result["passed"], result["failed"]), (1, 0))

    def test_disagreement_reported_not_rewritten(self):
        result = self.run_cases([sample(expected="assignment_authorized")])
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["cases"][0]["actual"], "resource_constraint_reject")

    def test_missing_review_metadata_rejected(self):
        c = sample()
        del c["reviewer"]
        with self.assertRaises(ValueError):
            self.run_cases([c])

    def test_duplicate_case_id_rejected(self):
        with self.assertRaises(ValueError):
            self.run_cases([sample(), sample()])

    def test_engine_error_reported(self):
        result = self.run_cases([sample(experiment_id="unknown")])
        self.assertEqual(result["cases"][0]["error"], "ValueError")
        self.assertEqual(result["failed"], 1)

    def test_no_mutation_of_reference(self):
        raw = json.dumps(sample())
        self.path.write_text(raw, encoding="utf-8")
        evaluate_reviewed_cases(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), raw)
