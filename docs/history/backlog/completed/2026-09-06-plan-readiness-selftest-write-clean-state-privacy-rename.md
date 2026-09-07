# Backlog: plan_readiness selftest `write_clean_state` privacy-underscore rename

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-06-plan-readiness-polish-code-review-r1.md (code review r1, finding F2, Low, non-blocking)
Severity: Low
Scope: scripts/plan_readiness.py

## Problem

Module-level selftest helpers in `scripts/plan_readiness.py` have inconsistent privacy prefixes: `_clean_reviews_dir`, `_review_markdown`, `_clear_sidecar`, and all `_selftest_*` functions are underscore-prefixed, but `write_clean_state` is exported at module level without the underscore despite being selftest-only (definition near line 645, plus roughly a dozen call sites across the `_selftest_*` fixture runners). Readers may assume `write_clean_state` is a public API of the module rather than a selftest fixture writer.

## Suggested fix

Mechanical rename `write_clean_state` → `_write_clean_state` at the definition and every call site; re-run `python3 scripts/plan_readiness.py --selftest` (expect 90 PASS, ALL PASS).

## Why not fixed now

Deferred because the executing plan (docs/plans/2026-09-06-plan-readiness-polish.md, Task 3) pins the helper name `write_clean_state` verbatim ("`write_clean_state`, `_review_markdown`, and `_clear_sidecar` keep their signatures and semantics and move to module level"), so renaming on this branch would contradict the reviewed plan prescription. Decision made by the address-review pre-authorization (defer with durable backlog capture where the executing plan's pinned text blocks the fix).
