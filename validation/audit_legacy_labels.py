"""Read-only comparison with the ORIGINAL 34-case legacy fixture.

This is a compatibility audit, NOT independently approved accuracy.
Does not modify datasets, reviewer approval, or result files.
"""
import json
from pathlib import Path
from src.engine import execute_routing_decision

def audit(path):
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    result = []
    for case in rows:
        try:
            actual = execute_routing_decision(case["experiment_id"], case["input"])
            error = None
        except Exception as exc:
            actual = None
            error = type(exc).__name__
        result.append({"id": case["id"], "experiment_id": case["experiment_id"],
                       "legacy_expected": case["expected"], "current_actual": actual,
                       "exact_match": error is None and actual == case["expected"],
                       "error": error})
    return {"basis": "legacy-label-compatibility-not-independent-accuracy",
            "total": len(result), "matches": sum(r["exact_match"] for r in result),
            "mismatches": [r for r in result if not r["exact_match"]]}

if __name__ == "__main__":
    path = Path(__file__).with_name("independent_cases.jsonl")
    print(json.dumps(audit(path), indent=2))
