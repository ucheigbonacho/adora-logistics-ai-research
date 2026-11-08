import tempfile
import unittest
from pathlib import Path
from validation.reproduce_exp14 import reproduce

class Exp14ReproductionTests(unittest.TestCase):
    def test_isolated_process_recovery(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "exp14-new"
            report = reproduce(dest, repetitions=1)
            self.assertEqual(report["fresh_trial_count"], 6)
            self.assertEqual(len(report["fresh_groups"]), 6)
            self.assertTrue((dest / "manifest.json").exists())
            with self.assertRaises(FileExistsError):
                reproduce(dest, repetitions=1)
