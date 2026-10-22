"""Dispatch request classification. Text alone never authorizes execution."""
PROPOSAL_TERMS = ("alternate route", "another road", "reroute", "road closed", "route blocked")

def evaluate_dispatch_request(payload):
    if not isinstance(payload, dict):
        return "clarification_required"
    if payload.get("request_type") == "execute_route_change":
        required = ("authenticated", "authorized_role", "context_valid", "constraints_passed", "confirmed")
        if not all(payload.get(k) is True for k in required):
            return "authorization_denied"
        if not all(isinstance(payload.get(k), str) and payload[k].strip() for k in ("load_id", "route_id", "action_id")):
            return "clarification_required"
        return "authorize_intent"
    if payload.get("request_type") == "propose_route":
        return "route_proposal_requested"
    phrase = payload.get("utterance", "")
    if not isinstance(phrase, str):
        return "clarification_required"
    phrase = phrase.casefold().strip()
    if phrase in ("", "alternate_gating"):
        return "clarification_required"
    return "route_proposal_requested" if any(term in phrase for term in PROPOSAL_TERMS) else "clarification_required"
