# Main-branch reviewer approval reconciliation — 2026-10-26

**Engineering verification; not a certification of the reviewer's identity or sign-off.**

## Source records examined

- Main commit `19da3bd5cfdd15c4e822888fee051aca4114490d`
- `main/reviewer_approval.txt`, attributed to Chika Ibegbu, dated 2026-10-26
- `main/validation/independent_cases.jsonl` (34 existing cases)
- `main/src/engine.py` and `main/src/rules.py` (different decision functions)
- `main/validation/summary.csv` (older 33/34 claim)
- Repair branch `src/engine.py`, `src/authorization.py`, and the six-case draft ontology

## Conflicting versions of the rules

**Do not report 34/34 as independently verified.** The reviewer document
claims 34/34 but does not provide six individually signed Q1-E01 decisions
or executable proof tied to a commit SHA.

The two main-branch engines disagree in important ways:

- `src/engine.py` returns `notification_broadcast_authorized` and
  `uncommitted_state_suppression` for Q4-E01, and
  `transaction_committed` and `idempotency_filter_match` for Q4-E02.
- `src/rules.py` instead returns `send/block` and
  `apply/deduplicate`. It also treats certain action-ID strings as
  authorization for Q1-E01, even without confirmed intent.
- The original 34-case fixture expects the first label vocabulary, not
  `send/block/apply/deduplicate`.

A direct **static comparison** of the existing 34 cases with these exact
source rules gives:
- Main `src/engine.py`: 32/34 expected labels (Q1-E01 V02 and V04 differ).
- Main `src/rules.py`: 24/34 expected labels (Q1-E01 V02 and V04 plus all
  eight Q4-E01/Q4-E02 cases differ).
- Repair branch `src/engine.py`: 28/34 expected labels because Q1-E01
  uses a new, non-executing taxonomy.

These figures are source-derived comparisons, **not fresh benchmark
execution results**. The historical `validation/summary.csv` remains
33/34 and has not been overwritten.

## Review evidence still required

The uploaded `reviewer_approval.txt` records a named reviewer and an
approval assertion, but it does **not**:
- individually approve the six new five-category Q1-E01 labels;
- document reviewer rationale for each disputed case;
- link to an immutable tested code SHA, test output and sign-off;
- explain why the Q4 label vocabulary differs between main modules.

A claim of 100% automated agreement is not a substitute for independently
reviewed operational ground truth. Reviewer identity and actual sign-off
should be confirmed through the original author or a verifiable record.

## Corrections already made on repair branch

- Single canonical routing function with `src.rules` re-exporting it.
- Fail-closed route proposal vs authorization separation.
- Signed approval, atomic outbox, local receiver and signed receipt
  enforcement; production dispatch disabled.
- Original EXP-09 acceptance expectation preserved alongside the changed
  safety criterion.
- Read-only reviewed-reference evaluator and a blank reviewer worksheet.
- CI passing for the previously inspected repair commit.

## Release gates

1. Obtain a signed or verifiable six-case Q1-E01 approval with the exact
   accepted ontology version and explanations.
2. Keep main historical fixtures and reviewer file unchanged.
3. Execute read-only comparison on an identified commit SHA, retaining
   disagreements.
4. Resolve `src/rules.py` vs `src/engine.py` vocabulary and unsafe
   action-ID authorization before merge.
5. Review and merge the existing draft PR only after code and evidence
   reconciliation, not to force a 100% score.

No EXP-15/16 work is represented as completed.
