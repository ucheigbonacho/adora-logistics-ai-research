# EXP-15 compound-failure test results and next investigation — November 9, 2026

## Verified execution
The automated regression test `tests/test_exp15_compound_failures.py` passed in GitHub Actions for commit `c1c36f188fe41acbe9f7bd0d3ca67b4c3cc9fcc8` (run `42585846459`). The test invokes `experiments/EXP_15/compound_failures.py` with eight concurrent claim workers per scenario.

| Local test scenario | Verified expected invariant |
|---|---|
| Concurrent claim, restart and late acknowledgement | One successful claim, one recorded attempt, acknowledgement accepted after lease expiry |
| Concurrent claim, expiry without receiver receipt | One successful claim, one recorded attempt, uncertain status retained without automatic replay |
| Conflicting payload while status uncertain | Payload conflict rejected; no second claim |
| Duplicate enqueue after acknowledgement | Duplicate recognized; no second claim |

All four test paths assert `external_dispatch_attempted == False`. These are new November 2026 software tests in an isolated local SQLite environment, not evidence of actual remote receiver mutations, transport recovery or historical Q3 execution.

## Technological question for the next iteration
Can a transaction left `uncertain` after a process interruption be resolved safely when a delayed or conflicting receiver receipt arrives, including concurrent receipt delivery and repeated recovery attempts?

## Proposed new failure cases (not yet completed)
1. Two workers concurrently acknowledge the same action using the same receipt; expected one accepted and one duplicate acknowledgement.
2. Two workers concurrently acknowledge with different receipt values; expected one accepted and one receipt conflict, with no silent replacement.
3. A late acknowledgement arrives after an uncertain lease; expected resolution to acknowledged without a new dispatch attempt.
4. Multiple expired-lease claims race before the receipt arrives; expected no automatic retry and at most one original claim.
5. A receipt arrives for an unknown or never-dispatched action; expected rejection without creating an action.

## Evidence capture for next execution
Record source SHA, actual execution time, worker count, scenario IDs, SQLite state before/after, receipt values, outcome codes, number of claims and attempted external sends. Preserve failing cases and rerun records. Never equate a local state transition with an externally confirmed dispatch event.

**Status:** Four compound-failure tests verified; receipt-race extension proposed for prospective execution.
