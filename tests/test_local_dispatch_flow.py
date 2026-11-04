"""Controlled local integration: no network and no production dispatch."""
import tempfile
import unittest
from pathlib import Path
from src.dispatch_outbox import DispatchOutbox, DisabledDispatchAdapter
from src.local_receiver import LocalDispatchReceiver

class LocalDispatchFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.outbox = DispatchOutbox(base / "outbox.sqlite")
        self.receiver = LocalDispatchReceiver(base / "receiver.sqlite")

    def test_acknowledged_flow(self):
        payload = {"load_id": "L-1", "route_id": "R-2"}
        self.assertEqual(self.outbox.enqueue("A-1", payload), "pending")
        self.assertEqual(self.outbox.claim("A-1", now=100), payload)
        status, receipt = self.receiver.receive("A-1", payload)
        self.assertEqual(status, "accepted")
        self.assertEqual(self.outbox.acknowledge("A-1", receipt), "acknowledged")
        self.assertEqual(self.outbox.status("A-1"), "acknowledged")

    def test_lost_ack_reconciled_without_duplicate_execution(self):
        payload = {"load_id": "L-1", "route_id": "R-2"}
        self.outbox.enqueue("A-1", payload)
        self.outbox.claim("A-1", lease_seconds=10, now=100)
        status, receipt = self.receiver.receive("A-1", payload)
        self.assertEqual(status, "accepted")
        # Simulated acknowledgement loss: receiver persists, outbox has not.
        self.assertIsNone(self.outbox.claim("A-1", now=111))
        self.assertEqual(self.outbox.status("A-1"), "uncertain")
        self.assertEqual(self.receiver.lookup("A-1"), receipt)
        self.assertEqual(self.outbox.acknowledge("A-1", receipt), "acknowledged")
        self.assertEqual(self.receiver.receive("A-1", payload), ("duplicate", receipt))

    def test_no_external_transport(self):
        with self.assertRaises(RuntimeError):
            DisabledDispatchAdapter().send("A-1", {"route_id": "R-2"})
