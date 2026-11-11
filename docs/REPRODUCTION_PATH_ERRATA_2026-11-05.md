# Reproduction path errata — 2026-11-05

This is a current-facing correction note; the historical README and experiment files are preserved unchanged pending review.

| README reference | Finding | Existing path |
|---|---|---|
| `experiments/EXP-09/deep/deep_routing_engine.py` | File absent | `experiments/EXP-09/deep/routing_engine.py` |
| `experiments/EXP-10/concurrent_ingestion_engine.py` | File absent | `experiments/EXP-10/routing_engine.py` |
| `experiments/EXP-11/network_consensus.py` | File absent; historical spelling differs | `experiments/EXP-11/network_concensus.py` |
| `validation/recompute_benchmarks.py` | Referenced in other documentation but absent on `main` | No verified equivalent |
| `experiments/EXP-12/outbox_validator.py` | Exists but writes original results in place; docstring incorrectly calls experiment EXP-13 | Do not run in original checkout before isolating output |

**Scope:** These entries correct file locations. Execution results and metric comparisons are recorded separately in the experiment reproduction reports.

Suggested non-mutating inspection from repository root:
```bash
python -m validation.audit_approval_and_generated_labels
python -m validation.audit_exp12
```
Run any experiment generator only in a disposable copy or with output redirected away from the original `results/` files. Preserve raw evidence and record new run timestamps, code SHAs and results separately.

## Claims to qualify
The README uses language such as `production`, `guarantee` and `exactly-once message delivery`. Existing EXP-12 code is a deterministic simulation; the EXP-12 simulation measures modeled delivery outcomes; production transport and external acknowledgement behavior are addressed in separate integration tests. Align descriptions with the tested environment, measured outcomes and separately documented integration scope.

**Status:** File paths inspected; full reproduction matrix not yet executed.
