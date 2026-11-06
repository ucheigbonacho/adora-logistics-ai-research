import unittest
from validation.audit_experiments_09_14 import audit

class ExperimentSourceReviewTests(unittest.TestCase):
    def test_source_rows_and_strategy_counts(self):
        report = audit()
        self.assertEqual(report["EXP-10"]["rows"], 200)
        self.assertEqual(report["EXP-10"]["raw_aggregates"]["volatile"]["passes"], 0)
        self.assertEqual(report["EXP-10"]["raw_aggregates"]["durable"]["passes"], 100)
        self.assertEqual(report["EXP-11"]["rows"], 600)
        self.assertEqual(report["EXP-11"]["raw_aggregates"]["eventual_consistency_stream"]["rows"], 300)
        self.assertEqual(report["EXP-11"]["raw_aggregates"]["distributed_quorum_gating"]["rows"], 300)
        self.assertEqual(report["EXP-12"]["rows"], 2411)
        self.assertEqual(report["EXP-14"]["rows"], 18)
        self.assertEqual(report["EXP-14"]["raw_aggregates"]["unbuffered_retry_stream"]["passes"], 3)
        self.assertEqual(report["EXP-14"]["raw_aggregates"]["durable_outbox_idempotent_receiver"]["passes"], 9)
