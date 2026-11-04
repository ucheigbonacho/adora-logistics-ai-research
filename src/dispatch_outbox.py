"""Local-only dispatch outbox. No network or production execution.

SQLite persists requests before a worker can claim them. This module is a
test harness for transaction/recovery behaviour, not a live TMS adapter.
"""
import hashlib
import json
import sqlite3
import time
from pathlib import Path

def _digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

class DispatchOutbox:
    def __init__(self, path):
        self.path = str(Path(path))
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS dispatch_outbox (
                action_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending','in_flight','acknowledged','uncertain')),
                lease_until REAL,
                attempts INTEGER NOT NULL DEFAULT 0,
                receipt TEXT
            )""")

    def _db(self):
        db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        db.execute("PRAGMA busy_timeout=15000")
        return db

    def enqueue(self, action_id, payload):
        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError("action_id required")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("nonempty payload required")
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = _digest(payload)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload_sha256 FROM dispatch_outbox WHERE action_id=?", (action_id,)).fetchone()
            if row:
                return "duplicate" if row[0] == digest else "conflict"
            db.execute("INSERT INTO dispatch_outbox(action_id,payload_json,payload_sha256,status) VALUES(?,?,?,'pending')",
                       (action_id, raw, digest))
            return "pending"

    def claim(self, action_id, lease_seconds=30, now=None):
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        now = time.time() if now is None else now
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status,lease_until,payload_json FROM dispatch_outbox WHERE action_id=?", (action_id,)).fetchone()
            if not row:
                return None
            status, until, payload = row
            # An expired lease is NOT evidence that external execution failed.
            # Never auto-retry uncertain in-flight requests.
            if status == "in_flight" and until is not None and until <= now:
                db.execute("UPDATE dispatch_outbox SET status='uncertain' WHERE action_id=?", (action_id,))
                return None
            if status != "pending":
                return None
            db.execute("UPDATE dispatch_outbox SET status='in_flight',lease_until=?,attempts=attempts+1 WHERE action_id=?",
                       (now + lease_seconds, action_id))
            return json.loads(payload)

    def acknowledge(self, action_id, receipt):
        if not isinstance(receipt, str) or not receipt.strip():
            raise ValueError("nonempty receiver receipt required")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status,receipt FROM dispatch_outbox WHERE action_id=?", (action_id,)).fetchone()
            if not row:
                return "unknown_action"
            status, existing = row
            if status == "acknowledged":
                return "duplicate_ack" if existing == receipt else "receipt_conflict"
            if status not in ("in_flight", "uncertain"):
                return "not_dispatched"
            db.execute("UPDATE dispatch_outbox SET status='acknowledged',receipt=?,lease_until=NULL WHERE action_id=?",
                       (receipt, action_id))
            return "acknowledged"

    def status(self, action_id):
        with self._db() as db:
            row = db.execute("SELECT status FROM dispatch_outbox WHERE action_id=?", (action_id,)).fetchone()
            return row[0] if row else None

class DisabledDispatchAdapter:
    """Hard safety boundary: cannot send a real dispatch command."""
    def send(self, action_id, payload):
        raise RuntimeError("Production dispatch disabled: no transport configured")
