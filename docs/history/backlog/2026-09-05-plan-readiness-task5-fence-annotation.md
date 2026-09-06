Status: open
Workflow: backlog
Date: 2026-09-05
Severity: Low
Scope: docs/plans/2026-09-05-plan-readiness-migration.md (archived copy)

Source: code-review r5 of the plan-readiness-migration branch (contract-docs, Low); deferred at the max_review_rounds budget.

Problem: the plan's Task 5 fenced review-loop paragraph records the narrow non-zero-exit wording, while the shipped agents/skills/review-loop/SKILL.md paragraph (broadened in review r3 to name missing reviews_dir and sibling compat failure) carries no divergence annotation, unlike the plan's other fence-vs-shipped divergences.

Suggested fix: in the archived plan copy, append one annotation line after the Task 5 review-loop fence: shipped paragraph broadens the non-zero-exit meaning (r3 review fix); the fence records the prescription, not the final bytes.
