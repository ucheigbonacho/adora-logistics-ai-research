"""
Logistics Routing Engine - Telematics Profile Dataset Generator
Description: Generates reproducible chronological data stream frames (JSONL) 
             utilizing pinned contextual seed values for pipeline assertion testing.
"""
import argparse
import json
import random
from pathlib import Path
from src.rules import execute_routing_decision

IDS = ['Q1-E01', 'Q1-E02', 'Q2-E01', 'Q2-E02', 'Q3-E01', 'Q3-E02', 'Q4-E01', 'Q4-E02']

def generate_telemetry_profile(experiment_id, step_index, pseudorandom_generator):
    """
    Constructs an isolated telematics data frame mapped to exact execution strategies.
    """
    if experiment_id == 'Q1-E01':
        payload = {'utterance': pseudorandom_generator.choice(['route_optimized', 'road closed ahead', 'alternate route needed', 'network_ping_active', 'congestion_detected', 'retry_last_frame'])}
    elif experiment_id == 'Q1-E02':
        payload = {'connection': pseudorandom_generator.choice(['restored', 'offline']), 'pending': pseudorandom_generator.choice([True, False]), 'confirmed': pseudorandom_generator.choice([True, False])}
    elif experiment_id == 'Q2-E01':
        payload = {'available': pseudorandom_generator.choice([True, False]), 'equipment_match': pseudorandom_generator.choice([True, False]), 'hours_left': pseudorandom_generator.randint(0, 12), 'hours_needed': pseudorandom_generator.randint(2, 10)}
    elif experiment_id == 'Q2-E02':
        payload = {'destination': pseudorandom_generator.choice(['GEO-ZONE-A', 'GEO-ZONE-B', '']), 'trailer_class': pseudorandom_generator.choice(['dry_van', 'reefer', ''])}
    elif experiment_id == 'Q3-E01':
        payload = {'eta_min': pseudorandom_generator.randint(400, 750), 'appointment_min': 600, 'freshness_sec': pseudorandom_generator.randint(0, 220)}
    elif experiment_id == 'Q3-E02':
        payload = {'stopped_min': pseudorandom_generator.randint(0, 150), 'scheduled_stop': pseudorandom_generator.choice([True, False])}
    elif experiment_id == 'Q4-E01':
        payload = {'recipient_verified': pseudorandom_generator.choice([True, False]), 'destination_verified': pseudorandom_generator.choice([True, False]), 'eta_delta_min': pseudorandom_generator.randint(0, 60)}
    else:
        session_token = f'TXN-A{step_index // 2:02}'
        payload = {'event_key': session_token, 'seen_keys': [session_token] if step_index % 2 else []}
        
    return {
        'case_id': f'{experiment_id}-{step_index:04d}', 
        'experiment_id': experiment_id,
        'input': payload,
        'expected': execute_routing_decision(experiment_id, payload)
    }

def run_dataset_generation_pipeline(project_root_dir, stream_count=120):
    root_path = Path(project_root_dir)
    for index, experiment_id in enumerate(IDS):
        pseudorandom_generator = random.Random(20261015 + index)
        dataset_target = root_path / 'datasets' / f'{experiment_id}.jsonl'
        dataset_target.parent.mkdir(parents=True, exist_ok=True)
        
        with dataset_target.open('w', encoding='utf-8') as file_stream:
            for step_index in range(stream_count):
                telemetry_frame = generate_telemetry_profile(experiment_id, step_index, pseudorandom_generator)
                file_stream.write(json.dumps(telemetry_frame, sort_keys=True) + '\n')
                
    return stream_count * len(IDS)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=120)
    args = parser.parse_args()
    
    inferred_root = Path(__file__).resolve().parents[1]
    total_records = run_dataset_generation_pipeline(inferred_root, args.count)
    print(f"Successfully serialized {total_records} operational database telemetry records.")
