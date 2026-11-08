import tempfile
import unittest
from pathlib import Path
from validation.reproduce_exp13 import reproduce

class Exp13ReproductionTests(unittest.TestCase):
    def test_isolated_http_sqlite_reproduction(self):
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "exp13-new"
            report = reproduce(dest)
            self.assertEqual(report["returncode"], 0)
            self.assertTrue(report["fresh_summary"]["state_integrity_pass"])
            self.assertEqual(report["fresh_summary"]["total_http_requests_ingested"], 203)
            self.assertTrue((dest / "manifest.json").exists())
            with self.assertRaises(FileExistsError):
                reproduce(dest)
