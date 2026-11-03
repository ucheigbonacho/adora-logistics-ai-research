# Executed 96-to-30 reconciliation — 2026-11-02

**Read-only exact comparison.** This does not verify historical event provenance or independently approved labels.

- Four user-uploaded JSONL sources: **96** records.
- GitHub user-supplied Q1/Q2/November dataset: **30** records.
- Exact case-ID matches: **0**.
- Exact normalized utterance matches: **0**.
- Unmatched records: **30**.
- Comparison normalization: lowercase and collapse whitespace only; no semantic similarity was treated as an event match.
- Original sources unchanged. December records excluded.

## Case-level results

| New case | Exact ID match | Exact utterance matches | Status |
|---|---|---|---|
| PL-Q1-RUN-001 | No | None | UNMATCHED |
| PL-Q1-RUN-002 | No | None | UNMATCHED |
| PL-Q1-RUN-003 | No | None | UNMATCHED |
| PL-Q1-RUN-004 | No | None | UNMATCHED |
| PL-Q1-RUN-005 | No | None | UNMATCHED |
| PL-Q1-RUN-006 | No | None | UNMATCHED |
| PL-Q1-RUN-007 | No | None | UNMATCHED |
| PL-Q1-RUN-008 | No | None | UNMATCHED |
| PL-Q1-RUN-009 | No | None | UNMATCHED |
| PL-Q1-RUN-010 | No | None | UNMATCHED |
| PL-Q2-RUN-011 | No | None | UNMATCHED |
| PL-Q2-RUN-012 | No | None | UNMATCHED |
| PL-Q2-RUN-013 | No | None | UNMATCHED |
| PL-Q2-RUN-014 | No | None | UNMATCHED |
| PL-Q2-RUN-015 | No | None | UNMATCHED |
| PL-Q2-RUN-016 | No | None | UNMATCHED |
| PL-Q2-RUN-017 | No | None | UNMATCHED |
| PL-Q2-RUN-018 | No | None | UNMATCHED |
| PL-Q2-RUN-019 | No | None | UNMATCHED |
| PL-Q2-RUN-020 | No | None | UNMATCHED |
| PL-Q3-RUN-021 | No | None | UNMATCHED |
| PL-Q3-RUN-022 | No | None | UNMATCHED |
| PL-Q3-RUN-023 | No | None | UNMATCHED |
| PL-Q3-RUN-024 | No | None | UNMATCHED |
| PL-Q3-RUN-025 | No | None | UNMATCHED |
| PL-Q3-RUN-026 | No | None | UNMATCHED |
| PL-Q3-RUN-027 | No | None | UNMATCHED |
| PL-Q3-RUN-028 | No | None | UNMATCHED |
| PL-Q3-RUN-029 | No | None | UNMATCHED |
| PL-Q3-RUN-030 | No | None | UNMATCHED |

## Remaining gaps
The 96 uploaded records provide case IDs, scenarios, utterances, signal values and labels, but no verified cross-dataset load/event IDs or the structured ETA, appointment, freshness, connection and dispatch authorization fields needed by the engine. Similar descriptions do not establish event identity. Do not fill missing measurements from unrelated cases. Original Q3-labeled November records are Q4-timestamped regression candidates.
