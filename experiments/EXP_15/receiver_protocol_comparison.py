"""EXP-15 isolated sender/receiver recovery protocol comparison.

This is a prospective fault-injection instrument, not an external dispatch
integration. Receiver truth is held in a separate SQLite ledger. All protocols
receive identical deterministic fault scenarios. No network or live dispatch.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

SCENARIOS = (
    "commit_ack_lost",
    "crash_before_commit",
    "ledger_temporarily_unavailable",
    "conflicting_receipt_digest",
)
PROTOCOLS = ("safe_hold", "blind_retry", "receiver_reconciliation")

class Receiver:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.execute("CREATE TABLE effects (action_id TEXT, ordinal INTEGER, digest TEXT, PRIMARY KEY(action_id, ordinal))")
    def connect(self):
        return sqlite3.connect(self.path)
    def commit(self, action_id, digest):
        with self.connect() as db:
            ordinal = db.execute("SELECT COUNT(*) FROM effects WHERE action_id=?", (action_id,)).fetchone()[0] + 1
            db.execute("INSERT INTO effects VALUES (?,?,?)", (action_id, ordinal, digest))
    def ledger(self, action_id):
        with self.connect() as db:
            return db.execute("SELECT digest FROM effects WHERE action_id=? ORDER BY ordinal", (action_id,)).fetchall()

def evaluate(protocol, scenario, receiver_path):
    receiver = Receiver(receiver_path)
    action_id, digest = "EXP15-RECEIVER-001", hashlib.sha256(b'{"route":"A"}').hexdigest()
    events = []
    if scenario != "crash_before_commit":
        receiver.commit(action_id, digest)
        events.append("receiver_commit_before_ack_loss")
    else:
        events.append("crash_before_receiver_commit")
    if scenario == "conflicting_receipt_digest":
        reported_receipt = "mismatched-digest"
    else:
        reported_receipt = None
    events.append("acknowledgement_not_available_to_sender")
    resolution = "uncertain"
    if protocol == "safe_hold":
        events.append("hold_for_reconciliation")
    elif protocol == "blind_retry":
        receiver.commit(action_id, digest)
        events.append("blind_retry_committed")
        resolution = "acknowledged"
    elif protocol == "receiver_reconciliation":
        if scenario == "ledger_temporarily_unavailable":
            events.append("ledger_query_unavailable")
        elif reported_receipt and reported_receipt != digest:
            events.append("conflicting_receipt_quarantined")
        else:
            ledger = receiver.ledger(action_id)
            events.append("receiver_ledger_queried")
            if len(ledger) == 1 and ledger[0][0] == digest:
                resolution = "acknowledged"
                events.append("verified_prior_commit")
            elif not ledger:
                receiver.commit(action_id, digest)
                events.append("verified_absence_then_retry")
                resolution = "acknowledged"
            else:
                events.append("inconsistent_ledger_quarantined")
    else:
        raise ValueError("Unknown protocol")
    ledger = receiver.ledger(action_id)
    return {
        "protocol": protocol, "scenario": scenario, "receiver_effect_count": len(ledger),
        "duplicate_effects": max(0, len(ledger) - 1),
        "safety_pass": len(ledger) <= 1,
        "resolved": resolution == "acknowledged",
        "resolution": resolution, "events": events,
        "production_dispatch_enabled": False,
    }

def run(output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory must be new")
    # One independent receiver database per protocol/scenario; no shared sender state.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="exp15-receiver-") as root:
        rows = [evaluate(protocol, scenario, Path(root) / f"{protocol}_{scenario}.sqlite3")
                for scenario in SCENARIOS for protocol in PROTOCOLS]
    summary = {}
    for protocol in PROTOCOLS:
        subset = [r for r in rows if r["protocol"] == protocol]
        summary[protocol] = {
            "scenarios": len(subset),
            "safety_passes": sum(r["safety_pass"] for r in subset),
            "resolved": sum(r["resolved"] for r in subset),
            "duplicate_effects": sum(r["duplicate_effects"] for r in subset),
        }
    dest.mkdir(parents=True)
    raw = json.dumps(rows, indent=2) + "\n"
    (dest / "observations.json").write_text(raw, encoding="utf-8")
    manifest = {
        "classification": "PROSPECTIVE_LOCAL_RECEIVER_FAULT_INJECTION",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observations_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "scenarios": list(SCENARIOS),
        "protocols": list(PROTOCOLS),
        "summary": summary,
        "scope": "Deterministic isolated SQLite receiver model; no remote receiver, external dispatch or production mutation.",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    print(json.dumps(run(p.parse_args().output_dir), indent=2))
