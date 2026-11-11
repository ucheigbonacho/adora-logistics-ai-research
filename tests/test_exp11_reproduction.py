import tempfile
import unittest
from pathlib import Path
from validation.reproduce_exp11 import reproduce

class Exp11IsolatedReproductionTests(unittest.TestCase):
    def test_reproduction_is_separate_and_comparable(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "new-exp11"
            result = reproduce(dest)
            self.assertEqual(result["new_trial_count"], 600)
            self.assertEqual(len(result["comparison"]), 2)
            self.assertTrue((dest / "manifest.json").exists())
            self.assertTrue((dest / "trials.csv").exists())
            self.assertTrue(all("matches_published_summary" in item for item in result["comparison"]))
            self.assertEqual([item["new_summary"]["state_compliance_pass"] for item in result["comparison"]], [15, 300])
            self.assertEqual([item["matches_published_summary"] for item in result["comparison"]], [False, False])
            with self.assertRaises(FileExistsError):
                reproduce(dest)
