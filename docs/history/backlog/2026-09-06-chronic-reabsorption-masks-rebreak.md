# Chronic re-absorption: repair-then-rebreak of the same sidecar stays note-silent

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-06-2026-09-05-summarizer-round-3-residuals-code-review-r2.md, round r2, finding F5 (Low, non-blocking), risk worker; deferred at orchestrator direction (accepted design limit)

## Problem

Chronic membership in the set-based retry-delta (`retry_drops = unparseable_now - chronic`) is decided from the initial-buffer parse state. A sidecar that was unparseable at init (chronic), repaired, then re-broken inside the same retry window is still excluded from `retry_drops` even though its final state is retry-induced, so a retry-induced parse drop can leave the operability stderr note silent in that double-flip window. The consequence is bounded to the note: exit code, published report, and ledger remain correct by design (the plan's invariant). Requires two successive mutations of the same chronic sidecar in one retry window; not produced by the existing test hook pattern.

Pattern: security#chronic-reabsorption-masks-rebreak.

## Location

`scripts/summarize_review_stats.py`, `_publish` closure inside `cmd_strict_audit` (the `chronic = set(ledger["unreadable"])` / `retry_drops = unparseable_now - chronic` lines, ~line 2301).

## Suggested fix

Candidate direction: key chronicity on per-attempt parse transitions (a sidecar unparseable at init AND unparseable at publish stays chronic; one that became parseable and then unparseable again within the retry window counts as retry-induced) instead of the initial-buffer snapshot alone. Only worth closing if the note silence ever matters operationally.

## Severity and source reference

Low, non-blocking; theoretical reachability, local blast radius. Review doc path above, round r2, finding F5.

## Why not fixed now

Deferred by orchestrator direction (2026-09-06 r2 fix pass): accepted design-limit residual of plan item 3 (docs/plans/2026-09-05-summarizer-round-3-residuals.md); the plan's invariant keeps exit code, report, and ledger unaffected.
