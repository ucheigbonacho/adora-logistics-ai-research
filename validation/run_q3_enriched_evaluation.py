"""Executed Q3-E01 enriched case comparison (not independent validation).

Reads original user-reported enriched data and does not modify it.
"""
import json
from pathlib import Path
from validation.q3_eta_timestamp_adapter import evaluate_jsonl

SOURCE = Path(__file__).with_name("q3_enriched_user_reported_10_2026-11-02.jsonl")

def summary(source=SOURCE):
    results = evaluate_jsonl(source)
    eligible = [r for r in results if r["evaluation_status"] == "EVALUATED_Q3_E01"]
    return {
        "status": "USER_REPORTED_SOURCE_NOT_INDEPENDENTLY_VERIFIED",
        "total": len(results),
        "q3_e01_evaluated": len(eligible),
        "not_evaluated": len(results) - len(eligible),
        "candidate_label_agreement": sum(r["expected_agreement"] is True for r in eligible),
        "cases": results,
    }

if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
