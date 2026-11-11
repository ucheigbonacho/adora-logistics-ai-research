# EXP-09–14 source-format review — 2026-11-06

This review compares repository output file structures with the published experiment specifications. Original files remain unchanged.

| Experiment | Source inspection | Reported outcome | Reproduction next action |
|---|---|---|---|
| EXP-09 | `results.csv` records paired baseline and gated scenarios; some serialized list fields have irregular quoting | Specification: 2/12 baseline and 12/12 gated | Check CSV parsing and scenario-level expectations; preserve scenario 09-09 distinction from later authorization |
| EXP-10 | `results/trials.csv` has 200 data rows, using columns `seed,strategy,correct,...` with strategy values `volatile` and `durable` | Summary: 0/100 and 100/100 | Compare pass column `correct` and source strategy mapping with summary terminology |
| EXP-11 | `results/trials.csv` contains 600 data rows **without a header** | Summary: 6/300 and 300/300 | Use explicit positional column definitions verified against `network_concensus.py`; avoid dropping first data row as a header |
| EXP-12 | Original trial file has 2,411 data rows, including repeated profile-1050 combinations | Summary: 265/800, 600/800, 800/800 | Run isolated reproduction and retain the comparison; source-to-summary reconciliation remains tracked |
| EXP-13 | `results/http_requests.csv` and summary exist | Summary: 203 requests, 51 commits, 151 matches, 1 collision | Verify response-category totals against raw rows, then reproduce local HTTP behavior in isolated runtime |
| EXP-14 | `results/trials.csv` has 18 data rows; `state_compliance_pass` is written as `True`/`False` | Summary: durable strategy passes 9/9; unbuffered passes 3/9 | Parse boolean values correctly, verify six phase-strategy groups, and review process interruption evidence |

`validation/audit_experiments_09_14.py` is a read-only aggregator that now accounts for the EXP-10 schema, headerless EXP-11 output, and EXP-14 boolean values. It does not execute experiment generators or modify raw files. Its output should be checked against the original code's field definitions and archived as a new dated comparison.

## Next verification sequence
1. Run the read-only audit under CI or an isolated checkout and record its output.
2. Review source code for EXP-11 to confirm positional field mapping.
3. Compare each experiment's raw-file totals with its summary.
4. Reproduce experiments in separate output directories and retain runtime metadata and output hashes.
5. Update the technical investigation matrix with source-to-summary results and measured engineering conclusions.

This document describes verified file structures and published figures, not a replacement for original source reports.
