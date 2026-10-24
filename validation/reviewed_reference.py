"""Read-only validation against separately reviewed reference cases.

This module does not generate expected labels or overwrite historic results.
A fixture must declare a reviewer, review date and expected outcome.
Metadata is self-declared and NOT independently authenticated.
"""
import json
from pathlib import Path

from src.engine import execute_routing_decision


def evaluate_reviewed_cases(path):
    source = Path(path)
    cases = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not cases:
        raise ValueError("reviewed reference set is empty")
    seen = set()
    results = []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case must be object")
        required = ("id", "experiment_id", "input", "expected", "reviewer", "reviewed_at", "reference")
        if any(k not in case for k in required):
            raise ValueError("case missing review metadata or expected outcome")
        if not all(isinstance(case[k], str) and case[k].strip() for k in
                   ("id", "experiment_id", "expected", "reviewer", "reviewed_at", "reference")):
            raise ValueError("invalid review metadata")
        if not isinstance(case["input"], dict):
            raise ValueError("case input must be an object")
        if case["id"] in seen:
            raise ValueError("duplicate reviewed case ID")
        seen.add(case["id"])
        try:
            actual = execute_routing_decision(case["experiment_id"], case["input"])
            error = None
        except Exception as exc:
            actual = None
            error = type(exc).__name__
        results.append({"id": case["id"], "experiment_id": case["experiment_id"],
                        "expected": case["expected"], "actual": actual,
                        "pass": actual == case["expected"] and error is None,
                        "error": error, "reviewer": case["reviewer"],
                        "reference": case["reference"]})
    return {"total": len(results), "passed": sum(x["pass"] for x in results),
            "failed": sum(not x["pass"] for x in results), "cases": results}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("reviewed_cases", help="path to independently reviewed JSONL")
    args = parser.parse_args()
    print(json.dumps(evaluate_reviewed_cases(args.reviewed_cases), indent=2))


if __name__ == "__main__":
    main()
