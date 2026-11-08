# Source-to-summary outcome reconciliation — EXP-09, 10, 13 and 14
Prepared November 7, 2026.

## Method
The existing recorded CSV outputs were parsed using Python CSV semantics, preserving quoted commas and string boolean fields. Strategy-level pass counts and endpoint outcome categories were compared with the existing experiment specifications and JSON summaries. The original data files were not changed.

| Experiment | Source | Recorded observations | Source-to-summary assessment |
|---|---|---|---|
| EXP-09 | `experiments/EXP-09/results.csv` | 24 rows, 12 per strategy. `unprotected_stream` passes 2/12; `idempotent_gating` passes 12/12 | Aligns with reported 2/12 and 12/12 |
| EXP-10 | `experiments/EXP-10/results/trials.csv` | 200 rows, 100 per strategy. `volatile` passes 0/100; `durable` passes 100/100 | Aligns with reported 0/100 and 100/100; source strategy labels differ from published labels |
| EXP-13 | `experiments/EXP-13/results/http_requests.csv` | 203 rows: `TRANSACTION_COMMITTED` 51, `IDEMPOTENCY_FILTER_MATCH` 151, `MUTATION_COLLISION_ABORT` 1 | Aligns with published endpoint outcome totals |
| EXP-14 | `experiments/EXP-14/results/trials.csv` | 18 rows; unbuffered strategy passes 3/9; durable strategy passes 9/9 | Aligns with reported six phase/strategy groups |

## Reproducibility work remaining
- EXP-09: compare original scenario expectations and current authorization policy in separately versioned runs.
- EXP-10: run source code in isolated output and compare full metrics, not just pass counts.
- EXP-13: run the local HTTP integration in a controlled environment, retaining runtime details and request logs.
- EXP-14: execute subprocess interruption cases in an isolated environment and compare the resulting state transitions.
- EXP-11 and EXP-12: continue the separately documented source-version and repeated-row reconciliation.

## Engineering conclusion
The selected recorded outcome totals align with their published results. This provides a traceable foundation for the subsequent source-code reproduction and technological-investigation analysis. This report is a November 2026 source review and retains the original experiment records.
