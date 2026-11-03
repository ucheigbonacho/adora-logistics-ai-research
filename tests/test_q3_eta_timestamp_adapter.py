import unittest
from validation.q3_eta_timestamp_adapter import evaluate_record

def record(**changes):
    base = {
        "case_id": "UNIT-TEST-ONLY",
        "scenario": "sequence_delay_detection",
        "expected": "escalate",
        "appointment_time": "2026-11-02T09:00:00Z",
        "calculated_eta": "2026-11-02T09:45:00Z",
        "telemetry_event_timestamp": "2026-11-02T08:15:21.050Z",
        "evaluation_timestamp": "2026-11-02T08:15:22.125Z",
    }
    base.update(changes)
    return base

class Q3TimestampAdapterTests(unittest.TestCase):
    def test_fresh_delay(self):
        result = evaluate_record(record())
        self.assertEqual(result["engine_output"], "delay_alert_triggered")
        self.assertAlmostEqual(result["freshness_sec"], 1.075)
        self.assertEqual(result["evaluation_status"], "EVALUATED_Q3_E01")
        self.assertEqual(result["event_id_match_status"], "UNVERIFIED_REQUIRES_SOURCE_EVENT")

    def test_stale_delay_suppressed(self):
        result = evaluate_record(record(telemetry_event_timestamp="2026-11-02T08:10:00Z"))
        self.assertEqual(result["engine_output"], "stale_telemetry_suppressed")

    def test_missing_timestamp_rejected(self):
        result = evaluate_record(record(evaluation_timestamp=None))
        self.assertEqual(result["evaluation_status"], "REJECTED_INVALID_TIMESTAMPS")

    def test_negative_freshness_rejected(self):
        result = evaluate_record(record(evaluation_timestamp="2026-11-02T08:15:20Z"))
        self.assertEqual(result["evaluation_status"], "REJECTED_INVALID_TIMESTAMPS")

    def test_non_eta_scenario_not_scored(self):
        result = evaluate_record(record(scenario="constraint_gating"))
        self.assertEqual(result["evaluation_status"], "NOT_EVALUATED_PROFILE_MISMATCH")
        self.assertIsNone(result["engine_output"])

    def test_no_source_mutation(self):
        original = record()
        before = dict(original)
        evaluate_record(original)
        self.assertEqual(original, before)
