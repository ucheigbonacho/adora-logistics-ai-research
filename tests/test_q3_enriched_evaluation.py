import unittest
from validation.run_q3_enriched_evaluation import summary

class Q3EnrichedEvaluationTests(unittest.TestCase):
    def test_enriched_case_scoping(self):
        result = summary()
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["q3_e01_evaluated"], 4)
        self.assertEqual(result["not_evaluated"], 6)
        self.assertEqual(result["candidate_label_agreement"], 4)
        self.assertTrue(all(r["source_status"] == "USER_REPORTED_NOT_INDEPENDENTLY_VERIFIED"
                            for r in result["cases"]))
