# EXP-12 reconciliation — source-preserving audit (2026-11-05)

## Source records
- `experiments/EXP-12/results/summary.json` reports 800 cases per strategy and pass totals **265 / 600 / 800**.
- `experiments/EXP-12/results/trials.csv` contains **2,411 parseable data rows**, plus a blank physical line at line 614, compared with 2,400 unique expected profile/phase/strategy combinations.
- Raw-file aggregate by strategy:
  - `unbuffered_retry_stream`: 803 rows, 263 passes, 1,013 redundant mutations, 0 drops.
  - `volatile_pre_flight_registry`: 804 rows, 603 passes, 0 redundant mutations, 201 drops.
  - `durable_outbox_idempotent_receiver`: 804 rows, 804 passes, 0 redundant mutations, 0 drops.
- Lines **615–625** contain 11 duplicate combinations for profile **1050**; one duplicate `before_send/unbuffered_retry_stream` row is absent from the extra block. Some duplicate rows differ from their earlier counterparts in transmission attempt counts.
- The published summary and unfiltered CSV aggregates differ; the 11 repeated profile-1050 combinations require a documented row-selection and reproduction comparison. The 2,400-key unique set requires a documented deduplication policy and separate recomputation. Do not silently replace source files or select rows to force published totals.

## Execution scope and source preservation
`experiments/EXP-12/outbox_validator.py` is a deterministic simulation. Its module docstring currently calls itself EXP-13, and its `run_outbox_assertion_suite` writes directly to the original `results/trials.csv` and `results/summary.json` paths. **Do not run it on the original evidence without redirecting its output to a new directory.** This run models the specified interruption phases using a deterministic simulation; live transport testing is a separate integration workstream.

## Corrective steps
1. Retain original CSV and JSON byte-for-byte; calculate and record source hashes.
2. Use `validation/audit_exp12.py` to report raw aggregates, duplicate keys and the published-summary mismatch without writing source files.
3. Recompute a separately labeled, deduplicated analytical view and explicitly document why a row-selection policy was chosen; do not replace the original.
4. Execute the experiment code only in an isolated output directory, label results **new reproduction**, and compare its output with both the raw file and original summary.
5. Review source and README reproduction commands, align production and delivery terminology with the scope of the tests performed, and correct broken paths in current-facing documentation with dated errata.
6. Maintain this discrepancy as open until the provenance of the duplicated profile 1050 rows and original summary is established.

**Status:** EXP-12 source-to-summary reconciliation remains open for the unbuffered strategy and repeated profile-1050 rows. Original experimental files are retained. This report was prepared in November 2026.
