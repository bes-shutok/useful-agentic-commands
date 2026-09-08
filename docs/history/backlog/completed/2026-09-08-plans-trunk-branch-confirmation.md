# Backlog: skip redundant confirmation for feature branches from trunk

Status: done
Workflow: backlog
Covered by: Task 8 of docs/plans/2026-09-08-execute-plan-fresh-review-coverage-gaps.md (do not join into other plans; archive at that plan's completion)
Origin: User feedback during CRM-691 plan authoring on 2026-09-08
Severity: Low
Scope: `agents/skills/plans/SKILL.md` Phase 0 branch setup; audit the equivalent `execute-plan` branch gate if it shares the same interaction pattern

## Problem

The plans workflow asks for explicit confirmation before creating a feature branch even when the repository is on a clean, definitive trunk branch such as `master` or `main`. For a normal feature-plan flow, this adds an unnecessary interaction before the required requirements discussion. In the triggering session, the user confirmed branch creation and then encountered a second, unrelated requirements-scope question, making the workflow feel like it required repeated permission to proceed.

## Exact location

- `agents/skills/plans/SKILL.md`, Phase 0 Step 0.1, which unconditionally says to ask the user for confirmation before branch creation.
- `agents/skills/execute-plan/SKILL.md`, Phase 0 branch setup, as a related surface to inspect for the same redundant confirmation behavior.

## Suggested fix

Add a fail-closed automatic path for branch creation when all of these facts are verified: the current branch is exactly `master` or `main`, the working tree is clean, the proposed branch name is derived from the requested task, and the destination branch does not already exist. In that case, create and verify the local feature branch without asking for branch confirmation. Preserve the confirmation gate for detached HEAD, non-trunk bases, dirty or ignored user content, ambiguous branch targets, existing destination branches, or any operation that would overwrite or rewrite history. Keep push authorization unchanged.

Add regression coverage or a mechanically testable workflow fixture for both `master` and `main`, plus negative cases proving that a dirty trunk or non-trunk base still asks before branching. The check must distinguish branch creation from requirements and scope confirmation; skipping branch confirmation must not skip the separate requirements gate.

## Why not fixed now

This is a cross-workflow skill change outside the current CRM-691 plan. The user requested a durable backlog record rather than changing the shared skill during feature-plan authoring. No product code or CRM repository file should be changed for this item.

## Acceptance criteria

- Clean `master` and clean `main` automatically create the derived local feature branch after the branch target is verified.
- Dirty trunk, non-trunk bases, detached HEAD, ambiguous targets, and existing destination branches retain an explicit confirmation or safe stop.
- The workflow still verifies the resulting branch and tracking state before requirements discovery.
- Requirements and scope confirmation remain separate and are not silently bypassed.
- No push or history rewrite is introduced by the automatic path.
