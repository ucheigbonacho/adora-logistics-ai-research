# SR&ED technical evidence matrix — initial source audit (2026-11-03)

**Status:** Initial repository inventory and risk assessment, not a CRA eligibility determination, an independent source-authenticity certification, or verification of any expenditure. Original files unchanged. Review branch only; no merge.

## Evidence grading
- **Present:** repository file located; not necessarily authenticated or contemporaneous.
- **Tested:** automated CI passed for repair branch, not necessarily for each historical experiment.
- **Unverified:** provenance, dates, people, source logs or real-world results not independently established.
- **Not located:** no supporting file found in this review; does not prove it never existed.

## Quarterly experiment matrix

| Profile | Research question / uncertainty reflected in repository | Located evidence | Key audit gap |
|---|---|---|---|
| Q1-E01 | Distinguish ambiguous speech from executable dispatch intent | `experiments/Q1-E01/README.md`; `src/authorization.py`; `validation/independent_cases.jsonl`; `records/logbook_archive.txt` | Historical two-label ontology conflicts with repaired classifier; real audio, independent labels, contemporaneous source provenance unverified |
| Q1-E02 | Recover interrupted sessions without unauthorized resume | `experiments/Q1-E02/README.md`; `src/engine.py`; session tests; logbook | Actual connection events, pending/confirmed state records, source-system timestamps and field link unverified |
| Q2-E01 | Enforce equipment and hours constraints under dispatch pressure | `experiments/Q2-E01/README.md`; `src/engine.py`; 34-case fixture; logbook | Original fleet availability, HOS, equipment compatibility and load-specific decisions unverified |
| Q2-E02 | Reject incomplete or inconsistent load attributes | `experiments/Q2-E02/README.md`; `src/engine.py`; logbook | Source manifests, schema revisions, before/after failure counts and actual operating impact unverified |
| Q3-E01 | Detect late ETAs without accepting stale telemetry | `experiments/Q3-E01/README.md`; `validation/q3_eta_timestamp_adapter.py`; 10 enriched user-reported records | Source event IDs/checksums not independently verified; four eligible cases are a limited compatibility test, not blind validation |
| Q3-E02 | Separate scheduled stops from billable detention | `experiments/Q3-E02/README.md`; `src/engine.py`; logbook | Original geofence dwell sequences, manifests, timestamps and billing evidence unverified |
| Q4-E01 | Prevent notifications from uncommitted/invalid state | `experiments/Q4-E01/README.md`; `src/engine.py`; 34-case fixture | Local rule is not proof of real notification delivery or verified recipient/committed transaction linkage |
| Q4-E02 | Suppress duplicate actions on retries | `experiments/Q4-E02/README.md`; `src/engine.py`; outbox/receiver tests | Production execution/acknowledgement not enabled; exactly-once delivery claims exceed verified local scope |

## Additional EXP-09–EXP-14 evidence

| Experiment | Located technical assets | Reported result (repository only) | Evidence qualification |
|---|---|---|---|
| EXP-09 | scenario JSONL, event trace CSV, routing engines, results, deep disruption trials | Comparative event-ordering/idempotency traces | Scenario-based; verify generation scripts, historical dates, and real-event linkage |
| EXP-10 | routing engine, trials, summary | 100/100 compliant under idempotent gating vs 0/100 unprotected | Repository output, not independent operational validation |
| EXP-11 | network consensus code, trials, summary | 300/300 compliant quorum gating vs 6/300 eventual consistency | Need repeatability and environment details; not proof of distributed production consensus |
| EXP-12 | outbox validator, trials, summary | 800/800 compliant durable outbox vs 265/800 unbuffered | Local experimental result; do not claim external exactly-once transport |
| EXP-13 | loopback API server, integration runner, HTTP request CSV, summary | 203 HTTP requests, 51 committed sessions, 151 duplicate matches | Loopback integration, not live TMS or real carrier network |
| EXP-14 | worker, runner, trials, summary, README | 18 process interruption profiles | Check actual subprocess logs and repeatability; summary claims 'ENTERPRISE_PRODUCTION_BUILD_VERIFIED' beyond independently confirmed scope |

## Cross-cutting audit findings
1. **Historical label conflict:** Original validation summary reports 33/34, executed repaired legacy compatibility is 28/34. User-reported six-label agreement after development changes is not independent blind accuracy.
2. **Provenance:** Some logbook entries have named personnel and dates but repository presence does not authenticate when entries were authored. Do not backdate or rewrite.
3. **Terminology:** Several files use 'production', 'verified', 'independent' or 'contemporaneous' beyond what source evidence independently proves. Preserve originals; add accurate qualification in separate audit notes.
4. **Financial support:** No complete contract-to-invoice-to-payment-to-person-hours-to-experiment reconciliation was established by this technical repository review. A $700,000 software contract is not automatically a $700,000 eligible SR&ED expenditure.
5. **2025 continuity:** Link to the actual 2025 experiment files, dated hypotheses and results; do not assert a verified lineage from descriptions alone.
6. **Source integrity:** User-reported operational data contains shortened checksum fragments and unmatched event IDs. Do not represent those as full SHA-256 verification.
7. **Q4:** EXP-15/16 and December-dated records are not part of completed work as of this audit.

## Priority evidence requests
1. Original 2025 experimental work records and verified link to 2026 hypotheses.
2. Source commit/export timestamps, test-run logs, environment/configuration, failed iterations and reproducibility instructions per experiment.
3. Real personnel roster, actual work allocations, contractor deliverables and interview-ready technical owners.
4. SOW, invoices, bank payments, accounting entries and allocation methodology, retained in a private controlled-access evidence vault.
5. Source telematics exports and independent reviewer sign-offs, with redacted deterministic join keys.

**No eligibility conclusion, success probability or verified $700,000 qualifying expenditure is established by this matrix.**
