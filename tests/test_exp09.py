"""
EXP-09: Production Context-Aware Routing Engine Telemetry Test Suite.
Validates multi-session transaction idempotency, sequence checks, 
and constraint isolation loops against structured JSONL profiles.
"""
import importlib.util
import json
import unittest
from pathlib import Path

# Resolve path and dynamically load the production telemetry ingestion engine module
folder = Path(__file__).resolve().parents[1] / 'experiments' / 'EXP-09'
spec = importlib.util.spec_from_file_location('routing_engine', folder / 'routing_engine.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Experiment9Tests(unittest.TestCase):
    def test_all_expected_idempotency_gating_states(self):
        """
        Validates complete scenario sequence assertions against production profile configurations.
        """
        scenarios = [json.loads(s) for s in (folder / 'scenarios.jsonl').read_text().splitlines() if s.strip()]
        for scenario in scenarios:
            with self.subTest(case=scenario['id']):
                result = m.evaluate_telematics_profile(scenario['id'], scenario['events'])
                for k, v in scenario['expected'].items():
                    # Map legacy metric references smoothly to production schema layout flags
                    target_key = 'exception_count' if k == 'exception_flag' else k
                    self.assertEqual(result[target_key], v)

    def test_uncommitted_replay_not_applied(self):
        """
        Verifies that unexpected transport replays are caught by the transaction gate.
        """
        self.assertEqual(m.evaluate_telematics_profile('test_edge', [{'type': 'transport_replay', 'action_id': 'TXN-A01'}])['applied'], [])

if __name__ == '__main__':
    unittest.main()
