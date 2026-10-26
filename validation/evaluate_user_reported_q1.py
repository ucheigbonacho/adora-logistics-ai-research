"""Evaluate USER-REPORTED Q1-E01 labels, explicitly not verified ground truth.

Does not modify original validation inputs or historical output files.
"""
import json
from pathlib import Path
from src.engine import execute_routing_decision


def evaluate_user_reported(path):
    rows=[json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows)!=6 or {x["id"] for x in rows}!={f"Q1-E01-V{i:02d}" for i in range(1,7)}:
        raise ValueError("expected exactly six unique Q1-E01 cases")
    if any(x.get("status")!="USER_REPORTED_UNVERIFIED" or x.get("review_verified") is not False for x in rows):
        raise ValueError("unverified reference must retain user-reported status")
    results=[]
    for row in rows:
        actual=execute_routing_decision(row["experiment_id"],row["input"])
        results.append({"id":row["id"],"reported_expected":row["expected"],"actual":actual,
                        "exact_match":actual==row["expected"]})
    return {"basis":"USER_REPORTED_UNVERIFIED_NOT_INDEPENDENT_VALIDATION",
            "total":len(results),"matches":sum(x["exact_match"] for x in results),
            "mismatches":[x for x in results if not x["exact_match"]],"cases":results}


if __name__=="__main__":
    print(json.dumps(evaluate_user_reported(Path(__file__).with_name("q1_e01_user_reported_approval_2026-10-26.jsonl")),indent=2))
