"""Test conservative driver intent behavior beyond the six review candidates."""
import unittest
from src.authorization import classify_driver_utterance, evaluate_dispatch_request

class IntentClassificationTests(unittest.TestCase):
    def test_six_user_reported_labels(self):
        cases = [
            ("road closed ahead", "informational_report"),
            ("please find another road", "route_proposal_requested"),
            ("can you hear me", "clarification_required"),
            ("I heard the road is closed?", "informational_report"),
            ("alternate route", "clarification_required"),
            ("route may be blocked", "informational_report"),
        ]
        for utterance, expected in cases:
            with self.subTest(utterance=utterance):
                self.assertEqual(classify_driver_utterance(utterance), expected)

    def test_explicit_options_request_not_execution(self):
        self.assertEqual(classify_driver_utterance("suggest another route for load 12"), "route_proposal_requested")

    def test_plain_reroute_instruction_does_not_authorize(self):
        self.assertNotEqual(evaluate_dispatch_request({"utterance": "reroute load 12 via B"}), "authorize_intent")

    def test_uncertain_report_not_execution(self):
        self.assertEqual(classify_driver_utterance("road might be blocked"), "informational_report")

    def test_missing_and_nonstring_input(self):
        self.assertEqual(classify_driver_utterance(None), "clarification_required")
        self.assertEqual(classify_driver_utterance(""), "clarification_required")
