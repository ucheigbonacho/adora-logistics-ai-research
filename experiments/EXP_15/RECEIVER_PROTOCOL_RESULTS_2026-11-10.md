# EXP-15 receiver recovery protocol comparison — November 10, 2026

## Execution and scope
The test `tests/test_exp15_receiver_protocol_comparison.py` passed on the audit branch at commit `29c644133824a2321ed85cf602e8550558813dd6`, GitHub Actions run `42792941902`. It exercises `experiments/EXP_15/receiver_protocol_comparison.py` against a separate local SQLite receiver ledger for each of four deterministic fault scenarios and three protocols.

| Protocol | Safety passes / 4 | Resolved / 4 | Duplicate receiver effects |
|---|---:|---:|---:|
| Safe hold | 4 | 0 | 0 |
| Blind retry | 1 | 4 | 3 |
| Receiver reconciliation | 4 | 2 | 0 |

**Metric definitions:** Safety pass means no more than one receiver ledger mutation for the immutable action ID. Resolved means the sender-side test protocol reached acknowledged status. These are distinct measures; acknowledgement is not by itself evidence of an externally verified effect.

## Fault cases
- Receiver committed, acknowledgement lost: safe hold remains uncertain; blind retry creates a duplicate; reconciliation observes the receiver ledger and resolves.
- Crash before receiver commit: safe hold remains uncertain; blind retry commits once; reconciliation confirms absence and commits once.
- Ledger temporarily unavailable: safe hold remains uncertain; blind retry duplicates an existing effect; reconciliation remains uncertain.
- Conflicting receipt digest: safe hold remains uncertain; blind retry duplicates an existing effect; reconciliation quarantines inconsistent evidence and remains uncertain.

## Technical interpretation
The experiment illustrates a modeled trade-off: blind retry favors completion while potentially duplicating receiver-side effects; conservative hold avoids duplicates but may remain unresolved; receiver reconciliation can improve completion when durable authoritative evidence is available. These behaviors are consistent with established distributed-systems principles and are **not, by themselves, proof of an SR&ED technological advancement**.

The current receiver simulator provides an authoritative ledger without testing consistency under multiple receiver replicas, ledger staleness, partial writes, split-brain, or unavailable quorum. The next research question is whether uncertainty persists under realistic consistency limitations after standard recovery and idempotency approaches are evaluated.

## Next prospective investigation
1. Pre-register receiver-ledger consistency assumptions and expected safety/liveness outcomes.
2. Compare authoritative, stale, unavailable and conflicting receiver-ledger observations.
3. Introduce an independent receiver-side idempotency-key baseline so blind retry is not compared only against an artificially non-idempotent receiver.
4. Measure safety, completion, unresolved time and query overhead separately.
5. Retain raw traces and source hashes from new executions, and record failures and design decisions at the time they occur.

Original experimental records are unchanged. No JEVEEB routine dispatch integration or production dispatch command was used.
