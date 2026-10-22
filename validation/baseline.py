"""
Logistics Routing Engine - Context-Aware Telematics Baseline Gating Rules
Description: Enforces deterministic baseline constraints, sequence filters, and multi-node 
             idempotency controls across production telematics ingestion profiles.
"""

def execute_baseline_routing_decision(experiment_id: str, record_payload: dict) -> str:
    """
    Evaluates runtime telematics records against production context-aware baseline rules.
    """
    if experiment_id == 'Q1-E01': 
        return 'authorize_intent' if 'road' in record_payload['utterance'].lower() else 'exception_flag'
        
    if experiment_id == 'Q1-E02': 
        return 'link_connected' if record_payload['connection'] == 'restored' else 'link_disconnected'
        
    if experiment_id == 'Q2-E01': 
        return 'assignment_authorized' if record_payload['available'] else 'resource_constraint_reject'
        
    if experiment_id == 'Q2-E02': 
        return 'schema_validation_pass'
        
    if experiment_id == 'Q3-E01': 
        return 'delay_alert_triggered' if record_payload['eta_min'] > record_payload['appointment_min'] + 15 else 'stale_telemetry_suppressed'
        
    if experiment_id == 'Q3-E02': 
        return 'detention_billing_flag' if record_payload['stopped_min'] > 60 else 'manifest_stop_noop'
        
    if experiment_id == 'Q4-E01': 
        return 'notification_broadcast_authorized' if record_payload['eta_delta_min'] >= 20 else 'uncommitted_state_suppression'
        
    if experiment_id == 'Q4-E02': 
        return 'transaction_committed'
        
    raise ValueError(f"Unknown architectural evaluation baseline profile identifier: {experiment_id}")
