"""EXP-12 fresh deterministic reproduction; NEVER writes original experiment results.

Run from repository root:
    python -m validation.reproduce_exp12 --output-dir /tmp/adora-exp12-reproduction

Output directory must not exist; run is refused otherwise.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = (ROOT / "experiments" / "EXP-12" / "results").resolve()
ENGINE = ROOT / "experiments" / "EXP-12" / "outbox_validator.py"

def reproduce(output_dir):
    destination = Path(output_dir).resolve()
    if destination == ORIGINAL or ORIGINAL in destination.parents or destination in ORIGINAL.parents:
        raise ValueError("Output must be separate from the original EXP-12 results directory")
    if destination.exists():
        raise FileExistsError("Refusing to overwrite existing output directory")
    spec = importlib.util.spec_from_file_location("exp12_original_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [module.evaluate_outbox_profile(strategy, phase, profile_id)
            for profile_id in range(1000, 1200)
            for phase in module.PHASES for strategy in module.STRATEGIES]
    summary = []
    for strategy in module.STRATEGIES:
        subset = [r for r in rows if r["delivery_strategy"] == strategy]
        summary.append({
            "delivery_strategy": strategy,
            "profiles_evaluated": len(subset),
            "state_compliance_pass": sum(r["state_compliance_pass"] for r in subset),
            "redundant_mutations_executed": sum(r["redundant_mutations"] for r in subset),
            "dropped_transactions": sum(r["dropped_transactions"] for r in subset),
        })
    original_summary = json.loads((ORIGINAL / "summary.json").read_text(encoding="utf-8"))
    original_map = {r["delivery_strategy"]: r for r in original_summary}
    comparison = [
        {"strategy": s["delivery_strategy"], "fresh": s,
         "original_published": original_map[s["delivery_strategy"]],
         "matches_original_published": s == original_map[s["delivery_strategy"]]}
        for s in summary
    ]
    destination.mkdir(parents=True)
    with (destination / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "classification": "NEW_REPRODUCTION_NOT_HISTORICAL_EVIDENCE",
        "source_engine_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        "original_trials_sha256": hashlib.sha256((ORIGINAL / "trials.csv").read_bytes()).hexdigest(),
        "original_summary_sha256": hashlib.sha256((ORIGINAL / "summary.json").read_bytes()).hexdigest(),
        "fresh_rows": len(rows),
        "comparison": comparison,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(reproduce(args.output_dir), indent=2))

if __name__ == "__main__":
    main()
