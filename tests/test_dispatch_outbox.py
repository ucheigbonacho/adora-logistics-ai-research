import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.dispatch_outbox import DispatchOutbox, DisabledDispatchAdapter

class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/"outbox.db"
        self.db = DispatchOutbox(self.path)

    def test_enqueue_duplicate_conflict(self):
        self.assertEqual(self.db.enqueue("A1", {"route":"R1"}), "pending")
        self.assertEqual(self.db.enqueue("A1", {"route":"R1"}), "duplicate")
        self.assertEqual(self.db.enqueue("A1", {"route":"R2"}), "conflict")

    def test_restart_persists_pending(self):
        self.db.enqueue("A1", {"route":"R1"})
        self.assertEqual(DispatchOutbox(self.path).status("A1"), "pending")

    def test_claim_ack_and_duplicate_ack(self):
        self.db.enqueue("A1", {"route":"R1"})
        self.assertEqual(self.db.acknowledge("A1","receipt-1"), "not_dispatched")
        self.assertEqual(self.db.claim("A1", now=100), {"route":"R1"})
        self.assertIsNone(self.db.claim("A1", now=101))
        self.assertEqual(self.db.acknowledge("A1","receipt-1"), "acknowledged")
        self.assertEqual(self.db.acknowledge("A1","receipt-1"), "duplicate_ack")
        self.assertEqual(self.db.acknowledge("A1","receipt-2"), "receipt_conflict")

    def test_expired_lease_never_auto_retries(self):
        self.db.enqueue("A1", {"route":"R1"})
        self.db.claim("A1", lease_seconds=10, now=100)
        self.assertIsNone(DispatchOutbox(self.path).claim("A1", now=111))
        self.assertEqual(self.db.status("A1"), "uncertain")
        self.assertIsNone(self.db.claim("A1", now=112))
        self.assertEqual(self.db.acknowledge("A1","receiver-confirmed"),"acknowledged")

    def test_concurrent_claim_one_winner(self):
        self.db.enqueue("A1", {"route":"R1"})
        with ThreadPoolExecutor(max_workers=8) as pool:
            values=list(pool.map(lambda _:self.db.claim("A1",now=100),range(16)))
        self.assertEqual(sum(x is not None for x in values),1)

    def test_adapter_never_executes(self):
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            DisabledDispatchAdapter().send("A1", {"route":"R1"})
