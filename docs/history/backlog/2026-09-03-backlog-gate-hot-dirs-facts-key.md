# Backlog inbox gate: externalize hot dirs to a facts key

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-03-backlog-inbox-location-gate-code-review-r3.md, round r3, finding F9, design-simplicity worker
Plan context: docs/plans/2026-09-03-backlog-inbox-location-gate.md (branch 2026-09-03-backlog-inbox-location-gate)

## Problem

`HOT_DIRS` in `scripts/check_backlog_inbox_location.py` (`docs/maintenance`, `docs/architecture`, `docs/tmp`) hardcodes this repo's docs-layout conventions in a gate the shared `done` skill runs in every vendored repo. In a repo with a different layout, rule 1 silently no-ops (no dirs match), so untracked misfiled inbox files inside that repo's actual hot dirs are invisible; only rule 2 (tracked pair-token files) still fires.

## Location

`scripts/check_backlog_inbox_location.py`, module constant `HOT_DIRS` / `HOT_DIR_PARTS`.

## Suggested fix

Externalize as an optional `.ai-playbook/facts.md` TOML key (e.g. `backlog_hot_dirs`, list of repo-relative dirs) with the current three as fallback defaults, mirroring the existing `backlog_dir` resolution pattern; at minimum, document the degradation in the script docstring and README row.

## Severity and source

Low (architecture#hardcoded-convention-in-shared-gate). Staging doc r3 F9.

## Why not fixed now

Architecture change beyond this plan's scope (touches the facts contract shared with `bootstrap-ai-playbook` and vendored consumers); deferred by the r3 address pass (execute-plan Phase 3) per the fix plan.
