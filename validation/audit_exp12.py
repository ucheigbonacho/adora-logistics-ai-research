"""Read-only EXP-12 CSV / summary reconciliation. Does not execute experiment or write evidence."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "EXP-12" / "results"
STRATEGIES = ("unbuffered_retry_stream", "volatile_pre_flight_registry", "durable_outbox_idempotent_receiver")

def audit():
    with (RESULTS / "trials.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    published = {x["delivery_strategy"]: x for x in json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))}
    keys = collections.defaultdict(list)
    for index, row in enumerate(rows, start=2):
        keys[(row["profile_id"], row["interruption_phase"], row["delivery_strategy"])].append(index)
    aggregates = {}
    for strategy in STRATEGIES:
        subset = [row for row in rows if row["delivery_strategy"] == strategy]
        aggregates[strategy] = {
            "rows": len(subset),
            "state_compliance_pass": sum(int(row["state_compliance_pass"]) for row in subset),
            "redundant_mutations_executed": sum(int(row["redundant_mutations"]) for row in subset),
            "dropped_transactions": sum(int(row["dropped_transactions"]) for row in subset),
            "published": published[strategy],
        }
    duplicates = [{"key": list(key), "record_positions_including_header": positions}
                  for key, positions in keys.items() if len(positions) > 1]
    return {"status": "UNRECONCILED_HISTORICAL_OUTPUT", "raw_rows": len(rows),
            "unique_combinations": len(keys), "duplicate_combinations": duplicates,
            "aggregates": aggregates}

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
