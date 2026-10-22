"""Signed dispatch approval and durable reservation; no external execution."""
import hashlib
import hmac
import json
import sqlite3
import time

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def verify_claim(claim, signature, secret, now=None):
    if not isinstance(claim, dict) or not isinstance(signature, str) or not isinstance(secret, bytes) or len(secret) < 32:
        return False
    required = ("load_id", "route_id", "action_id", "subject")
    if not all(isinstance(claim.get(k), str) and claim[k].strip() for k in required):
        return False
    if claim.get("permission") != "dispatch.route.execute" or claim.get("confirmed") is not True:
        return False
    if claim.get("context_valid") is not True or claim.get("constraints_passed") is not True:
        return False
    expiry = claim.get("expires_at")
    if not isinstance(expiry, int) or isinstance(expiry, bool) or expiry <= (time.time() if now is None else now):
        return False
    expected = hmac.new(secret, canonical(claim), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

class DurableReservationGate:
    """A reservation is NOT a confirmed external dispatch execution."""
    def __init__(self, db_path, secret):
        self.db_path = str(db_path)
        self.secret = secret
        with sqlite3.connect(self.db_path, timeout=15) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("CREATE TABLE IF NOT EXISTS reservations (action_id TEXT PRIMARY KEY, payload_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state='reserved'))")

    def reserve(self, claim, signature, now=None):
        if not verify_claim(claim, signature, self.secret, now):
            return "authorization_denied"
        fingerprint = hashlib.sha256(canonical(claim)).hexdigest()
        with sqlite3.connect(self.db_path, timeout=15, isolation_level=None) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute("SELECT payload_sha256 FROM reservations WHERE action_id=?", (claim["action_id"],)).fetchone()
                if row:
                    result = "duplicate_reservation" if row[0] == fingerprint else "action_id_conflict"
                else:
                    conn.execute("INSERT INTO reservations VALUES (?, ?, 'reserved')", (claim["action_id"], fingerprint))
                    result = "reserved_not_executed"
                conn.execute("COMMIT")
                return result
            except Exception:
                conn.execute("ROLLBACK")
                raise
