"""Fail-closed prospective blind evaluation gate.

This tool does not authenticate reviewers or create source data.
It refuses to score an intake set that fails structural preflight.
"""
import argparse
import json
from pathlib import Path

from validation.blind_intake import validate
from validation.reviewed_reference import evaluate_reviewed_cases


def evaluate_blind(path):
    source = Path(path)
    preflight = validate(source)
    if not preflight["passes_structural_checks"]:
        return {"status": "REJECTED_PRECHECK", "preflight": preflight, "evaluation": None}
    scored = evaluate_reviewed_cases(source)
    return {"status": "STRUCTURALLY_ACCEPTED_NOT_AUTHENTICATED",
            "preflight": preflight,
            "evaluation": scored}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", help="independently labeled, reviewed cases")
    args = parser.parse_args()
    result = evaluate_blind(args.jsonl)
    print(json.dumps(result, indent=2))
    if result["status"] == "REJECTED_PRECHECK":
        raise SystemExit(2)
