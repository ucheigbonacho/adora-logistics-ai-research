"""Run EXP-14 subprocess interruption tests with fresh outputs only.

Usage: python -m validation.reproduce_exp14 --output-dir /tmp/adora-exp14-new
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "experiments/EXP-14/run.py"
ORIGINAL = (ROOT / "experiments/EXP-14/results").resolve()

def reproduce(output_dir, repetitions=3):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    if dest == ORIGINAL or ORIGINAL in dest.parents or dest in ORIGINAL.parents:
        raise ValueError("Output directory must be separate from original results")
    spec = importlib.util.spec_from_file_location("exp14_isolated_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [module.evaluate_process_interruption(strategy, phase, index)
            for strategy in module.MODES for phase in module.PHASES for index in range(repetitions)]
    groups = {}
    for strategy in module.MODES:
        for phase in module.PHASES:
            subset = [r for r in rows if r["delivery_strategy"] == strategy and r["interruption_phase"] == phase]
            groups[f"{strategy}/{phase}"] = {
                "profiles_evaluated": len(subset),
                "state_compliance_pass": sum(r["state_compliance_pass"] == "True" for r in subset),
                "redundant_mutations_executed": sum(r["redundant_mutations_executed"] for r in subset),
                "dropped_transactions": sum(r["dropped_transactions"] for r in subset),
            }
    dest.mkdir(parents=True)
    with (dest / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    published = json.loads((ORIGINAL / "summary.json").read_text(encoding="utf-8"))
    manifest = {
        "classification": "NEW_EXP14_SUBPROCESS_REPRODUCTION",
        "fresh_trial_count": len(rows),
        "source_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        "worker_sha256": hashlib.sha256((ENGINE.parent / "worker.py").read_bytes()).hexdigest(),
        "original_trials_sha256": hashlib.sha256((ORIGINAL / "trials.csv").read_bytes()).hexdigest(),
        "original_summary_sha256": hashlib.sha256((ORIGINAL / "summary.json").read_bytes()).hexdigest(),
        "fresh_groups": groups,
        "published_groups": published["evaluation_strategy_groups"],
        "groups_match_published": groups == published["evaluation_strategy_groups"],
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output_dir), indent=2))
