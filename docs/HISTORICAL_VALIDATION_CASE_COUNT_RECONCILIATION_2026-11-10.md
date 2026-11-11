# Historical validation case-count reconciliation — November 10, 2026

## Scope and evidence
This is a current read-only reconciliation of existing repository artifacts, not a newly created historical experiment. Original datasets, summaries and Git history remain unchanged.

### Two distinct validation populations
1. `validation/independent_cases.jsonl` contains 34 explicitly enumerated validation cases across Q1-E01 through Q4-E02 (Q1-E01: 6; seven other groups: 4 each). `validation/summary.csv` reports 33/34 production matches; Q1-E01-V02 is the disagreement. The filename `independent_cases` alone does not establish independently adjudicated labels.
2. `results/summary.csv` reports **120 cases for each of eight experiment IDs**, or **960 reported case executions in total**. This is not the same as one 120-case October dataset. The reported 100% consistency is affected by the documented `src/generate.py` expected-label circularity: expected labels are calculated by the same routing rule that the evaluator checks.

The 24-row count reported by the external review has not yet been independently tied to a specific source file in this reconciliation. The 34-case validation population and 960 generated-result population must not be conflated.

### User-provided proposed directory/generator
The pasted `generate_historical_cases.py` describes prospective output counts of Q1 48, Q2 48, Q3 48 and October 120, totaling 264. It is a separate proposed construction from the eight-by-120 `results/summary.csv` population. The pasted script is incomplete and does not prove that those outputs exist, were historically executed, or have independently reviewed labels. Do not use its generated historical-looking timestamps, reviewer IDs, authorization IDs or approval references as verified historical observations.

## Outstanding case-level checks
- Identify the exact original input file(s) underlying each 120-per-experiment figure, including Git blob SHA and any LFS object content.
- Trace `src/generate.py` parameters, seeds, rule version, record IDs, and the distinction between generated case rows and actual executed test runs.
- Compare raw `results/trials.csv` or other per-case outputs against each reported 120; count unique IDs, duplicates and missing rows.
- Verify whether any 24-row file is a distinct source population and record its exact path and SHA.
- Verify label provenance independently of the evaluated function; otherwise classify scores as deterministic rule-consistency, not independent accuracy.
- Resolve reviewer approval 34/34 vs observed 33/34 without altering originals.
- Separate retrospective reconstruction and current reproduction from January–October execution evidence.

## Reporting decision pending reconciliation
Do not state that 120 original historical tests were recovered. Do not silently replace 24 with 120, or 120 with 960, until each figure is tied to a precisely identified file and methodology. Retain reported counts as **source claims**, with verification status and supporting links.

## Next step
Audit exact source paths and line counts, map every summary row to the generator and per-case result, and publish a dated source-linked reconciliation table. Keep this on the audit branch for review; no merge to main without approval.
