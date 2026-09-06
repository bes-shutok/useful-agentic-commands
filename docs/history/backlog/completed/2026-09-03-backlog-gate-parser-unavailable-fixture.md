# Backlog: selftest fixture for the facts-parser-unavailable branch

- Date: 2026-09-03
- Status: done
- Origin: execute-plan Phase 3 r5 review (2026-09-03-backlog-inbox-location-gate), testing lens, deferred at the 5-round cap
- Plan: docs/plans/2026-09-03-backlog-inbox-location-gate.md (archived to docs/plans/completed/)

## Finding

`scripts/check_backlog_inbox_location.py`: no fixture drives the `facts_paths`-is-None
branch (ImportError guard). A mutation that crashes (AttributeError) or drops the
`warning: facts parser unavailable` line ships green; every current fixture runs the
script from its real directory where the sibling import always succeeds.

## Suggested fix

shutil.copy the script alone into a temp dir (no facts_paths.py beside it), run it with
`--repo-root` over a fixture containing a committed pair-token file, and assert exit 1 +
the rule-2 line + `facts parser unavailable` in stderr.
