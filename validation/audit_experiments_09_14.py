"""Read-only summary-versus-raw reconciliation for EXP-09 through EXP-14.

This utility reads existing records; it does not run experiment generators or
modify any historical file. Run: python -m validation.audit_experiments_09_14
"""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "experiments"
CONFIG = {
    "EXP-09": ("results.csv", "engine_strategy", "pass_status", None),
    "EXP-10": ("results/trials.csv", "strategy", "correct", "results/summary.json"),
    "EXP-11": ("results/trials.csv", "network_strategy", "state_compliance_pass", "results/summary.json"),
    "EXP-12": ("results/trials.csv", "delivery_strategy", "state_compliance_pass", "results/summary.json"),
    "EXP-13": ("results/http_requests.csv", None, None, "results/summary.json"),
    "EXP-14": ("results/trials.csv", "delivery_strategy", "state_compliance_pass", "results/summary.json"),
}

def audit():
    report = {}
    for exp, (raw_path, group_field, pass_field, summary_path) in CONFIG.items():
        base = ROOT / exp
        raw_file = base / raw_path
        if not raw_file.exists():
            report[exp] = {"status": "RAW_FILE_NOT_FOUND", "path": raw_path}
            continue
        with raw_file.open(newline="", encoding="utf-8-sig") as stream:
            if exp == "EXP-11":
                columns = ["profile_id", "network_strategy", "state_compliance_pass", "applied_actions", "duplicate_actions_executed", "concurrency_collisions_intercepted", "network_timeout_exceptions", "synchronized_sequence_index", "packet_acknowledgement_timeouts"]
                reader = csv.DictReader(stream, fieldnames=columns)
            else:
                reader = csv.DictReader(stream)
                columns = reader.fieldnames or []
            rows = list(reader)
        entry = {"raw_path": raw_path, "rows": len(rows), "columns": columns}
        if group_field in columns and pass_field in columns:
            groups = collections.defaultdict(lambda: {"rows": 0, "passes": 0, "invalid_pass_values": 0})
            for row in rows:
                group = groups[row[group_field]]
                group["rows"] += 1
                try:
                    group["passes"] += int(row[pass_field]) if row[pass_field] in ("0", "1") else int(row[pass_field].lower() == "true")
                except (ValueError, TypeError, AttributeError):
                    group["invalid_pass_values"] += 1
            entry["raw_aggregates"] = dict(groups)
        if summary_path:
            path = base / summary_path
            entry["published_summary"] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else "NOT_FOUND"
        report[exp] = entry
    return report

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
