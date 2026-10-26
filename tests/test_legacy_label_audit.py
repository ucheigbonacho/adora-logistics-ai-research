import json
import tempfile
import unittest
from pathlib import Path
from validation.audit_legacy_labels import audit

class LegacyLabelAuditTests(unittest.TestCase):
    def test_preserves_fixture_and_reports_disagreement(self):
        rows = [
            {"id": "a", "experiment_id": "Q2-E01",
             "input": {"available": True, "equipment_match": False,
                       "hours_left": 8, "hours_needed": 3},
             "expected": "resource_constraint_reject"},
            {"id": "b", "experiment_id": "Q2-E01",
             "input": {"available": True, "equipment_match": False,
                       "hours_left": 8, "hours_needed": 3},
             "expected": "assignment_authorized"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.jsonl"
            original = "\n".join(json.dumps(x) for x in rows)
            path.write_text(original, encoding="utf-8")
            result = audit(path)
            self.assertEqual((result["total"], result["matches"], len(result["mismatches"])), (2, 1, 1))
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertIn("not-independent-accuracy", result["basis"])
