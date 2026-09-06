# Summarizer + CLI follow-ups: publish-retry stale snapshot race, source-flag triplication

Status: done
Completion: Completed by docs/plans/completed/2026-09-02-summarizer-hardening-round-2.md (executed + reviewed 2026-09-04/05).
Workflow: backlog
Source: docs/reviews/2026-08-28-review-artifact-contracts-code-review-r6.md, round r6, findings F4 + F12 (validated as real defects; deliberately deferred)

## Problem

1. **F4 (`security#publish-retry-stale-snapshot`, Medium)**: fixed 2026-09-01 by docs/plans/2026-09-01-summarizer-publish-lock-hardening.md (the publish-with-recheck path no longer emits a report computed from the originally read, pre-race buffers). F12 below remains open.
2. **F12 (`simplification#cli-source-flag-triplication`, Low)**: the three source-digest CLI flags in `scripts/validate_review_staging.py` triple one wiring and one test shape (argparse entries, empty-value loop, mutual-exclusivity list, if/elif routing); the three selftest families repeat the same five cases over ~200 duplicated lines, with drift already visible (empty-value case only in the plan family, mutual-exclusivity only in the document family) (~line 4045).

## Location

- `scripts/summarize_review_stats.py`, publish retry path (~line 1931).
- `scripts/validate_review_staging.py`, source-flag CLI wiring and selftests (~line 4045).

## Suggested fix

F12: keep the three flags but drive routing and empty checks from one flag-to-kind table, and factor the five-case selftest into one parameterized family run over each kind.

## Severity

Medium (F4; wrong published artifact, no data loss, never observed live), Low (F12).

## Why not fixed now

User policy 2026-08-28: low-risk findings backlogged; the fix-fix cycle was producing more issues than it closed. F4's race was code-traced but never demonstrated live, and F12 is a refactor whose test consolidation should absorb the F9/F10 coverage follow-ups in the same pass. Decision made by the user (orchestrator scoped-fix instruction, 2026-08-28).
