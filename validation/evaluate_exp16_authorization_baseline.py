"""EXP-16 voice authorization baseline: conservative rule evaluation only.

This module does not infer ground truth. It requires a separately reviewed
authorization-label file, with independently supplied input features. The
baseline is a predeclared fail-closed rule, not a trained speech classifier.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from validation.validate_exp16_authorization_reviews import validate

LABELS = ("authorize", "reject", "clarify")
REQUIRED_FEATURES = ("case_id", "utterance", "auth_verified", "confirmation_matches", "state_fresh")

def baseline(row):
    """Only authorize a recognized explicit dispatch command with all checks true."""
    text = row["utterance"].strip().lower()
    command = text.startswith("dispatch ") and len(text) > len("dispatch ")
    if not command:
        return "clarify"
    if row["auth_verified"] is False or row["confirmation_matches"] is False:
        return "reject"
    if all(row[key] is True for key in ("auth_verified", "confirmation_matches", "state_fresh")):
        return "authorize"
    return "clarify"

def evaluate(review_source, feature_source, output_dir):
    dest = Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("Output directory already exists")
    review_summary = validate(review_source)
    review_raw = Path(review_source).read_bytes()
    feature_raw = Path(feature_source).read_bytes()
    reviews = [json.loads(line) for line in review_raw.decode("utf-8").splitlines() if line.strip()]
    features = [json.loads(line) for line in feature_raw.decode("utf-8").splitlines() if line.strip()]
    feature_map = {}
    for row in features:
        if not isinstance(row, dict) or any(key not in row for key in REQUIRED_FEATURES):
            raise ValueError("Missing required authorization input feature")
        if row["case_id"] in feature_map:
            raise ValueError("Duplicate feature case ID")
        if any(row[key] not in (True, False, None) for key in ("auth_verified", "confirmation_matches", "state_fresh")):
            raise ValueError("Authorization checks must be true, false or null")
        if not isinstance(row["utterance"], str):
            raise ValueError("Utterance must be text")
        feature_map[row["case_id"]] = row
    review_ids = {r["case_id"] for r in reviews}
    if set(feature_map) != review_ids:
        raise ValueError("Review and feature case IDs must match exactly")
    observations = []
    for review in reviews:
        row = feature_map[review["case_id"]]
        prediction = baseline(row)
        observations.append({
            "case_id": row["case_id"], "review_label": review["authorization_label"],
            "baseline": prediction, "correct": prediction == review["authorization_label"],
            "review_evidence_ref": review["review_evidence_ref"],
        })
    counts = Counter((r["review_label"], r["baseline"]) for r in observations)
    summary = {
        "classification": "EXP16_INDEPENDENT_AUTHORIZATION_BASELINE_EVALUATION",
        "review_sha256": review_summary["source_sha256"],
        "features_sha256": hashlib.sha256(feature_raw).hexdigest(),
        "total": len(observations),
        "correct": sum(row["correct"] for row in observations),
        "confusion": {f"{actual}_as_{predicted}": counts[(actual, predicted)]
                      for actual in LABELS for predicted in LABELS},
        "scope": "Deterministic conservative authorization rule; source labels and features require independent verification.",
    }
    dest.mkdir(parents=True)
    (dest / "observations.json").write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
    (dest / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", required=True)
    parser.add_argument("--features", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.reviews, args.features, args.output_dir), indent=2))
