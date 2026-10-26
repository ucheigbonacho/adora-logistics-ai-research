# Blind driver-intent validation protocol — 2026-10-26

**Status: prospective evaluation protocol, NOT a completed field experiment.**

## Purpose
Measure how the repaired Q1-E01 classifier generalizes beyond the six
user-reported cases that guided its revision. A 6/6 match on those cases
is a development-set result, not evidence of independent generalization.

## Before testing
1. Assign a qualified domain reviewer not involved in writing the
   classification rules, where practical.
2. Collect authentic, permissioned, de-identified driver utterances from
   a defined source and period. Record the source and consent/privacy
   handling. If no such records exist, do not invent them.
3. Exclude the six Q1-E01 V01–V06 development cases and exact duplicates.
4. Freeze a classifier commit SHA before revealing labels.
5. Have the reviewer label cases **without seeing model predictions**.
6. Use the draft v0.1 ontology only if genuinely approved; otherwise
   document the approved replacement version.
7. Capture uncertainty, missing context and reviewer disagreements.
8. Store source provenance, review timestamps and approval separately
   from any model-generated output.

## Acceptance gates (proposed, not pre-approved)
- Zero raw-utterance cases classified as independently authorized
  execution, regardless of accuracy.
- Report per-category precision, recall, confusion matrix and coverage.
- Report sample size, class distribution, abstentions and confidence
  intervals; do not claim production accuracy from a small convenience set.
- Independently inspect every false execution-related classification.
- Define numerical release thresholds with the domain owner **before**
  the blind evaluation, not after seeing results.

## Execution and audit
- Use `validation.reviewed_reference` only after genuine review metadata
  is available and verified.
- Retain original utterances under appropriate access controls; keep a
  de-identified case index in the repository where safe.
- Preserve mismatches and exceptions. Never silently change labels.
- Archive the exact code SHA, inputs, output, run logs and reviewer
  sign-off as distinct artifacts.
- Never copy live driver recordings or personal data into a public repo.

## Important scope boundary
No blind reference dataset has been supplied or generated here.
No independent accuracy result is claimed. EXP-15/16 remain future
planned Q4 work. No production dispatch or merge is authorized.
