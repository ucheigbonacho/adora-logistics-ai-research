import hashlib
import hmac
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.atomic_dispatch_admission import AtomicDispatchAdmission
from src.trusted_gateway import canonical

SECRET = b"local-atomic-admission-test-secret-32-bytes"
NOW = 1_000_000_000


def claim():
    return {"action_id": "A1", "load_id": "L1", "route_id": "R1",
            "subject": "test-user", "permission": "dispatch.route.execute",
            "confirmed": True, "context_valid": True, "constraints_passed": True,
            "expires_at": NOW + 1000}


def sign(c):
    return hmac.new(SECRET, canonical(c), hashlib.sha256).hexdigest()


class AtomicAdmissionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "admission.sqlite"
        self.gate = AtomicDispatchAdmission(self.path, SECRET)

    def test_atomic_success(self):
        c = claim()
        self.assertEqual(self.gate.admit(c, sign(c), now=NOW), "admitted_pending")
        self.assertEqual(self.gate.inspect("A1"), ("reserved", "pending"))

    def test_after_reservation_failure_rolls_back(self):
        c = claim()
        with self.assertRaisesRegex(RuntimeError, "after reservation"):
            self.gate.admit(c, sign(c), now=NOW, fault_at="after_reservation")
        self.assertEqual(self.gate.inspect("A1"), (None, None))

    def test_before_commit_failure_rolls_back(self):
        c = claim()
        with self.assertRaisesRegex(RuntimeError, "before commit"):
            self.gate.admit(c, sign(c), now=NOW, fault_at="before_commit")
        self.assertEqual(AtomicDispatchAdmission(self.path, SECRET).inspect("A1"), (None, None))

    def test_duplicate_and_conflict(self):
        c = claim()
        self.gate.admit(c, sign(c), now=NOW)
        self.assertEqual(self.gate.admit(c, sign(c), now=NOW), "duplicate_admission")
        altered = dict(c, route_id="R2")
        self.assertEqual(self.gate.admit(altered, sign(altered), now=NOW), "action_id_conflict")

    def test_invalid_claim_creates_nothing(self):
        c = claim()
        c["confirmed"] = False
        self.assertEqual(self.gate.admit(c, sign(c), now=NOW), "authorization_denied")
        self.assertEqual(self.gate.inspect("A1"), (None, None))

    def test_concurrent_one_admission(self):
        c = claim()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.gate.admit(c, sign(c), now=NOW), range(16)))
        self.assertEqual(results.count("admitted_pending"), 1)
        self.assertEqual(results.count("duplicate_admission"), 15)
        self.assertEqual(self.gate.inspect("A1"), ("reserved", "pending"))

    def test_recover_after_rollback(self):
        c = claim()
        with self.assertRaises(RuntimeError):
            self.gate.admit(c, sign(c), now=NOW, fault_at="before_commit")
        self.assertEqual(self.gate.admit(c, sign(c), now=NOW), "admitted_pending")
