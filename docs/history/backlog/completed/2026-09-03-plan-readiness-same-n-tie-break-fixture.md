# Backlog: plan_readiness selftest: pin same-N cross-date tie-break in latest_round_selection

Status: done
Workflow: backlog
Resolution (2026-09-05, plan-readiness-migration): fixture landed in the selftest's `latest_round_selection` family (`latest_round_selection_tie_break`, both polarities pinned: later-dated `ready=no` fails readiness, later-dated `ready=yes` passes, under adversarial year-2100 mtimes on the earlier-dated pair).
Source: code review r1, 2026-09-03-reviewed-plan-readiness-gate (finding T5)
Severity: Low (test-gap-only; behavior verified correct by code reading in round r1)
Scope: scripts/plan_readiness.py selftest

## Problem

`latest_review_round` in `scripts/plan_readiness.py` resolves same-`r<N>`
ties across dates by filename order (date prefix included), but no
`--selftest` fixture pins that tie-break. Existing fixtures cover different
`r<N>` values and the mtime-is-never-used invariant; deleting or changing the
filename tie-break inside `max(candidates)` would leave the selftest green.

## Suggested fix

Add a `selftest#latest_round_selection_tie_break` fixture: two review
artifacts with the SAME round suffix `r1` but different date prefixes (for the
same feature slug and plan bytes), where the later-dated file carries a
`ready=no` verdict and the earlier-dated one `ready=yes`; expect readiness to
fail with the later-dated filename deciding. Extension of the existing
`latest_round_selection` fixture family.

## Why not fixed now

Deferred at review r1 triage: test-gap-only class (observed behavior is
correct, pinned by code reading this round), low regression risk, and the
round's fix budget went to the blocking and named-fix findings.

## References

- Staging doc: `docs/reviews/2026-09-03-2026-09-03-reviewed-plan-readiness-gate-code-review-r1.md` (finding T5)
- Location: `scripts/plan_readiness.py`, `latest_review_round`
- Re-confirmed by review r2 (2026-09-03, finding V15 in `docs/reviews/2026-09-03-2026-09-03-reviewed-plan-readiness-gate-code-review-r2.md`): the same-N cross-date tie-break fixture is still missing after the r2 fix pass; item remains open.
