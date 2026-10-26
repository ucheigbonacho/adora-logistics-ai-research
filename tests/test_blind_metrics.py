import unittest
from validation.blind_metrics import classification_report

class BlindMetricsTests(unittest.TestCase):
    def test_metrics_and_confusion_counts(self):
        cases = [
            {"expected":"informational_report","actual":"informational_report","pass":True},
            {"expected":"informational_report","actual":"clarification_required","pass":False},
            {"expected":"route_proposal_requested","actual":"route_proposal_requested","pass":True},
        ]
        result = classification_report({"status":"STRUCTURALLY_ACCEPTED_NOT_AUTHENTICATED",
                                        "evaluation":{"cases":cases}})
        self.assertEqual(result["total"],3)
        self.assertEqual(result["correct"],2)
        self.assertAlmostEqual(result["accuracy"],2/3)
        self.assertEqual(result["per_category"]["informational_report"]["recall"],0.5)
        self.assertEqual(result["per_category"]["informational_report"]["precision"],1.0)

    def test_zero_denominator_reported_as_none(self):
        result=classification_report({"status":"STRUCTURALLY_ACCEPTED_NOT_AUTHENTICATED",
                                      "evaluation":{"cases":[{"expected":"informational_report",
                                      "actual":"clarification_required","pass":False}]}})
        self.assertIsNone(result["per_category"]["informational_report"]["precision"])

    def test_reject_unaccepted_input(self):
        with self.assertRaises(ValueError):
            classification_report({"status":"REJECTED_PRECHECK","evaluation":None})
