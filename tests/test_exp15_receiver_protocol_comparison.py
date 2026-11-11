import tempfile
import unittest
from pathlib import Path
from experiments.EXP_15.receiver_protocol_comparison import run

class Exp15ReceiverProtocolTests(unittest.TestCase):
    def test_competing_protocols_under_identical_faults(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "comparison"
            report = run(dest)
            self.assertEqual(len(report["scenarios"]), 4)
            self.assertEqual(report["summary"]["safe_hold"], {
                "scenarios": 4, "safety_passes": 4, "resolved": 0, "duplicate_effects": 0})
            self.assertEqual(report["summary"]["blind_retry"], {
                "scenarios": 4, "safety_passes": 1, "resolved": 4, "duplicate_effects": 3})
            self.assertEqual(report["summary"]["receiver_reconciliation"], {
                "scenarios": 4, "safety_passes": 4, "resolved": 2, "duplicate_effects": 0})
            self.assertTrue((dest / "manifest.json").exists())
            with self.assertRaises(FileExistsError):
                run(dest)
