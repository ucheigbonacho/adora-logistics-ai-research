"""
EXP-12: Production Transactional Outbox Pipeline Integration Test Suite.
Validates multi-phase interruption recovery, receiver idempotency filtration,
and data boundary mutation compliance parameters using dynamic spec execution.
"""
import importlib.util
import pathlib
import unittest

# Resolve path and dynamically load the production outbox assertion module
P = pathlib.Path(__file__).resolve().parents[1] / 'experiments' / 'EXP-12' / 'outbox_validator.py'
spec = importlib.util.spec_from_file_location('outbox_validator', P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestExp12(unittest.TestCase):
    def test_receiver_idempotency_deduplication(self):
        """
        Verifies that the durable outbox architecture maintains perfect compliance 
        and rejects redundant mutations across all interruption phases.
        """
        for phase in m.PHASES:
            x = m.evaluate_outbox_profile('durable_outbox_idempotent_receiver', phase, 1001)
            self.assertEqual(
                (x['state_compliance_pass'], x['redundant_mutations'], x['dropped_transactions']),
                (1, 0, 0)
            )

    def test_isolated_failure_boundaries(self):
        """
        Quantifies known dropped transactions and redundant mutation execution boundaries 
        across unbuffered retry streams and volatile pre-flight registries.
        """
        self.assertEqual(
            m.evaluate_outbox_profile('volatile_pre_flight_registry', 'before_send', 1001)['dropped_transactions'],
            1
        )
        self.assertGreater(
            m.evaluate_outbox_profile('unbuffered_retry_stream', 'after_send_before_ack', 1001)['redundant_mutations'],
            0
        )

if __name__ == '__main__':
    unittest.main()
