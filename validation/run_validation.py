"""
Logistics Routing Engine - Telematics Strategy Comparative Evaluation Suite
Description: Recomputes cross-strategy baseline vs production measurements, 
             validating algorithmic compliance and pipeline integrity constraints.
"""
import csv
import json
from pathlib import Path
from validation.baseline import execute_baseline_routing_decision
from src.rules import execute_routing_decision

def run_strategy_cross_evaluation():
    root_path = Path(__file__).resolve().parent
    profile_source = root_path / 'independent_cases.jsonl'
    
    if not profile_source.exists():
        raise FileNotFoundError(f"Missing mandatory validation source: {profile_source}")
        
    profile_cases = [json.loads(x) for x in profile_source.read_text(encoding='utf-8').splitlines() if x.strip()]
    telemetry_rows = [] 
    aggregate_totals = {}
    
    for case in profile_cases:
        experiment_id = case['experiment_id'] if 'experiment_id' in case else case['experiment']
        record_payload = case['input']
        target_state = case['expected']
        
        # Execute decision paths against independent baseline and production architectures
        baseline_state = execute_baseline_routing_decision(experiment_id, record_payload)
        production_state = execute_routing_decision(experiment_id, record_payload)
        
        is_baseline_compliant = int(baseline_state == target_state)
        is_production_compliant = int(production_state == target_state)
        
        telemetry_rows.append({
            'experiment_id': experiment_id,
            'profile_id': case['id'],
            'input': json.dumps(record_payload, sort_keys=True),
            'target_pipeline_state': target_state,
            'computed_baseline_state': baseline_state,
            'computed_production_state': production_state,
            'baseline_integrity_pass': is_baseline_compliant,
            'production_integrity_pass': is_production_compliant
        })
        
        tracker = aggregate_totals.setdefault(experiment_id, [0, 0, 0])
        tracker[0] += 1
        tracker[1] += is_baseline_compliant
        tracker[2] += is_production_compliant

    # Serialize structured verification datasets
    with (root_path / 'case_results.csv').open('w', newline='', encoding='utf-8') as f:
        data_writer = csv.DictWriter(f, fieldnames=list(telemetry_rows[0].keys()))
        data_writer.writeheader()
        data_writer.writerows(telemetry_rows)
        
    # Serialize high-level strategic summary matrices
    with (root_path / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        summary_writer = csv.writer(f)
        summary_writer.writerow([
            'experiment_id', 'cases', 'baseline_compliance_pass', 
            'production_compliance_pass', 'baseline_integrity_rate', 'production_integrity_rate'
        ])
        for exp_id, (total_cnt, baseline_pass, production_pass) in sorted(aggregate_totals.items()):
            summary_writer.writerow([
                exp_id, total_cnt, baseline_pass, production_pass,
                round(100 * baseline_pass / total_cnt, 1),
                round(100 * production_pass / total_cnt, 1)
            ])
            
    print(f"Processed {len(telemetry_rows)} profiles. Baseline Pass: {sum(x['baseline_integrity_pass'] for x in telemetry_rows)} | Production Pass: {sum(x['production_integrity_pass'] for x in telemetry_rows)}")

if __name__ == '__main__':
    run_strategy_cross_evaluation()
