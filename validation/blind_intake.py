"""Read-only blind Q1-E01 intake preflight. Metadata is self-declared."""
import argparse
import hashlib
import json
from pathlib import Path

LABELS = {"informational_report", "route_proposal_requested", "clarification_required",
          "execution_request_pending_authorization", "execution_authorized"}
DEVELOPMENT = {"road closed ahead", "please find another road", "can you hear me",
               "i heard the road is closed?", "alternate route", "route may be blocked"}
REQUIRED = ("id", "experiment_id", "input", "expected", "reviewer",
            "reviewed_at", "reference", "ontology_version",
            "source_reference", "review_method", "approval_reference")

def normalize(text):
    return " ".join(text.casefold().split())

def validate(path):
    data = Path(path).read_bytes()
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    errors, ids, utterances = [], set(), set()
    if not rows:
        errors.append("no cases supplied")
    for i, row in enumerate(rows, 1):
        prefix = f"row {i}"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: not an object")
            continue
        missing = [k for k in REQUIRED if k not in row]
        if missing:
            errors.append(f"{prefix}: missing {', '.join(missing)}")
            continue
        if any(not isinstance(row[k], str) or not row[k].strip()
               for k in REQUIRED if k != "input"):
            errors.append(f"{prefix}: invalid metadata")
            continue
        if row["id"] in ids:
            errors.append(f"{prefix}: duplicate case ID")
        ids.add(row["id"])
        if row["experiment_id"] != "Q1-E01":
            errors.append(f"{prefix}: wrong experiment")
        if row["expected"] not in LABELS:
            errors.append(f"{prefix}: unrecognized label")
        payload = row["input"]
        if not isinstance(payload, dict) or not isinstance(payload.get("utterance"), str) or not payload["utterance"].strip():
            errors.append(f"{prefix}: invalid utterance")
            continue
        utterance = normalize(payload["utterance"])
        if utterance in DEVELOPMENT:
            errors.append(f"{prefix}: development-set overlap")
        if utterance in utterances:
            errors.append(f"{prefix}: duplicate utterance")
        utterances.add(utterance)
        if row.get("review_verified") is not True:
            errors.append(f"{prefix}: review verification not asserted")
    return {"status": "INTAKE_ONLY_NOT_AUTHENTICITY_VERIFICATION",
            "input_sha256": hashlib.sha256(data).hexdigest(),
            "cases": len(rows), "passes_structural_checks": not errors,
            "errors": errors}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl")
    args = parser.parse_args()
    print(json.dumps(validate(args.jsonl), indent=2))
