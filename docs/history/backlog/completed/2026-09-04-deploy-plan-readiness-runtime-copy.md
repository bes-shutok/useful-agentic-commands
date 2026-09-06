# Backlog: deploy plan_readiness.py runtime copy to the shared scripts dir

Status: done (deployed 2026-09-04)
Workflow: backlog
Source: 2026-09-03 reviewed-plan-readiness-gate plan, code review r4 finding X2
Severity: Medium (consumer-repo gates fail closed with no in-skill escape until deployed)
Scope: runtime script deployment, execute-plan Step 0.5, done Step 1.5

## Problem

The readiness validator ships canonically at `scripts/plan_readiness.py` in
the skills repository, and both skill-layer gates resolve their runtime copy
via env-var override with two fallbacks (repo-local copy if present, then the
deployed runtime copy at `~/.ai-playbook/scripts/plan_readiness.py`). No plan
task ever performs the deployment: the runtime copy is absent, so in consumer
repos without a repo-local copy the gates brick fail-closed (by design, and
reported as a deployment gap, not a readiness failure).

Deployment is deliberately out of the plan's scope (repo-verifiable
acceptance) and is a user decision per the runtime-registry sync model: the
runtime scripts directory is a managed registry, not a blind mirror.

## Suggested fix

Decide and deploy: copy `plan_readiness.py` plus its sibling modules
(`validate_review_staging.py`, `facts_paths.py`; the script imports them from
its own directory) to `~/.ai-playbook/scripts/`, or wire the deployment into
the runtime-registry sync flow so future updates propagate. The gate-carrier
wording already carries the manual remedy line
(`cp scripts/plan_readiness.py ~/.ai-playbook/scripts/` plus siblings).

## Acceptance criteria

- `~/.ai-playbook/scripts/plan_readiness.py` (and both siblings) exist after
  the chosen deployment path runs.
- `python3 ~/.ai-playbook/scripts/plan_readiness.py --selftest` exits 0 from
  a directory outside the skills repository.
- The decision (manual copy vs registry sync) is recorded here when made.

## Decision (2026-09-04)

Deployed via symlink, matching the existing `facts_paths.py` convention:
`~/.ai-playbook/scripts/plan_readiness.py -> ~/Projects/myrepos/ai-playbook/scripts/plan_readiness.py`.
`validate_review_staging.py` was verified byte-identical to the repo copy (and its
selftest passes), so no sibling refresh was needed; the script's
`Path(__file__).resolve().parent` sys.path insert resolves siblings through the symlink.

Acceptance verified: `python3 ~/.ai-playbook/scripts/plan_readiness.py --selftest`
exits 0 from `/tmp` (outside the repo); live runs from a project root return
`readiness OK` for a freshly reviewed plan and named stale-digest/missing-plan
failures otherwise.

Correction (review r1 of this decision): the byte-identical check above is not
load-bearing. Because the script resolves siblings via
`Path(__file__).resolve().parent`, the symlinked validator imports
`validate_review_staging.py` from the REPO scripts dir, bypassing the deployed
snapshot copy entirely. The deployed snapshot remains the direct-invocation
default for the review-staging skills, so two live copies of the shared
validator serve two gate families; divergence between them is the drift risk
tracked by `2026-09-04-validator-sibling-version-check.md`. The simpler
alternative of symlinking the sibling too (dissolving the duplicate) was
considered and deferred to that unification decision rather than rejected on
merits.
