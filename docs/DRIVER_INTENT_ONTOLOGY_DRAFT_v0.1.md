# Driver intent ontology — proposed version 0.1

**Status: DRAFT FOR DOMAIN REVIEW. Not an approved validation reference.**

This specification proposes a non-executing intent taxonomy for Q1-E01.
It is not an amendment to the original 2026 research evidence or to
`validation/independent_cases.jsonl`.

## Proposed categories

| Category | Meaning | Permitted system behaviour |
|---|---|---|
| `informational_report` | Driver describes road, traffic or route conditions without requesting an action | Record or ask follow-up; never dispatch |
| `route_proposal_requested` | Driver explicitly requests alternative route options | Calculate/display options; never dispatch |
| `clarification_required` | Fragment, uncertain wording or missing referent | Ask a targeted clarification; never dispatch |
| `execution_request_pending_authorization` | Explicit instruction to change a specified load/route | Validate identity, permissions, load scope, constraints and confirmation; never execute from text alone |
| `execution_authorized` | Verified, scoped, confirmed and unexpired approval issued by a trusted service | Eligible for atomic outbox admission; not proof of external execution |

**Security invariant:** No raw utterance, classification score, or caller-provided
boolean alone may produce `execution_authorized`. Only a verified signed
authorization accepted by the admission service can authorize a request.

## Existing Q1-E01 cases — proposed review candidates

These are *suggestions* requiring independent domain review, not ground truth.

| Case | Utterance | Proposed category | Rationale / reviewer question |
|---|---|---|---|
| V01 | road closed ahead | informational_report | A road condition is reported, but no action requested |
| V02 | please find another road | route_proposal_requested | Explicit request to find options, not to change a route |
| V03 | can you hear me | clarification_required | Conversation connectivity question, no routing intent |
| V04 | I heard the road is closed? | informational_report | Question about road condition; could warrant confirmation |
| V05 | alternate route | clarification_required | Incomplete fragment; intent is not explicit |
| V06 | route may be blocked | informational_report | Uncertain condition report, not execution |

## Approval required before use as validation ground truth

For each case, a qualified dispatcher/domain reviewer should record:
- Their identity and role, review date, source reference, and whether they
  have access to the original operating context.
- Approved category, or `undetermined` when context is insufficient.
- Explanation, risk severity, and whether another reviewer disagrees.
- Policy version and explicit sign-off.

Do not update the original historical JSONL. Approved decisions should be
stored in a new, versioned, separately reviewed reference set. Cases with
unresolved disagreement should be reported separately, not counted as passes.

## Known limitations

This is a policy proposal, not an independent accuracy measurement.
The current keyword-based classifier does not reliably distinguish
statements from questions or fragments. Future implementation should
separate informational classification from signed authorization.
No live trucking dispatch is enabled.
