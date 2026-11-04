import hashlib
import hmac
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from src.trusted_gateway import DurableReservationGate, canonical, verify_claim

SECRET = b"local-test-key-not-for-production-123456789"
def claim():
    return {"load_id":"LOAD-123","route_id":"R-B","action_id":"A-1","subject":"dispatcher-7","permission":"dispatch.route.execute","confirmed":True,"context_valid":True,"constraints_passed":True,"expires_at":2000000000}
def sign(c):
    return hmac.new(SECRET, canonical(c), hashlib.sha256).hexdigest()
class TrustedGatewayTests(unittest.TestCase):
    def test_valid_claim(self):
        c=claim(); self.assertTrue(verify_claim(c,sign(c),SECRET,now=1000000000))
    def test_reject_tamper(self):
        c=claim(); s=sign(c); c["route_id"]="R-C"; self.assertFalse(verify_claim(c,s,SECRET,now=1000000000))
    def test_expired(self):
        c=claim(); self.assertFalse(verify_claim(c,sign(c),SECRET,now=2000000000))
    def test_missing_permission(self):
        c=claim(); c["permission"]="dispatch.route.read"; self.assertFalse(verify_claim(c,sign(c),SECRET,now=1000000000))
    def test_no_confirmation(self):
        c=claim(); c["confirmed"]=False; self.assertFalse(verify_claim(c,sign(c),SECRET,now=1000000000))
    def test_restart_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"actions.db"; c=claim(); s=sign(c)
            self.assertEqual(DurableReservationGate(p,SECRET).reserve(c,s,now=1000000000),"reserved_not_executed")
            self.assertEqual(DurableReservationGate(p,SECRET).reserve(c,s,now=1000000000),"duplicate_reservation")
            other={**c,"route_id":"R-C"}
            self.assertEqual(DurableReservationGate(p,SECRET).reserve(other,sign(other),now=1000000000),"action_id_conflict")
    def test_concurrent_single_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            gate=DurableReservationGate(Path(d)/"actions.db",SECRET); c=claim(); s=sign(c)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda _:gate.reserve(c,s,now=1000000000),range(16)))
            self.assertEqual(results.count("reserved_not_executed"),1)
            self.assertEqual(results.count("duplicate_reservation"),15)
