import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.local_receiver import LocalDispatchReceiver


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'receiver.sqlite'
        self.receiver = LocalDispatchReceiver(self.path)

    def test_idempotent_receipt(self):
        first, receipt = self.receiver.receive('a1', {'route': 'R1'})
        self.assertEqual(first, 'accepted')
        self.assertEqual(self.receiver.receive('a1', {'route': 'R1'}), ('duplicate', receipt))
        self.assertEqual(self.receiver.lookup('a1'), receipt)

    def test_conflicting_payload_rejected(self):
        self.receiver.receive('a1', {'route': 'R1'})
        self.assertEqual(self.receiver.receive('a1', {'route': 'R2'}), ('conflict', None))

    def test_restart_preserves_receipt(self):
        _, receipt = self.receiver.receive('a1', {'route': 'R1'})
        self.assertEqual(LocalDispatchReceiver(self.path).lookup('a1'), receipt)

    def test_concurrent_only_one_accept(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.receiver.receive('a1', {'route': 'R1'}), range(16)))
        self.assertEqual(sum(s == 'accepted' for s, _ in results), 1)
        self.assertEqual(sum(s == 'duplicate' for s, _ in results), 15)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.receiver.receive('', {'route': 'R1'})
        with self.assertRaises(ValueError):
            self.receiver.receive('a1', {})
