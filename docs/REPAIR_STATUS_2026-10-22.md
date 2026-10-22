# Engineering repair status — 2026-10-22

This branch contains current-day engineering repairs. It does **not** establish
that historical experimental work occurred, that data was collected from
production, or that project expenditure is eligible for SR&ED.

## Confirmed repairs
- Restore the missing `src.rules` import by forwarding to `src.engine`.
- Add safety tests for non-authorizing route questions and proposals.

## Unresolved release blockers
- EXP-09 scenario 09-09 expects two actions for a sequence containing
  `alternate_gating`. The expected result requires product-owner review;
  do not weaken the classifier solely to make the test pass.
- The 34-case independent validation contains a disputed route-proposal
  expectation; retain original fixture for audit traceability.
- Eight 120-case datasets use labels that differ from engine outputs.
  A label mapping can reconcile names, but it is not independent accuracy
  evidence. Do not replace original results.
- Dataset generation computes expected answers from the same engine under
  test; such results are not independent validation.
- EXP-15 and EXP-16 are absent from the inspected main snapshot.
- Some raw paths are LFS pointers; Q4-E01 raw input is empty.
- Trusted identity provider, signed approval issuance, outbox delivery,
  receiver acknowledgement and recovery are not integrated end-to-end.
- Original contemporaneous research, work hours, invoices and payments
  must be substantiated separately.

## Verify
```sh
python -m unittest discover -s tests -v
python -m validation.run_validation
```

No production deployment or final readiness is claimed by this branch.
