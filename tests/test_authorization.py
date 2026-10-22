import unittest
from src.authorization import evaluate_dispatch_request
from src.engine import execute_routing_decision
class AuthorizationSafetyTests(unittest.TestCase):
    def test_raw_utterance_cannot_authorize(self):
        for phrase in ("please find another road","reroute load 123","road closed ahead","alternate_gating"):
            with self.subTest(phrase=phrase):
                self.assertNotEqual(execute_routing_decision("Q1-E01",{"utterance":phrase}),"authorize_intent")
    def test_proposal(self):
        self.assertEqual(evaluate_dispatch_request({"utterance":"please find another road"}),"route_proposal_requested")
    def test_missing_controls_denied(self):
        self.assertEqual(evaluate_dispatch_request({"request_type":"execute_route_change","confirmed":True}),"authorization_denied")
    def test_complete_structured_authorization(self):
        p={"request_type":"execute_route_change","authenticated":True,"authorized_role":True,"context_valid":True,"constraints_passed":True,"confirmed":True,"load_id":"LOAD-123","route_id":"ROUTE-B","action_id":"ACT-1"}
        self.assertEqual(evaluate_dispatch_request(p),"authorize_intent")
        for k in ("authenticated","authorized_role","context_valid","constraints_passed","confirmed"):
            with self.subTest(k=k): self.assertEqual(evaluate_dispatch_request({**p,k:False}),"authorization_denied")
        for k in ("load_id","route_id","action_id"):
            with self.subTest(k=k): self.assertEqual(evaluate_dispatch_request({**p,k:""}),"clarification_required")
