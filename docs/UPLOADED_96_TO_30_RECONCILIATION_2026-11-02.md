# 96 uploaded records vs 30 operational cases — reconciliation status

**Scope:** Q1-E01, Q1-E02, Q2-E01, Q3-E01 (24 each), plus the 30-case
user-supplied Q1/Q2/November dataset. December records are excluded.

## Source data and limitations
The four separately uploaded JSONL files are readable actual JSON, not
Git LFS pointer text. Their records have `case_id`, `experiment_id`,
`scenario`, `utterance`, `expected`, `signal`, and `kind`.

- Q1-E01: 24 cases; 13 exception / 11 routine.
- Q1-E02: 24 cases; 18 hold / 6 resume.
- Q2-E01: 24 cases; 16 hold / 8 assign.
- Q3-E01: 24 cases; 12 risk / 12 normal.

The 30-case dataset is in
`validation/user_supplied_q1_q2_november_30_2026-11-02.jsonl`.

**Do not infer exact cross-file event identity from similar utterances.**
The 96-record files do not supply the required `eta_min`,
`appointment_min`, `freshness_sec`, `connection`, `pending`,
`confirmed`, `available`, `equipment_match`, `hours_left`,
or `hours_needed` fields. No common verified load/event identifier
has been established between these sources and the 30-case dataset.

## Safe interpretation
- Similarity of scenario text is a candidate relationship, not a join.
- Label crosswalks are proposed semantics, not independently approved
  ground truth or engine predictions.
- Original files and labels must remain unchanged.
- Full SHA-256 hashes for the **actual source files** should be recorded
  separately from the eight-character telemetry checksum fragments.
- Q3-labeled November records occurred in calendar Q4; describe them
  as November retests of Q3 scenarios, not Q3 execution dates.
- Original reviewer IDs and approval references remain user-reported,
  not authenticated.
- No December Q4 or final-validation records are included.

## Completion requirements
Obtain source event/load identifiers or original correlated event logs.
Where no match exists, record UNMATCHED and leave structured engine
fields missing. Never fill missing fields using unrelated historical
records merely to make the classifier run.

This is a structural reconciliation note, not a new field measurement
or an independently verified validation result.
