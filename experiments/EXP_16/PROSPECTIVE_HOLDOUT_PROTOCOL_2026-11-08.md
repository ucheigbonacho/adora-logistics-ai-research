# EXP-16 prospective holdout protocol — 2026-11-08

**Status: preregistered design, before collection and evaluation of new held-out actual operational records.** The ten November 2 records were used for exploratory rule selection and must not be counted as held-out evaluation data.

## Technical question
Does incorporating ETA lateness and connection-state context improve detection of actual escalation requirements relative to a signal-score-only threshold, without causing unnecessary escalations under conflicting conditions?

## Frozen candidate rules for future evaluation
- **Baseline:** `escalate` when `signal_metric >= 0.70`; otherwise `routine`.
- **ETA-context candidate:** `escalate` when `calculated_eta > appointment_time`; otherwise `routine`.
- **Missing/stale ETA:** report separately as `needs_review`; do not force a routine or escalation label without a reviewed fallback policy.
- Connection-state transitions are a **stratification variable**, not yet a trained decision rule. Analyze by `CONNECTED_TO_CONNECTED`, `CONNECTED_TO_DEGRADED`, `DEGRADED_TO_LOST`, and `LOST_TO_CONNECTED`.

## Challenge conditions to be collected and reviewed
1. ETA late but no actionable exception (possible false escalation).
2. ETA on time but a constraint, safety, or authorization exception exists (possible missed escalation).
3. Degraded/lost connection with ETA on time.
4. Delayed or stale telemetry and missing ETA.
5. Conflicting ETA updates, repeated event IDs, and asynchronous confirmations.

## Independent labeling and evaluation
Before running the frozen rules on a new holdout, retain the source-system records and independent adjudication of the operational `escalate`/`routine` outcome. Record reviewer, decision criteria, timestamp, and any disagreement. Keep dispatch authorization (`authorize`/`reject`/`clarify`) in a separate labeled dataset. Do not use rule-generated labels as ground truth.

Target a sufficiently varied held-out set; sample size and strata must be fixed before outcome inspection. Report confusion matrices, missed escalation rate, unnecessary escalation rate, missing-data coverage, per-stratum metrics and confidence intervals where appropriate. Do not claim improved generalization on the ten exploratory records.

## Engineering safety
No external dispatch execution is permitted. Preserve original files, hashes, code revisions, test dates and actual investigator logs. Record failed cases and changes prospectively; do not relabel existing records or retrospectively describe this protocol as a historical Q3 experiment.
