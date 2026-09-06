# Backlog: version constant and sibling compatibility check for the validators

Status: done (unification half 2026-09-04; detection/backstop half 2026-09-05, see final resolution)
Workflow: backlog
Resolution (2026-09-05, plan-readiness-migration): the unification half was already done 2026-09-04 (runtime scripts symlinked to repo canonical copies); the detection/backstop half landed as the consumer-side-only COMPAT_VERSION handshake (`validate_review_staging.py` declares `COMPAT_VERSION`, `plan_readiness.py` checks it at every launch, failing loudly on missing or mismatched value; the both-stale-consistent case stays invisible and is documented as the accepted Low-severity residual). The origin acceptance criterion `both validators' selftests cover the mismatch path` is deliberately narrowed to: plan_readiness's selftest covers the mismatch and missing-constant paths while vrs's selftest covers the constant declaration (a mutual check is impossible without an import cycle).
Source: 2026-09-03 reviewed-plan-readiness-gate plan, code review r4 finding X12
Severity: Low (stale-copy silent drift)
Scope: scripts/plan_readiness.py, scripts/validate_review_staging.py (validator-pass territory)

## Problem

`plan_readiness.py` imports digest, schema, sidecar-path, and review-parsing
rules from `validate_review_staging.py` in its own directory, and
`validate_review_staging.py` itself shares modules with its siblings. Neither
carries a version constant or a sibling compatibility check, so a partially
updated deployment (one file refreshed, a sibling left stale) can drift
silently: imports still resolve, but semantics diverge between copies.

## Suggested fix

Belongs to the validator-pass plan: introduce a shared version constant (or
protocol handshake) that each validator checks against its imported siblings
at startup, failing loudly on mismatch. Do not bolt a one-off check onto only
one script; design it as a cross-module convention in the same pass that
consolidates validator behavior.

## Acceptance criteria

- A version/compat mismatch between deployed sibling validators produces a
  named error (not silent behavior drift).
- Both validators' selftests cover the mismatch path.

## Addendum (code review r5 Y9, 2026-09-04): repo-local shadow direction

The staleness hazard runs in BOTH directions. The gate carriers
(`execute-plan` Step 0.5, `done` Step 1.5) resolve the validator via
env-var override, then a REPO-LOCAL `scripts/plan_readiness.py` copy, then
the deployed `~/.ai-playbook/scripts/` runtime copy. A stale repo-local
copy can therefore shadow a NEWER deployed validator (repo-local shadows
deployed), not just the sibling-to-sibling drift described above. Fold this
direction into the same version-constant/handshake design: the handshake
must also make "repo-local copy is older than the deployed copy" visible
instead of silently preferring the repo-local file.

## Addendum (2026-09-04, deploy-decision review r1)

Extend this item to cover convention unification, not just drift detection: the
runtime scripts dir now mixes symlink deployments (`facts_paths.py`,
`plan_readiness.py`) with snapshot copies (`validate_review_staging.py`,
`summarize_review_stats.py`). The symlinked readiness validator bypasses the
deployed validator snapshot entirely (its sys.path insert resolves into the repo
scripts dir), so two live copies of the shared validator serve two gate
families. Simplest unification: symlink the snapshot copies too, dissolving the
duplicate; version-handshake detection then becomes a backstop rather than the
primary defense.

## Resolution (2026-09-04, later the same day)

The unification half of this item is DONE: all remaining snapshot copies in
`~/.ai-playbook/scripts/` were converted to symlinks into the repo's
`scripts/` (every script in the runtime dir now follows the repo canonical
copy; host-only files `sync-mcp-credentials.sh`, `scan-public-hygiene.sh.bak-20260819`,
and `.stale-backup-2026-08-16/` were left untouched). Spot checks: done-lock
status, validate_review_staging --selftest, check-instruction-size, and the
hygiene scan all pass through the symlinked paths. What remains OPEN is the
detection/backstop half: a version or parity check would now be redundant for
divergence (symlinks cannot diverge) but may still be worth adding as a
fail-loud guard against a symlink being replaced by a stale copy.
