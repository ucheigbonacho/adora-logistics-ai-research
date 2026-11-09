# EXP-16 Q4 operational baseline — November 2026 actual records

Source: `data/q4_2026/actual_november_records.jsonl` (10 owner-confirmed actual Q4 November 2026 records). Import manifest: `data/q4_2026/import_manifest.json`. This is a derived evaluation, not an original operational record.

**Baseline method:** Predict `escalate` if `signal_metric >= 0.70`, otherwise `routine`.

| Metric | Count |
|---|---:|
| Correct escalations | 4 |
| Correct routine outcomes | 4 |
| Missed escalations | 1 |
| Unnecessary escalations | 1 |
| Total agreement | 8/10 |

Mismatches: `PL-Q3-RUN-004` (recorded routine, predicted escalate) and `PL-Q3-RUN-007` (recorded escalate, predicted routine).

**Interpretation:** 80% agreement on this ten-record operational outcome sample. This is not independently validated voice-intent authorization accuracy, not a generalization estimate and not proof of a technological advance. Authorization labels and a held-out dataset remain to be developed and reviewed independently.

**Reproduction:** `python -m validation.evaluate_exp16_q4 --source data/q4_2026/actual_november_records.jsonl --output-dir /tmp/exp16-q4-baseline` from the repository root, using a fresh output directory.

The original Q4 data remains unchanged. This evaluation is a later technical analysis of the November records.
