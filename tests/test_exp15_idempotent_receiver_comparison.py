import tempfile
import unittest
from pathlib import Path
from experiments.EXP_15.idempotent_receiver_comparison import run

class Exp15IdempotentReceiverComparisonTests(unittest.TestCase):
    def test_standard_idempotency_and_stale_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "results"
            report = run(dest)
            self.assertEqual(report["summary"]["hold"], {
                "cases": 5, "safety_passes": 5, "resolved": 0, "duplicate_suppressed": 0})
            self.assertEqual(report["summary"]["idempotent_retry"], {
                "cases": 5, "safety_passes": 5, "resolved": 5, "duplicate_suppressed": 4})
            self.assertEqual(report["summary"]["conservative_reconcile"], {
                "cases": 5, "safety_passes": 5, "resolved": 2, "duplicate_suppressed": 0})
            self.assertFalse(report["production_dispatch_enabled"])
            self.assertTrue((dest / "observations.json").exists())
            with self.assertRaises(FileExistsError):
                run(dest)
