"""Read-only cross-check of EXP-09, 10, 13 and 14 recorded outcomes.

Run: python -m validation.audit_experiments_09_10_13_14
Uses csv.DictReader (including quoted commas); never rewrites source records.
"""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "experiments"

def read(exp, path):
    with (ROOT / exp / path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))

def grouped(rows, field, pass_field):
    groups = collections.defaultdict(lambda: {"rows": 0, "passes": 0})
    for row in rows:
        groups[row[field]]["rows"] += 1
        groups[row[field]]["passes"] += int(str(row[pass_field]).lower() in ("1", "true"))
    return dict(groups)

def audit():
    exp09 = read("EXP-09", "results.csv")
    exp10 = read("EXP-10", "results/trials.csv")
    exp13 = read("EXP-13", "results/http_requests.csv")
    exp14 = read("EXP-14", "results/trials.csv")
    exp13_categories = dict(collections.Counter(row["engine_outcome"] for row in exp13))
    exp13_status = dict(collections.Counter(row["http_status"] for row in exp13))
    phase = collections.defaultdict(lambda: {"rows": 0, "passes": 0})
    for row in exp14:
        key = row["delivery_strategy"] + "/" + row["interruption_phase"]
        phase[key]["rows"] += 1
        phase[key]["passes"] += int(row["state_compliance_pass"].lower() == "true")
    return {
        "EXP-09": {"rows": len(exp09), "strategies": grouped(exp09, "engine_strategy", "pass_status")},
        "EXP-10": {"rows": len(exp10), "strategies": grouped(exp10, "strategy", "correct"),
                   "published_summary": json.loads((ROOT / "EXP-10/results/summary.json").read_text(encoding="utf-8"))},
        "EXP-13": {"rows": len(exp13), "outcomes": exp13_categories, "http_statuses": exp13_status,
                   "published_summary": json.loads((ROOT / "EXP-13/results/summary.json").read_text(encoding="utf-8"))},
        "EXP-14": {"rows": len(exp14), "phases": dict(phase),
                   "published_summary": json.loads((ROOT / "EXP-14/results/summary.json").read_text(encoding="utf-8"))},
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
