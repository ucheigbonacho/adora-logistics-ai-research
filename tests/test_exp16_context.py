import tempfile
import unittest
from pathlib import Path
from validation.analyze_exp16_context import analyze

ROOT = Path(__file__).resolve().parents[1]

class Exp16ContextTests(unittest.TestCase):
    def test_actual_november_record_context(self):
        source = ROOT / "data/q4_2026/actual_november_records.jsonl"
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "analysis"
            report = analyze(source, destination)
            self.assertEqual(report["sample_size"], 10)
            self.assertEqual(report["signal_only_correct"], 8)
            self.assertEqual(report["eta_context_correct_in_sample"], 10)
            self.assertEqual(report["signal_only_mismatches"], ["PL-Q3-RUN-004", "PL-Q3-RUN-007"])
            self.assertEqual(report["eta_context_mismatches"], [])
            self.assertTrue((destination / "observations.json").exists())
            with self.assertRaises(FileExistsError):
                analyze(source, destination)
