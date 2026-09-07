# Backlog: plan_readiness VERDICT_TOKEN_RE comment still carries pre-fix eligibility wording

Created: 2026-09-06
Status: done
Origin: code review r5 F1, docs/reviews/2026-09-06-plan-readiness-polish-code-review-r5.md (plan-readiness-polish execution, Phase 3)

The module comment above VERDICT_TOKEN_RE in scripts/plan_readiness.py (line 68) still reads "(eligible only once `--sweep` coverage reports covered equal to total)" is the exact wording the plan-readiness-polish plan's Task 1 corrected in agents/hooks/plan-readiness/README.md, missing the positive-total clause that run_sweep's gate actually enforces ("total is positive and covered equals total").

Suggested fix: one-line comment edit to "...reports a positive total with covered equal to total" so the comment matches the README and the executable gate. Comment-only; no behavior change; the README forbidden sweep does not cover this copy.
