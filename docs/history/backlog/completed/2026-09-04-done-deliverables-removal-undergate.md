# Backlog: done deliverables-log removal under-gate residual

Status: done (2026-09-06; executed via docs/plans/completed/2026-09-04-done-deliverables-log-dedupe-and-anchors.md)
Workflow: backlog
Source: 2026-09-03 reviewed-plan-readiness-gate plan, code review r8 finding AB3
Severity: Low (contrived triple-condition residual)
Scope: agents/skills/done/SKILL.md (Step 1.5 removal rule and Step 3 producers)

## Problem

The Step 1.5 removal rule for `{tmp_dir}/done-session/plan-deliverables.txt`
removes a listed path once it passes the gate, is exempted via the
execute-plan manifest marker, is recorded-stopped, or no longer exists under
`{plans_dir}`. A narrow triple condition can leave a plan deliverable
un-gated across done sessions:

1. `{plans_dir}` is gitignored (shadow-path repo), so the ignored-matching
   arm is the only status arm that sees the plan.
2. The plans-skill append producer (producer 1) was skipped for the
   mutation (e.g. the plan was edited by a non-plans skill that did not run
   the append), so the path never lands in the log and the ignored arm has
   nothing to scope it to.
3. Drift after a prior exemption: the path was already removed from the log
   via the manifest exemption, then the plan drifted post-exemption.

Under all three at once, the mtime fallback's session-window anchor may also
be unavailable (no done-session artifacts, no log entries to timestamp), so
an authoring-session plan modified this session can be mis-attributed to its
authoring session and get no gate.

## Why not fixed now

Contrived: producer 1 re-appends on every plans-skill plan-file mutation, the
ignored arm plus the log covers the normal paths, and the r8 session-window
anchor definition (done-session artifact creation time, earliest-log-entry
fallback) closes the common ambiguity. The residual requires a non-plans-skill
edit that skips the append AND a gitignored plans dir AND post-exemption
drift simultaneously.

## Suggested fix

If this ever bites, extend producer 1's obligation to cover non-plans-skill
edits of plan files under `{plans_dir}` (any skill or tool that mutates a
plan file appends to the log), or add a last-resort anchor (repo-local
session log start time) to the mtime fallback when both done-session
artifacts and the log are absent.

## Acceptance criteria

- A plan mutated by a non-plans skill under a gitignored `{plans_dir}` is
  still identified as a session deliverable at done time.
- The residual conditions are either impossible or produce a named refusal
  rather than a silent no-gate.

## Extension (review r9, 2026-09-04)

Two further Low residuals in the same session-window anchor sentence (done Step 1.5), backlogged from review round 9:

1. Dead fallback: "earliest plan-deliverables.txt entry timestamp" can never fire (producers write paths only, no timestamps; and the log is itself a done-session artifact, so its absence implies no entries). Fix options: drop the fallback clause and prescribe conservative gating (treat unanchorable `!!` plans as this session's deliverables), or stamp producer appends (`# <ISO8601> <path>`).
2. Stale anchor: the primary anchor (done-session artifact creation time) can predate the current chat (the log intentionally persists across done runs), widening the window -> spurious refusal (fail-closed). Fix option: anchor on the newest done-session marker created since the last done completed.
