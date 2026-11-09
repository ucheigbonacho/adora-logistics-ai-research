# EXP-16 exploratory ETA and connection-state review — November 8, 2026

Source: `data/q4_2026/actual_november_records.jsonl` (10 owner-confirmed actual Q4 November operational/test records). Analysis: `validation/analyze_exp16_context.py`.

## Observations
The signal-only threshold at 0.70 agrees with recorded escalation/routine outcomes in 8/10 cases. The mismatches are:
- `PL-Q3-RUN-004`: signal 0.762 suggests escalation, but recorded outcome is routine; ETA is **8 minutes before** appointment; connection remains connected.
- `PL-Q3-RUN-007`: signal 0.510 suggests routine, but recorded outcome is escalation; ETA is **25 minutes after** appointment; connection transitions from connected to degraded.

Across these ten records, all five recorded escalations have positive ETA delay (+25 to +55 minutes), while all five recorded routine cases have negative ETA delay (-8 to -48 minutes). A simple ETA-late rule agrees with 10/10 of the recorded operational outcomes **on this same examined sample**.

## Interpretation and prospective validation
This ETA rule was selected after reviewing the ten records. **10/10 is post-hoc in-sample agreement, not held-out accuracy, a pre-registered experimental result, or proof of technological advancement.** The data cannot distinguish a robust causal mechanism from the possibility that the recorded outcome labels already reflect ETA lateness.

Next: independently review operational labels and source-system event traces; pre-register the proposed ETA/context rule and baseline before collecting a new held-out sample; test mixed cases (late ETA but routine, on-time ETA but other exception, degraded connection without delay, missing/stale ETA); compare false escalations and missed escalations. A separate independently labeled voice-authorization dataset is required for authorization claims.

Original records remain unchanged, and no production dispatch is enabled.
