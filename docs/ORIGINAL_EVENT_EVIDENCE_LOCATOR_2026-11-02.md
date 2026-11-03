# Original event evidence locator — 2026-11-02

**Scope:** Thirty user-reported Q1/Q2/November records; December excluded.
**Status:** Repository inventory only. No new field observations inferred.

## Sources inspected
- `validation/user_supplied_q1_q2_november_30_2026-11-02.jsonl`
- Four uploaded 24-record Q1-E01, Q1-E02, Q2-E01 and Q3-E01 JSONL files
- `experiments/EXP-09/event_trace.csv`
- `experiments/EXP-09/deep/results/sample_traces.jsonl`

## What the additional trace files actually contain
- EXP-09 `event_trace.csv` has **scenario**, **engine_strategy**,
  **execution_step**, serialized **event_type**, **engine_outcome**,
  **active_gps_seq**, and **total_applied_actions**. It includes
  synthetic scenario identifiers like `09-02` and action IDs like
  `TXN-A01`.
- EXP-09 deep `sample_traces.jsonl` has **seed**, **strategy**,
  **state_correct**, **duplicates**, **lost_actions**, **stale_accepted**,
  **unsafe_ambiguous**, **dropped_confirms**, **recovery_ms**, and
  nested event traces with `at_ms`, `event`, `seq`, `outcome`,
  `gps` and `applied`.

Neither inspected file supplies a verified link to the 30 user-reported
`PL-Q*-RUN-*` cases. They are scenario/simulation trace evidence,
**not** proof of original GPS/ETA/driver event measurements for those
specific records. Do not reuse their measurements as field inputs.

## Requested primary sources for a valid join
- Telematics/GPS export with stable event ID, load ID, device ID,
  UTC event time, UTC ingestion time, GPS sequence, coordinates and
  freshness calculation.
- Dispatch/TMS event export with load ID, action ID, planned arrival,
  calculated ETA, appointment, constraints and decision timestamp.
- Voice/session event export with session ID, utterance or transcript
  reference, connectivity transitions and confirmed authorization state.
- Reviewer source approval records, full file SHA-256 digests and
  documented provenance of each cross-dataset join.

Keep driver identifiers and personal data outside a public repository.
A redacted join manifest can be stored separately with source hashes
and explicit MATCHED / UNMATCHED status.

## Result
The prior exact 96-to-30 reconciliation found zero matching case IDs
or normalized utterances. Additional EXP-09 trace inspection does not
establish a valid event join. The 30 records remain unmatched and no
structured ETA, connection or authorization values are populated.

Next step: obtain actual source exports, perform read-only deterministic
joins, preserve unmatched records and independently review ambiguous
matches. No merge, history rewrite or production dispatch.
