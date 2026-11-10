# EXP-16 authorization baseline prospective evaluation protocol — November 10, 2026

## Status
Prospective evaluation protocol; no independently adjudicated authorization dataset has been supplied or evaluated. This protocol is not a record of historical testing.

## Question
Does a conservative explicit-command authorization baseline adequately distinguish `authorize`, `reject` and `clarify` outcomes when utterances, confirmation evidence, authentication and state freshness conflict? What residual limitations, if any, remain after application of known fail-closed authorization rules?

## Frozen baseline implementation
`validation/evaluate_exp16_authorization_baseline.py` implements:
- `authorize` only when utterance begins with `dispatch `, contains additional text, and `auth_verified`, `confirmation_matches`, and `state_fresh` are all true.
- `reject` for an explicit dispatch instruction with a false authorization or false confirmation match.
- `clarify` for other cases, including stale/unknown state.

This is a simple deterministic **engineering baseline**, not a voice understanding model or a safety certification. Its use of a literal `dispatch ` prefix is deliberately narrow and may not cover natural-language commands. A test pass proves implementation behavior only.

## Data independence and collection
The ten November 2 records are exploratory operational `routine`/`escalate` examples; they cannot be treated as authorization labels. Before evaluation:
1. Obtain actual case-level utterance and authorization context, preserving original source and hash.
2. Obtain a **separate** reviewer-adjudicated label (`authorize`, `reject`, `clarify`) with rationale, reviewer ID, review time and evidence reference.
3. Preserve raw features (`utterance`, `auth_verified`, `confirmation_matches`, `state_fresh`) without deriving them from the baseline prediction.
4. Keep review records and input features in separate JSONL files with matching unique case IDs.
5. Freeze and checksum both files before running the evaluator. Retain disagreements rather than overwriting them.

## Challenge conditions
- Clear authorized instruction with verified confirmation and fresh state.
- Explicit command with invalid authentication.
- Explicit command with mismatched confirmation.
- Ambiguous request that does not clearly authorize an action.
- Missing or stale authorization/telemetry context.
- Conflicting or delayed confirmation.
- Repeated or out-of-order utterances.
- Ordinary status narration containing dispatch-related words.

Use only genuinely sourced cases for an operational evaluation. Controlled synthetic test fixtures, if used, must be separately labeled as synthetic and cannot substitute for independent operational evidence.

## Metrics and decision rules
Report per-class confusion matrix; false authorizations (review label `reject` or `clarify` predicted `authorize`); incorrect rejections; unnecessary clarifications; class coverage; and disagreements with reviewer rationale. Do not report held-out accuracy on cases used to tune the rule. Do not assert technological advancement merely because the baseline has errors: first assess standard speech-intent, authorization-state-machine, token binding and stale-message rejection techniques.

## Execution
Validate reviews with `python -m validation.validate_exp16_authorization_reviews --source REVIEWS.jsonl`, then evaluate using `python -m validation.evaluate_exp16_authorization_baseline --reviews REVIEWS.jsonl --features FEATURES.jsonl --output-dir NEW_RESULTS_DIR`. Record source SHA, Git commit, runtime and actual run date.

## Safety and attribution
No live dispatch, receiver mutation or JEVEEB routine operational integration is permitted. No reviewer identity, individual staff contribution, work date, or test outcome is inferred. Sponsor-reported staff assignment for activity 16-I remains unassigned.
