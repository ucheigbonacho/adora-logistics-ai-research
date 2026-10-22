"""
EXP-13: Production High-Concurrency API Ingestion Integration Test Suite.
Validates multi-threaded request processing layers, socket connection drop recovery, 
and atomic transactional boundary idempotency keys over persistent database runtimes.
"""
import csv
import json
import sqlite3
import tempfile
import threading
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from server import Receiver

def initialize_active_gateway_node(database_path):
    server = Receiver(('127.0.0.1', 0), database_path)
    worker_thread = threading.Thread(target=server.serve_forever, daemon=True)
    worker_thread.start()
    return server, worker_thread

def transmit_api_payload(port, transaction_token, operational_payload):
    data_payload = json.dumps({'action_key': transaction_token, 'payload': operational_payload}).encode()
    request_client = urllib.request.Request(
        f'http://127.0.0.1:{port}/actions', 
        data=data_payload, 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    try:
        with urllib.request.urlopen(request_client, timeout=10) as response_stream:
            return response_stream.status, json.load(response_stream)['status']
    except urllib.error.HTTPError as network_exception:
        return network_exception.code, json.load(network_exception)['status']

def main():
    telemetry_rows = []
    with tempfile.TemporaryDirectory() as production_env_dir:
        database_path = Path(production_env_dir) / 'production_ingestion_store.sqlite3'
        gateway_node, background_thread = initialize_active_gateway_node(database_path)
        active_port = gateway_node.server_address[1]
        
        try:
            with ThreadPoolExecutor(max_workers=12) as execution_pool:
                async_tasks = []
                for i in range(50):
                    token_id = f'TXN-A{i:02}'
                    structured_payload = {'route_optimization_profile': f'PROFILE_MATRIX_{i:02}'}
                    for transmission_index in range(3):
                        async_tasks.append((
                            token_id, 
                            f'retry_{transmission_index}', 
                            execution_pool.submit(transmit_api_payload, active_port, token_id, structured_payload)
                        ))
                for token_id, retry_label, task_promise in async_tasks:
                    http_code, engine_status = task_promise.result()
                    telemetry_rows.append({
                        'session_phase': 'concurrent_processing',
                        'transaction_token': token_id,
                        'transmission_index': retry_label,
                        'http_status': http_code,
                        'engine_outcome': engine_status
                    })
                    
            # Model network packet confirmation drops: process initial transmission and trace subsequent recovery retries
            timeout_token = 'TXN-A99_TIMEOUT'
            timeout_payload = {'route_optimization_profile': 'PROFILE_TIMEOUT_RECOVERY'}
            
            http_code, engine_status = transmit_api_payload(active_port, timeout_token, timeout_payload)
            telemetry_rows.append({
                'session_phase': 'network_timeout_initial', 'transaction_token': timeout_token,
                'transmission_index': 'retry_0', 'http_status': http_code, 'engine_outcome': engine_status
            })
            
            http_code, engine_status = transmit_api_payload(active_port, timeout_token, timeout_payload)
            telemetry_rows.append({
                'session_phase': 'network_timeout_retry', 'transaction_token': timeout_token,
                'transmission_index': 'retry_1', 'http_status': http_code, 'engine_outcome': engine_status
            })
            
        finally:
            gateway_node.shutdown()
            gateway_node.server_close()
            background_thread.join()
            
        # Re-initialize the active gateway node instance, leveraging the identical persistent data runtime store
        gateway_node, background_thread = initialize_active_gateway_node(database_path)
        active_port = gateway_node.server_address[1]
        
        try:
            for i in range(50):
                token_id = f'TXN-A{i:02}'
                structured_payload = {'route_optimization_profile': f'PROFILE_MATRIX_{i:02}'}
                http_code, engine_status = transmit_api_payload(active_port, token_id, structured_payload)
                telemetry_rows.append({
                    'session_phase': 'post_recovery_replay', 'transaction_token': token_id,
                    'transmission_index': 'retry_3', 'http_status': http_code, 'engine_outcome': engine_status
                })
                
            collision_token = 'TXN-A00'
            collision_payload = {'route_optimization_profile': 'MUTATION_COLLISION_ABORT_OVERWRITE'}
            http_code, engine_status = transmit_api_payload(active_port, collision_token, collision_payload)
            telemetry_rows.append({
                'session_phase': 'payload_collision_check', 'transaction_token': collision_token,
                'transmission_index': 'retry_4', 'http_status': http_code, 'engine_outcome': engine_status
            })
            
        finally:
            gateway_node.shutdown()
            gateway_node.server_close()
            background_thread.join()
            
        with sqlite3.connect(database_path) as storage_connection:
            isolated_sessions = storage_connection.execute('SELECT COUNT(*) FROM actions').fetchone()[0]
            concurrency_override_errors = storage_connection.execute(
                "SELECT COUNT(*) FROM actions WHERE key='TXN-A00' AND payload!=?",
                (json.dumps({'route_optimization_profile': 'PROFILE_MATRIX_00'}, sort_keys=True),)
            ).fetchone()[0]
            
    output_directory = Path(__file__).parent / 'results'
    output_directory.mkdir(exist_ok=True)
    
    with (output_directory / 'http_requests.csv').open('w', newline='') as csv_file:
        data_writer = csv.DictWriter(csv_file, fieldnames=list(telemetry_rows[0].keys()))
        data_writer.writeheader()
        data_writer.writerows(telemetry_rows)
        
    outcome_metrics = {
        status: sum(r['engine_outcome'] == status for r in telemetry_rows) 
        for status in sorted(set(r['engine_outcome'] for r in telemetry_rows))
    }
    
    state_integrity_pass = (
        isolated_sessions == 51 and 
        concurrency_override_errors == 0 and 
        outcome_metrics.get('TRANSACTION_COMMITTED') == 51 and 
        outcome_metrics.get('IDEMPOTENCY_FILTER_MATCH') == 151 and 
        outcome_metrics.get('MUTATION_COLLISION_ABORT') == 1
    )
    
    final_analytics_summary = {
        'total_http_requests_ingested': len(telemetry_rows),
        'isolated_sessions_committed': isolated_sessions,
        'concurrency_override_sync_errors': concurrency_override_errors,
        'api_endpoint_outcomes': outcome_metrics,
        'state_integrity_pass': state_integrity_pass
    }
    
    (output_directory / 'summary.json').write_text(json.dumps(final_analytics_summary, indent=2))
    print(json.dumps(final_analytics_summary, indent=2))
    assert final_analytics_summary['state_integrity_pass']

if __name__ == '__main__':
    main()
