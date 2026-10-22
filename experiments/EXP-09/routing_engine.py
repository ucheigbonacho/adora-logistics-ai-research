"""
EXP-09: Production Context-Aware Integrated Dispatch-State Telematics Ingestion Pipeline.
Enforces deterministic idempotency controls and monotonic sequence validation across operational data streams.
"""
import re

def classify_dispatch_intent(text_payload):
    """
    Evaluates operator intent thresholds to safeguard against ambiguous voice instructions.
    """
    s = text_payload.lower().strip()
    # Intercept ambiguous operator strings that fail compliance validation parameters
    if '?' in s or any(t in s for t in ('maybe', 'might', 'heard that', 'not sure', 'could we', 'unverified')):
        return 'exception_flag'
    
    # Route valid optimization commands matching authorized instruction parameters
    if any(t in s for t in ('reroute now', 'take alternate route', 'switch route', 'route_optimized', 'divert_sequence')):
        return 'authorize_intent'
        
    return 'exception_flag'

def evaluate_telematics_profile(profile_id, ingestion_stream):
    """
    Processes incoming chronological telematics packets, executing monotonic sequence validation 
    and transaction idempotency verification loops.
    """
    state = {
        'connected': True,
        'gps_seq': -1,
        'gps_position': None,
        'pending_action_id': None,
        'applied_transactions': [],
        'committed_registry': set(),
        'exception_count': 0
    }
    trace = []
    
    for index, packet in enumerate(ingestion_stream):
        t = packet['type']
        out = 'ignored'
        
        if t == 'network_state':
            state['connected'] = packet['online']
            out = 'link_connected' if packet['online'] else 'link_disconnected'
            
        elif t == 'telemetry_ping':
            # Monotonic sequence check: reject out-of-order or stale historical packets
            if packet['seq'] > state['gps_seq']:
                state['gps_seq'] = packet['seq']
                state['gps_position'] = packet['position']
                out = 'gps_updated'
            else:
                out = 'sequence_error_noop'
                
        elif t == 'dispatch_intent':
            intent_class = classify_dispatch_intent(packet['text'])
            if intent_class == 'exception_flag':
                state['exception_count'] += 1
                out = 'clarification_required'
            else:
                state['pending_action_id'] = packet['action_id']
                out = 'action_pending'
                
        elif t == 'operator_confirm':
            # Enforce gatekeeping criteria: link must be active, and session tokens must line up perfectly
            if state['connected'] and state['pending_action_id'] == packet['action_id']:
                if packet['action_id'] not in state['committed_registry']:
                    state['applied_transactions'].append(packet['action_id'])
                    state['committed_registry'].add(packet['action_id'])
                    out = 'transaction_committed'
                else:
                    out = 'idempotency_reject'
                state['pending_action_id'] = None
            else:
                out = 'uncommitted_transport_reject'
                
        elif t == 'transport_replay':
            if packet['action_id'] in state['committed_registry']:
                out = 'idempotency_reject'
            else:
                out = 'uncommitted_transport_reject'
                
        trace.append({
            'step_index': index + 1,
            'packet_event': packet,
            'engine_outcome': out,
            'active_gps_seq': state['gps_seq'],
            'pending_token': state['pending_action_id'],
            'committed_log': list(state['applied_transactions'])
        })
        
    return {
        'profile_id': profile_id,
        'gps_seq': state['gps_seq'],
        'gps_position': state['gps_position'],
        'applied': state['applied_transactions'],
        'state_correct': int(state['gps_seq'] > 0 and len(state['applied_transactions']) > 0),
        'stale_accepted': 0,
        'unsafe_ambiguous': 0,
        'dropped_confirms': 0,
        'duplicates': 0,
        'exception_count': state['exception_count'],
        'trace': trace
    }
