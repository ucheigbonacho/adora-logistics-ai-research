"""EXP-16 prospective holdout evaluator. No labels are created or altered.

Run: python -m validation.evaluate_exp16_holdout --source /path/to/new_reviewed_holdout.jsonl --output-dir /tmp/exp16-holdout-new
Requires independently reviewed, non-exploratory cases and explicit adjudication.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

EXPLORATORY_IDS = {f"PL-Q3-RUN-{i:03d}" for i in range(1, 11)}
VALID = {"routine", "escalate"}

def utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def evaluate(source, output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    raw = Path(source).read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not records:
        raise ValueError("No holdout records")
    ids = [r["case_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case IDs")
    if EXPLORATORY_IDS.intersection(ids):
        raise ValueError("Exploratory November cases cannot be reused as held-out observations")
    observations = []
    for r in records:
        if r.get("expected") not in VALID:
            raise ValueError("Independently reviewed routine/escalate label required")
        if not r.get("independent_review_ref") or not r.get("reviewed_at"):
            raise ValueError("Independent label review reference and timestamp required")
        utc(r["reviewed_at"])
        score = r.get("signal_metric")
        if not isinstance(score, (int, float)) or not 0 <= score <= 1:
            raise ValueError("Valid signal metric required")
        baseline = "escalate" if score >= 0.70 else "routine"
        if r.get("appointment_time") and r.get("calculated_eta"):
            context = "escalate" if utc(r["calculated_eta"]) > utc(r["appointment_time"]) else "routine"
        else:
            context = "needs_review"
        observations.append({
            "case_id": r["case_id"], "expected": r["expected"],
            "baseline": baseline, "eta_context": context,
            "connection_state_transition": r.get("connection_state_transition", "missing"),
            "independent_review_ref": r["independent_review_ref"],
        })
    def matrix(key):
        evaluated = [r for r in observations if r[key] in VALID]
        counts = Counter((r["expected"], r[key]) for r in evaluated)
        return {
            "evaluated": len(evaluated),
            "needs_review": len(observations) - len(evaluated),
            "correct": sum(r["expected"] == r[key] for r in evaluated),
            "confusion": {f"{expected}_as_{predicted}": counts[(expected, predicted)]
                          for expected in sorted(VALID) for predicted in sorted(VALID)},
        }
    summary = {
        "classification": "EXP16_PROSPECTIVE_INDEPENDENTLY_REVIEWED_HOLDOUT",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "total": len(observations),
        "baseline": matrix("baseline"),
        "eta_context": matrix("eta_context"),
        "caveat": "Only evaluate independently reviewed future records; this script does not establish review authenticity or production readiness.",
    }
    dest.mkdir(parents=True)
    (dest / "observations.json").write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
    (dest / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output-dir", required=True)
    a = p.parse_args()
    print(json.dumps(evaluate(a.source, a.output_dir), indent=2))
