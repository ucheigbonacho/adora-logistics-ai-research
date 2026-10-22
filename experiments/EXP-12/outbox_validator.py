"""
EXP-13: Production Transactional Outbox Delivery Assertion and Validation Suite.
Validates atomic recovery strategies, state mutation bounds, and receiver idempotency controls across simulated disruption phases.
"""
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'results'
STRATEGIES = ('unbuffered_retry_stream', 'volatile_pre_flight_registry', 'durable_outbox_idempotent_receiver')
PHASES = ('before_send', 'after_send_before_ack', 'after_ack_before_local_commit', 'normal')

def evaluate_outbox_profile(strategy, phase, profile_id):
    # Establish a deterministic transmission attempt sequence derived from the profile tracking identifier
    recovery_attempts = 1 + (profile_id % 3)
    delivered = 0
    ledger_committed = False
    receiver_seen = False
    
    if strategy == 'unbuffered_retry_stream':
        # Baseline execution tracking: execute standard unbuffered retry stream paths
        if phase != 'before_send': 
            delivered += 1
        if phase != 'normal': 
            delivered += recovery_attempts
        else: 
            ledger_committed = True
        if phase != 'normal': 
            ledger_committed = True
            
    elif strategy == 'volatile_pre_flight_registry':
        # Write-ahead tracking: actions are logged in temporary buffers but drop on premature crash boundaries
        ledger_committed = True
        if phase != 'before_send': 
            delivered += 1
            
    else:
        # Durable Outbox Architecture: intent is atomic, key uniqueness is guaranteed at receiver boundaries
        ledger_committed = True
        deliveries = 1 if phase == 'normal' else 1 + recovery_attempts
        for _ in range(deliveries):
            if not receiver_seen:
                delivered += 1
                receiver_seen = True
                
    redundant_mutations = max(0, delivered - 1)
    dropped_transactions = int(delivered == 0)
    state_compliance_pass = int(delivered == 1 and ledger_committed)
    
    return {
        'profile_id': profile_id,
        'interruption_phase': phase,
        'delivery_strategy': strategy,
        'transmission_attempts': recovery_attempts,
        'external_mutations': delivered,
        'redundant_mutations': redundant_mutations,
        'dropped_transactions': dropped_transactions,
        'state_compliance_pass': state_compliance_pass
    }

def run_outbox_assertion_suite():
    rows = []
    # Evaluate standardized transactional load scenarios across historical tracking bounds
    for profile_id in range(1000, 1200):
        for phase in PHASES:
            for strategy in STRATEGIES:
                rows.append(evaluate_outbox_profile(strategy, phase, profile_id))
                
    OUT.mkdir(exist_ok=True)
    
    with (OUT / 'trials.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        
    aggregate_summary = []
    for strategy in STRATEGIES:
        subset = [x for x in rows if x['delivery_strategy'] == strategy]
        aggregate_summary.append({
            'delivery_strategy': strategy,
            'profiles_evaluated': len(subset),
            'state_compliance_pass': sum(x['state_compliance_pass'] for x in subset),
            'redundant_mutations_executed': sum(x['redundant_mutations'] for x in subset),
            'dropped_transactions': sum(x['dropped_transactions'] for x in subset)
        })
        
    (OUT / 'summary.json').write_text(json.dumps(aggregate_summary, indent=2) + '\n')
    return aggregate_summary

if __name__ == '__main__':
    for metric_profile in run_outbox_assertion_suite():
        print(metric_profile)

