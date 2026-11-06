# Technical documentation reporting standard — 2026-11-06

**Purpose:** Consistent, accurate and professional presentation of Adora Logistics AI engineering work, experiments and SR&ED supporting records.

## Standard
1. State the objective, methodology, environment, measured outcome and conclusion in that order.
2. Describe technical differences using the actual metric, affected case, source file and planned reconciliation. Avoid generalized characterizations of the project or contributors.
3. Distinguish original experimental observations, later reproductions, regression checks and independent-reference evaluations by what each test actually measures.
4. Keep technical reports focused on engineering findings; use a separate dated discrepancy register for detailed source-to-source comparisons and open actions. The register remains available for review and is not used to conceal material information.
5. Preserve source datasets, historical approvals, experiment logs, commit objects and reported figures unchanged. Make revisions through clearly dated corrections and traceable version control.
6. Avoid unsupported absolute claims such as guaranteed production exactly-once delivery. Identify simulation, local integration and production behavior accurately.
7. Attribute human work only when supported by project records. Do not invent identities, work dates, approvals or results.
8. Do not insert irrelevant commentary about documentation preparation tools into technical authorship sections. Respond accurately to material questions about development methods if specifically required.
9. Separate technical performance reporting from financial SR&ED eligibility assessments, which require their own supporting records.
10. Before external submission, check all reports against the source files and review open material reconciliation items.

## Examples of preferred language
- **EXP-12:** “The current deterministic reproduction yields 266/800 for the unbuffered strategy, compared with 265/800 in the original summary. The one-case difference is recorded for reconciliation.”
- **Approval:** “The validation case-results file reports 33/34 matches, while the dated approval records 34/34. The test version and approval scope are being confirmed.”
- **Git chronology:** “The listed commits contain the recorded Git timestamps and changes shown in the provenance table. Additional source delivery records will be indexed where available.”
- **Regression:** “The automated regression checks completed successfully for the tested branch and configuration.”

This reporting standard is a presentation guide, **not** permission to suppress material exceptions, change historical evidence or imply tests occurred when they did not.
