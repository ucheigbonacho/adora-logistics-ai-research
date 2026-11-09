import json
import tempfile
import unittest
from pathlib import Path
from validation.evaluate_exp16_q4 import evaluate

class Exp16Q4OperationalBaselineTests(unittest.TestCase):
    def test_threshold_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            source = root / "fixture.jsonl"
            rows = [
                {"case_id": "test-1", "expected": "escalate", "signal_metric": 0.8},
                {"case_id": "test-2", "expected": "routine", "signal_metric": 0.2},
                {"case_id": "test-3", "expected": "routine", "signal_metric": 0.75},
            ]
            raw = "".join(json.dumps(row) + "\n" for row in rows)
            source.write_text(raw, encoding="utf-8")
            result = evaluate(source, root / "new-results")
            self.assertEqual(result["count"], 3)
            self.assertEqual(result["correct"], 2)
            self.assertEqual(result["confusion"]["routine_as_escalate"], 1)
            self.assertEqual(source.read_text(encoding="utf-8"), raw)
            with self.assertRaises(FileExistsError):
                evaluate(source, root / "new-results")
