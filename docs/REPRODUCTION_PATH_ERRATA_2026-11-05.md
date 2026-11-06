# Reproduction path errata — 2026-11-05

This is a current-facing correction note; the historical README and experiment files are preserved unchanged pending review.

| README reference | Finding | Existing path |
|---|---|---|
| `experiments/EXP-09/deep/deep_routing_engine.py` | File absent | `experiments/EXP-09/deep/routing_engine.py` |
| `experiments/EXP-10/concurrent_ingestion_engine.py` | File absent | `experiments/EXP-10/routing_engine.py` |
| `experiments/EXP-11/network_consensus.py` | File absent; historical spelling differs | `experiments/EXP-11/network_concensus.py` |
| `validation/recompute_benchmarks.py` | Referenced in other documentation but absent on `main` | No verified equivalent |
| `experiments/EXP-12/outbox_validator.py` | Exists but writes original results in place; docstring incorrectly calls experiment EXP-13 | Do not run in original checkout before isolating output |

**Warning:** A file existing at the corrected path does not certify the experiment is reproducible or the metrics are valid. These are file-location corrections, not test execution results.

Suggested non-mutating inspection from repository root:
```bash
python -m validation.audit_approval_and_generated_labels
python -m validation.audit_exp12
```
Run any experiment generator only in a disposable copy or with output redirected away from the original `results/` files. Preserve raw evidence and record new run timestamps, code SHAs and results separately.

## Claims to qualify
The README uses language such as `production`, `guarantee` and `exactly-once message delivery`. Existing EXP-12 code is a deterministic simulation; no real production transport or end-to-end external acknowledgement is established by that simulation. Replace broad claims with accurately scoped experimental findings after technical review.

**Status:** File paths inspected; full reproduction matrix not yet executed.
