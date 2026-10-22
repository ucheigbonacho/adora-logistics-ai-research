"""
EXP-14: Production Subprocess Interruption Isolation Worker Component.
Executes atomic telematics transaction mutation sequences under isolated runtime parameters, 
providing structural hook barriers for operating system-level process durability profiling.
"""
import sqlite3
import sys
import time
import pathlib

# Parse command line runtime parameters passing from the orchestration harness
delivery_strategy, interruption_phase, database_path, barrier_marker = sys.argv[1:]

connection = sqlite3.connect(database_path, timeout=5, isolation_level=None)
connection.execute('PRAGMA journal_mode=WAL')
connection.execute('CREATE TABLE IF NOT EXISTS actions (action_key TEXT PRIMARY KEY, status TEXT NOT NULL)')
connection.execute('CREATE TABLE IF NOT EXISTS receiver (id INTEGER PRIMARY KEY AUTOINCREMENT, action_key TEXT NOT NULL)')

# Initialize transaction token parameter boundaries
transaction_token = 'TXN-A42_DISPATCH_NOTIFY'
connection.execute('INSERT OR IGNORE INTO actions VALUES (?,?)', (transaction_token, 'pending'))

def execute_checkpoint_barrier(boundary_label):
    if interruption_phase == boundary_label:
        pathlib.Path(barrier_marker).write_text(boundary_label)
        # Block process execution path to allow orchestration harness time to issue native termination signal
        time.sleep(60)

execute_checkpoint_barrier('pre_flight_boundary')

if delivery_strategy == 'durable_outbox_idempotent_receiver':
    # Secure Quorum Gating: execute explicit receiver-side unique key constraint validation inside isolated transaction boundary
    connection.execute('BEGIN IMMEDIATE')
    connection.execute(
        'INSERT INTO receiver(action_key) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM receiver WHERE action_key=?)',
        (transaction_token, transaction_token)
    )
    connection.commit()
else:
    # Unprotected Stream Ingestion: execute blind payload entry tracking paths
    connection.execute('INSERT INTO receiver(action_key) VALUES (?)', (transaction_token,))

execute_checkpoint_barrier('post_mutation_boundary')

# Harden transaction commitment record parameters inside storage engine database layer
connection.execute("UPDATE actions SET status='TRANSACTION_ACKNOWLEDGED' WHERE action_key=?", (transaction_token,))

execute_checkpoint_barrier('post_acknowledgement_boundary')

connection.close()
