"""Integration security checks: local-only dispatch and fail-closed inputs."""
import tempfile
import unittest
from pathlib import Path
from src.dispatch_outbox import DisabledDispatchAdapter
from src.local_dispatch_coordinator import LocalDispatchCoordinator
from src.signed_local_dispatch import SignedLocalCoordinator

class ProductionBoundaryIntegrationTests(unittest.TestCase):
    def test_production_transport_refuses_send(self):
        with self.assertRaisesRegex(RuntimeError, "Production dispatch disabled"):
            DisabledDispatchAdapter().send("TEST-ONLY", {"load_id": "TEST"})

    def test_unsigned_local_submission_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            coordinator = LocalDispatchCoordinator(
                Path(folder) / "outbox.sqlite",
                Path(folder) / "receiver.sqlite",
                b"i" * 32,
            )
            result = coordinator.submit(
                {"action_id": "TEST-ONLY", "load_id": "L", "route_id": "R",
                 "subject": "tester", "permission": "dispatch.route.execute",
                 "confirmed": True, "context_valid": True,
                 "constraints_passed": True, "expires_at": 4102444800},
                "invalid-signature",
            )
            self.assertEqual(result, "authorization_denied")
            with self.assertRaisesRegex(RuntimeError, "Production dispatch disabled"):
                coordinator.send_production("TEST-ONLY", {})

    def test_signed_coordinator_still_blocks_external_send(self):
        with tempfile.TemporaryDirectory() as folder:
            coordinator = SignedLocalCoordinator(
                Path(folder) / "outbox.sqlite",
                Path(folder) / "receiver.sqlite",
                b"i" * 32,
                b"r" * 32,
            )
            with self.assertRaisesRegex(RuntimeError, "Production dispatch disabled"):
                coordinator.send_production("TEST-ONLY", {})
