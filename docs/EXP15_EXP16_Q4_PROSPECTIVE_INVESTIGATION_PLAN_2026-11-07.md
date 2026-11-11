# Q4 experimental planning register — EXP-15 and EXP-16
Prepared November 7, 2026. **Prospective planning document only.** No EXP-15 or EXP-16 tests are represented here as completed or previously performed.

## Candidate EXP-15 — Durable dispatch recovery under compounded interruptions
**Candidate technological question:** Under overlapping acknowledgement loss, process restart and duplicate/modified replay, can the system preserve a single authorized dispatch state transition while also recovering unfinished work?

**Available baseline:** Existing idempotent outbox/receiver and recovery tests from EXP-12–14. Baseline capabilities must be measured in the actual selected code revision, not assumed from historical summaries.

**Proposed investigation:** Define a fault-injection matrix spanning acknowledgement-before/after commit, process termination, replay order, payload collision, and concurrent recovery workers. Capture pre-run prediction and explicit success/failure conditions before running each configuration.

**Proposed observations:** attempted deliveries, committed mutations, duplicate suppressions, unauthorized mutation count, recovery completion, crash checkpoint, run seed, database state before/after and trace identifiers.

**Decision points:** Identify observed failures; change only one controlled design variable per iteration where practical; rerun the same cases and document any regression.

**Status:** Hypothesis and protocol require engineering-owner review before first prospective run. No result or technical advance claimed.

## Candidate EXP-16 — Authorization uncertainty across speech intent and dispatch state
**Candidate technological question:** Can ambiguous or conflicting operator intent, stale telematics and asynchronous confirmations be resolved safely without losing valid dispatch actions under delayed or reordered messages?

**Available baseline:** Current fail-closed intent classifier, deterministic routing engine and EXP-09 scenario corpus. Historical scenario 09-09 expects an action that current authorization policy rejects; preserve both versions and their rationale.

**Proposed investigation:** Construct independently reviewed intent labels and dispatch-event scenarios, with a fixed held-out evaluation set. Compare deterministic classifier/confirmation gating with a candidate revised strategy under ambiguous instructions, contradictory confirmations, GPS reorder, offline transitions and repeated transaction IDs.

**Proposed observations:** independently labeled authorized/clarification cases, false-authorize count, false-reject count, replay effects, state correctness, case-specific trace and reviewer adjudication. Avoid generating expected labels from the same rules being evaluated.

**Decision points:** Document failed classifications, causal hypotheses, modified rules and measured changes on held-out cases. Separate classification metrics from downstream state-safety metrics.

**Status:** Candidate scope for owner approval; no experiment results or technological advance claimed.

## Mandatory prospective record for each run
1. Date/time, investigator and actual work performed (not backdated).
2. Code commit SHA, environment, dependencies, hardware and data provenance.
3. Uncertainty and prior technical knowledge, including why routine engineering methods did not resolve the question.
4. Pre-run hypothesis, prediction, baseline, test design and acceptance criteria.
5. Raw logs, datasets, output hashes, failures and unexpected observations.
6. Dated interpretation, next iteration, decision and follow-up owner.
7. Time and contractor evidence cross-reference maintained separately from technical results.

Use the Q4 Documentation Protocol and Excel Kit as the authoritative operational template for weekly records, experiment logs and discrepancies. This planning register does not supersede that kit or the project's historical documents.
