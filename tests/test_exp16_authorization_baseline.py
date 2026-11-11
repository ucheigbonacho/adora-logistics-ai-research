import json
import tempfile
import unittest
from pathlib import Path
from validation.evaluate_exp16_authorization_baseline import baseline, evaluate

class Exp16AuthorizationBaselineTests(unittest.TestCase):
    def test_rule_safety_cases(self):
        common = {"utterance": "dispatch load 12", "auth_verified": True,
                  "confirmation_matches": True, "state_fresh": True}
        self.assertEqual(baseline(common), "authorize")
        self.assertEqual(baseline({**common, "auth_verified": False}), "reject")
        self.assertEqual(baseline({**common, "confirmation_matches": False}), "reject")
        self.assertEqual(baseline({**common, "state_fresh": None}), "clarify")
        self.assertEqual(baseline({**common, "utterance": "GPS heartbeat stable"}), "clarify")

    def test_independently_labeled_evaluation_interface(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            reviews = root / "reviews.jsonl"
            features = root / "features.jsonl"
            output = root / "results"
            reviews.write_text(json.dumps({
                "case_id": "TEST-ONLY-001", "authorization_label": "clarify",
                "reviewer_id": "TEST-FIXTURE", "reviewed_at": "2026-11-10T12:00:00Z",
                "review_evidence_ref": "TEST-FIXTURE", "label_rationale": "Unit test only"
            }) + "\n")
            features.write_text(json.dumps({
                "case_id": "TEST-ONLY-001", "utterance": "GPS heartbeat stable",
                "auth_verified": True, "confirmation_matches": None,
                "state_fresh": True
            }) + "\n")
            summary = evaluate(reviews, features, output)
            self.assertEqual(summary["correct"], 1)
            self.assertEqual(summary["total"], 1)
            self.assertTrue((output / "observations.json").exists())
            with self.assertRaises(FileExistsError):
                evaluate(reviews, features, output)
