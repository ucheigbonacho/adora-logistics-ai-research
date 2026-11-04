"""Crash-window tests use temporary SQLite files and no production transport."""
import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path

from src.signed_local_dispatch import SignedLocalCoordinator
from src.trusted_gateway import canonical

ISSUER = b"crash-test-issuer-key-32-bytes-minimum-123"
RECEIVER = b"crash-test-receiver-key-32-bytes-minimum"
NOW = 1_000_000_000


def claim():
    return {"action_id": "CRASH-A1", "load_id": "TEST-L1", "route_id": "TEST-R1",
            "subject": "test-dispatcher", "permission": "dispatch.route.execute",
            "confirmed": True, "context_valid": True, "constraints_passed": True,
            "expires_at": NOW+1000}


def signature(c):
    return hmac.new(ISSUER, canonical(c), hashlib.sha256).hexdigest()


class CrashWindowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.outbox_path = root/"outbox.sqlite"
        self.receiver_path = root/"receiver.sqlite"
        self.flow = self.restart()

    def restart(self):
        return SignedLocalCoordinator(self.outbox_path, self.receiver_path, ISSUER, RECEIVER)

    def test_restart_before_claim(self):
        c = claim()
        self.assertEqual(self.flow.submit(c, signature(c), now=NOW), "pending")
        self.flow = self.restart()
        self.assertEqual(self.flow.process_local(c, signature(c), now=NOW), "acknowledged")

    def test_restart_after_claim_without_receiver(self):
        c = claim()
        self.flow.submit(c, signature(c), now=NOW)
        payload = self.flow.outbox.claim(c["action_id"], lease_seconds=10, now=NOW)
        self.flow = self.restart()
        self.assertIsNone(self.flow.outbox.claim(c["action_id"], now=NOW+11))
        self.assertEqual(self.flow.outbox.status(c["action_id"]), "uncertain")
        self.assertEqual(self.flow.reconcile_local(c["action_id"], payload, now=NOW+11), "receiver_not_confirmed")

    def test_restart_after_receiver_before_ack(self):
        c = claim()
        self.flow.submit(c, signature(c), now=NOW)
        payload = self.flow.outbox.claim(c["action_id"], lease_seconds=10, now=NOW)
        self.flow.receiver.accept(c["action_id"], payload, expires_at=NOW+60)
        self.flow = self.restart()
        self.flow.outbox.claim(c["action_id"], now=NOW+11)
        self.assertEqual(self.flow.reconcile_local(c["action_id"], payload, now=NOW+11), "acknowledged")
        self.assertEqual(self.flow.receiver._receiver.receive(c["action_id"], payload)[0], "duplicate")

    def test_reconciliation_rejects_wrong_payload(self):
        c = claim()
        self.flow.submit(c, signature(c), now=NOW)
        payload = self.flow.outbox.claim(c["action_id"], now=NOW)
        self.flow.receiver.accept(c["action_id"], payload, expires_at=NOW+60)
        wrong = dict(payload, route_id="OTHER")
        self.assertEqual(self.flow.reconcile_local(c["action_id"], wrong, now=NOW), "payload_conflict")
        self.assertEqual(self.flow.outbox.status(c["action_id"]), "in_flight")

    def test_no_receipt_no_acknowledgement(self):
        c = claim()
        self.flow.submit(c, signature(c), now=NOW)
        payload = self.flow.outbox.claim(c["action_id"], now=NOW)
        self.assertEqual(self.flow.reconcile_local(c["action_id"], payload, now=NOW), "receiver_not_confirmed")
        self.assertNotEqual(self.flow.outbox.status(c["action_id"]), "acknowledged")
