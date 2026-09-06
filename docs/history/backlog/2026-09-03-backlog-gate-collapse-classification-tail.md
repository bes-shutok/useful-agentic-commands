# Backlog inbox gate: collapse duplicated classification tail in scan_repo

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-03-backlog-inbox-location-gate-code-review-r3.md, round r3, finding F10, design-simplicity worker
Plan context: docs/plans/2026-09-03-backlog-inbox-location-gate.md (branch 2026-09-03-backlog-inbox-location-gate)

## Problem

`scan_repo` in `scripts/check_backlog_inbox_location.py` has two structurally identical classification tails: the rule-1 filesystem-walk loop and the rule-2 `git ls-files` loop both do classify-then-`violations.setdefault`. The duplication can drift if either loop's dedupe semantics is later edited in isolation.

## Location

`scripts/check_backlog_inbox_location.py`, `scan_repo` (rule-1 `os.walk` loop and rule-2 `ls-files` loop).

## Suggested fix

Extract a shared helper (e.g. `_record(rel_path, backlog_home, violations)`) used by both loops, keeping `setdefault` first-wins semantics; add a selftest witness if behavior-equivalence is not obvious by inspection.

## Severity and source

Low (simplification#duplicated-classification-tail). Staging doc r3 F10.

## Why not fixed now

Taste-adjacent refactor with regression risk exceeding benefit in this round; deferred by the r3 address pass (execute-plan Phase 3) per the fix plan.
