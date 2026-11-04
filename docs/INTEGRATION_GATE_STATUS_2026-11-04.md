# Integration gate status — 2026-11-04

**Draft PR #2; do not merge.**

Integration branch was created from main commit
`19da3bd5cfdd15c4e822888fee051aca4114490d`,
and 23 selected repair source/test files were staged without changing
the original research data or historical experiment fixtures.

CI run https://github.com/ucheigbonacho/adora-logistics-ai-research/actions/runs/41815135287
executed 77 tests and failed one:
`test_exp09.Experiment9Tests.test_all_expected_idempotency_gating_states`
for scenario `09-09`.

Main's historical `experiments/EXP-09/scenarios.jsonl` expects
`applied = ["TXN-A01", "TXN-A02"]` for a second dispatch intent
with text `alternate_gating`. The integrated fail-closed behavior
returns only `["TXN-A01"]`. The repair branch's source scenario differs.
This is a **historical fixture versus safety semantics conflict**;
do not silently change the original historical fixture or loosen
authorization to force the test green.

Required next steps:
1. Preserve the original historical expected result and source file.
2. Review whether `alternate_gating` was ever legitimately authorized,
   using actual historical test method and source evidence.
3. Document a separately versioned current-safety acceptance case and
   retain the historical discrepancy in the audit evidence register.
4. Run a full integration regression on the new acceptance policy,
   without misrepresenting the original historical test as passing.
5. Independently review all 23 selected source/test files, confirm
   production dispatch is disabled, and obtain user approval before merge.

The repair branch's 2026 Q3 enriched cases, provenance notes and other
validation files have not been copied into this first integration stage.
EXP-15 and EXP-16 are not included. This is a partial integration,
not a release or an SR&ED evidence certification.
