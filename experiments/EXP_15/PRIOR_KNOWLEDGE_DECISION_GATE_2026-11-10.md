# EXP-15 prior-knowledge assessment and investigation decision — November 10, 2026

**Classification:** Current-source engineering assessment prepared November 10, 2026. This is not a reconstruction of an earlier investigator's knowledge or a determination of SR&ED eligibility.

## Investigated requirement
Prevent duplicate receiver-side mutations after acknowledgement loss while permitting recovery of unfinished actions, under a unique immutable action ID and payload contract.

## Existing methods considered
| Established technique | Problem addressed | Evidence from current repository | Residual issue |
|---|---|---|---|
| SQLite unique-key constraint | Duplicate durable effects for one action ID | `idempotent_receiver_comparison.py`, 5/5 safety passes | Multi-replica consistency not modeled |
| Receiver-side idempotency and immutable payload digest | Repeated and conflicting requests | 5/5 safe, 5/5 resolved with idempotent retry | Assumes receiver preserves and consistently enforces key/digest |
| Durable outbox and uncertain lease state | Sender crash and indeterminate acknowledgement | `src/dispatch_outbox.py` and recovery tests | Sender cannot alone establish remote commit |
| Authoritative receiver-ledger reconciliation | Resolve indeterminate external effects | 5/5 safe, 2/5 resolved in modeled cases | Unavailable, stale and conflicting reads remain unresolved |
| Hold pending external verification | Avoid unsafe retransmission | 5/5 safe, 0/5 resolved | May block completion indefinitely |

These are widely established distributed-systems/database patterns. This table is a repository-based comparison, **not a completed external literature or practitioner survey**.

## Decision gate
**Decision: Close the current single-receiver duplicate-suppression question as routine engineering within the tested scope.** The observed behavior is explained by established receiver-side idempotency, so the five deterministic cases do not support claiming a technological advance.

**Do not automatically close the entire EXP-15 workstream.** A new technological uncertainty may be investigated only after the engineering owner identifies a specific, measurable requirement not resolved by established patterns and records the available prior knowledge, attempted standard solutions and their observed limitations.

## Possible residual research question — not yet substantiated
Under inconsistent or partitioned *replicated* receiver ledgers, can a recovery protocol maintain at-most-one externally effective mutation and bounded completion when stale reads and concurrent writes occur? The current SQLite receiver does **not** implement replication or distributed quorum. This is a candidate scope only, not evidence that a technological uncertainty exists.

Before starting it:
1. Document why known unique keys, idempotent inboxes, consensus/quorum and established transaction/reconciliation protocols are insufficient for the actual specified requirements.
2. Define the required consistency model, failure assumptions, safety/liveness bounds, and observable receiver effects.
3. Pre-register a test matrix and independent receiver-side truth oracle.
4. Obtain engineering-owner sign-off on the uncertainty and hypotheses before implementing a new approach.
5. Preserve dated source versions, failed attempts, raw traces and time records.

## SR&ED boundary
The decision concerns technical characterization, not CRA eligibility or expenditure allocation. Ordinary dispatch operations and routine integration are excluded from this experimental workstream. The current test suite must not be described as proof that JEVEEB's $700,000 contractor charge is eligible. Historical experiment and financial evidence remain separately subject to reconciliation.

## Next priority
Prioritize EXP-16's independently labeled operational/authorization evaluation and technical uncertainty assessment while EXP-15's potential replicated-ledger question is held at this decision gate. Do not create speculative EXP-15 test results to support a claim.
