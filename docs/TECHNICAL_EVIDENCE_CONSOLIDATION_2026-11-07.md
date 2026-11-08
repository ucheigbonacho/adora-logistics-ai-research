# Technical evidence consolidation — November 7, 2026

This is a dated status supplement to `TECHNICAL_INVESTIGATION_EVIDENCE_MATRIX_2026-11-06.md` and `EXPERIMENTS_09_14_SOURCE_FORMAT_REVIEW_2026-11-06.md`. It does not replace historical experiment files or convert current tests into contemporaneous evidence.

| Experiment | Original source-to-summary review | New isolated reproduction | Open technical item |
|---|---|---|---|
| EXP-09 | 24 source rows, 2/12 baseline and 12/12 gated match original reporting | `validation/reproduce_exp09.py`; automated test passes; compares 12 historical expectations with current fail-closed engine | Document case 09-09 and other current-policy differences by version; archive full scenario comparison |
| EXP-10 | 200 source rows, 0/100 volatile and 100/100 durable | `validation/reproduce_exp10.py`; isolated smoke test passes (3 profiles per strategy) | Execute full 100 profiles/strategy, archive manifest, compare source-version metrics |
| EXP-11 | 601 source rows: 300 eventual and 301 quorum; 141 repeated profile/strategy keys | `validation/reproduce_exp11.py`; 600-profile-pair reproduction test passes; current-code metrics baseline 15/300, quorum 300/300 | Original summary 6/300 baseline differs from current source; trace original generator version and repeated rows |
| EXP-12 | 2,411 original raw rows with repeated keys; reported 265/800, 600/800, 800/800 | `validation/reproduce_exp12.py` and tests | Current source unbuffered 266/800; source-summary and duplicate-key reconciliation |
| EXP-13 | 203 requests; 51 commits, 151 idempotency matches, one collision | `validation/reproduce_exp13.py`; local HTTP/SQLite integration test passes | Archive actual run artifacts, runtime configuration, and confirm summary comparison |
| EXP-14 | 18 original trial rows; unbuffered 3/9 and durable 9/9 | `validation/reproduce_exp14.py`; six combinations with one repetition each pass | Run full 3 repetitions per combination, archive platform and result comparison |

## Interpretation and limitations
The above passing tests confirm the specified automated checks on the remediation branch. They do not establish historical authorship, contemporaneous Q1–Q3 experiment dates, eligibility of contractor costs or operation of a live external production dispatch network. The original specifications and records remain preserved.

The November 6 source-format review's statement that EXP-11 contains 600 rows is superseded by the verified **601-row** source count and the EXP-11 reconciliation supplements.

## Evidence work remaining
1. Capture full-size isolated reproduction outputs and SHA-256 manifests in an immutable, dated artifact index.
2. Attach dated engineering problem reports, decisions and iteration traces where available; distinguish retrospective explanations.
3. Reconcile EXP-11 and EXP-12 source-version differences, without changing original summaries.
4. Start EXP-15 and EXP-16 under the prospective Q4 protocol: pre-register uncertainty, baseline, hypothesis, experiment configuration, predicted outcomes, raw observations, failures, and decision records before each test.
5. Cross-reference separately verified personnel timesheets, invoices, work assignments and payment records; do not infer SR&ED eligibility from code execution alone.

**Status:** Consolidated source and CI review complete; full-run artifact archiving and prospective Q4 experimental planning next.
