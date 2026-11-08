# EXP-11 fresh reproduction comparison — November 7, 2026

## Method
The current `experiments/EXP-11/network_concensus.py` was reviewed using its documented deterministic evaluation procedure for profile IDs 21000–21299. `validation/reproduce_exp11.py` provides an isolated Python execution and manifest workflow. The calculated results below are derived from the source algorithm; the accompanying GitHub automated test verifies the expected reproduction counts when CI completes.

## Source-code reproduction comparison
| Metric | Original published: eventual | Current source: eventual | Original published: quorum | Current source: quorum |
|---|---:|---:|---:|---:|
| Profiles | 300 | 300 | 300 | 300 |
| State-compliance passes | 6 | 15 | 300 | 300 |
| Duplicate actions | 277 | 240 | 0 | 0 |
| Collisions intercepted | 0 | 0 | 242 | 240 |
| Network timeout exceptions | 311 | 300 | 311 | 300 |
| Sequence desync errors | 225 | 224 | 0 | 0 |

The current deterministic evaluation retains **300/300** quorum state-compliance passes. Other figures differ from the original published summary, and the current raw CSV contains 601 rows including repeated profile/strategy pairs (see `docs/EXP11_SOURCE_RECONCILIATION_2026-11-07.md`).

## Engineering interpretation
The current implementation models two-node synchronization through in-memory registries, deterministic link-availability rules and sequence updates. It demonstrates comparative behavior under these modeled conditions; physical distributed-node transport is a separate integration scope.

## Follow-up
1. Archive the isolated Python reproduction manifest and generated files from an actual dated run.
2. Determine the source version and profile selection used for the original published summary.
3. Correlate original run logs and engineering decisions with the metrics, retaining original source files unchanged.
4. Use version-specific figures in technical reporting, with the run environment and source revision.

**Status:** Current-source metric comparison recorded; original-summary version reconciliation in progress.
