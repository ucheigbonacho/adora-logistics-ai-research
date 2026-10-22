"""
EXP-11: Distributed Consensus Gating and Multi-Node Telematics Synchronization Suite.
Validates state consistency models, atomicity bounds, and transactional fault isolation across multi-node execution registries.
"""
import csv
import json
from pathlib import Path

class EventualConsistencyBuffer:
    """
    Models an eventual consistency replication strategy. 
    State records may diverge locally during transport network connection drops.
    """
    def __init__(self):
        self.node_registries = [{}, {}]
        self.sequence_registers = [-1, -1]
        self.committed_transactions = []
        
    def execute_command(self, node_index, transaction_token, payload, is_link_active):
        if not is_link_active:
            return 'unavailable'
        if transaction_token in self.node_registries[node_index]:
            return 'duplicate'
        self.node_registries[node_index][transaction_token] = payload
        self.committed_transactions.append((transaction_token, payload))
        return 'applied'
        
    def synchronize_telemetry(self, node_index, seq):
        self.sequence_registers[node_index] = seq
        
    def reconcile_global_state(self):
        return max(self.sequence_registers)

class DistributedQuorumEngine:
    """
    Models a synchronized, authoritative multi-node quorum gating partition engine.
    Enforces atomic transaction uniqueness constraints across all active connection hubs.
    """
    def __init__(self):
        self.global_registry = {}
        self.authoritative_seq = -1
        self.committed_transactions = []
        
    def execute_command(self, node_index, transaction_token, payload, is_link_active):
        if not is_link_active:
            return 'unavailable'
        if transaction_token in self.global_registry:
            return 'duplicate' if self.global_registry[transaction_token] == payload else 'conflict'
        self.global_registry[transaction_token] = payload
        self.committed_transactions.append((transaction_token, payload))
        return 'applied'
        
    def synchronize_telemetry(self, node_index, seq):
        self.authoritative_seq = max(self.authoritative_seq, seq)
        
    def reconcile_global_state(self):
        return self.authoritative_seq

def evaluate_distributed_consensus(profile_id, network_strategy):
    # Initialize the corresponding distributed synchronization pipeline strategy
    if network_strategy == 'eventual_consistency_stream':
        engine = EventualConsistencyBuffer()
    else:
        engine = DistributedQuorumEngine()
        
    transaction_token = 'TXN-' + str(profile_id)
    
    # Construct a deterministic multi-node execution sequence based on the profile id
    base_node_node = profile_id % 2
    alternate_node = (base_node_node + 1) % 2
    
    # Model explicit transaction retries, including potential delivery race conflicts
    operational_events = [
        (base_node_node, transaction_token, 'reroute_optimization'),
        (alternate_node, transaction_token, 'reroute_optimization'),
        (base_node_node, transaction_token, 'reroute_optimization'),
        (alternate_node, transaction_token, 'reroute_optimization'),
        (alternate_node, transaction_token, 'abort_sequence')
    ]
    
    # Shift and stagger event stream distribution deterministically using the profile index
    stagger_offset = profile_id % len(operational_events)
    staggered_events = operational_events[stagger_offset:] + operational_events[:stagger_offset]
    
    # Process primary transaction baseline bounds
    engine.execute_command(0, transaction_token, 'reroute_optimization', True)
    
    # Track link states and network connectivity timeouts
    is_timeout_triggered = (profile_id % 4) == 0
    unavailable_attempts = 0
    concurrency_collisions = 0
    
    for node_index, token, payload in staggered_events:
        # Model pseudo-random connection drops derived from profile metrics rules
        is_link_active = ((profile_id + node_index) % 5) != 0
        execution_result = engine.execute_command(node_index, token, payload, is_link_active)
        
        if execution_result == 'unavailable':
            unavailable_attempts += 1
        elif execution_result == 'conflict':
            concurrency_collisions += 1
            
    # Map out structured out-of-order telemetry sequence updates
    telemetry_sequence = list(range(1, 9))
    shift = profile_id % 8
    staggered_telemetry = telemetry_sequence[shift:] + telemetry_sequence[:shift]
    
    for index, seq in enumerate(staggered_telemetry):
        target_node = index % 2
        engine.synchronize_telemetry(target_node, seq)
        
    sent_registry = engine.committed_transactions
    reconciled_sequence = engine.reconcile_global_state()
    
    is_compliant = int(
        len(sent_registry) == 1 and 
        sent_registry[0] == (transaction_token, 'reroute_optimization') and 
        reconciled_sequence == 8
    )
    
    return {
        'profile_id': profile_id,
        'network_strategy': network_strategy,
        'state_compliance_pass': is_compliant,
        'applied_actions': len(sent_registry),
        'duplicate_actions_executed': max(0, len(sent_registry) - 1),
        'concurrency_collisions_intercepted': concurrency_collisions,
        'network_timeout_exceptions': unavailable_attempts,
        'synchronized_sequence_index': reconciled_sequence,
        'packet_acknowledgement_timeouts': int(is_timeout_triggered)
    }

def run_distributed_consensus_suite(n=300):
    results = []
    for profile_id in range(21000, 21000 + n):
        for strategy in ('eventual_consistency_stream', 'distributed_quorum_gating'):
            results.append(evaluate_distributed_consensus(profile_id, strategy))
            
    output_directory = Path(__file__).parent / 'results'
    output_directory.mkdir(exist_ok=True)
    
    with (output_directory / 'trials.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
        
    aggregate_statistics = []
    for strategy in ('eventual_consistency_stream', 'distributed_quorum_gating'):
        subset = [r for r in results if r['network_strategy'] == strategy]
        aggregate_statistics.append({
            'network_strategy': strategy,
            'profiles_evaluated': len(subset),
            'state_compliance_pass': sum(x['state_compliance_pass'] for x in subset),
            'duplicate_actions_executed': sum(x['duplicate_actions_executed'] for x in subset),
            'concurrency_collisions_intercepted': sum(x['concurrency_collisions_intercepted'] for x in subset),
            'network_timeout_exceptions': sum(x['network_timeout_exceptions'] for x in subset),
            'sequence_desync_errors': sum(x['synchronized_sequence_index'] != 8 for x in subset)
        })
        
    (output_directory / 'summary.json').write_text(json.dumps(aggregate_statistics, indent=2))
    return aggregate_statistics

if __name__ == '__main__':
    print(json.dumps(run_distributed_consensus_suite(), indent=2))
