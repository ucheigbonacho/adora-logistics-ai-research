# EXP-16 technical uncertainty assessment and evidence gate — November 10, 2026

## Verified scope of current evidence
Ten owner-confirmed actual Q4 November 2026 operational/test records contain utterances, signal metrics, ETA and connectivity fields, with recorded outcomes `escalate` or `routine`. The score threshold agreed in 8/10 cases; a post-hoc ETA-late rule agreed in 10/10. These outcomes describe operational escalation, **not** whether a voice command should be authorized, rejected or clarified. Neither result establishes independently reviewed voice-intent accuracy or technological advancement.

## Distinct candidate investigations
**A. Operational escalation decision under incomplete context.** Question: When ETA and connection-state signals conflict, become stale or are missing, can a decision method preserve safety-critical escalation while limiting unnecessary alerts? Existing rules and conventional decision tables are the baseline. A prospective holdout with independently reviewed operational outcomes is needed to establish whether the issue remains unresolved.

**B. Voice dispatch authorization under ambiguous intent and asynchronous state.** Question: Can an authorization mechanism correctly resolve ambiguous or contradictory operator utterances when confirmation tokens, telemetry state and authorization status change asynchronously? This requires separate, independently adjudicated `authorize`/`reject`/`clarify` labels and actual command/confirmation context. The current ten `escalate`/`routine` labels cannot answer this question.

## Established-technique check
Before asserting technological uncertainty, review standard threshold and rule-based classification, finite-state authorization, token binding, fail-closed handling, stale-message rejection, independent adjudication and existing speech-intent classification methods. Record which methods were actually tried, measured limitations and why routine application could not satisfy a specified requirement. A failure to achieve a preferred business metric alone is not necessarily SR&ED technological uncertainty.

## Prospective evaluation prerequisites
1. Preserve original operational/test records and their SHA-256 manifest.
2. Create a separate reviewer-approved authorization-label record for each case used in investigation B. Never infer authorization labels from `expected`, `verified_dispatch_auth`, or an existing classifier.
3. Freeze hypotheses, baseline, comparison methods, acceptance criteria, failure cases, dataset selection and review protocol **before** inspecting new holdout outcomes.
4. Include contradictory/missing ETA, stale connection state, ambiguous utterances, mismatched confirmations and duplicate event IDs where actually observed or in separately identified controlled test scenarios.
5. Record raw observations, errors, environment, code revision, dated investigator decisions and follow-up iterations.
6. Keep routine dispatch operations and standard integrations outside the experimental cost allocation.

## Current decision
**Do not claim EXP-16 has demonstrated a technological advancement.** The existing operational records establish an exploratory baseline and identify cases for investigation. Continue only with separately documented operational holdout review and independently labeled authorization testing; do not create labels or assert reviewer sign-offs without evidence.

This document is a current engineering assessment, not a retroactive historical experiment record or a CRA eligibility determination.
