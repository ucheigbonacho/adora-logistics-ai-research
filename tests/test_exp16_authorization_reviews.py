import json
import tempfile
import unittest
from pathlib import Path
from validation.validate_exp16_authorization_reviews import validate

class Exp16AuthorizationReviewIntakeTests(unittest.TestCase):
    def test_independent_review_schema(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "review.jsonl"
            record = {"case_id":"CASE-001","authorization_label":"clarify",
                      "reviewer_id":"REVIEWER-001","reviewed_at":"2026-11-10T12:00:00Z",
                      "review_evidence_ref":"REVIEW-001","label_rationale":"Ambiguous instruction"}
            p.write_text(json.dumps(record)+"\n",encoding="utf-8")
            self.assertEqual(validate(p)["labels"],{"clarify":1})
            record["authorization_label"]="escalate"
            p.write_text(json.dumps(record)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Invalid authorization"):
                validate(p)
