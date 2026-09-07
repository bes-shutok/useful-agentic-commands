# Backlog: done run-start marker behaviors lack validation probes in the plan

Status: done
Origin: docs/reviews/2026-09-06-2026-09-04-done-deliverables-log-dedupe-and-anchors-code-review-r1.md (findings R1-2 Medium + R1-5 Low, testing lens, non-blocking; execute-plan Phase 3 round 1)

## Finding

The `## Validation Commands` block of `docs/plans/2026-09-04-done-deliverables-log-dedupe-and-anchors.md` does not pin the done Step 0 run-start executable snippet or three plan-mandated behaviors:

- No probe pins the Step 0 bash snippet itself (only the prose obligation sentence is pinned): deleting the snippet block (the `mkdir -p` line, the `run-start-$(date -u ...)` marker-write line) would still pass the whole sweep (R1-2).
- Three plan-mandated behaviors are unpinned (R1-5): the never-delete pruning constraint (never the newest previous-run marker, never the current run's marker), directory creation (`mkdir -p .../done-session`, "create the directory if missing"), and the producer-scope `(excluding {plans_completed_dir})` exclusion.

## Suggested fix

Add to the plan's Validation Commands block (when the plan is next unfrozen): positive `grep -Fq`/`grep -cF` probes for the snippet lines (`mkdir -p "${TMP_DIR%/}/done-session"`, `run-start-$(date -u +%Y%m%dT%H%M%SZ)`), the never-delete pruning wording, the directory-creation wording, and the `excluding \`{plans_completed_dir}\`` producer scope.

## Why deferred

The plan bytes were checkbox-frozen during execute-plan execution (checkbox marks mutate the digest after the final review round), so probe additions to the Validation Commands block cannot land mid-run; they land post-archive as a follow-up edit. The r1 fixes (round 1 of Phase 3) already reworked the snippet and added the Step 2.62 `done-session/` classification, so the behaviors exist on disk, only the validation pins are missing. Deferred by the execute-plan Phase 3 round 1 address agent (non-interactive run).

## r2 additions (2026-09-06, round 2)

Origin: docs/reviews/2026-09-06-2026-09-04-done-deliverables-log-dedupe-and-anchors-code-review-r2.md (findings R2-9 Medium + R2-10 Low, non-blocking; frozen-plan-bytes class, dedup group {R2-9, R2-10}). Same deferral reason as above: plan bytes are checkbox-frozen during execution; all of these land post-archive.

- R2-9: the plan's Task 1 quote is stale versus the post-r1/post-r2 snippet on disk. Task 1 claims the Step 0 snippet was inserted "verbatim" as "four lines", but the current snippet is seven lines (added in r1: `REPO_TOP` resolution, `$REPO_TOP`-anchored fallback, `MARKER` variable, printf echo; added in r2: `| head -n 1` on the sed pipeline, the `case "$TMP_DIR"` relative-path anchor). Post-archive fix: update the Task 1 quote/checkbox wording to drop the verbatim/four-lines claim, or annotate that the snippet evolved during Phase 3 rounds.
- R2-10: the plan's Validation block still lacks pins for r1/r2 load-bearing wording: the removal-rule rewording ("remove every line listing that path", r2 R2-7b), the repo-relative path form ("one repo-relative path per line"), and the r2 snippet lines (`head -n 1`, the `case "$TMP_DIR"` anchor line, the marker-echo chat-context sentence). Extend this item's Suggested fix probe list with those literals when the plan unfreezes.

## r3/r4 additions (2026-09-06, rounds 3-4)

Origin: docs/reviews/2026-09-06-2026-09-04-done-deliverables-log-dedupe-and-anchors-code-review-r3.md and `...-code-review-r4.md` (r4 findings R4-11 Low, non-blocking; frozen-plan-bytes class). Same deferral reason as above: plan bytes are checkbox-frozen during execution; these land post-archive via the same mechanism.

Probe pins to add to the plan's Validation Commands block when it unfreezes, all against `agents/skills/done/SKILL.md` (`grep -Fq` positive probes):

- The r3 canonicalization line (Step 0 snippet): `MARKER="$(cd "$(dirname "$MARKER")" && pwd)/$(basename "$MARKER")"`; plus the r4-widened sed literal `s/^tmp_dir = ["'\'']\(.*\)["'\'']$/\1/p` (character class accepting single- or double-quoted TOML).
- The Step 0 echo-loss canonical statement: `If it is lost or matches no marker at gate time, Step 1.5 treats the window as unanchorable (conservative gating) and the Step 2.62 sweep prunes no `run-start-*` markers this run; never guess by recency.` (probe on a stable substring, e.g. `matches no marker at gate time`).
- The Step 1.5 echo-loss back-reference, including the no-match arm and the never-recency clause: `if the echoed marker path is lost or matches no marker under \`{tmp_dir}/done-session/\` at gate time, apply the Step 0 echo-loss fallback` plus `never substitute the newest on-disk marker` (two probes).
- The Step 2.62 prune-skip clause: `If the echoed marker path is lost or matches no marker under this directory, prune no \`run-start-*\` markers this run` (stable substring: `prune no \`run-start-*\` markers this run`, count 2 after r4: one in Step 0 canonical statement, one in Step 2.62).
