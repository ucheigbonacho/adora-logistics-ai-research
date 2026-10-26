# Existing acceptance-case review register — 2026-10-26

**Status: engineering triage only; not independent domain approval.**
Source: `validation/independent_cases.jsonl` (34 existing cases), current
`src/engine.py` and `src/authorization.py`. Original inputs and expected
labels are preserved. No historical results were overwritten.

## Reconciliation of current engine against existing expected labels

- Q1-E01: **0/6 exact label matches**. The earlier expectation uses
  `authorize_intent` for some raw phrases and `exception_flag` for others.
  The current safe classifier returns `route_proposal_requested` or
  `clarification_required`; it never executes from raw text alone.
- Q1-E02, Q2-E01, Q2-E02, Q3-E01, Q3-E02, Q4-E01 and Q4-E02:
  **28/28 exact matches** under the current deterministic decision rules.
- Overall: **28/34** exact matches (82.35%), computed by comparing the
  current rules with the existing 34 reference records. This is a
  **static source-level assessment**, not a new executed benchmark or
  independently verified accuracy measurement.
- The committed `validation/summary.csv` reports 33/34 under an
  earlier engine and must not be represented as the current result.

## Cases requiring a domain acceptance decision

| Case | Original input | Original expected | Current output | Review question |
|---|---|---|---|---|
| Q1-E01-V01 | road closed ahead | authorize_intent | route_proposal_requested | Is this a report, a request for options, or an instruction? |
| Q1-E01-V02 | please find another road | authorize_intent | route_proposal_requested | Confirm that route proposal is distinct from execution |
| Q1-E01-V03 | can you hear me | exception_flag | clarification_required | Clarification vs generic exception taxonomy |
| Q1-E01-V04 | I heard the road is closed? | exception_flag | route_proposal_requested | Should an informational question be classified separately? |
| Q1-E01-V05 | alternate route | authorize_intent | route_proposal_requested | Fragment should not authorize execution |
| Q1-E01-V06 | route may be blocked | exception_flag | route_proposal_requested | Should uncertain statements be flagged as reports, not proposals? |

**Do not silently relabel these records.** Reviewer should specify the
authoritative ontology (e.g. `informational_report`, `proposal_request`,
`clarification_required`, `execution_authorized`), review source and
whether the existing model needs improvement. Keep historical criteria
versioned, and add a *new* reviewed acceptance set only after approval.

## Additional validation gaps

1. Existing labels were authored for earlier decision semantics.
2. Dataset generator derives `expected` directly from the engine, so
   generated 960/960 matching results cannot independently measure accuracy.
3. Current Q1-E01 is keyword-based; it may misclassify informational or
   uncertain speech as proposal requests.
4. Structured authorization flags are caller-supplied unless bound to the
   signed local coordinator; Q1-E01 must not be exposed as a production
   authorization endpoint.
5. Reviewer identity, case provenance and operational domain approval
   have not been verified.
6. EXP-15 and EXP-16 are planned later in Q4 and are not treated as overdue.

## Next gate

Obtain a domain-reviewed, versioned set of expected decisions, preserve the
original JSONL unchanged, run the read-only `validation.reviewed_reference`
evaluator, and publish both passing and failing cases. Do not claim an
independent validation success before that review occurs.
