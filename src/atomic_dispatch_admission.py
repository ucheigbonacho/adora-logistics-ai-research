"""Atomic signed-approval reservation + outbox enqueue in one SQLite database.

Development only. Does not execute dispatch or provide identity-provider auth.
"""
import hashlib
import json
import sqlite3

from src.dispatch_outbox import DispatchOutbox, _digest
from src.trusted_gateway import canonical, verify_claim


class AtomicDispatchAdmission:
    def __init__(self, db_path, issuer_secret):
        if not isinstance(issuer_secret, bytes) or len(issuer_secret) < 32:
            raise ValueError("issuer secret must be at least 32 bytes")
        self.outbox = DispatchOutbox(db_path)
        self.path = str(db_path)
        self.secret = issuer_secret
        with sqlite3.connect(self.path, timeout=15) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS atomic_reservations (
                action_id TEXT PRIMARY KEY,
                claim_digest TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state='reserved')
            )""")

    def admit(self, claim, signature, now=None, fault_at=None):
        if not verify_claim(claim, signature, self.secret, now=now):
            return "authorization_denied"
        if fault_at not in (None, "after_reservation", "before_commit"):
            raise ValueError("unknown fault injection point")
        action_id = claim["action_id"]
        claim_digest = hashlib.sha256(canonical(claim)).hexdigest()
        payload = {"load_id": claim["load_id"], "route_id": claim["route_id"],
                   "subject": claim["subject"]}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = _digest(payload)
        with sqlite3.connect(self.path, timeout=15, isolation_level=None) as db:
            db.execute("PRAGMA busy_timeout=15000")
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute(
                    "SELECT claim_digest FROM atomic_reservations WHERE action_id=?", (action_id,)
                ).fetchone()
                outbox_row = db.execute(
                    "SELECT payload_sha256 FROM dispatch_outbox WHERE action_id=?", (action_id,)
                ).fetchone()
                if row or outbox_row:
                    if row and outbox_row and row[0] == claim_digest and outbox_row[0] == digest:
                        result = "duplicate_admission"
                    else:
                        result = "action_id_conflict"
                else:
                    db.execute(
                        "INSERT INTO atomic_reservations(action_id,claim_digest,state) VALUES (?,?,'reserved')",
                        (action_id, claim_digest),
                    )
                    if fault_at == "after_reservation":
                        raise RuntimeError("injected failure after reservation")
                    db.execute(
                        "INSERT INTO dispatch_outbox(action_id,payload_json,payload_sha256,status) "
                        "VALUES (?,?,?,'pending')", (action_id, raw, digest),
                    )
                    if fault_at == "before_commit":
                        raise RuntimeError("injected failure before commit")
                    result = "admitted_pending"
                db.execute("COMMIT")
                return result
            except BaseException:
                db.execute("ROLLBACK")
                raise

    def inspect(self, action_id):
        with sqlite3.connect(self.path, timeout=15) as db:
            reservation = db.execute(
                "SELECT state FROM atomic_reservations WHERE action_id=?", (action_id,)
            ).fetchone()
            outbox = db.execute(
                "SELECT status FROM dispatch_outbox WHERE action_id=?", (action_id,)
            ).fetchone()
        return (reservation[0] if reservation else None, outbox[0] if outbox else None)
