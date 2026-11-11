import tempfile
import unittest
from pathlib import Path
from validation.reproduce_exp09 import reproduce

class Exp09CurrentCodeReproductionTests(unittest.TestCase):
    def test_isolated_scenario_comparison(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "exp09-new"
            report = reproduce(dest)
            self.assertEqual(report["scenarios"], 12)
            self.assertTrue((dest / "manifest.json").exists())
            self.assertTrue((dest / "scenario_comparison.csv").exists())
            self.assertIn("09-09", report["mismatches"])
            with self.assertRaises(FileExistsError):
                reproduce(dest)
