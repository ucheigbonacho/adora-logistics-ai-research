import tempfile
import unittest
from pathlib import Path
from validation.reproduce_exp10 import reproduce

class Exp10ReproductionTests(unittest.TestCase):
    def test_isolated_reproduction(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "exp10-new"
            report = reproduce(dest, count=3)
            self.assertEqual(report["new_trial_count"], 6)
            self.assertEqual(len(report["fresh_summary"]), 2)
            self.assertTrue((dest / "manifest.json").exists())
            self.assertTrue((dest / "trials.csv").exists())
            with self.assertRaises(FileExistsError):
                reproduce(dest, count=3)
