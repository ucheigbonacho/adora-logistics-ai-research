# EXP-16 Q4 holdout intake and independent review instructions
Prepared November 8, 2026. Prospective process document; no new operational observations are asserted.

## Intake boundary
The ten actual November 2 records in `data/q4_2026/actual_november_records.jsonl` were used to examine and select the ETA-context candidate. They must remain in the exploratory set, not the independent holdout.

New records should come from a source-system export of actual operational/test events after the candidate comparison was fixed. Preserve the unmodified export separately and calculate its SHA-256 digest before deriving the evaluator input.

## Required per-case fields
- `case_id`: new, unique identifier; never reuse `PL-Q3-RUN-001` through `PL-Q3-RUN-010`
- `timestamp`: original event timestamp with timezone
- `expected`: independently adjudicated operational outcome, `routine` or `escalate`
- `signal_metric`: original numeric score in [0,1]
- `appointment_time` and `calculated_eta`: source timestamps with timezone, or null if unavailable
- `connection_state_transition`: recorded connectivity transition, or `missing`
- `independent_review_ref`: traceable review record identifier
- `reviewed_at`: actual date/time of independent review

Keep original utterance, telemetry IDs, dispatch authorization fields, event timestamps and approval references in the source export where present. Do not infer missing values or treat the operational `expected` field as a voice-authorization label.

## Review procedure
1. Export the new source records; retain the original byte-for-byte.
2. Have a qualified reviewer adjudicate escalation need using operational evidence and documented criteria, without using the two candidate predictions as the label source.
3. Record disagreements and their resolutions separately; do not overwrite earlier decisions.
4. Freeze the holdout file and checksum before running the evaluator.
5. Run `python -m validation.evaluate_exp16_holdout --source /path/to/new_reviewed_holdout.jsonl --output-dir /path/to/new_output_dir`.
6. Record the evaluation commit SHA, Python/runtime details, manifest and confusion matrices, and retain failed cases.
7. Report missed escalations, unnecessary escalations, missing-ETA coverage and performance by connection-state group. Do not infer population-level accuracy from a small or convenience sample.

## Challenge coverage
Include naturally occurring cases that can distinguish ETA from escalation need: late ETA without an actionable issue, on-time ETA with an independent safety/constraint exception, degraded connectivity without delay, missing/stale ETA, and contradictory updates.

**Status:** Intake and review procedure ready. No new actual holdout dataset has been provided, imported, or evaluated. No new independent accuracy result is claimed.
