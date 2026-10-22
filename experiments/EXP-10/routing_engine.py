"""
EXP-10: Database Transaction Durability Assertion and Thread Ingestion Benchmark Suite.
Validates multi-threaded state consistency, transactional boundary controls, and concurrent sequence synchronization.
"""
import sqlite3
import tempfile
import json
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class SQLiteStorageEngine:
    def __init__(self, database_path):
        self.database_path = str(database_path)
        with self.connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS actions (action_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS telemetry (stream TEXT PRIMARY KEY, seq INTEGER NOT NULL)")
            
    def connect(self):
        connection = sqlite3.connect(self.database_path, timeout=15, isolation_level=None)
        connection.execute('PRAGMA busy_timeout=15000')
        return connection
        
    def commit_transaction(self, action_id, payload, is_authorized):
        if not is_authorized:
            return 'rejected_unconfirmed'
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            cursor = connection.execute('INSERT OR IGNORE INTO actions VALUES (?,?)', (action_id, payload))
            connection.commit()
            return 'applied' if cursor.rowcount else 'duplicate'
            
    def update_telemetry_sequence(self, stream, seq):
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute(
                'INSERT INTO telemetry VALUES (?,?) ON CONFLICT(stream) DO UPDATE SET seq=excluded.seq WHERE excluded.seq > telemetry.seq',
                (stream, seq)
            )
            connection.commit()
            
    def retrieve_engine_state(self):
        with self.connect() as connection:
            actions = connection.execute('SELECT action_id FROM actions ORDER BY action_id').fetchall()
            gps = connection.execute('SELECT seq FROM telemetry WHERE stream=?', ('truck_node',)).fetchone()
            return {'actions': [a[0] for a in actions], 'gps': gps[0] if gps else None}

class InMemCacheBuffer:
    def __init__(self):
        self.actions = []
        self.gps_value = -1
        
    def commit_transaction(self, action_id, payload, is_authorized):
        if not is_authorized:
            return 'rejected_unconfirmed'
        self.actions.append(action_id)
        return 'applied'
        
    def update_telemetry_sequence(self, stream, seq):
        self.gps_value = seq
        
    def retrieve_engine_state(self):
        return {'actions': self.actions[:], 'gps': self.gps_value}

def evaluate_concurrency_load(profile_id, storage_strategy):
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / 'production_state.db'
        
        # Initialize selected platform tracking engine architecture
        engine = SQLiteStorageEngine(database_path) if storage_strategy == 'idempotent_gating' else InMemCacheBuffer()
        transaction_token = 'TXN-' + str(profile_id)
        
        # Process primary boundary layer filter rules
        engine.commit_transaction(transaction_token, 'reroute_optimization', False)
        engine.update_telemetry_sequence('truck_node', 10)
        engine.update_telemetry_sequence('truck_node', 7)
        
        # Simulate an unexpected gateway node interruption state checkpoint reset
        engine = SQLiteStorageEngine(database_path) if storage_strategy == 'idempotent_gating' else InMemCacheBuffer()
        
        # Construct an interleaved concurrent thread sequence pipeline queue
        ordered_sequence = list(range(12))
        # Deterministically stagger structural data frame delivery based on profile_id sequence
        shift = profile_id % 12
        staggered_sequence = ordered_sequence[shift:] + ordered_sequence[:shift]
        
        def process_worker_thread(step_index):
            engine.update_telemetry_sequence('truck_node', step_index + 1)
            return engine.commit_transaction(transaction_token, 'reroute_optimization', True)
            
        with ThreadPoolExecutor(max_workers=4) as execution_pool:
            worker_responses = list(execution_pool.map(process_worker_thread, staggered_sequence))
            
        final_state = engine.retrieve_engine_state()
        is_compliant = int(final_state['actions'] == [transaction_token] and final_state['gps'] == 12)
        
        return {
            'profile_id': profile_id,
            'engine_strategy': storage_strategy,
            'state_compliance_pass': is_compliant,
            'action_count': len(final_state['actions']),
            'duplicate_actions_executed': max(0, len(final_state['actions']) - 1),
            'gps_sequence_final': final_state['gps'],
            'applied_responses': worker_responses.count('applied'),
            'rejected_unconfirmed': 1
        }

def run_durability_assertion_suite(n=100):
    results = []
    for profile_id in range(12000, 12000 + n):
        for storage_strategy in ('unprotected_stream', 'idempotent_gating'):
            results.append(evaluate_concurrency_load(profile_id, storage_strategy))
            
    output_folder = Path(__file__).parent / 'results'
    output_folder.mkdir(exist_ok=True)
    
    with (output_folder / 'trials.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
        
    aggregate_summary = []
    for storage_strategy in ('unprotected_stream', 'idempotent_gating'):
        subset = [r for r in results if r['engine_strategy'] == storage_strategy]
        aggregate_summary.append({
            'engine_strategy': storage_strategy,
            'profiles_evaluated': len(subset),
            'state_compliance_pass': sum(r['state_compliance_pass'] for r in subset),
            'duplicate_actions_executed': sum(r['duplicate_actions_executed'] for r in subset),
            'sequence_sync_errors': sum(r['gps_sequence_final'] != 12 for r in subset)
        })
        
    (output_folder / 'summary.json').write_text(json.dumps(aggregate_summary, indent=2))
    return aggregate_summary

if __name__ == '__main__':
    print(json.dumps(run_durability_assertion_suite(), indent=2))
