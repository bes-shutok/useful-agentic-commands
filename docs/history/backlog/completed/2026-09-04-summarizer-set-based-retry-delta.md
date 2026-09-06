# Summarizer parse-drop delta uses set-based retry-delta detection (mask scenario)

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-04-2026-09-02-summarizer-hardening-round-2-code-review-r1.md, round r1, finding F4 (Low, non-blocking), correctness-completeness worker; deferred at orchestrator direction (fix 8 / defer 2 pass)

## Problem

The retry-induced parse-drop note in the `_publish` closure of `cmd_strict_audit` computes `delta = dropped - len(ledger["unreadable"])` (count-based subtraction of the pre-race chronic population from the post-refresh drop count). Mask scenario: when one chronically unreadable sidecar is repaired at the retry while a different sidecar is broken in the same retry window, both terms move and `delta` returns to 0, so the `dropped {delta} unparseable sidecar(s) (retry-induced)` note stays silent even though a genuine retry-induced drop occurred. The note is the only publish-time signal that a sidecar's bytes were dropped from the published report; exit code, published report, and the `classes=` summary are unaffected.

The formula is exactly what the certified plan (docs/plans/2026-09-02-summarizer-hardening-round-2.md, Task 3) prescribes, so this is a plan-inherited mechanism limitation, not implementation drift; fixing it mid-run would deviate from the certified plan's mechanism.

## Location

`scripts/summarize_review_stats.py`, `_publish` closure inside `cmd_strict_audit` (the `delta = dropped - len(ledger["unreadable"])` line).

## Suggested fix

Compute the delta against the refreshed classification instead of the initial count: capture `chronic = set(ledger["unreadable"])` at classification time and emit the note when any path that is unparseable at publish time is not in `chronic` (set membership, not count subtraction). Add a selftest arm in the `strict_audit_stale_snapshot` family: two sidecars, one chronic-unreadable repaired by the hook at the retry while the hook simultaneously breaks the other; expect the note to fire with count 1. Requires a small plan or plan amendment since the certified plan pins the count-based formula in Task 3's wording.

## Severity and source reference

Low, non-blocking; theoretical reachability, local blast radius. Review doc path above, round r1, finding F4.

## Why not fixed now

Deferred by orchestrator instruction (2026-09-04 fix pass): the implementation matches the certified plan's prescribed formula; changing the mechanism belongs in a future plan that can also amend the plan-pinned wording and add the masking-scenario arm.
