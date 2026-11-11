"""Isolated current-code EXP-09 scenario comparison.

Usage: python -m validation.reproduce_exp09 --output-dir /tmp/adora-exp09-new
Preserves the original scenarios, historical results and source code.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "experiments/EXP-09"
SOURCE = FOLDER / "routing_engine.py"
SCENARIOS = FOLDER / "scenarios.jsonl"

def reproduce(output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    if dest == FOLDER.resolve() or FOLDER.resolve() in dest.parents or dest in FOLDER.resolve().parents:
        raise ValueError("Output directory must be separate from original experiment")
    spec = importlib.util.spec_from_file_location("exp09_current_engine", SOURCE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    scenarios = [json.loads(line) for line in SCENARIOS.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for scenario in scenarios:
        actual = engine.evaluate_telematics_profile(scenario["id"], scenario["events"])
        expected = scenario["expected"]
        checks = {
            "gps_seq": actual["gps_seq"] == expected["gps_seq"],
            "gps_position": actual["gps_position"] == expected["gps_position"],
            "applied": actual["applied"] == expected["applied"],
            "exception_flag": actual["exception_count"] == expected["exception_flag"],
        }
        rows.append({
            "scenario_id": scenario["id"],
            "current_code_matches_historical_expectation": all(checks.values()),
            "field_checks": checks,
            "expected": expected,
            "actual": {k: actual[k] for k in ("gps_seq", "gps_position", "applied", "exception_count")},
        })
    dest.mkdir(parents=True)
    with (dest / "scenario_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("scenario_id", "current_code_matches_historical_expectation", "mismatched_fields"))
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "scenario_id": row["scenario_id"],
                "current_code_matches_historical_expectation": row["current_code_matches_historical_expectation"],
                "mismatched_fields": ";".join(k for k, v in row["field_checks"].items() if not v),
            })
    (dest / "scenario_comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "classification": "NEW_EXP09_CURRENT_CODE_SCENARIO_COMPARISON",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "scenario_sha256": hashlib.sha256(SCENARIOS.read_bytes()).hexdigest(),
        "original_results_sha256": hashlib.sha256((FOLDER / "results.csv").read_bytes()).hexdigest(),
        "scenarios": len(rows),
        "matches": sum(row["current_code_matches_historical_expectation"] for row in rows),
        "mismatches": [row["scenario_id"] for row in rows if not row["current_code_matches_historical_expectation"]],
        "note": "Current fail-closed authorization rules may differ from historical expected actions; do not alter historical expectations.",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(reproduce(parser.parse_args().output_dir), indent=2))
