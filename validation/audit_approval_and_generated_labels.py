"""Read-only audit of source approval claims and generated-label provenance."""
import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit():
    rows = list(csv.DictReader((ROOT / "validation/case_results.csv").open(encoding="utf-8", newline="")))
    total = len(rows)
    passed = sum(int(row["production_integrity_pass"]) for row in rows)
    failures = [row["profile_id"] for row in rows if row["production_integrity_pass"] != "1"]
    summary = list(csv.DictReader((ROOT / "validation/summary.csv").open(encoding="utf-8", newline="")))
    summary_total = sum(int(row["cases"]) for row in summary)
    summary_pass = sum(int(row["production_compliance_pass"]) for row in summary)
    approval = (ROOT / "reviewer_approval.txt").read_text(encoding="utf-8")
    generator = (ROOT / "src/generate.py").read_text(encoding="utf-8")
    evaluator = (ROOT / "src/evaluate.py").read_text(encoding="utf-8")
    return {
        "status": "SOURCE_RECONCILIATION_NOT_INDEPENDENT_VALIDATION",
        "case_results": {"total": total, "passed": passed, "failed_case_ids": failures},
        "summary": {"total": summary_total, "passed": summary_pass},
        "approval_claims_34_of_34": "34 / 34" in approval,
        "approval_discrepancy": "34 / 34" in approval and (passed, total) != (34, 34),
        "generator_expected_uses_rule_function": "'expected': execute_routing_decision(" in generator,
        "evaluator_computed_uses_same_rule_function": "computed_state = execute_routing_decision(" in evaluator,
        "generated_results_independent_accuracy": False,
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
