# Backlog: delete legacy Summary verdict grammar from plan_readiness

Status: open
Workflow: backlog
Source: 2026-09-04-plan-readiness-sidecar-verdict-field acceptance criterion 3 (legacy grammar deletion lands only after the corpus sweep confirms no remaining pre-adoption artifacts), spun off by the 2026-09-05 plan-readiness-migration plan
Severity: Low (time-gated)
Scope: scripts/plan_readiness.py

## Problem

The Summary total-rule grammar remains in `evaluate_readiness` as the legacy
fallback for pre-adoption artifacts: when a round's sidecar lacks a conforming
`verdict` field, the verdict is established by scanning the review Markdown
`## Summary` for word-bounded `ready=yes` / `ready=no` tokens (last occurrence
wins). The migration plan added the sidecar verdict field and the consumer
precedence rule, but deliberately kept the fallback while any live artifact
predates the producer contract.

## Eligibility gate

Eligible only when `python3 scripts/plan_readiness.py --sweep` prints coverage
with total is positive and covered equal to total: every live `*-plan-review-*.md` under `{reviews_dir}`
has a sidecar carrying a conforming `verdict` field (`yes` or `no` string).
Until then the fallback must stay; deleting it early would newly fail readiness
for every pre-adoption artifact.

## Verdict-source drift disposition

Deleting the fallback also ends the only verdict-source drift signal that
compares the sidecar against the artifact prose. The fix must do one of the
following:

- add a sweep anomaly for a conforming sidecar `verdict` that contradicts the
  artifact Summary's last verdict token (keeping drift detection alive on the
  sweep side), or
- explicitly record the end of Summary-token drift detection as an accepted
  consequence of the deletion (once the sidecar field is the sole verdict
  source, a stray Summary token can no longer flip readiness and need not be
  monitored).

## Suggested fix

Delete the Summary fallback path from the verdict step of `evaluate_readiness`
(keep the sweep's mention detector), keeping the sidecar `verdict` field as the
sole verdict source. Remove the now-dead `VERDICT_TOKEN_RE` machinery and its
comment block, update the selftest fixtures that pin the fallback behavior, and
update the precedence documentation in `agents/hooks/plan-readiness/README.md`
and `agents/skills/review-plan/SKILL.md` to drop the fallback clause.
