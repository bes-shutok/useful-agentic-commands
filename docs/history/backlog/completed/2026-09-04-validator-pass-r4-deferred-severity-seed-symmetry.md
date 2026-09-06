# Validator pass r4 deferred: align severity-seed convention between the two apply_events calls

Status: done (executed via plan 2026-09-05-validator-pass-r4-deferred-residuals, branch 2026-09-06-validator-pass-r4-residuals)
Workflow: backlog
Source: docs/reviews/2026-09-02-validator-pass-code-review-r4.md F3 (quality#inconsistent-seed-convention); deferred per fix-risk stop (the asymmetry was itself created by the r3 F3 fix)

## Problem

In `parse_markdown_findings`, the non-fallback `apply_events` call passes the local `current_severity` while the fallback call passes literal `None`; both are provably the same value today (the local is initialized None and never reassigned before either call), but a reader must re-derive that to see the branches are symmetric.

## Suggested fix

Pass literal `None` in both calls (or seed both from the local) so the symmetry is visible without the comment. One-line change plus comment touch-up; behavior identical (fence family characterizes both paths).
