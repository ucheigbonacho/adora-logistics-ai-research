# Historical commit provenance audit — 2026-11-05

**Scope:** Six commits with author dates before September 2026 on `repair/authorization-and-validation-2026-10-22`. Read-only inspection of GitHub commit objects and changed-file lists. The inspection records Git metadata and file changes; original development chronology is assessed alongside available source records.

| Recorded author date (UTC) | Commit | Message summary | Actual Git object observation | Provenance status |
|---|---|---|---|---|
| 2026-01-15 | `b691596d825b` | Implement parsing layer | Root commit adds only `.gitattributes` (2 lines) | Commit contains only repository attributes |
| 2026-02-18 | `c7134a49e388` | Import driver utterance data | No file changes; tree identical to parent | No file changes in this commit |
| 2026-02-20 | `21da3fa297c3` | Commit Q1-E02 recovery pipelines | Adds three `data/raw/*_production_inputs.jsonl` files, each shown as three-line Git LFS pointer text; underlying objects require separate retrieval | LFS pointer files; retrieve associated content |
| 2026-05-22 | `46ea2ee224e8` | Map dispatch restriction matrices | No file changes; tree identical to parent | Empty commit; unsupported |
| 2026-06-30 | `d953cdef3439` | Archive Q1/Q2 logs | No file changes; tree identical to parent | Empty commit; unsupported |
| 2026-08-12 | `3e9be0b55060` | GPS captures and dwell parameters | No file changes; tree identical to parent | Empty commit; unsupported |

**All six commits:** GitHub REST reports unsigned commit objects (`verification.reason=unsigned`), matching author and committer timestamps, and the same GitHub account identity. Additional source records are needed to attribute individual work and establish the original delivery timeline.

**Additional lineage caution:** February 20 commit has parent `d475e7d...`, rather than being a direct child of the listed January/February empty-commit sequence. Inspect graph/ancestry before treating the six as a single chronological chain.

## CRA evidence treatment
- Preserve these Git objects and their SHA identifiers unchanged.
- Do not rewrite, backdate, cherry-pick or recreate them to imply earlier activity.
- Distinguish the timestamp recorded in Git metadata from independently verified original work dates.
- Obtain original source archives, earlier remote repository history, work tickets, contemporaneous communications, signed delivery records and actual LFS objects before attributing Q1–Q3 work to these commits.
- Correlate commit descriptions with actual changed files and associated development records.
- Keep October–November consolidation and later Q4 tests accurately dated.

## Status
**Chronology reconciliation remains open:** these six commits record Git metadata and limited file changes; associated source and delivery records will be indexed when available. No original files, branches or history were modified by this audit.
