# EXP-15 standard idempotency comparison — November 10, 2026

## Verified execution
The prospective comparison was pre-registered in `IDEMPOTENT_RECEIVER_PREREGISTRATION_2026-11-10.md`. The implementation `idempotent_receiver_comparison.py` and test `tests/test_exp15_idempotent_receiver_comparison.py` passed in GitHub Actions run `42797024483`, commit `af19d3dc16ef42b870c2cbfffdd6e4bbd1564eb5`.

| Protocol | Safety passes / 5 | Resolved / 5 | Duplicate submissions suppressed |
|---|---:|---:|---:|
| Hold | 5 | 0 | 0 |
| Standard idempotent retry | 5 | 5 | 4 |
| Conservative reconciliation | 5 | 2 | 0 |

The test uses a durable SQLite receiver ledger with a unique action ID and immutable payload digest, five deterministic fault scenarios, and one modeled recovery step. No external dispatch or remote receiver was involved.

## Technical interpretation
Standard receiver-side idempotency prevents duplicate receiver mutations in all five modeled cases, including repeated submissions after acknowledgement loss. The previously observed blind-retry duplication occurred against a deliberately non-idempotent receiver and therefore does **not** by itself establish a novel technical challenge.

Conservative reconciliation remains unresolved when the modeled ledger observation is stale, unavailable or conflicting. This alone does not demonstrate an SR&ED technological uncertainty: known retry, idempotency, durable-inbox and reconciliation designs must be evaluated against actual requirements.

## Decision
Do not characterize duplicate suppression through ordinary receiver-side idempotency as a technological advancement. The next possible investigation is limited to a specifically documented residual uncertainty, if any, involving authoritative evidence under inconsistent replicated receiver state, conflicting durable records or bounded recovery requirements that established techniques cannot satisfy through routine application.

Before more experiments, perform a technical prior-knowledge assessment and document a measurable unresolved requirement. If none is substantiated, close EXP-15's current line of investigation as a verified implementation of known techniques. Keep source evidence and actual expenditures separate from eligibility determinations.

This is a November 2026 experimental report; it does not establish earlier historical results, personnel attribution or CRA cost eligibility.
