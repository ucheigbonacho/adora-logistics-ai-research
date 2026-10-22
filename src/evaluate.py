"""
Logistics Routing Engine - Telematics Evaluation Suite
Description: Processes authentic chronological production telematics records (JSONL),
             enforces context-aware routing decisions, and logs runtime metrics (CSV).
"""
import csv
import json
import time
import statistics
from pathlib import Path
from src.rules import execute_routing_decision
from src.generate import IDS

def evaluate_telematics_suite(project_root_dir):
    root_path = Path(project_root_dir)
    output_directory = root_path / 'results'
    output_directory.mkdir(exist_ok=True)
    aggregate_metrics_log = []
    
    for profile_id in IDS:
        dataset_source = root_path / 'datasets' / f'{profile_id}.jsonl'
        if not dataset_source.exists(): 
            raise FileNotFoundError(f"Missing mandatory telemetry source: {dataset_source}")
            
        telemetry_rows = [] 
        latency_records = []
        
        for line in dataset_source.read_text(encoding='utf-8').splitlines():
            if not line.strip(): 
                continue
            item = json.loads(line)
            
            # Execute precise nanosecond delta telemetry timing loop
            start_tick = time.perf_counter_ns()
            computed_state = execute_routing_decision(profile_id, item['input'])
            latency_ns = time.perf_counter_ns() - start_tick
            
            latency_records.append(latency_ns)
            
            # Map out structural execution categories based on unique project domains
            if "Q1" in profile_id:
                target_header, computed_header = "target_intent_class", "computed_intent_class"
            elif "Q2" in profile_id:
                target_header, computed_header = "target_allocation_status", "computed_allocation_status"
            elif "Q3" in profile_id:
                target_header, computed_header = "target_dwelling_state", "computed_dwelling_state"
            else:
                target_header, computed_header = "target_idempotency_state", "computed_idempotency_state"
                
            telemetry_rows.append({
                'case_id': item['case_id'],
                target_header: item['expected'],
                computed_header: computed_state,
                'pipeline_integrity_pass': int(computed_state == item['expected']),
                'latency_ns': latency_ns
            })
            
        if not telemetry_rows: 
            raise ValueError(f'Empty database ingestion profile target: {profile_id}')
            
        with (output_directory / f'{profile_id}_runs.csv').open('w', newline='', encoding='utf-8') as f:
            data_writer = csv.DictWriter(f, fieldnames=list(telemetry_rows[0].keys()))
            data_writer.writeheader()
            data_writer.writerows(telemetry_rows)
            
        compliance_pass_count = sum(r['pipeline_integrity_pass'] for r in telemetry_rows)
        validation_exceptions = sum(not r['pipeline_integrity_pass'] for r in telemetry_rows)
        integrity_rate = round(100 * compliance_pass_count / len(telemetry_rows), 2)
        
        aggregate_metrics_log.append({
            'experiment_id': profile_id,
            'cases': len(telemetry_rows),
            'state_compliance_pass': compliance_pass_count,
            'sync_validation_exceptions': validation_exceptions,
            'pipeline_integrity_rate': integrity_rate,
            'median_latency_ns': round(statistics.median(latency_records))
        })
        
    with (output_directory / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        summary_writer = csv.DictWriter(f, fieldnames=list(aggregate_metrics_log[0].keys()))
        summary_writer.writeheader()
        summary_writer.writerows(aggregate_metrics_log)
        
    return aggregate_metrics_log

if __name__ == '__main__':
    inferred_root = Path(__file__).resolve().parents[1]
    for metric_profile in evaluate_telematics_suite(inferred_root): 
        print(metric_profile)
