import unittest
from validation.audit_approval_and_generated_labels import audit

class AuditApprovalAndGeneratedLabelsTests(unittest.TestCase):
    def test_historical_discrepancy_is_preserved(self):
        result = audit()
        self.assertEqual(result["case_results"]["total"], 34)
        self.assertEqual(result["case_results"]["passed"], 33)
        self.assertIn("Q1-E01-V02", result["case_results"]["failed_case_ids"])
        self.assertEqual(result["summary"], {"total": 34, "passed": 33})
        self.assertTrue(result["approval_discrepancy"])

    def test_generated_labels_are_not_independent(self):
        result = audit()
        self.assertTrue(result["generator_expected_uses_rule_function"])
        self.assertTrue(result["evaluator_computed_uses_same_rule_function"])
        self.assertFalse(result["generated_results_independent_accuracy"])
