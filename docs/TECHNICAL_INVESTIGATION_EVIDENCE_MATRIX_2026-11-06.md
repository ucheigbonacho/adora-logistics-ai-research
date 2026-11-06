# Technical Investigation and Evidence Matrix — EXP-09 through EXP-14
Prepared November 6, 2026. Engineering evidence organization for Poulina / JEVEEB Adora Logistics AI.

## Purpose and methodology
This matrix maps the project's existing experiment specifications to the technological questions, compared approaches, reported observations and retained source records. The **questions below are engineering interpretations of the documented objectives**, not newly discovered historical hypotheses. A contemporaneous hypothesis or decision is attributed only when supported by a dated source record.

| ID | Documented technical objective / question | Approaches evaluated | Results reported in original specification | Code and supporting records | Next verification activity |
|---|---|---|---|---|---|
| EXP-09 | Maintain consistent state under out-of-order delivery, channel interruptions and overlapping transaction intents | Unbuffered ingestion vs idempotency gating | Full-state scenario passes **2/12 vs 12/12**; redundant mutations **5 vs 0** | `experiments/EXP-09/EXP09_Integrated_State_Consistency_Specification.txt`; `run.py`, `routing_engine.py`, `scenarios.jsonl`, `results.csv`, `event_trace.csv` | Link each scenario to the original trace; document historical `09-09` expectation and current authorization behavior separately |
| EXP-10 | Maintain durable transaction and sequence state across concurrent retries and node recovery | Unbuffered ingestion vs durable outbox/idempotent receiver | Compliance **0/100 vs 100/100**; redundant mutations **1,100 vs 0**; sequence errors **92 vs 0** | `experiments/EXP-10/EXP10_Durability_Concurrent_Ingestion_Specification.txt`; `routing_engine.py`, `results/trials.csv`, `results/summary.json` | Correct current execution path; reproduce in an isolated environment; identify what was tested beyond established SQLite transaction controls |
| EXP-11 | Maintain cross-worker consistency under packet interruptions, concurrent acknowledgements and conflicting updates | Eventual-consistency stream vs quorum gating | Compliance **6/300 vs 300/300**; collisions intercepted **0 vs 242**; sequence errors **225 vs 0** | `experiments/EXP-11/EXP11_Distributed_Consensus_Specification.txt`; `network_concensus.py`, `results/trials.csv`, `results/summary.json` | Correct current path spelling; identify actual worker/node topology, network modeling and test inputs |
| EXP-12 | Compare transaction outcomes under acknowledgement failures and interruption phases | Unbuffered retry, volatile registry and durable outbox/idempotent receiver | Original specification: passes **265/800, 600/800, 800/800**; original raw-file totals and fresh code reproduction tracked separately | `experiments/EXP-12/EXP12_Transactional_Outbox_Specification.txt`; `outbox_validator.py`, `results/trials.csv`, `results/summary.json`; `docs/EXP12_SOURCE_RECONCILIATION_2026-11-05.md` | Complete profile-1050 duplicate-row reconciliation and record fresh isolated reproduction |
| EXP-13 | Preserve idempotent state across concurrent HTTP requests, retries, collision attempts and restart | Local threaded HTTP ingestion with persistent SQLite boundary | **203** requests: **51** commits, **151** duplicate matches, **1** collision response; reported zero concurrency override errors | `experiments/EXP-13/EXP13_Integration_Suite_Specification.txt`; `run_integration.py`, `server.py`, `results/http_requests.csv`, `results/summary.json` | Run isolated local integration test; retain runtime configuration and request trace; separate loopback behavior from external transport |
| EXP-14 | Preserve transaction correctness following process termination at defined transaction phases | Unbuffered retry vs durable idempotent receiver | **18** runs across pre-flight, post-mutation and post-ack phases; durable configuration reports **9/9** passes; unbuffered **3/9** | `experiments/EXP-14/EXP14_Process_Interruption_Specification.txt`; `run.py`, `worker.py`, `results/trials.csv`, `results/summary.json` | Verify process-termination mechanics and recovery traces; record execution platform and durable-state observations |

## Systematic investigation structure
For each experiment, maintain these fields in a separate evidence sheet:
1. **Observed technical problem** — cite the original dated source, not only a later summary.
2. **Technological uncertainty** — identify the behavior that could not be predicted from the available engineering knowledge; distinguish routine implementation constraints.
3. **Baseline and alternatives** — specify control and proposed approach, including configuration and version.
4. **Hypothesis and prediction** — cite any original pre-run record; if absent, identify the statement as a retrospective technical interpretation.
5. **Method and environment** — executable, inputs, runtime versions, topology, failure injection, run count.
6. **Measured observations** — quote source file, rows, metric definitions and exceptions.
7. **Technical learning and next iteration** — connect actual failure/decision records to the next change.
8. **Personnel and expenditure cross-reference** — refer to separately maintained verified assignments and accounting schedules; no assumed attribution.
9. **Source location and integrity** — Git SHA, original file hash, timestamp basis, output location.
10. **Reconciliation status** — precise open item, owner and resolution record.

## Reporting guidance
The source specifications include descriptions such as “production” and “verified.” Report results within the actual test configuration (deterministic simulation, local threaded integration or subprocess interruption) and state the measured outcomes. Avoid treating an implementation pattern by itself as proof of technological uncertainty. Preserve original reports and make corrections through dated supplements.

## Immediate next actions
- Cross-check EXP-09 through EXP-14 raw outputs and code against each specification.
- Create a reproducibility matrix with command, input, expected output, actual output and artifact hash.
- Add original dated problem statements, failed attempts and design decisions where they exist; do not reconstruct missing dates as original records.
- Use the Q4 Documentation Protocol and Kit prospectively for EXP-15 and EXP-16.

This document is an **evidence map and engineering interpretation** prepared November 2026; it does not revise the original experiment specifications.
