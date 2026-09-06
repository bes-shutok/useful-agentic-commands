# Backlog: docs-branch: register cleanup trap before the restore region to close the interrupt-window leak

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-04-2026-09-03-docs-branch-temp-file-hygiene-code-review-r1.md, round r1, finding F5 (Low, security#temp-file-cleanup-window-before-trap-registration)

## Problem

In the docs-branch Step 2 script (`agents/skills/docs-branch/SKILL.md`), the
`docs_branch_cleanup` trap registers only after the restore region (the
`git show-ref` block, ~lines 195-251 in the r1-reviewed revision). During that
window a SIGINT/SIGTERM or a `set -e` abort leaks the three mktemp files
(`DOCS_STAGED_DELETES_FILE`, `RESTORED_PATHS_FILE`, `DOCS_TMP_SWEEP_FILE`).
Contents are repo-relative path names with 0600 modes; disk hygiene only, no
disclosure. Pre-existing (not introduced by the temp-file hygiene plan, which
fixed only the SHADOW_PATHS-empty early-exit leak).

## Suggested fix

Move the trap registration (and, as needed, the `docs_branch_cleanup` function
definition) above the first mktemp call in the restore region, so the three
files are trap-covered from creation. Blocked for now by the temp-file hygiene
plan's Assumptions, whose fix-risk triage forbids reordering the restore region
(regressed in r2 leak / r5 use-after-delete); revisit with a dedicated plan that
re-runs the full probe suite against the reorder.

## Why not fixed now

Out of scope by plan Assumptions (fix-risk triage: restore region regressed
r2/r5); decision made by the execute-plan Phase 3 round 1 address worker
(2026-09-04), per orchestrator direction to defer with a durable backlog item.
