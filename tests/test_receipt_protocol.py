import copy
import unittest
from src.receipt_protocol import sign_receipt, verify_receipt

SECRET = b"receiver-test-only-secret-at-least-32-bytes"
NOW = 1000

class ReceiptProtocolTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"load_id": "L1", "route_id": "R2"}
        self.envelope = sign_receipt("A1", self.payload, SECRET, expires_at=NOW+60)

    def test_valid(self):
        self.assertTrue(verify_receipt(self.envelope, "A1", self.payload, SECRET, now=NOW))

    def test_wrong_action(self):
        self.assertFalse(verify_receipt(self.envelope, "A2", self.payload, SECRET, now=NOW))

    def test_wrong_payload(self):
        self.assertFalse(verify_receipt(self.envelope, "A1", {"load_id":"L1","route_id":"R3"}, SECRET, now=NOW))

    def test_tamper(self):
        changed = copy.deepcopy(self.envelope)
        changed["body"]["issuer"] = "forged"
        self.assertFalse(verify_receipt(changed, "A1", self.payload, SECRET, issuer="forged", now=NOW))

    def test_expiry(self):
        self.assertFalse(verify_receipt(self.envelope, "A1", self.payload, SECRET, now=NOW+60))

    def test_wrong_secret(self):
        self.assertFalse(verify_receipt(self.envelope, "A1", self.payload, b"x"*32, now=NOW))

    def test_malformed(self):
        self.assertFalse(verify_receipt({"body":{},"signature":"0"*64}, "A1", self.payload, SECRET, now=NOW))
