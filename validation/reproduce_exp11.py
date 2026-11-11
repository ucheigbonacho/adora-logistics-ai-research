"""Isolated EXP-11 deterministic reproduction; original result files are read-only.

Usage: python -m validation.reproduce_exp11 --output-dir /tmp/adora-exp11-new
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "experiments/EXP-11/network_concensus.py"
ORIGINAL = (ROOT / "experiments/EXP-11/results").resolve()

def reproduce(output_dir):
    destination = Path(output_dir).resolve()
    if destination.exists():
        raise FileExistsError("Output directory must be new; existing artifacts will not be overwritten")
    if destination == ORIGINAL or ORIGINAL in destination.parents or destination in ORIGINAL.parents:
        raise ValueError("Output must be separate from the original results directory")
    spec = importlib.util.spec_from_file_location("exp11_reproduction_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    strategies = ("eventual_consistency_stream", "distributed_quorum_gating")
    rows = [module.evaluate_distributed_consensus(profile_id, strategy)
            for profile_id in range(21000, 21300) for strategy in strategies]
    summary = []
    for strategy in strategies:
        subset = [r for r in rows if r["network_strategy"] == strategy]
        summary.append({
            "network_strategy": strategy,
            "profiles_evaluated": len(subset),
            "state_compliance_pass": sum(x["state_compliance_pass"] for x in subset),
            "duplicate_actions_executed": sum(x["duplicate_actions_executed"] for x in subset),
            "concurrency_collisions_intercepted": sum(x["concurrency_collisions_intercepted"] for x in subset),
            "network_timeout_exceptions": sum(x["network_timeout_exceptions"] for x in subset),
            "sequence_desync_errors": sum(x["synchronized_sequence_index"] != 8 for x in subset),
        })
    original_summary = json.loads((ORIGINAL / "summary.json").read_text(encoding="utf-8"))
    published = {r["network_strategy"]: r for r in original_summary}
    comparison = [{"strategy": r["network_strategy"], "new_summary": r,
                   "published_summary": published[r["network_strategy"]],
                   "matches_published_summary": r == published[r["network_strategy"]]} for r in summary]
    destination.mkdir(parents=True)
    with (destination / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "classification": "NEW_DETERMINISTIC_REPRODUCTION",
        "source_engine_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        "original_trials_sha256": hashlib.sha256((ORIGINAL / "trials.csv").read_bytes()).hexdigest(),
        "original_summary_sha256": hashlib.sha256((ORIGINAL / "summary.json").read_bytes()).hexdigest(),
        "new_trial_count": len(rows),
        "comparison": comparison,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(reproduce(parser.parse_args().output_dir), indent=2))

if __name__ == "__main__":
    main()
