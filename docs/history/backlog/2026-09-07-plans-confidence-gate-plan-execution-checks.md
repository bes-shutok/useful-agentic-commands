# Backlog: confidence-gate plan execution-check residuals (r6 F1-F3)

Status: open
Workflow: backlog
Source: review-plan r6 residuals on docs/plans/2026-09-07-plans-facts-do-not-resolve-design-ambiguity.md (2026-09-07, ready=yes zero blocking; residuals valid but unfixed because the plan bytes are digest-frozen at certification and the reconciliation round budget was spent)
Severity: Low
Scope: Task 7/8 execution checks of the implementing plan above; apply as a plan amendment at execute-plan start (the post-execution review round re-certifies the amended bytes)

## Findings

1. Task 8 scope-integrity equality omits session-owned artifacts: `<base>..HEAD` touched-path set must include the plan doc itself (per-task checkbox commits) and review artifacts, and the done commit-all path must be fenced, or the equality gate false-fails on correct execution.
2. Task 1's RED-today sweep step is ordered after the edits it must precede; move the pre-edit sweep item above the edit items (or mark it "run before the first edit of this task").
3. The em-dash Validation Command lists `scripts/plan_readiness.py`, but the scanner skips non-prose extensions unless `CHECK_NO_EM_DASH_ALL=1` is set; prefix the variable or drop the .py operand.

## Acceptance criteria

- The implementing plan's Task 1 ordering, Task 8 invariant, and em-dash command carry the corrections above before or during execution.
- The corrections are folded as plan amendments, never as post-certification silent edits: the executing session's review round certifies the amended digest.

## Not part of this backlog item

- No changes to the shipped skill or script content; all three residuals concern the plan document's own execution checks.
