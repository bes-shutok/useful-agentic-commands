Status: open
Workflow: backlog
Date: 2026-09-05
Severity: Low
Scope: scripts/plan_readiness.py

Source: code-review r1 of the plan-readiness-migration branch (design-simplicity worker, architecture#god-method-growth); deferred as out of the plan's Review Scope freeze.

Problem: `run_selftest` in `scripts/plan_readiness.py` spans over 1200 lines after the 2026-09-05 plan-readiness-migration additions. Each fixture family repeats the same write-state / mutate-sidecar / run / check / cleanup loop, and the cleanup loop (`for path in reviews_dir.iterdir(): path.unlink()`) recurs per fixture. The code review r1 of 2026-09-05 flagged the growth; a prior r6 fold (sweep-fixture leftover state) demonstrated the convention's cost.

Suggested fix: extract a fixture context helper (write state, yield, clean the reviews dir on exit) or per-family functions called from `run_selftest`. Behavior-preserving refactor; keep fixture names and check output identical so the selftest contract and any grep pins on fixture names stay stable.
