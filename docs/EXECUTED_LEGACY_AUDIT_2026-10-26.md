# Executed legacy compatibility verification — 2026-10-26

**This is an executed software compatibility audit, not independently reviewed classification accuracy or historical SR&ED evidence.**

## Reproducible source
- GitHub Actions run: https://github.com/ucheigbonacho/adora-logistics-ai-research/actions/runs/40398690057
- Run head SHA: `25f005fe77da13c3c40f7ec97292d8959740e023`
- Archived artifact: `legacy-label-audit`, ID `12688186092`
- Command: `python -m validation.audit_legacy_labels`
- Original input: `validation/independent_cases.jsonl`
- Output is produced separately; original inputs and historical results are unchanged.

## Executed result
- Original cases: **34**
- Exact label matches: **28**
- Mismatches: **6**
- All six mismatches concern Q1-E01.

| Case | Original expected | Executed current output |
|---|---|---|
| Q1-E01-V01 | authorize_intent | route_proposal_requested |
| Q1-E01-V02 | authorize_intent | route_proposal_requested |
| Q1-E01-V03 | exception_flag | clarification_required |
| Q1-E01-V04 | exception_flag | clarification_required |
| Q1-E01-V05 | authorize_intent | route_proposal_requested |
| Q1-E01-V06 | exception_flag | clarification_required |

This corrects earlier narrative summaries that incorrectly described V04
or V06 as `route_proposal_requested`. The executed GitHub Actions log
is the authoritative record for this code revision.

## Why not 100%?
The historical fixture uses a two-category intent ontology. The current
repair engine uses non-executing proposal/clarification labels.
Changing either labels or predictions merely to force 34/34 would be
invalid. The reviewer file on main attributed to Chika Ibegbu claims
34/34 but does not individually approve six cases under the new ontology.

## Release blockers
1. Obtain real, independently approved six-case labels and reviewer rationale.
2. Confirm the ontology version and reviewer sign-off.
3. Run `validation.reviewed_reference` against the approved reference set.
4. Resolve or document disagreements without modifying historical fixtures.
5. Keep the repair branch separate from main until user authorizes integration.
6. Production dispatch remains disabled.

EXP-15 and EXP-16 are future planned work.
