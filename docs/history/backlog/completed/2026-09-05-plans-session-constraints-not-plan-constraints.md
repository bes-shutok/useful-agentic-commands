# Plans skill: authoring-session constraints must not enter the plan document

Status: done
Workflow: backlog
Source: 2026-09-05 session: plans authored from scheduling prompts inherited the prompt's "do not create a new branch, work and commit on the current branch; never push" as plan assumptions and acceptance criteria (four plans in this repo, one in homelab-llm), so execute-plan skipped branch setup and ran on the default branch. Prompt template fixed and plans de-leaked the same day (UL#296); the skill-level rule below was deferred because `agents/skills/plans/SKILL.md` carried uncommitted peer edits.


Disposition (2026-09-05): landed as the plans-skill rule "Authoring-session constraints are not plan constraints" in agents/skills/plans/SKILL.md:125 (assumptions/Gist/Evaluation Criteria/Validation Commands sweep with the four leak patterns), commits 21b5ec8 + b242dd7 on main; review-loop r1-r2 (focused r1: 1 Low folded in b242dd7, 1 dropped not-a-defect; fresh hybrid r2: zero findings, design-simplicity covered the tip), staging docs/reviews/2026-09-05-main-review-r{1,2}.md; hygiene scan green; unblocked by the scope-control-family squash a8a72c7 which committed the previously-peer-held skill edits.

## Finding

The plans skill has no rule distinguishing task-prompt/session constraints from plan constraints. An authoring agent that is told "no new branch, never push" (meant only for the authoring run's git behavior) records it in the plan's assumptions ("basis: task constraint") and sometimes acceptance criteria ("committed on `main`"). The executor then treats the plan as the authority and suppresses its normal Phase 0 dedicated-branch setup.

## Desired change

Add a rule to the plans skill (authoring workflow, assumptions/scope section): constraints in the authoring task prompt that scope the session's own git behavior (branching, pushing, commit placement) are authoring-session-scoped; do not write them into the plan document as assumptions, gist, or acceptance criteria; keep plans branch-agnostic and push-agnostic; before finishing, sweep those sections for "current branch", "no new branch", hardcoded branch names, and "never push" and delete any hit.

## References

- UL#296 (Session constraints must not be written into plans)
- homelab-llm commit ea1bc15, ai-playbook commit 3505395 (de-leak witnesses)
