"""Conservative driver-intent classifier; raw speech never authorizes execution.

This is a rules-based engineering baseline, not an independently validated
speech-understanding model. Signed admission remains a separate trust boundary.
"""
import re

_ROUTE_TERMS = ("route", "road", "reroute", "detour", "way")
_PROPOSAL_VERBS = ("find", "suggest", "show", "recommend", "propose", "calculate", "give")
_REPORT_CUES = ("closed", "blocked", "traffic", "accident", "construction", "delay")


def classify_driver_utterance(utterance):
    if not isinstance(utterance, str):
        return "clarification_required"
    phrase = " ".join(utterance.casefold().strip().split())
    if not phrase or phrase == "alternate_gating":
        return "clarification_required"
    words = set(re.findall(r"[a-z0-9]+", phrase))
    if not words.intersection(_ROUTE_TERMS):
        return "clarification_required"
    # A fragment naming a route is not a request to propose or execute one.
    if len(words) <= 2 and not words.intersection(_REPORT_CUES):
        return "clarification_required"
    # A question about road conditions is informational, not an action.
    if (phrase.endswith("?") or phrase.startswith(("is ", "are ", "did ", "have ", "i heard "))) and not words.intersection(_PROPOSAL_VERBS):
        return "informational_report"
    # Explicit option-finding language is distinct from an instruction to execute.
    if words.intersection(_PROPOSAL_VERBS) and words.intersection(_ROUTE_TERMS):
        return "route_proposal_requested"
    # Uncertain or descriptive road statements are reports, not proposals.
    if words.intersection(_REPORT_CUES) or words.intersection(("may", "might", "possibly")):
        return "informational_report"
    return "clarification_required"


def evaluate_dispatch_request(payload):
    if not isinstance(payload, dict):
        return "clarification_required"
    if payload.get("request_type") == "execute_route_change":
        # These booleans are NOT sufficient proof of authorization in production.
        # Actual dispatch admission requires the separately verified signed claim.
        required = ("authenticated", "authorized_role", "context_valid", "constraints_passed", "confirmed")
        if not all(payload.get(k) is True for k in required):
            return "authorization_denied"
        if not all(isinstance(payload.get(k), str) and payload[k].strip() for k in ("load_id", "route_id", "action_id")):
            return "clarification_required"
        return "authorize_intent"
    if payload.get("request_type") == "propose_route":
        return "route_proposal_requested"
    return classify_driver_utterance(payload.get("utterance", ""))
