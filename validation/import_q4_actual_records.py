"""Import owner-confirmed actual Q4 JSONL records without rewriting source fields.

Usage: python -m validation.import_q4_actual_records --source /path/to/original.jsonl --output-dir /path/to/new-import
Only the original ten JSON objects belong in --source; do not include the separate Python snippet.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED = ("case_id", "timestamp", "scenario", "expected", "signal_metric",
            "kind", "utterance", "telemetry_checksum_sha256", "reviewer_id",
            "approval_ref", "appointment_time", "calculated_eta",
            "connection_state_transition", "verified_dispatch_auth",
            "original_telemetry_event_id", "telemetry_event_timestamp",
            "evaluation_timestamp", "actual_telemetry_event_id")

def validate(source):
    raw = Path(source).read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 10:
        raise ValueError(f"Expected ten actual Q4 records; found {len(rows)}")
    ids = [row["case_id"] for row in rows]
    expected_ids = [f"PL-Q3-RUN-{i:03d}" for i in range(1, 11)]
    if ids != expected_ids or len(set(ids)) != len(ids):
        raise ValueError("Case IDs differ from the ten owner-confirmed records")
    for row in rows:
        if not isinstance(row, dict) or any(k not in row for k in REQUIRED):
            raise ValueError("Missing required source field")
        if not row["timestamp"].startswith("2026-11-02T"):
            raise ValueError("Record timestamp does not match November 2, 2026")
        datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        if row["expected"] not in ("escalate", "routine"):
            raise ValueError("Unexpected source outcome label")
    return raw, rows

def import_records(source, output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    raw, rows = validate(source)
    if Path(source).resolve() == dest or Path(source).resolve() in dest.parents:
        raise ValueError("Source and output paths must be separate")
    dest.mkdir(parents=True)
    (dest / "actual_q4_november_2026.jsonl").write_bytes(raw)
    manifest = {
        "classification": "OWNER_CONFIRMED_ACTUAL_Q4_NOVEMBER_2026_OPERATIONAL_TEST_RECORDS",
        "source_file_sha256": hashlib.sha256(raw).hexdigest(),
        "record_count": len(rows),
        "case_ids": [r["case_id"] for r in rows],
        "recorded_outcomes": dict(Counter(r["expected"] for r in rows)),
        "source_prefix_preserved": True,
        "source_bytes_preserved": True,
        "provenance": "Owner-confirmed actual operational/test records; source-system verification separate",
        "excluded": "Separate Python data-generation snippet is not part of these ten records",
    }
    (dest / "import_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(import_records(args.source, args.output_dir), indent=2))
