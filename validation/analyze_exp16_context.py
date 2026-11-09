"""EXP-16 exploratory context analysis of owner-confirmed actual November records.

Run: python -m validation.analyze_exp16_context --source data/q4_2026/actual_november_records.jsonl --output-dir /tmp/exp16-context-new

The contextual rule is POST-HOC on this 10-record dataset and is NOT a
held-out result, production rule, or independent voice-authorization evaluation.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def analyze(source, output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory must be new")
    raw = Path(source).read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not records or len({r["case_id"] for r in records}) != len(records):
        raise ValueError("Records must be nonempty and have unique case IDs")
    observations = []
    for row in records:
        if row["expected"] not in ("routine", "escalate"):
            raise ValueError("Unexpected operational outcome label")
        delay = (parse_time(row["calculated_eta"]) - parse_time(row["appointment_time"])).total_seconds() / 60
        signal_prediction = "escalate" if row["signal_metric"] >= 0.70 else "routine"
        # Explicitly post-hoc exploratory comparison, not pre-registered or held out.
        eta_prediction = "escalate" if delay > 0 else "routine"
        observations.append({
            "case_id": row["case_id"],
            "expected_operational_outcome": row["expected"],
            "signal_metric": row["signal_metric"],
            "eta_delay_minutes": delay,
            "connection_state_transition": row["connection_state_transition"],
            "signal_only_prediction": signal_prediction,
            "eta_context_prediction": eta_prediction,
            "signal_only_correct": signal_prediction == row["expected"],
            "eta_context_correct": eta_prediction == row["expected"],
        })
    summary = {
        "classification": "EXP16_POST_HOC_EXPLORATORY_CONTEXT_ANALYSIS",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "sample_size": len(observations),
        "signal_threshold": 0.70,
        "eta_rule": "calculated_eta later than appointment_time => escalate",
        "signal_only_correct": sum(r["signal_only_correct"] for r in observations),
        "eta_context_correct_in_sample": sum(r["eta_context_correct"] for r in observations),
        "signal_only_mismatches": [r["case_id"] for r in observations if not r["signal_only_correct"]],
        "eta_context_mismatches": [r["case_id"] for r in observations if not r["eta_context_correct"]],
        "connection_transition_counts": dict(Counter(r["connection_state_transition"] for r in observations)),
        "caveat": "ETA comparison selected after examining these records. In-sample agreement is exploratory, not an independent validation or evidence of improved generalization. Operational outcomes are not authorization labels.",
    }
    dest.mkdir(parents=True)
    (dest / "observations.json").write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
    (dest / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.source, args.output_dir), indent=2))
