# Branch source inventory and integration plan — 2026-10-26

**Preparation only. No merge, force-push, history rewrite or production dispatch.**

## Verified heads
- Main: `19da3bd5cfdd15c4e822888fee051aca4114490d`
- Repair: `37bd5fb84a5d5caebfd3f32c26236e45c3cecaff`
- Latest completed repair GitHub Actions run: **success**.
- Pull request #1: closed, **not merged**.
- GitHub compare API: **no common ancestor** between these branch refs.

## File-level reconciliation

Repository tree comparison returned **73 tracked blobs on main** and
**120 tracked blobs on repair**. Counts describe inventory, not quality.

Identical Git blob hashes on both branches:
- `src/evaluate.py` and `src/generate.py`
- `tests/test_engine.py`, `tests/test_exp09.py`, `tests/test_exp12.py`
- `validation/baseline.py`, `validation/independent_cases.jsonl`,
  `validation/run_validation.py`, `validation/case_results.csv`,
  `validation/summary.csv`

Different Git blobs on both branches:
- `src/engine.py`: main uses keyword-triggered `authorize_intent`;
  repair delegates Q1-E01 to fail-closed `src.authorization`.
- `src/rules.py`: main contains a separate implementation with
  action-ID-only authorization and differing Q4 output labels; repair
  re-exports the canonical `src.engine`.

Files only present on main:
- `reviewer_approval.txt` — attributed to Chika Ibegbu, dated 2026-10-26.
  Its claimed 34/34 result is not yet independently reconciled.

Notable repair-only additions:
- `src/authorization.py`, `src/trusted_gateway.py`,
  `src/atomic_dispatch_admission.py`, `src/dispatch_outbox.py`,
  `src/local_receiver.py`, `src/receipt_protocol.py`,
  `src/signed_local_dispatch.py`.
- New security/recovery/transaction regression tests.
- `validation/reviewed_reference.py` and
  `validation/audit_legacy_labels.py`.
- CI workflow and documented review/acceptance criteria.

## Safe eventual integration sequence (NOT AUTHORIZED YET)
1. Preserve both branch heads and the main reviewer approval record.
2. Start a new integration branch from the **then-current** main commit.
3. Bring across the canonical rule compatibility and safe authorization
   changes, then the atomic admission/receiver modules and their tests.
4. Keep `validation/independent_cases.jsonl` and historical summaries
   unchanged; report differences in new output artifacts.
5. Keep any newly approved reference labels separately versioned and
   verifiably signed off; do not infer approval from the existing summary.
6. Run all regression tests and read-only compatibility evaluation.
7. Inspect all changes and review the security boundary before seeking
   explicit approval to merge.

## Unresolved blockers
- Six Q1-E01 classifications require actual reviewer-approved outcomes,
  not only a generalized 34/34 statement.
- The current main reviewer approval and old summary are inconsistent
  with the repaired engine's label taxonomy.
- Current source-history divergence must be reconciled without erasing
  either history.
- Production identity provider, external TMS and real receiver remain
  unintegrated; live dispatch is disabled.
- EXP-15 and EXP-16 remain planned future Q4 work.

This inventory is based on GitHub branch trees and known source files,
not a claim that an independently verified field experiment occurred.
