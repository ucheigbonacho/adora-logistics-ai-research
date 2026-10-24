# Independent reference validation: preparation

The repository now provides a **read-only** evaluator:
`python -m validation.reviewed_reference path/to/reviewed_cases.jsonl`.

The reviewed case file is deliberately **not populated** with invented
authoritative labels. Each JSONL record must contain:

- `id`: unique case ID
- `experiment_id`: existing engine experiment identifier
- `input`: original input object
- `expected`: outcome determined independently of the engine
- `reviewer`: reviewer identifier
- `reviewed_at`: review date
- `reference`: traceable specification, ticket or signed review reference

These fields are required but not independently authenticated by the
evaluator. The organization must verify reviewer identity, independence,
source provenance, review dates and the acceptance criteria.

The evaluator prints actual/expected disagreements and does not change
original datasets, experiment fixtures or historic result files. Tests use
explicitly fictional unit-test cases; they are **not** validation evidence.

Next: obtain approved authoritative cases, review Q1-E01 proposal semantics,
resolve EXP-09's changed criterion explicitly, and compare raw-vs-normalized
labels with mapping versioning. EXP-15 and EXP-16 are planned future work.
