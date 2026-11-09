import json
import tempfile
import unittest
from pathlib import Path
from validation.import_q4_actual_records import import_records

class Q4ActualRecordImportTests(unittest.TestCase):
    def test_lossless_import_and_manifest(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            source = root / "source.jsonl"
            records = []
            for i in range(1, 11):
                row = {
                    "case_id": f"PL-Q3-RUN-{i:03d}",
                    "timestamp": "2026-11-02T08:15:22Z",
                    "scenario": "routine_transit",
                    "expected": "routine",
                    "signal_metric": 0.3,
                    "kind": "status",
                    "utterance": "Fixture only",
                    "telemetry_checksum_sha256": "12345678",
                    "reviewer_id": "fixture-reviewer",
                    "approval_ref": "fixture-approval",
                    "appointment_time": "2026-11-02T09:00:00Z",
                    "calculated_eta": "2026-11-02T09:10:00Z",
                    "connection_state_transition": "CONNECTED_TO_CONNECTED",
                    "verified_dispatch_auth": "fixture-auth",
                    "original_telemetry_event_id": "fixture-event",
                    "telemetry_event_timestamp": "2026-11-02T08:15:21Z",
                    "evaluation_timestamp": "2026-11-02T08:15:22Z",
                    "actual_telemetry_event_id": f"fixture-{i}",
                }
                records.append(json.dumps(row))
            source.write_text("\n".join(records) + "\n", encoding="utf-8")
            destination = root / "import"
            manifest = import_records(source, destination)
            self.assertEqual(manifest["record_count"], 10)
            self.assertEqual((destination / "actual_q4_november_2026.jsonl").read_bytes(), source.read_bytes())
            self.assertEqual(manifest["recorded_outcomes"], {"routine": 10})
            with self.assertRaises(FileExistsError):
                import_records(source, destination)
