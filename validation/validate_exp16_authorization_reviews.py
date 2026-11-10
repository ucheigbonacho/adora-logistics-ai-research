"""EXP-16 authorization review intake validator; no inferred labels or decisions.

The original Q4 dataset contains operational outcomes, not authorization labels.
This module validates a separately reviewed authorization-label JSONL export.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

LABELS = {"authorize", "reject", "clarify"}
REQUIRED = ("case_id", "authorization_label", "reviewer_id",
            "reviewed_at", "review_evidence_ref", "label_rationale")

def validate(source):
    raw = Path(source).read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not records:
        raise ValueError("No authorization reviews supplied")
    ids = set()
    for row in records:
        if not isinstance(row, dict) or any(not row.get(field) for field in REQUIRED):
            raise ValueError("Missing independently reviewed authorization label metadata")
        if row["authorization_label"] not in LABELS:
            raise ValueError("Invalid authorization label")
        if row["case_id"] in ids:
            raise ValueError("Duplicate case ID")
        ids.add(row["case_id"])
    return {
        "classification": "EXP16_SEPARATE_AUTHORIZATION_LABEL_REVIEW_INTAKE",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "review_count": len(records),
        "labels": dict(Counter(row["authorization_label"] for row in records)),
        "scope": "Schema validation only; review authenticity and label independence require source evidence.",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    print(json.dumps(validate(parser.parse_args().source), indent=2))
