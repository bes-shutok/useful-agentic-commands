# Backlog: sidecar verdict field and legacy verdict-grammar deletion

Status: done
Workflow: backlog
Resolution (2026-09-05, plan-readiness-migration): producer + schema + consumer precedence landed (`review-plan` writes the `verdict` field, the version-1 schema type-checks it, `evaluate_readiness` prefers the sidecar field with the Summary rule as legacy fallback, plus the sweep coverage counter and review-loop pre-round wiring); the deletion half is spun off to `docs/history/backlog/2026-09-05-plan-readiness-legacy-verdict-grammar-deletion.md`.
Source: 2026-09-03 reviewed-plan-readiness-gate plan, code review r4 finding X1 (reconciliation directive, items 4-5)
Severity: Low (representation migration once corpus ages out)
Scope: scripts/plan_readiness.py, review-plan producer contract, validator-pass plan

## Problem

The readiness validator's consumer verdict rule is a TOTAL rule over the
review Markdown `## Summary` (any line with a word-bounded `ready=yes` /
`ready=no` token; last occurrence wins), adopted by r4 reconciliation after
the prefix/label grammar missed attested corpus shapes three review rounds in
a row. The rule is total to stay robust over the pre-adoption corpus, but the
durable representation should be structured: a `verdict` field in the
`.stats.json` sidecar, with the Summary grammar as a legacy fallback only.

## Suggested fix

Belongs to the validator-pass plan:

- Add a `verdict: "yes" | "no"` field to the sidecar schema (producer:
  `review-plan` writes it alongside the canonical Summary line).
- Consumer precedence becomes: sidecar verdict field > Summary last-token
  rule (documented in `agents/hooks/plan-readiness/README.md`).
- Once the pre-adoption corpus ages out (no live `*-plan-review-*.md` under
  `{reviews_dir}` lacks the sidecar verdict field), delete the legacy Summary
  grammar from `plan_readiness.py` and keep `--sweep` as the drift detector.

Related follow-up in the same family: wire `plan_readiness.py --sweep` into
`review-loop` as a pre-round check so verdict-shape drift is caught before a
round starts rather than at gate time.

## Acceptance criteria

- Sidecar verdict field specified in the staging schema and written by
  `review-plan`.
- `plan_readiness.py` prefers the sidecar field and falls back to the Summary
  rule while legacy artifacts remain.
- The legacy grammar deletion lands only after the corpus sweep confirms no
  remaining pre-adoption artifacts.
