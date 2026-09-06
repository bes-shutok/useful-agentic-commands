# Validator-residuals plan r5 residual cosmetic Lows (3)

Status: done (folded by docs/plans/completed/2026-09-05-certified-plan-prose-residue-sweep.md, executed 2026-09-06)
Workflow: backlog
Source: docs/reviews/2026-09-05-plan-review-validator-pass-r4-deferred-residuals-r5.md (non-blocking Lows; regenerating cosmetic class at the review cap, backlogged per the churn-control bound instead of a sixth round)

## Findings (all in docs/plans/2026-09-05-validator-pass-r4-deferred-residuals.md)

1. Task 2 helper snippet uses a quoted return annotation `"Iterator[io.StringIO]"`; prefer the unquoted form with the modern import.
2. Validation Commands use `grep -nq " ;" ...`; the `-n` flag is redundant under `-q`.
3. Task 1 carries a fixture-coupled rationale comment that could be shortened when the plan is next edited.

All three are cosmetic; none affect any gate. Fold opportunistically if the plan is ever updated for a real reason; do not reopen a review round for them alone.
