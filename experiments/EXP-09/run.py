"""
EXP-09: Production Regression Testing and Multi-Variant Gating Protocol Runner.
Validates production telematics logic state outputs against standardized regression scenarios.
"""
import csv
import json
import importlib.util
from pathlib import Path

folder = Path(__file__).resolve().parent

# Dynamically link and load the clean core routing execution asset
engine_path = folder / 'routing_engine.py'
spec = importlib.util.spec_from_file_location('routing_engine', engine_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Ingest standardized telematics scenario profiles
scenarios = [json.loads(s) for s in (folder / 'scenarios.jsonl').read_text().splitlines() if s.strip()]
rows = []
traces = []

for sc in scenarios:
    # Evaluate data layers against production strategy matrices
    for strategy_variant in ('sequence_guard', 'confirmed_idempotent'):
        # Execute the primary telematics processing loop inside your clean core engine
        result = m.evaluate_telematics_profile(sc['id'], strategy=strategy_variant)
        
        # Verify execution matrix alignment criteria
        is_state_correct = int(result['state_correct'])
        rows.append({
            'scenario_id': sc['id'],
            'description': sc['description'],
            'engine_strategy': strategy_variant,
            'pass_status': is_state_correct,
            'stale_accepted_count': result['stale_accepted'],
            'unsafe_ambiguous_count': result['unsafe_ambiguous'],
            'dropped_confirmations': result['dropped_confirms'],
            'duplicate_actions_detected': result['duplicates']
        })
        
        # Log granular system state execution tracks
        for index, item in enumerate(result['trace']):
            traces.append({
                'scenario_id': sc['id'],
                'engine_strategy': strategy_variant,
                'execution_step': index,
                'event_type': item['event'],
                'engine_outcome': item['outcome'],
                'active_gps_seq': item['gps'],
                'total_applied_actions': item['applied']
            })

# Export finalized performance telemetry reports
for name, records in [('results.csv', rows), ('event_trace.csv', traces)]:
    with (folder / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=records[0].keys())
        w.writeheader()
        w.writerows(records)

# Print execution matrix benchmarks directly to system output
for strategy_variant in ('sequence_guard', 'confirmed_idempotent'):
    selected = [x for x in rows if x['engine_strategy'] == strategy_variant]
    print(
        f"Strategy: {strategy_variant:<20} "
        f"Full State Pass: {sum(x['pass_status'] for x in selected)} / {len(selected)} "
        f"Duplicate Actions Bypassed: {sum(x['duplicate_actions_detected'] for x in selected)}"
    )
