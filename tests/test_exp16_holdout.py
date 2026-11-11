import json
import tempfile
import unittest
from pathlib import Path
from validation.evaluate_exp16_holdout import evaluate

class Exp16HoldoutTests(unittest.TestCase):
    def test_reviewed_cases_and_missing_eta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "new_holdout.jsonl"
            rows = [
                {"case_id":"NEW-001","expected":"routine","signal_metric":0.9,
                 "appointment_time":"2026-11-09T10:00:00Z","calculated_eta":"2026-11-09T09:55:00Z",
                 "independent_review_ref":"REVIEW-001","reviewed_at":"2026-11-09T11:00:00Z"},
                {"case_id":"NEW-002","expected":"escalate","signal_metric":0.3,
                 "independent_review_ref":"REVIEW-002","reviewed_at":"2026-11-09T11:00:00Z"},
            ]
            source.write_text("\n".join(json.dumps(r) for r in rows)+"\n",encoding="utf-8")
            result = evaluate(source, root / "out")
            self.assertEqual(result["total"], 2)
            self.assertEqual(result["baseline"]["correct"], 0)
            self.assertEqual(result["eta_context"]["evaluated"], 1)
            self.assertEqual(result["eta_context"]["needs_review"], 1)
            self.assertEqual(result["eta_context"]["correct"], 1)
    def test_original_exploratory_cases_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.jsonl"
            source.write_text(json.dumps({"case_id":"PL-Q3-RUN-001","expected":"escalate",
                "signal_metric":0.8,"independent_review_ref":"R","reviewed_at":"2026-11-09T11:00:00Z"})+"\n")
            with self.assertRaisesRegex(ValueError,"Exploratory"):
                evaluate(source, root / "out")
