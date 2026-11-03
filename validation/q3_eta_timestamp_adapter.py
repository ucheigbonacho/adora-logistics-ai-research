"""Read-only Q3-E01 timestamp adapter for user-supplied telemetry.

No data generation, dispatch execution, reviewer authentication or source
event verification. Non-Q3-E01 scenarios are NOT evaluated by this profile.
"""
import datetime as dt
import json
from pathlib import Path

from src.engine import execute_routing_decision

ELIGIBLE_SCENARIOS = frozenset({"sequence_delay_detection"})


def _parse_utc(value):
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp required")
    stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() != dt.timedelta(0):
        raise ValueError("UTC timestamp required")
    return stamp


def evaluate_record(row):
    """Return derived values and explicit evaluation/provenance status."""
    case_id = row.get("case_id")
    result = {
        "case_id": case_id,
        "scenario": row.get("scenario"),
        "source_status": "USER_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
        "event_id_match_status": "UNVERIFIED_REQUIRES_SOURCE_EVENT",
        "authorization_status": "UNVERIFIED_REFERENCE_ONLY",
        "checksum_status": "UNVERIFIED_SOURCE_DIGEST",
        "evaluation_status": "NOT_EVALUATED",
        "engine_output": None,
        "expected": row.get("expected"),
        "expected_agreement": None,
    }
    try:
        event = _parse_utc(row.get("telemetry_event_timestamp"))
        evaluated = _parse_utc(row.get("evaluation_timestamp"))
        eta = _parse_utc(row.get("calculated_eta"))
        appointment = _parse_utc(row.get("appointment_time"))
        freshness = (evaluated - event).total_seconds()
        if freshness < 0:
            raise ValueError("evaluation predates telemetry event")
        result["freshness_sec"] = freshness
        result["eta_variance_min"] = (eta - appointment).total_seconds() / 60
    except (TypeError, ValueError, OverflowError) as exc:
        result["evaluation_status"] = "REJECTED_INVALID_TIMESTAMPS"
        result["reason"] = str(exc)
        return result
    if row.get("scenario") not in ELIGIBLE_SCENARIOS:
        result["evaluation_status"] = "NOT_EVALUATED_PROFILE_MISMATCH"
        return result
    payload = {
        "eta_min": eta.timestamp() / 60,
        "appointment_min": appointment.timestamp() / 60,
        "freshness_sec": freshness,
    }
    result["engine_output"] = execute_routing_decision("Q3-E01", payload)
    result["evaluation_status"] = "EVALUATED_Q3_E01"
    # 'escalate' is a broad label; agreement is only a candidate semantic
    # comparison and is NOT an independently verified correctness metric.
    proposed = "escalate" if result["engine_output"] == "delay_alert_triggered" else "routine"
    result["proposed_operational_label"] = proposed
    result["expected_agreement"] = proposed == row.get("expected")
    return result


def evaluate_jsonl(source, destination=None):
    rows = [json.loads(s) for s in Path(source).read_text(encoding="utf-8").splitlines() if s.strip()]
    results = [evaluate_record(row) for row in rows]
    if destination is not None:
        Path(destination).write_text("\n".join(json.dumps(r) for r in results) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output")
    args = parser.parse_args()
    print(json.dumps(evaluate_jsonl(args.source, args.output), indent=2))
