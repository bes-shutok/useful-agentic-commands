# Backlog: Collapse done Step 3 plan-deliverable append (0b vs 4c)

Status: done (2026-09-06; executed via docs/plans/completed/2026-09-04-done-deliverables-log-dedupe-and-anchors.md)
Workflow: pre-plan backlog (promote via plans skill when scheduled)

## Problem

Step 3 item 0b and item 4c both append staged `{plans_dir}` paths to `{tmp_dir}/done-session/plan-deliverables.txt` on a `done` commit. Skip-duplicates hides the double write today, but two homes invite drift against Step 1.5's three-producer list.

## Location

- `agents/skills/done/SKILL.md` Step 3 item 0b and item 4c
- Step 1.5 producer (2)/(3) wording

## Evidence

Review-loop r4 design-simplicity finding `simplification#yagni` on tip `ca97a9a`.

## Suggested fix

Keep a single commit-time append (0b after staging / immediately before `git commit`), remove 4c, and retarget Step 1.5 so producer (2) is that one home (producer (1) remains plans mutation append).

## Source

ai-playbook review-loop r4 (FQN/learn scoped tip), Low non-blocking, deferred at loop exit.
