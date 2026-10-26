# Q1-E01 user-reported reviewer approval — 2026-10-26

**Status: USER-REPORTED, NOT INDEPENDENTLY VERIFIED.**

The user stated on 2026-10-26 that Chika Ibegbu approved the six proposed
Q1-E01 classifications exactly as presented in
`docs/DRIVER_INTENT_ONTOLOGY_DRAFT_v0.1.md`.

The resulting **separate** reference candidate is:
`validation/q1_e01_user_reported_approval_2026-10-26.jsonl`.

Original `validation/independent_cases.jsonl`, `validation/summary.csv`,
and `main/reviewer_approval.txt` are unchanged. No original case has been
silently relabeled. The user-reported review date is not asserted to be
the date on which Chika performed the review.

## User-reported labels

| Case | Label |
|---|---|
| Q1-E01-V01 | informational_report |
| Q1-E01-V02 | route_proposal_requested |
| Q1-E01-V03 | clarification_required |
| Q1-E01-V04 | informational_report |
| Q1-E01-V05 | clarification_required |
| Q1-E01-V06 | informational_report |

## Supporting evidence still needed

1. Original signed worksheet or verifiable email from Chika Ibegbu
   approving each case and the exact label, not a generalized 34/34 claim.
2. Actual review date, Chika's role, organization and dispatch experience.
3. Source operational context reviewed, including whether audio, transcripts,
   load IDs and dispatcher procedures were available.
4. Reasoning for ambiguous statements, especially V01, V04, V05 and V06.
5. Review method, independence/conflicts, and any second-review disagreements.
6. The exact ontology version approved and a link to an immutable source
   version or documented review reference.

## Current engine limitations

The existing keyword classifier is not expected to match all six
user-reported labels. That is a genuine engineering gap, not permission
to rewrite reference decisions or retroactively assert test success.

## Safe evaluation

`python -m validation.evaluate_user_reported_q1`

This script reports agreement against user-reported labels only. It
does not represent independent verification. Do not use the
`validation.reviewed_reference` tool on this dataset until a genuine
review record supplies its missing metadata and approval is verified.

No merge or production dispatch is authorized by this document.
