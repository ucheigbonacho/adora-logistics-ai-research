"""
Logistics Routing Engine - Telematics Ingestion Core Unit Test Suite
Description: Enforces systematic verification across the dataset generation pipelines,
             rule engine thresholds, and latency metrics validation layers.
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from src.rules import execute_routing_decision
from src.generate import run_dataset_generation_pipeline
from src.evaluate import evaluate_telematics_suite

class TestExperiments(unittest.TestCase):
    def test_all_eight_generate_and_evaluate(self):
        """
        Validates complete multi-experiment pipeline loop integrity and execution stability.
        """
        with TemporaryDirectory() as tmp_dir:
            # Verify dataset serialization count bounds
            self.assertEqual(run_dataset_generation_pipeline(tmp_dir, 25), 200)
            
            # Execute automated performance evaluation suite
            metrics = evaluate_telematics_suite(tmp_dir)
            self.assertEqual(len(metrics), 8)
            
            # Verify pipeline integrity rate thresholds and exception containment properties
            self.assertTrue(all(
                m['cases'] == 25 and m['sync_validation_exceptions'] == 0 for m in metrics
            ))
            self.assertEqual(len(list((Path(tmp_dir) / 'results').glob('*_runs.csv'))), 8)
            
    def test_reject_infeasible_assignment(self):
        """
        Verifies that resource constraint gating triggers a reject status on hardware mismatches.
        """
        self.assertEqual(
            execute_routing_decision('Q2-E01', {'available': True, 'equipment_match': False, 'hours_left': 8, 'hours_needed': 3}),
            'resource_constraint_reject'
        )
        
    def test_deduplicate_retry(self):
        """
        Verifies that high-frequency packet replays hit the idempotency filter gate cleanly.
        """
        self.assertEqual(
            execute_routing_decision('Q4-E02', {'event_key': 'e1', 'seen_keys': ['e1']}),
            'idempotency_filter_match'
        )
        
    def test_unknown_experiment(self):
        """
        Ensures the engine isolation boundaries throw a ValueError on unmapped profiles.
        """
        with self.assertRaises(ValueError): 
            execute_routing_decision('Q9-E01', {})

if __name__ == '__main__':
    unittest.main()
