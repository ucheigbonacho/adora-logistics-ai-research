# Pre-merge integration readiness — 2026-10-26

**STATUS: PREPARATION ONLY — DO NOT MERGE.**

This document records engineering release gates for Adora Logistics AI.
It is not a statement that the 2026 experimental work, field operations,
contractor hours, invoices, or SR&ED eligibility have been verified.

## Verified repository state
- Current repair branch: `repair/authorization-and-validation-2026-10-22`.
- Last inspected repair head: `adae7186a8ef0a37abf1e0a4a9ef54fac7b03e37`.
- GitHub Actions for that commit: **success**.
- Pull request #1: **closed, not merged**.
- GitHub comparison of `main` and the repair branch returned **no common ancestor**.
- Production dispatch is disabled by the code path under review.
- EXP-15 and EXP-16 remain planned, not yet part of the accepted 2026 evidence.

## Work to finish before integration

### 1. Source reconciliation
- [ ] Identify why the branches lack a common ancestor and preserve both
  original commit graphs. Do not force-push or rewrite historic commits.
- [ ] Inventory all files changed on main since the repair branch was created.
- [ ] Create a **new** integration branch from the then-current main.
- [ ] Apply reviewed changes selectively with accurate new commit timestamps.
- [ ] Compare canonical `src.engine` and `src.rules` behavior. Do not
  reintroduce main's action-ID-only authorization shortcut.
- [ ] Keep historic experiment data, `reviewer_approval.txt` and original
  34-case reference inputs unchanged.

### 2. Independent validation
- [ ] Obtain individually approved classifications for Q1-E01 V01–V06
  with reviewer role, source context, rationale and verifiable sign-off.
- [ ] Reconcile the main-branch 34/34 approval claim with actual output
  labels and identified commit SHA.
- [ ] Run read-only legacy-label compatibility and independently reviewed
  reference evaluations; publish **all** disagreements.
- [ ] Record reviewed acceptance ontology version separately from old labels.

### 3. Security and reliability
- [ ] Verify all regression tests on the integration branch in GitHub CI.
- [ ] Require signed, scoped authorization before atomic admission.
- [ ] Verify receiver-bound signed acknowledgements and crash recovery.
- [ ] Confirm no live dispatch transport, keys or credentials are enabled.
- [ ] Threat-model issuer/receiver trust, tenant isolation, revocation,
  key rotation, receipt replay and operational rollback limitations.
- [ ] Independently check the exact receiver and outbox code versions.
- [ ] Add actual process termination tests when environment is available;
  SQLite restart tests alone do not establish process-crash resilience.

### 4. Final merge gate
- [ ] Full CI green on a commit with a common ancestor to main.
- [ ] Review approval recorded for the **current** commit, not older code.
- [ ] Critical safety and data-provenance issues closed or explicitly
  documented as blockers.
- [ ] User explicitly approves merging after reviewing the exact diff.

## Evidence boundary
Engineering tests and mock demonstrations do not substantiate historical
JEVEEB field work, contractor payments or a $700,000 SR&ED expenditure.
Never backdate generated records or convert proposed labels into signed
reviewer conclusions.

## Next engineering work
Start with source reconciliation and verified Q1-E01 review. No branch
merge or production action is authorized by this checklist.
