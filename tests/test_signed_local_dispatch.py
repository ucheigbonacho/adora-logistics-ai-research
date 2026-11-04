import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path

from src.signed_local_dispatch import SignedLocalCoordinator
from src.trusted_gateway import canonical

ISSUER = b"development-issuer-secret-at-least-32-bytes"
RECEIVER = b"development-receiver-secret-at-least-32-bytes"
NOW = 1_000_000_000


def claim():
    return {"action_id": "A1", "load_id": "L1", "route_id": "R2",
            "subject": "test-user", "permission": "dispatch.route.execute",
            "confirmed": True, "context_valid": True, "constraints_passed": True,
            "expires_at": NOW+1000}


def sign(data):
    return hmac.new(ISSUER, canonical(data), hashlib.sha256).hexdigest()


class SignedLocalFlowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.flow = SignedLocalCoordinator(root/"outbox.db", root/"receiver.db", ISSUER, RECEIVER)

    def test_end_to_end_signed_acknowledgement(self):
        c = claim()
        self.assertEqual(self.flow.submit(c, sign(c), now=NOW), "pending")
        self.assertEqual(self.flow.process_local(c, sign(c), now=NOW), "acknowledged")
        self.assertEqual(self.flow.outbox.status("A1"), "acknowledged")

    def test_tampering_cannot_enqueue(self):
        c = claim()
        original = sign(c)
        c["route_id"] = "R3"
        self.assertEqual(self.flow.submit(c, original, now=NOW), "authorization_denied")

    def test_receiver_mismatch_does_not_confirm(self):
        c = claim()
        self.flow.submit(c, sign(c), now=NOW)
        payload = self.flow.outbox.claim("A1", now=NOW)
        status, envelope = self.flow.receiver.accept("A1", payload, expires_at=NOW+60)
        self.assertEqual(status, "accepted")
        self.assertEqual(self.flow._accept_verified("A1", dict(payload, route_id="R3"), envelope, NOW),
                         "receipt_unverified")
        self.assertEqual(self.flow.outbox.status("A1"), "in_flight")

    def test_recovery_requires_receiver_record(self):
        c = claim()
        self.flow.submit(c, sign(c), now=NOW)
        payload = self.flow.outbox.claim("A1", lease_seconds=10, now=NOW)
        self.flow.outbox.claim("A1", now=NOW+11)
        self.assertEqual(self.flow.reconcile_local("A1", payload, now=NOW+11), "receiver_not_confirmed")

    def test_reconcile_persisted_signed_receipt(self):
        c = claim()
        self.flow.submit(c, sign(c), now=NOW)
        payload = self.flow.outbox.claim("A1", lease_seconds=10, now=NOW)
        self.flow.receiver.accept("A1", payload, expires_at=NOW+60)
        self.flow.outbox.claim("A1", now=NOW+11)
        self.assertEqual(self.flow.reconcile_local("A1", payload, now=NOW+11), "acknowledged")

    def test_separate_secrets_required(self):
        with self.assertRaises(ValueError):
            SignedLocalCoordinator(":memory:", ":memory:", ISSUER, ISSUER)

    def test_production_disabled(self):
        with self.assertRaises(RuntimeError):
            self.flow.send_production("A1", {"route_id": "R2"})
