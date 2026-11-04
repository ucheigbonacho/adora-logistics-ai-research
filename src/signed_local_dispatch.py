"""Strict local-only dispatch workflow with receiver-origin signed receipts.

Development harness only. No network, TMS, or production action.
"""
import json
import time

from src.dispatch_outbox import DisabledDispatchAdapter
from src.atomic_dispatch_admission import AtomicDispatchAdmission
from src.local_receiver import LocalDispatchReceiver
from src.receipt_protocol import sign_receipt, verify_receipt
from src.trusted_gateway import verify_claim


class SignedLocalReceiver:
    def __init__(self, path, receiver_secret):
        if not isinstance(receiver_secret, bytes) or len(receiver_secret) < 32:
            raise ValueError("receiver signing secret required")
        self._receiver = LocalDispatchReceiver(path)
        self._secret = receiver_secret

    def accept(self, action_id, payload, expires_at):
        status, receipt = self._receiver.receive(action_id, payload)
        if status not in ("accepted", "duplicate") or not receipt:
            return status, None
        return status, sign_receipt(action_id, payload, self._secret, expires_at=expires_at)

    def confirm(self, action_id, payload, expires_at):
        # Only a matching durable receiver record can be signed.
        from src.local_receiver import fingerprint
        import sqlite3
        with sqlite3.connect(self._receiver.path, timeout=15) as db:
            row = db.execute(
                "SELECT payload_digest FROM received_actions WHERE action_id=?", (action_id,)
            ).fetchone()
        if row is None or row[0] != fingerprint(payload):
            return None
        return sign_receipt(action_id, payload, self._secret, expires_at=expires_at)


class SignedLocalCoordinator:
    def __init__(self, outbox_path, receiver_path, issuer_secret, receiver_secret):
        if not isinstance(issuer_secret, bytes) or len(issuer_secret) < 32:
            raise ValueError("issuer verification secret required")
        if not isinstance(receiver_secret, bytes) or len(receiver_secret) < 32:
            raise ValueError("receiver verification secret required")
        if issuer_secret == receiver_secret:
            raise ValueError("issuer and receiver secrets must be distinct")
        self.admission = AtomicDispatchAdmission(outbox_path, issuer_secret)
        self.outbox = self.admission.outbox
        self.receiver = SignedLocalReceiver(receiver_path, receiver_secret)
        self._issuer_secret = issuer_secret
        self._receiver_secret = receiver_secret
        self._disabled = DisabledDispatchAdapter()

    @staticmethod
    def _payload(claim):
        return {"load_id": claim["load_id"], "route_id": claim["route_id"],
                "subject": claim["subject"]}

    def submit(self, claim, signature, now=None):
        outcome = self.admission.admit(claim, signature, now=now)
        return {"admitted_pending": "pending", "duplicate_admission": "duplicate",
                "action_id_conflict": "conflict"}.get(outcome, outcome)

    def _accept_verified(self, action_id, payload, envelope, now):
        if not verify_receipt(envelope, action_id, payload, self._receiver_secret, now=now):
            return "receipt_unverified"
        # The receipt is receiver-origin, bound to action+payload and time.
        return self.outbox.acknowledge(action_id, json.dumps(envelope, sort_keys=True))

    def process_local(self, claim, signature, now=None):
        if not verify_claim(claim, signature, self._issuer_secret, now=now):
            return "authorization_denied"
        now = time.time() if now is None else now
        action_id = claim["action_id"]
        payload = self.outbox.claim(action_id, now=now)
        if payload is None:
            return "not_claimable"
        if payload != self._payload(claim):
            return "payload_conflict"
        status, envelope = self.receiver.accept(action_id, payload, expires_at=int(now)+60)
        if status not in ("accepted", "duplicate"):
            return "receiver_conflict"
        return self._accept_verified(action_id, payload, envelope, now)

    def reconcile_local(self, action_id, payload, now=None):
        if self.outbox.status(action_id) not in ("in_flight", "uncertain"):
            return "not_reconcilable"
        # Never trust a caller-supplied payload during recovery.
        import sqlite3
        with sqlite3.connect(self.outbox.path, timeout=15) as db:
            row = db.execute("SELECT payload_json FROM dispatch_outbox WHERE action_id=?", (action_id,)).fetchone()
        if row is None or json.loads(row[0]) != payload:
            return "payload_conflict"
        now = time.time() if now is None else now
        envelope = self.receiver.confirm(action_id, payload, expires_at=int(now)+60)
        if envelope is None:
            return "receiver_not_confirmed"
        return self._accept_verified(action_id, payload, envelope, now)

    def send_production(self, action_id, payload):
        return self._disabled.send(action_id, payload)
