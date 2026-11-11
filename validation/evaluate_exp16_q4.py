"""EXP-16 operational outcome evaluation for owner-confirmed actual Q4 records.

Run: python -m validation.evaluate_exp16_q4 --source path/to/actual_q4_november_2026.jsonl --output-dir /tmp/exp16-new
This is a read-only operational escalation baseline, NOT authorization-label accuracy.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

def evaluate(source, output_dir, threshold=0.70):
    source = Path(source)
    destination = Path(output_dir).resolve()
    if destination.exists():
        raise FileExistsError("Output directory must be new")
    raw = source.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("No records")
    if len({r["case_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate case IDs")
    observed = []
    for r in rows:
        if r["expected"] not in ("escalate", "routine"):
            raise ValueError("Unsupported operational label")
        score = r["signal_metric"]
        if not isinstance(score, (float, int)) or not 0 <= score <= 1:
            raise ValueError("Signal metric outside 0..1")
        predicted = "escalate" if score >= threshold else "routine"
        observed.append({"case_id": r["case_id"], "expected_operational_outcome": r["expected"],
                         "threshold_prediction": predicted, "correct": predicted == r["expected"],
                         "signal_metric": score})
    matrix = Counter((r["expected_operational_outcome"], r["threshold_prediction"]) for r in observed)
    summary = {
        "classification": "EXP16_Q4_ACTUAL_RECORD_OPERATIONAL_THRESHOLD_BASELINE",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "count": len(observed),
        "threshold": threshold,
        "correct": sum(r["correct"] for r in observed),
        "confusion": {f"{a}_as_{b}": n for (a, b), n in sorted(matrix.items())},
        "scope": "Recorded escalation/routine outcome only; not dispatch authorization or independently adjudicated voice intent.",
    }
    destination.mkdir(parents=True)
    (destination / "observations.json").write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--threshold", type=float, default=0.70)
    a = p.parse_args()
    print(json.dumps(evaluate(a.source, a.output_dir, a.threshold), indent=2))
