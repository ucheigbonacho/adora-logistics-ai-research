import tempfile
import unittest
from pathlib import Path
from experiments.EXP_15.run import run

class Exp15BaselineTests(unittest.TestCase):
    def test_local_scenarios_are_isolated(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "new-exp15"
            result = run(dest)
            self.assertEqual(result["manifest"]["scenario_count"], 5)
            self.assertFalse(result["manifest"]["network_dispatch_enabled"])
            observations = {r["scenario"]: r for r in result["observations"]}
            self.assertEqual(observations["ack_after_expiry"]["final_status"], "acknowledged")
            self.assertEqual(observations["expired_without_receipt"]["final_status"], "uncertain")
            self.assertEqual(observations["conflicting_replay"]["replay"], "conflict")
            self.assertEqual(observations["duplicate_replay"]["replay"], "duplicate")
            with self.assertRaises(FileExistsError):
                run(dest)
