"""EXP-15 prospective receipt-race tests, local SQLite only.

No production dispatch, external receiver or transport is configured.
"""
import argparse
import hashlib
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.dispatch_outbox import DispatchOutbox

SCENARIOS = ("same_receipt_race", "conflicting_receipt_race", "late_uncertain_receipt",
             "expired_claim_race", "unknown_and_unclaimed_receipts")

def execute(name, path, workers=8):
    db = DispatchOutbox(path)
    action = "EXP15-RECEIPT-" + name
    if name == "unknown_and_unclaimed_receipts":
        unknown = db.acknowledge(action, "R1")
        db.enqueue(action, {"route": "A"})
        unclaimed = db.acknowledge(action, "R1")
        return {"scenario": name, "unknown": unknown, "unclaimed": unclaimed,
                "status": db.status(action), "external_dispatch_attempted": False}
    db.enqueue(action, {"route": "A"})
    db.claim(action, now=100, lease_seconds=10)
    if name in ("same_receipt_race", "conflicting_receipt_race"):
        receipts = ["R1"] * workers if name == "same_receipt_race" else ["R1" if i % 2 else "R2" for i in range(workers)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(pool.map(lambda receipt: DispatchOutbox(path).acknowledge(action, receipt), receipts))
        return {"scenario": name, "outcomes": outcomes,
                "status": db.status(action), "external_dispatch_attempted": False}
    if name == "late_uncertain_receipt":
        expired = DispatchOutbox(path).claim(action, now=111)
        ack = DispatchOutbox(path).acknowledge(action, "R1")
        replay = DispatchOutbox(path).claim(action, now=112)
        return {"scenario": name, "expired_claim_returned_none": expired is None,
                "ack": ack, "replay_returned_none": replay is None,
                "status": db.status(action), "external_dispatch_attempted": False}
    if name == "expired_claim_race":
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(pool.map(lambda _: DispatchOutbox(path).claim(action, now=111), range(workers)))
        return {"scenario": name, "post_expiry_claim_winners": sum(x is not None for x in outcomes),
                "status": db.status(action), "external_dispatch_attempted": False}
    raise ValueError("Unknown scenario")

def run(output_dir, workers=8):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory must be new")
    if workers < 2:
        raise ValueError("At least two workers required")
    with tempfile.TemporaryDirectory(prefix="exp15-receipts-") as tmp:
        rows = [execute(name, Path(tmp) / (name + ".sqlite3"), workers) for name in SCENARIOS]
    dest.mkdir(parents=True)
    raw = json.dumps(rows, indent=2) + "\n"
    (dest / "observations.json").write_text(raw, encoding="utf-8")
    manifest = {
        "classification": "NEW_EXP15_LOCAL_RECEIPT_RACE_TEST",
        "scenario_count": len(rows),
        "worker_count": workers,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observations_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "production_dispatch_enabled": False,
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "observations": rows}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--workers", type=int, default=8)
    a = p.parse_args()
    print(json.dumps(run(a.output_dir, a.workers), indent=2))
