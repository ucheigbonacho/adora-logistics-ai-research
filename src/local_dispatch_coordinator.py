"""Fail-closed local dispatch coordinator.

No network transport or production dispatch. Only accepts signed claims;
local receiver receipts are checked against the receiver's durable record.
"""
from src.trusted_gateway import verify_claim
from src.dispatch_outbox import DispatchOutbox, DisabledDispatchAdapter
from src.local_receiver import LocalDispatchReceiver


class LocalDispatchCoordinator:
    def __init__(self, outbox_path, receiver_path, issuer_secret):
        self.outbox = DispatchOutbox(outbox_path)
        self.receiver = LocalDispatchReceiver(receiver_path)
        self._issuer_secret = issuer_secret
        self._disabled_transport = DisabledDispatchAdapter()

    def submit(self, claim, signature, now=None):
        if not verify_claim(claim, signature, self._issuer_secret, now=now):
            return "authorization_denied"
        # Enqueue only the authorized identifiers, not mutable caller payload.
        payload = {
            "load_id": claim["load_id"],
            "route_id": claim["route_id"],
            "subject": claim["subject"],
        }
        return self.outbox.enqueue(claim["action_id"], payload)

    def process_local(self, claim, signature, now=None):
        """Exercise a controlled local receiver; never send external commands.

        Recheck authorization before claim, so expired claims cannot be used
        for first-time dispatch. In-flight outcomes remain uncertain on failure.
        """
        if not verify_claim(claim, signature, self._issuer_secret, now=now):
            return "authorization_denied"
        action_id = claim["action_id"]
        payload = self.outbox.claim(action_id, now=now)
        if payload is None:
            return "not_claimable"
        expected = {
            "load_id": claim["load_id"],
            "route_id": claim["route_id"],
            "subject": claim["subject"],
        }
        if payload != expected:
            # No receiver action; leave in-flight for investigation.
            return "payload_conflict"
        result, receipt = self.receiver.receive(action_id, payload)
        if result not in ("accepted", "duplicate") or not receipt:
            return "receiver_conflict"
        # A locally durable receiver record is required before acknowledgement.
        if self.receiver.lookup(action_id) != receipt:
            return "receipt_unverified"
        return self.outbox.acknowledge(action_id, receipt)

    def reconcile_local(self, action_id):
        """Reconcile uncertain local deliveries, never fabricate a receipt."""
        if self.outbox.status(action_id) not in ("uncertain", "in_flight"):
            return "not_reconcilable"
        receipt = self.receiver.lookup(action_id)
        if receipt is None:
            return "receiver_not_confirmed"
        return self.outbox.acknowledge(action_id, receipt)

    def send_production(self, action_id, payload):
        return self._disabled_transport.send(action_id, payload)
