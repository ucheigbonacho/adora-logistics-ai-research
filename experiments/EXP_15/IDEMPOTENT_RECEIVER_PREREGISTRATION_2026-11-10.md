# EXP-15 prospective receiver-idempotency and stale-ledger comparison
Prepared November 10, 2026, before the new comparison implementation and CI execution.

## Question and established-technique baseline
The preceding non-idempotent receiver comparison produced duplicate effects under blind retry. This follow-up tests whether **standard receiver-side idempotency keys** already resolve that safety issue, and whether stale/unavailable ledger reads affect sender-side recovery decisions. If standard idempotency resolves the requirement, that is a valid engineering finding, not a claim of novel technology.

## Fixed model and protocols
The new receiver uses a separate durable SQLite table with a unique action ID and immutable payload digest. Repeated submissions with matching digest return `duplicate` without a second mutation; mismatched digest returns `conflict`. This is a **known baseline technique**, not an invention.

Protocols:
- **Hold:** never retry without a verified acknowledgement.
- **Idempotent retry:** resend with the same action ID/digest, allowing the receiver to suppress duplicates.
- **Conservative reconcile:** use a trustworthy authoritative ledger response to resolve or retry; leave unavailable, stale or conflicting evidence unresolved. A stale response must not be treated as authoritative absence.

Fixed fault cases:
1. Receiver commit, acknowledgement lost.
2. Crash before receiver commit.
3. Receiver committed but ledger read is stale/empty.
4. Receiver committed but ledger read unavailable.
5. Receiver committed but read contains a conflicting digest.

## Pre-run measurements
For every protocol/scenario record actual receiver mutation count, duplicate-suppressed requests, conflicting requests, resolution status, ledger-read trust status and a deterministic event trace. Primary safety invariant: at most one durable receiver mutation for an action ID. Liveness is measured as resolution by the end of the **single modeled recovery step**, not real elapsed recovery time. Count unresolved cases separately.

Expected directional outcomes: receiver idempotency should prevent duplicate mutations even under repeated submissions. Conservative reconciliation should remain unresolved when the ledger response is stale, unavailable or contradictory. These are predictions, not findings.

## Validity boundary
This is a deterministic single-process fault-injection model with an isolated SQLite receiver. It does not simulate multi-replica consensus, network partitions with competing writes, real latency or actual trucking operations. Keep the original test and its findings unchanged. Archive a dated source SHA and new run outputs. No live dispatch is enabled.
