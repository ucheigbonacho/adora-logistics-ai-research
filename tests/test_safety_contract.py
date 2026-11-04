"""Safety regression checks for incomplete dispatch instructions."""
import unittest
from src.engine import execute_routing_decision

class SafetyContractTests(unittest.TestCase):
    def test_informational_question_does_not_authorize(self):
        self.assertEqual(
            execute_routing_decision("Q1-E01", {"utterance": "Is the road closed?"}),
            "informational_report",
        )

    def test_route_proposal_request_does_not_authorize(self):
        self.assertEqual(
            execute_routing_decision("Q1-E01", {"utterance": "please find another road"}),
            "route_proposal_requested",
        )

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError):
            execute_routing_decision("unknown", {})

if __name__ == "__main__":
    unittest.main()
