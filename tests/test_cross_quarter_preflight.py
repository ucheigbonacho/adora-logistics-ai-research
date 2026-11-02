"""Regression tests use unit-test fixtures, not historical field evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from validation.cross_quarter_preflight import audit

class CrossQuarterPreflightTests(unittest.TestCase):
    def test_quarter_and_checksum_warnings_without_mutation(self):
        record={"case_id":"PL-Q3-RUN-T1","timestamp":"2026-11-02T08:15:22Z",
                "scenario":"routine_transit","expected":"routine","signal_metric":0.2,
                "kind":"status","utterance":"test only","telemetry_checksum_sha256":"deadbeef",
                "reviewer_id":"TEST","approval_ref":"TEST"}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.jsonl"
            original=json.dumps(record)
            p.write_text(original,encoding="utf-8")
            result=audit(p)
            issues={x["issue"] for x in result["issues"]}
            self.assertEqual(result["total"],1)
            self.assertEqual(result["by_actual_quarter"]["Q4"],1)
            self.assertIn("id_quarter_mismatch",issues)
            self.assertIn("unverifiable_truncated_checksum",issues)
            self.assertEqual(p.read_text(encoding="utf-8"),original)

    def test_future_record_flagged(self):
        record={"case_id":"PL-Q4-T1","timestamp":"2026-12-10T08:00:00Z",
                "scenario":"test","expected":"routine","signal_metric":0.2,
                "kind":"status","utterance":"test","telemetry_checksum_sha256":"a"*64,
                "reviewer_id":"TEST","approval_ref":"TEST"}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.jsonl"
            p.write_text(json.dumps(record))
            result=audit(p)
            self.assertIn("future_timestamp",{x["issue"] for x in result["issues"]})
