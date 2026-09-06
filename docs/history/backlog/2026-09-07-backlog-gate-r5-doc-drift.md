# Backlog: backlog-gate hardening r5 doc-consistency residuals

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-06-backlog-gate-hardening-code-review-r5.md (two Low, non-blocking findings; deferred at the 5-round cap to avoid mutating the reviewed digest after the final clean round)
Severity: Low
Scope: scripts/check_backlog_inbox_location.py (selftest docstring), docs/plans/completed/2026-09-04-backlog-gate-hardening.md (annotations only)

## Items

1. `consistency#hot-dirs-fixture-arm-count-mismatch`: `_selftest_hot_dirs_key_repo` docstring says "Six arms:" but enumerates only six of the now-seven arms (aac741e added `dotdot-prefixed-name`); sibling fixtures were bumped. Fix: "Seven arms:" plus the (7) enumeration line.

2. `consistency#plan-first-segment-annotation-gap`: the archived plan's Gist item 3 still says invalid entries are "`..`-prefixed" and Task 4's GREEN-line annotation stops at the sixth arm; the shipped first-segment semantics and seventh arm are unannotated (embedded code snippet intentionally left as the historical prescription). Fix: one-line Gist amendment plus the seventh-arm/r4 annotation parenthetical.

## Why not fixed now

Both are documentation-only and mutate the reviewed diff; fixing them post-r5 would invalidate the fresh clean round at the budget cap. Fold at the next legitimate touch of the script or plan.
