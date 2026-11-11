import tempfile
import unittest
from pathlib import Path
from experiments.EXP_15.receipt_races import run

class Exp15ReceiptRaceTests(unittest.TestCase):
    def test_receipt_races_and_fail_closed_behavior(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "receipt-run"
            report = run(dest, workers=8)
            self.assertEqual(report["manifest"]["scenario_count"], 5)
            self.assertFalse(report["manifest"]["production_dispatch_enabled"])
            r = {item["scenario"]: item for item in report["observations"]}
            same = r["same_receipt_race"]["outcomes"]
            self.assertEqual(same.count("acknowledged"), 1)
            self.assertEqual(same.count("duplicate_ack"), 7)
            conflict = r["conflicting_receipt_race"]["outcomes"]
            self.assertEqual(conflict.count("acknowledged"), 1)
            self.assertEqual(conflict.count("receipt_conflict"), 4)
            self.assertEqual(conflict.count("duplicate_ack"), 3)
            self.assertEqual(r["late_uncertain_receipt"]["ack"], "acknowledged")
            self.assertTrue(r["late_uncertain_receipt"]["replay_returned_none"])
            self.assertEqual(r["expired_claim_race"]["post_expiry_claim_winners"], 0)
            self.assertEqual(r["expired_claim_race"]["status"], "uncertain")
            self.assertEqual(r["unknown_and_unclaimed_receipts"]["unknown"], "unknown_action")
            self.assertEqual(r["unknown_and_unclaimed_receipts"]["unclaimed"], "not_dispatched")
            self.assertTrue(all(not item["external_dispatch_attempted"] for item in r.values()))
