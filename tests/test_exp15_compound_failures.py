import tempfile
import unittest
from pathlib import Path
from experiments.EXP_15.compound_failures import run

class Exp15CompoundFailuresTests(unittest.TestCase):
    def test_compound_recovery_invariants(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "new-compound-run"
            report = run(dest, workers=8)
            self.assertEqual(report["manifest"]["scenario_count"], 4)
            self.assertFalse(report["manifest"]["production_dispatch_enabled"])
            results = {r["scenario"]: r for r in report["observations"]}
            for row in results.values():
                self.assertEqual(row["claim_winners"], 1)
                self.assertEqual(row["attempts"], 1)
                self.assertTrue(row["replay_claim_returned_none"])
                self.assertFalse(row["external_dispatch_attempted"])
            self.assertEqual(results["concurrent_claim_restart_late_ack"]["status"], "acknowledged")
            self.assertEqual(results["concurrent_claim_expiry_no_receipt"]["status"], "uncertain")
            self.assertEqual(results["conflicting_payload_during_uncertain"]["outcome"], "conflict")
            self.assertEqual(results["duplicate_enqueue_after_ack"]["outcome"], "duplicate")
            with self.assertRaises(FileExistsError):
                run(dest)
