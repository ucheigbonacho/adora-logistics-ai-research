import unittest
from validation.audit_experiments_09_10_13_14 import audit

class ExperimentOutcomeReconciliationTests(unittest.TestCase):
    def test_source_totals(self):
        r = audit()
        self.assertEqual(r["EXP-09"]["rows"], 24)
        self.assertEqual(r["EXP-09"]["strategies"]["unprotected_stream"], {"rows": 12, "passes": 2})
        self.assertEqual(r["EXP-09"]["strategies"]["idempotent_gating"], {"rows": 12, "passes": 12})
        self.assertEqual(r["EXP-10"]["rows"], 200)
        self.assertEqual(r["EXP-10"]["strategies"]["volatile"], {"rows": 100, "passes": 0})
        self.assertEqual(r["EXP-10"]["strategies"]["durable"], {"rows": 100, "passes": 100})
        self.assertEqual(r["EXP-13"]["rows"], 203)
        self.assertEqual(r["EXP-13"]["outcomes"], {"IDEMPOTENCY_FILTER_MATCH": 151,
                         "TRANSACTION_COMMITTED": 51, "MUTATION_COLLISION_ABORT": 1})
        self.assertEqual(r["EXP-14"]["rows"], 18)
        self.assertEqual(sum(x["passes"] for k, x in r["EXP-14"]["phases"].items()
                             if k.startswith("unbuffered_retry_stream/")), 3)
        self.assertEqual(sum(x["passes"] for k, x in r["EXP-14"]["phases"].items()
                             if k.startswith("durable_outbox_idempotent_receiver/")), 9)
