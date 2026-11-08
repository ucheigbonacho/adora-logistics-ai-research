"""Run EXP-10 in a new output directory, preserving recorded source files.

Usage: python -m validation.reproduce_exp10 --output-dir /tmp/adora-exp10-run
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "experiments/EXP-10/routing_engine.py"
ORIGINAL = (ROOT / "experiments/EXP-10/results").resolve()

def reproduce(output_dir, count=100):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    if dest == ORIGINAL or ORIGINAL in dest.parents or dest in ORIGINAL.parents:
        raise ValueError("Output must be separate from original results")
    spec = importlib.util.spec_from_file_location("exp10_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    strategies = ("unprotected_stream", "idempotent_gating")
    rows = [module.evaluate_concurrency_load(pid, strategy)
            for pid in range(12000, 12000 + count) for strategy in strategies]
    summary = []
    for strategy in strategies:
        subset = [row for row in rows if row["engine_strategy"] == strategy]
        summary.append({
            "engine_strategy": strategy,
            "profiles_evaluated": len(subset),
            "state_compliance_pass": sum(row["state_compliance_pass"] for row in subset),
            "duplicate_actions_executed": sum(row["duplicate_actions_executed"] for row in subset),
            "sequence_sync_errors": sum(row["gps_sequence_final"] != 12 for row in subset),
        })
    historical = json.loads((ORIGINAL / "summary.json").read_text(encoding="utf-8"))
    dest.mkdir(parents=True)
    with (dest / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (dest / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "classification": "NEW_EXP10_REPRODUCTION",
        "source_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        "original_trials_sha256": hashlib.sha256((ORIGINAL / "trials.csv").read_bytes()).hexdigest(),
        "original_summary_sha256": hashlib.sha256((ORIGINAL / "summary.json").read_bytes()).hexdigest(),
        "new_trial_count": len(rows),
        "fresh_summary": summary,
        "published_summary": historical,
        "matches_published": summary == historical,
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output_dir), indent=2))
