"""Non-destructive scenario crosswalk for user-supplied logistics records.

Maps scenario families to existing experiment profiles and suggests an
operational label only where the record supports it. Does NOT infer missing
structured inputs or claim the engine executed those profiles.
"""
import json
from pathlib import Path

PROFILES = {
    "driver_speech_intelligence": ("Q1-E01", None),
    "voice_session_interruption": ("Q1-E02", {"exception": "link_disconnected"}),
    "conflicting_dispatch_constraints": ("Q2-E01", {"exception": "resource_constraint_reject"}),
    "missing_load_attributes": ("Q2-E02", {"exception": "clarification_required"}),
    "sequence_delay_detection": ("Q3-E01", None),
    "routine_transit": (None, None),
    "detention_gating": ("Q3-E02", None),
    "constraint_gating": ("Q2-E01", {"escalate": "resource_constraint_reject"}),
}
REQUIRED_INPUTS = {
    "Q1-E01": ["utterance"],
    "Q1-E02": ["connection", "pending", "confirmed"],
    "Q2-E01": ["available", "equipment_match", "hours_left", "hours_needed"],
    "Q2-E02": ["destination", "trailer_class"],
    "Q3-E01": ["eta_min", "appointment_min", "freshness_sec"],
    "Q3-E02": ["stopped_min", "scheduled_stop"],
}

def crosswalk(rows):
    output = []
    for row in rows:
        scenario = row["scenario"]
        profile, candidates = PROFILES.get(scenario, (None, None))
        candidate = candidates.get(row["expected"]) if candidates else None
        required = REQUIRED_INPUTS.get(profile, [])
        missing = [field for field in required if field not in row]
        output.append({
            "case_id": row["case_id"],
            "timestamp": row["timestamp"],
            "original_scenario": scenario,
            "original_expected": row["expected"],
            "mapped_experiment": profile,
            "proposed_existing_category": candidate,
            "mapping_status": "PROPOSED_NOT_VALIDATED" if candidate else "REQUIRES_DOMAIN_REVIEW",
            "missing_engine_inputs": missing,
            "note": "Semantic proposal only; not engine prediction or independently approved ground truth",
        })
    return output

def run(source, destination):
    rows = [json.loads(line) for line in Path(source).read_text(encoding="utf-8").splitlines() if line.strip()]
    mapped = crosswalk(rows)
    Path(destination).write_text("\n".join(json.dumps(row) for row in mapped)+"\n", encoding="utf-8")
    return mapped

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("destination")
    a = p.parse_args()
    print(json.dumps({"cases": len(run(a.source, a.destination)), "status": "PROPOSED_CROSSWALK_ONLY"}))
