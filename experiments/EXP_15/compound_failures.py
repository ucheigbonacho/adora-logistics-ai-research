"""EXP-15 prospective compound-failure investigation, local SQLite only.

Run: python -m experiments.EXP_15.compound_failures --output-dir /tmp/exp15-compound-new
No external dispatch adapter is invoked. These are newly executed engineering tests,
not historical operational observations.
"""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.dispatch_outbox import DispatchOutbox

SCENARIOS = (
    "concurrent_claim_restart_late_ack",
    "concurrent_claim_expiry_no_receipt",
    "conflicting_payload_during_uncertain",
    "duplicate_enqueue_after_ack",
)

def inspect(db_path, action_id):
    with sqlite3.connect(db_path) as db:
        row = db.execute(
            "SELECT status,attempts,receipt FROM dispatch_outbox WHERE action_id=?",
            (action_id,),
        ).fetchone()
    return {"status": row[0], "attempts": row[1], "receipt": row[2]}

def execute(name, db_path, workers=8):
    db = DispatchOutbox(db_path)
    action = "EXP15-COMPOUND-" + name
    payload = {"route": "A", "authorized": True}
    db.enqueue(action, payload)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        claims = list(pool.map(
            lambda _: DispatchOutbox(db_path).claim(action, lease_seconds=10, now=100),
            range(workers),
        ))
    winners = sum(item == payload for item in claims)
    if name == "concurrent_claim_restart_late_ack":
        expired = DispatchOutbox(db_path).claim(action, now=111)
        outcome = DispatchOutbox(db_path).acknowledge(action, "receipt-confirmed")
        replay = DispatchOutbox(db_path).claim(action, now=112)
    elif name == "concurrent_claim_expiry_no_receipt":
        expired = DispatchOutbox(db_path).claim(action, now=111)
        outcome = "no_receiver_receipt"
        replay = DispatchOutbox(db_path).claim(action, now=112)
    elif name == "conflicting_payload_during_uncertain":
        expired = DispatchOutbox(db_path).claim(action, now=111)
        outcome = DispatchOutbox(db_path).enqueue(action, {"route": "B", "authorized": True})
        replay = DispatchOutbox(db_path).claim(action, now=112)
    elif name == "duplicate_enqueue_after_ack":
        expired = None
        DispatchOutbox(db_path).acknowledge(action, "receipt-confirmed")
        outcome = DispatchOutbox(db_path).enqueue(action, payload)
        replay = DispatchOutbox(db_path).claim(action, now=112)
    else:
        raise ValueError("Unknown scenario")
    state = inspect(db_path, action)
    return {
        "scenario": name, "workers": workers, "claim_winners": winners,
        "expired_claim_returned_none": expired is None,
        "replay_claim_returned_none": replay is None,
        "outcome": outcome, **state,
        "external_dispatch_attempted": False,
    }

def run(output_dir, workers=8):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory must be new")
    if workers < 2:
        raise ValueError("At least two workers required")
    with tempfile.TemporaryDirectory(prefix="exp15-compound-local-") as tmp:
        rows = [execute(name, Path(tmp) / (name + ".sqlite3"), workers) for name in SCENARIOS]
    dest.mkdir(parents=True)
    raw = json.dumps(rows, indent=2) + "\n"
    (dest / "observations.json").write_text(raw, encoding="utf-8")
    manifest = {
        "classification": "NEW_EXP15_LOCAL_COMPOUND_FAILURE_TEST",
        "scenario_count": len(rows),
        "worker_count": workers,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observations_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "production_dispatch_enabled": False,
        "note": "Local modeled concurrency, lease expiry and receipt recovery; no external mutation measured.",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "observations": rows}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir, args.workers), indent=2))
