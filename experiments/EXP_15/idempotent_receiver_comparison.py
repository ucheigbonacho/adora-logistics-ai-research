"""EXP-15 preregistered standard idempotency and ledger-consistency comparison.

Deterministic local SQLite receiver. No real dispatch, external API or JEVEEB
operational processing. The source of receiver truth is separate from the
simulated sender's observation of ledger state.
"""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

SCENARIOS = (
    "commit_ack_lost",
    "crash_before_commit",
    "stale_empty_ledger_after_commit",
    "ledger_unavailable_after_commit",
    "conflicting_ledger_digest",
)
PROTOCOLS = ("hold", "idempotent_retry", "conservative_reconcile")
ACTION = "EXP15-IDEMPOTENT-001"
DIGEST = hashlib.sha256(b'{"route":"A"}').hexdigest()

class IdempotentReceiver:
    def __init__(self, path):
        self.path = str(path)
        with self.db() as db:
            db.execute("CREATE TABLE effects(action_id TEXT PRIMARY KEY, digest TEXT NOT NULL)")
    def db(self):
        return sqlite3.connect(self.path, timeout=10)
    def submit(self, action_id, digest):
        with self.db() as db:
            current = db.execute("SELECT digest FROM effects WHERE action_id=?", (action_id,)).fetchone()
            if current:
                return "duplicate" if current[0] == digest else "conflict"
            db.execute("INSERT INTO effects VALUES (?,?)", (action_id, digest))
            return "committed"
    def truth(self, action_id):
        with self.db() as db:
            return db.execute("SELECT digest FROM effects WHERE action_id=?", (action_id,)).fetchall()

def evaluate(protocol, scenario, db_path):
    receiver = IdempotentReceiver(db_path)
    events, suppressed, conflicts = [], 0, 0
    if scenario != "crash_before_commit":
        assert receiver.submit(ACTION, DIGEST) == "committed"
        events.append("original_commit_acknowledgement_lost")
    else:
        events.append("original_crash_before_commit")
    resolution = "uncertain"
    ledger_trust = "not_queried"
    if protocol == "hold":
        events.append("sender_held_uncertain")
    elif protocol == "idempotent_retry":
        outcome = receiver.submit(ACTION, DIGEST)
        suppressed += int(outcome == "duplicate")
        conflicts += int(outcome == "conflict")
        events.append("retry_" + outcome)
        if outcome in ("committed", "duplicate"):
            resolution = "acknowledged"
    elif protocol == "conservative_reconcile":
        if scenario == "stale_empty_ledger_after_commit":
            observation, ledger_trust = [], "stale"
        elif scenario == "ledger_unavailable_after_commit":
            observation, ledger_trust = None, "unavailable"
        elif scenario == "conflicting_ledger_digest":
            observation, ledger_trust = [("incorrect-digest",)], "conflicting"
        else:
            observation, ledger_trust = receiver.truth(ACTION), "authoritative"
        events.append("ledger_" + ledger_trust)
        if ledger_trust == "authoritative":
            if observation == [(DIGEST,)]:
                resolution = "acknowledged"
                events.append("verified_prior_commit")
            elif not observation:
                outcome = receiver.submit(ACTION, DIGEST)
                suppressed += int(outcome == "duplicate")
                conflicts += int(outcome == "conflict")
                events.append("verified_absence_retry_" + outcome)
                if outcome in ("committed", "duplicate"):
                    resolution = "acknowledged"
            else:
                events.append("unexpected_authoritative_conflict")
        else:
            events.append("quarantined_no_retry")
    else:
        raise ValueError("Unknown protocol")
    actual = receiver.truth(ACTION)
    return {
        "protocol": protocol, "scenario": scenario,
        "receiver_mutations": len(actual),
        "safety_pass": len(actual) <= 1,
        "duplicate_suppressed": suppressed,
        "conflicts_rejected": conflicts,
        "resolved": resolution == "acknowledged",
        "resolution": resolution,
        "ledger_trust": ledger_trust,
        "events": events,
        "external_dispatch_attempted": False,
    }

def run(output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory must be new")
    with tempfile.TemporaryDirectory(prefix="exp15-idempotency-") as temp:
        rows = [evaluate(protocol, scenario, Path(temp) / (protocol + "_" + scenario + ".sqlite3"))
                for scenario in SCENARIOS for protocol in PROTOCOLS]
    summary = {
        protocol: {
            "cases": len(subset),
            "safety_passes": sum(row["safety_pass"] for row in subset),
            "resolved": sum(row["resolved"] for row in subset),
            "duplicate_suppressed": sum(row["duplicate_suppressed"] for row in subset),
        }
        for protocol in PROTOCOLS
        for subset in [[row for row in rows if row["protocol"] == protocol]]
    }
    dest.mkdir(parents=True)
    raw = json.dumps(rows, indent=2) + "\n"
    (dest / "observations.json").write_text(raw, encoding="utf-8")
    manifest = {
        "classification": "NEW_EXP15_STANDARD_IDEMPOTENCY_AND_LEDGER_CONSISTENCY_COMPARISON",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observations_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "scenarios": list(SCENARIOS), "protocols": list(PROTOCOLS),
        "summary": summary, "production_dispatch_enabled": False,
        "scope": "Local deterministic SQLite receiver; one recovery step per scenario",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(run(parser.parse_args().output_dir), indent=2))
