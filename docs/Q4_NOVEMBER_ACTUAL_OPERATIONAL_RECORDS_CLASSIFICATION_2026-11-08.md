# Q4 November 2026 actual operational/test records — classification
Prepared November 8, 2026.

## Owner-confirmed origin
The project owner confirmed that the ten JSON records supplied in the project conversation, case IDs `PL-Q3-RUN-001` through `PL-Q3-RUN-010`, are **actual operational/test records from November 2, 2026 (Q4)**. Describe these ten records as actual Q4 November records, not as generated or synthetic. This document records the owner's source declaration; external source-system verification remains a separate evidence step.

## Original identifiers and timestamps
The original `PL-Q3-RUN` prefixes are retained. Their Q3 wording does not change the November event timestamps. Do not rewrite identifiers, timestamps, reported labels, or other original fields.

## Separate code snippet
The Python snippet for constructing `PL-NOV-RUN-001` to `PL-NOV-RUN-250` is **not part of these ten actual records** and must not be conflated with them. It is excluded from the actual-record dataset.

## Use in prospective experiments
- EXP-15: use telemetry IDs, event timestamps and connection transitions as operational inputs, but distinguish these from actual retry, acknowledgement or crash traces, which are not present in these ten rows.
- EXP-16: use actual utterances, expected operational outcomes, signal metrics and ETA fields. The recorded categories `escalate` and `routine` are operational outcomes, not automatically authorization labels such as `authorize` or `clarify`.
- Retain a separate mapping/review record before using these rows to calculate authorization classification accuracy.

## Integrity and evidence handling
The field `telemetry_checksum_sha256` is supplied as an eight-character hexadecimal value. Preserve the original field and value. A complete SHA-256 verification requires source-system details or full digests.

The ten original JSON lines have not been committed to this repository by this note. Ingest them from an exact source copy with an import date and content hash. Do not backdate any later derived analysis or infer historical approvals from identifier fields alone.

**Status:** Q4 actual-record classification established based on owner confirmation; original-source import and technical analysis are separate subsequent steps.
