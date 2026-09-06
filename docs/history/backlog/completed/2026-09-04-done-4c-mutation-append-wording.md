# Backlog: Align done Step 3 item 4c wording with mutation append

Status: done (2026-09-06; executed via docs/plans/completed/2026-09-04-done-deliverables-log-dedupe-and-anchors.md)
Workflow: pre-plan backlog (promote via plans skill when scheduled)

## Problem

`done` Step 3 item 4c still says the `plans` skill primary producer is a Write append, after Step 1.5 producer (1) and `plans` Writing were widened to Write/Edit/StrReplace. Agents reading only 4c may treat Edit/StrReplace plan updates as exempt from `plan-deliverables.txt`.

## Location

- `agents/skills/done/SKILL.md` Step 3 item 4c (~line 452)
- Contrast: Step 1.5 producer (1); `agents/skills/plans/SKILL.md` Writing

## Evidence

Review-loop r4 contract-docs finding `consistency#stale-cross-reference` on tip `ca97a9a` vs base `87ae061`.

## Suggested fix

Reword 4c to "plans skill mutation append (Write/Edit/StrReplace)" (or drop 4c entirely if folded into Step 3 item 0b; see sibling backlog on 0b/4c duplication).

## Source

ai-playbook review-loop r4 (FQN/learn scoped tip), Low non-blocking, deferred at loop exit.
