"""Atomic submission is the only path through the signed local coordinator."""
import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path

from src.signed_local_dispatch import SignedLocalCoordinator
from src.trusted_gateway import canonical

ISSUER = b"atomic-flow-issuer-test-secret-at-least-32"
RECEIVER = b"atomic-flow-receiver-test-secret-at-least-32"
NOW = 1_000_000_000


def claim():
    return {"action_id": "A1", "load_id": "L1", "route_id": "R1",
            "subject": "test-user", "permission": "dispatch.route.execute",
            "confirmed": True, "context_valid": True, "constraints_passed": True,
            "expires_at": NOW+1000}


def sign(c):
    return hmac.new(ISSUER, canonical(c), hashlib.sha256).hexdigest()


class IntegratedAtomicFlowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.flow = SignedLocalCoordinator(root/"outbox.sqlite", root/"receiver.sqlite", ISSUER, RECEIVER)

    def test_atomic_submission_and_signed_ack(self):
        c = claim()
        self.assertEqual(self.flow.submit(c, sign(c), now=NOW), "pending")
        self.assertEqual(self.flow.admission.inspect("A1"), ("reserved", "pending"))
        self.assertEqual(self.flow.process_local(c, sign(c), now=NOW), "acknowledged")
        self.assertEqual(self.flow.admission.inspect("A1"), ("reserved", "acknowledged"))

    def test_duplicate_submission_and_conflict(self):
        c = claim()
        self.assertEqual(self.flow.submit(c, sign(c), now=NOW), "pending")
        self.assertEqual(self.flow.submit(c, sign(c), now=NOW), "duplicate")
        changed = dict(c, route_id="R2")
        self.assertEqual(self.flow.submit(changed, sign(changed), now=NOW), "conflict")

    def test_unauthorized_does_not_create_either_record(self):
        c = claim()
        c["confirmed"] = False
        self.assertEqual(self.flow.submit(c, sign(c), now=NOW), "authorization_denied")
        self.assertEqual(self.flow.admission.inspect("A1"), (None, None))
