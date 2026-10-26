import json
import tempfile
import unittest
from pathlib import Path
from validation.evaluate_user_reported_q1 import evaluate_user_reported


class UserReportedQ1Tests(unittest.TestCase):
    def test_user_reported_comparison_not_independent(self):
        labels=["informational_report","route_proposal_requested","clarification_required",
                "informational_report","clarification_required","informational_report"]
        phrases=["road closed ahead","please find another road","can you hear me",
                 "I heard the road is closed?","alternate route","route may be blocked"]
        rows=[{"id":f"Q1-E01-V{i:02d}","experiment_id":"Q1-E01",
               "input":{"utterance":phrase},"expected":label,
               "status":"USER_REPORTED_UNVERIFIED","review_verified":False}
              for i,(phrase,label) in enumerate(zip(phrases,labels),1)]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"q1.jsonl"
            original="\n".join(json.dumps(x) for x in rows)
            path.write_text(original,encoding="utf-8")
            result=evaluate_user_reported(path)
            self.assertEqual(result["total"],6)
            self.assertEqual(result["matches"],6)
            self.assertEqual(len(result["mismatches"]),0)
            self.assertIn("NOT_INDEPENDENT_VALIDATION",result["basis"])
            self.assertEqual(path.read_text(encoding="utf-8"),original)

    def test_rejects_false_verified_status(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"q1.jsonl"
            rows=[{"id":f"Q1-E01-V{i:02d}","experiment_id":"Q1-E01",
                   "input":{"utterance":"a"},"expected":"clarification_required",
                   "status":"VERIFIED","review_verified":True} for i in range(1,7)]
            path.write_text("\n".join(json.dumps(x) for x in rows))
            with self.assertRaises(ValueError):
                evaluate_user_reported(path)
