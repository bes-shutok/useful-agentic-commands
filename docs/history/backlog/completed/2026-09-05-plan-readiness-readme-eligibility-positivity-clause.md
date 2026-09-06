Status: done
Workflow: backlog
Date: 2026-09-05
Severity: Low
Scope: agents/hooks/plan-readiness/README.md

Source: code-review r5 of the plan-readiness-migration branch (correctness-completeness, Minor/Low); deferred at the max_review_rounds budget.

Problem: the hook README Verdict representation section states the deletion eligibility gate as only `covered equal to total over the live plan-review corpus`, while the sweep print and the spin-off deletion item both gate on `total is positive and covered equals total`. A maintainer reading only the README could treat an empty corpus (0/0, sweep exit 0) as eligible.

Suggested fix: change the README sentence to `eligible only once `--sweep` coverage reports a positive total with covered equal to total over the live plan-review corpus`.
