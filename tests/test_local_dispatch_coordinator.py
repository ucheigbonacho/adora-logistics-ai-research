"""Controlled integration checks. All records are ephemeral local test data."""
import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path

from src.local_dispatch_coordinator import LocalDispatchCoordinator
from src.trusted_gateway import canonical

SECRET = b"local-only-test-signing-key-1234567890"
NOW = 1_000_000_000


def valid_claim():
    return {
        "load_id": "TEST-L1",
        "route_id": "TEST-R2",
        "action_id": "TEST-A1",
        "subject": "local-test-dispatcher",
        "permission": "dispatch.route.execute",
        "confirmed": True,
        "context_valid": True,
        "constraints_passed": True,
        "expires_at": 2_000_000_000,
    }


def sign(claim):
    return hmac.new(SECRET, canonical(claim), hashlib.sha256).hexdigest()


class LocalCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.coordinator = LocalDispatchCoordinator(root / "outbox.sqlite", root / "receiver.sqlite", SECRET)

    def test_signed_local_flow(self):
        claim = valid_claim()
        self.assertEqual(self.coordinator.submit(claim, sign(claim), now=NOW), "pending")
        self.assertEqual(self.coordinator.process_local(claim, sign(claim), now=NOW), "acknowledged")
        self.assertEqual(self.coordinator.outbox.status(claim["action_id"]), "acknowledged")

    def test_tampered_claim_rejected(self):
        claim = valid_claim()
        signature = sign(claim)
        claim["route_id"] = "MALICIOUS"
        self.assertEqual(self.coordinator.submit(claim, signature, now=NOW), "authorization_denied")
        self.assertIsNone(self.coordinator.outbox.status(claim["action_id"]))

    def test_expired_claim_rejected(self):
        claim = valid_claim()
        self.assertEqual(self.coordinator.submit(claim, sign(claim), now=2_000_000_000), "authorization_denied")

    def test_signed_claim_cannot_process_different_enqueued_payload(self):
        claim = valid_claim()
        self.assertEqual(self.coordinator.submit(claim, sign(claim), now=NOW), "pending")
        altered = dict(claim, route_id="TEST-R3")
        self.assertEqual(self.coordinator.process_local(altered, sign(altered), now=NOW), "payload_conflict")
        self.assertIsNone(self.coordinator.receiver.lookup(claim["action_id"]))

    def test_recovery_requires_receiver_record(self):
        claim = valid_claim()
        self.coordinator.submit(claim, sign(claim), now=NOW)
        self.coordinator.outbox.claim(claim["action_id"], lease_seconds=10, now=NOW)
        self.coordinator.outbox.claim(claim["action_id"], now=NOW + 11)
        self.assertEqual(self.coordinator.reconcile_local(claim["action_id"]), "receiver_not_confirmed")
        self.assertEqual(self.coordinator.outbox.status(claim["action_id"]), "uncertain")

    def test_recovery_after_lost_ack(self):
        claim = valid_claim()
        self.coordinator.submit(claim, sign(claim), now=NOW)
        payload = self.coordinator.outbox.claim(claim["action_id"], lease_seconds=10, now=NOW)
        _, receipt = self.coordinator.receiver.receive(claim["action_id"], payload)
        self.coordinator.outbox.claim(claim["action_id"], now=NOW + 11)
        self.assertEqual(self.coordinator.reconcile_local(claim["action_id"]), "acknowledged")
        self.assertEqual(self.coordinator.receiver.lookup(claim["action_id"]), receipt)

    def test_no_production_transport(self):
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            self.coordinator.send_production("TEST-A1", {"route_id": "TEST-R2"})
