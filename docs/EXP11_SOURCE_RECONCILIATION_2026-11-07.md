# EXP-11 source-to-summary reconciliation — 2026-11-07

## Experimental design and reported outcome
The EXP-11 specification and `results/summary.json` describe 300 profiles per strategy, comparing an eventual-consistency stream with distributed quorum gating. Published state-compliance results are **6/300** and **300/300**, respectively.

## Raw-record inspection
The checked-in `experiments/EXP-11/results/trials.csv` has no header. Field order is established by the `csv.DictWriter` in `network_concensus.py`:
`profile_id, network_strategy, state_compliance_pass, applied_actions, duplicate_actions_executed, concurrency_collisions_intercepted, network_timeout_exceptions, synchronized_sequence_index, packet_acknowledgement_timeouts`.

The file contains **601** data rows: 300 eventual-consistency rows and 301 quorum rows. Recorded profile IDs span **21070–21299**. Across both strategies there are **460 unique profile/strategy pairs** and **141 repeated pairs**, including a repeated sequence spanning profile 21229–21299. The raw-file population and profile range differ from the generator's current default `21000–21299` design.

## Reconciliation method
1. Preserve the existing CSV and JSON source files.
2. Use `python -m validation.audit_experiments_09_14` to report raw record counts, profile range, repeated pairs and strategy aggregates.
3. Produce a separate, dated reproduction from the current experiment code in a new output directory. Compare its 600 expected rows and summary with the preserved records.
4. Determine whether the raw CSV represents a partial run, combined exports or a later appended segment by checking original run artifacts and execution records. Do not select a duplicate-removal policy solely to match the published summary.
5. Record the source file hashes and source commit SHA in the final evidence index.

## Reporting statement
“The EXP-11 experiment compares two state-synchronization strategies under modeled interruption and retry conditions. The published summary reports 6/300 baseline and 300/300 quorum compliance. The checked-in trial export contains repeated profile records; the source-to-summary comparison and current-code reproduction are maintained as separate technical verification records.”

**Status:** Source-format and repeated-record analysis completed; execution artifact comparison and origin of repeated rows remain scheduled.
