# EXP-15 technological uncertainty and alternative-method decision gate
Prepared November 9, 2026. Prospective technical planning; no historical research claims are created by this document.

## 1. Current verified engineering baseline
The local SQLite outbox supports atomic claim, durable pending state, uncertain status on expired lease, payload-conflict detection, and acknowledgement handling. Automated concurrent claim and receipt-race tests passed on the audit branch. These tests verify implemented behavior in a local environment; they do not by themselves demonstrate technological uncertainty or an advance beyond established database and idempotency methods.

No external receiver, live dispatch transport, remote acknowledgement or multi-host failure was exercised. Ordinary Excel dispatch processing and routine operational workflows are outside this experiment.

## 2. Candidate uncertainty requiring a genuine technical assessment
Under **indeterminate external execution** (a receiver may have committed an action before acknowledgement was lost), can a recovery protocol distinguish committed from uncommitted effects when retries, concurrent recovery workers, delayed receipts and conflicting payloads occur, without sacrificing either safety or eventual completion?

The essential information problem is that a local lease expiry cannot establish whether an external side effect occurred. A local SQLite transaction alone does not resolve remote execution ambiguity.

**Prior-knowledge check before SR&ED characterization:** Investigators must assess known patterns—receiver-side idempotency keys, transactional outbox/inbox, durable receipts, reconciliation queries, message brokers, and standard distributed-systems recovery protocols. If these established methods resolve the stated requirements through routine application, classify the work as ordinary engineering rather than claiming technological uncertainty.

## 3. Alternative protocols for prospective comparison
- **A — Safe hold:** retain `uncertain` status indefinitely pending an independently verifiable receipt or manual reconciliation. Predict no automatic duplicate sends, but possible indefinite noncompletion.
- **B — Blind retry:** after lease expiry, retransmit without a receiver idempotency contract. Predict improved completion attempts but possible duplicate side effects. Use a test-only receiver, never live dispatch.
- **C — Receiver-key reconciliation:** after lease expiry, query a durable receiver ledger by immutable action ID and payload digest, then either acknowledge the verified commit or safely retry when absence can be established. Requires explicit receiver semantics; query timeout or ambiguity must remain unresolved rather than being interpreted as nonexecution.
- **D — Reconciliation with conflicting evidence:** delayed receipt, mismatched payload digest, or inconsistent receiver state must be quarantined for review rather than silently resolved.

## 4. Proposed fault matrix and observations
Pre-register each run with scenario ID, seed, source SHA, simulated transport/receiver version, action ID, payload digest, injected failure boundary, worker count, receiver commit count, local attempts, reconciliation queries, resolution status, elapsed recovery time, conflicting evidence and invariant violations.

Faults: receiver commit followed by lost acknowledgement; crash before receiver commit; delayed acknowledgement after retry decision; simultaneous recovery workers; receiver ledger temporarily unavailable; duplicate and conflicting payload; inconsistent receipt metadata.

**Primary safety invariant:** no more than one accepted receiver-side mutation per immutable action ID and payload contract. **Liveness measure:** fraction resolved without manual intervention within a predeclared bounded recovery window. Safety and liveness must be reported separately.

## 5. Test validity and evidence requirements
Build an **isolated receiver simulator with its own durable ledger** so a test can distinguish actual receiver-side commits from the sender's belief. Implement the alternatives independently, without using the same assertion logic as the implementation to manufacture expected results. Preserve raw event logs, failing traces, environment, code revision and dated decisions.

Do not describe simulated receiver commits as live operational transactions. If the test only reconfirms standard idempotency behavior, report that finding and stop rather than asserting an SR&ED advance.

## 6. Claim and cost boundary
SR&ED characterization requires documented technological uncertainty, systematic investigation, actual technical learning and separately substantiated allowable expenditures. This document does not establish that any specific experiment or JEVEEB contractor charge qualifies. Keep regular dispatch operations, routine integration, deployment and maintenance outside the experimental cost allocation unless independently justified under the applicable rules.

## 7. Next engineering action
Create a **test-only durable receiver and failure-injection harness** for alternatives A–C; pre-register expected safety/liveness trade-offs; run and retain measured results; then determine whether the observed unresolved behavior is genuinely beyond routine application of known techniques. No live dispatch adapter is to be enabled.
