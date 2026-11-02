import unittest
from validation.operational_category_crosswalk import crosswalk

class OperationalCrosswalkTests(unittest.TestCase):
    def test_supported_exception_is_only_proposal(self):
        rows=[{"case_id":"T1","timestamp":"2026-06-01T00:00:00Z",
               "scenario":"missing_load_attributes","expected":"exception"}]
        out=crosswalk(rows)[0]
        self.assertEqual(out["mapped_experiment"],"Q2-E02")
        self.assertEqual(out["proposed_existing_category"],"clarification_required")
        self.assertEqual(out["mapping_status"],"PROPOSED_NOT_VALIDATED")
        self.assertIn("destination",out["missing_engine_inputs"])

    def test_routine_does_not_imply_engine_output(self):
        rows=[{"case_id":"T2","timestamp":"2026-11-02T00:00:00Z",
               "scenario":"routine_transit","expected":"routine"}]
        out=crosswalk(rows)[0]
        self.assertIsNone(out["mapped_experiment"])
        self.assertIsNone(out["proposed_existing_category"])
        self.assertEqual(out["mapping_status"],"REQUIRES_DOMAIN_REVIEW")

    def test_original_rows_not_mutated(self):
        rows=[{"case_id":"T3","timestamp":"2026-03-01T00:00:00Z",
               "scenario":"driver_speech_intelligence","expected":"exception"}]
        before=[dict(x) for x in rows]
        crosswalk(rows)
        self.assertEqual(rows,before)
