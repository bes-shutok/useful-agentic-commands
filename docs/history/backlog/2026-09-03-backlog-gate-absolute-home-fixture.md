# Backlog: selftest fixture for absolute/~ backlog-home anchoring

- Date: 2026-09-03
- Origin: execute-plan Phase 3 r5 review (2026-09-03-backlog-inbox-location-gate), testing lens, deferred at the 5-round cap
- Plan: docs/plans/2026-09-03-backlog-inbox-location-gate.md (archived to docs/plans/completed/)

## Finding

`scripts/check_backlog_inbox_location.py`: the absolute-path and expanduser arms of
`resolve_backlog_home` have no selftest fixture. A regression that re-anchors absolute
facts values against the repo root (dropping the `p.is_absolute()` branch) would leave
the rule-2 backlog-home exclusion dead while `--selftest` stays green.

## Suggested fix

Add a run_case-style fixture: facts with `backlog_dir = "<tmp>/abs-home"` plus a
committed `abs-home/pair-deferred-backlog.md`, asserted absent from reported violations
(mirror of `_selftest_hot_dir_home_repo`).
