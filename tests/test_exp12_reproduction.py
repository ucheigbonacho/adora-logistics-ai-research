import json
import tempfile
import unittest
from pathlib import Path

from validation.reproduce_exp12 import reproduce

class Exp12ReproductionTests(unittest.TestCase):
    def test_fresh_reproduction_is_isolated_and_compared(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "fresh"
            result = reproduce(dest)
            self.assertEqual(result["fresh_rows"], 2400)
            self.assertTrue((dest / "trials.csv").exists())
            self.assertTrue((dest / "manifest.json").exists())
            self.assertEqual(len(result["comparison"]), 3)
            self.assertTrue(all(item["matches_original_published"] is False for item in result["comparison"]))
            with self.assertRaises(FileExistsError):
                reproduce(dest)
