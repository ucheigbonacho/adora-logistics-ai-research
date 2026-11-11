"""EXP-15 prospective local-only fault-injection harness.

This code is an experimental instrument, not a record of earlier tests.
Run: python -m experiments.EXP_15.run --output-dir /tmp/exp15-new
No network transport or production dispatch is used.
"""
import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path
from src.dispatch_outbox import DispatchOutbox, DisabledDispatchAdapter

SCENARIOS = (
    "ack_before_expiry",
    "ack_after_expiry",
    "expired_without_receipt",
    "conflicting_replay",
    "duplicate_replay",
)

def execute_scenario(name, database_path):
    db = DispatchOutbox(database_path)
    action = "EXP15-" + name
    payload = {"route": "A", "authorized": True}
    initial = db.enqueue(action, payload)
    claimed = db.claim(action, lease_seconds=10, now=100)
    result = {"scenario": name, "enqueue": initial, "claimed": claimed == payload}
    if name == "ack_before_expiry":
        result["ack"] = db.acknowledge(action, "receipt-1")
    elif name == "ack_after_expiry":
        result["expired_claim"] = DispatchOutbox(database_path).claim(action, now=111)
        result["ack"] = db.acknowledge(action, "receipt-1")
    elif name == "expired_without_receipt":
        result["expired_claim"] = DispatchOutbox(database_path).claim(action, now=111)
        result["retry_claim"] = db.claim(action, now=112)
    elif name == "conflicting_replay":
        result["replay"] = db.enqueue(action, {"route": "B", "authorized": True})
    elif name == "duplicate_replay":
        result["replay"] = db.enqueue(action, payload)
    result["final_status"] = db.status(action)
    result["external_dispatch_attempted"] = False
    return result

def run(output_dir):
    destination = Path(output_dir).resolve()
    if destination.exists():
        raise FileExistsError("Output directory must not exist")
    with tempfile.TemporaryDirectory(prefix="exp15-local-") as tmp:
        rows = [execute_scenario(name, Path(tmp) / (name + ".sqlite3")) for name in SCENARIOS]
    destination.mkdir(parents=True)
    (destination / "observations.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    with (destination / "observations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=("scenario", "enqueue", "claimed", "final_status", "external_dispatch_attempted"))
        writer.writeheader()
        writer.writerows([{k: row[k] for k in writer.fieldnames} for row in rows])
    source = Path(__file__).resolve()
    manifest = {
        "classification": "PROSPECTIVE_EXP15_LOCAL_BASELINE",
        "instrument_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scenario_count": len(rows),
        "network_dispatch_enabled": False,
        "observation_sha256": hashlib.sha256((destination / "observations.json").read_bytes()).hexdigest(),
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "observations": rows}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(run(parser.parse_args().output_dir), indent=2))
