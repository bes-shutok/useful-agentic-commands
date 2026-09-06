# Backlog: cleanup workflows must preserve pre-existing content

Status: done
Workflow: backlog
Source: post-mortem on a feature-branch cleanup where review-driven simplification deleted unrelated branch content and pre-existing work
Severity: High
Scope: `agents/skills/grilling/SKILL.md`, `agents/skills/plans/SKILL.md`, `agents/skills/doing-code-review/SKILL.md`, `agents/skills/receiving-review/SKILL.md`, `agents/skills/review-loop/SKILL.md`, and `agents/skills/done/SKILL.md`

## Problem

Requests to simplify or clean a branch are being treated as permission to make the whole branch resemble its base branch. This is unsafe when the branch contains prerequisite work, neighboring features, or uncommitted changes that were not created by the current task.

The failure is amplified when review findings are treated as authorization to expand the change. A review loop can then repeatedly fix valid findings outside the user's intended feature boundary. The `grilling` skill requires clarification for unclear decisions, but cleanup wording is not currently a mandatory trigger, so the agent can act without asking the scope question.

Observed consequences include deleting files and classes that were unrelated to the primary feature, removing useful uncommitted content, and requiring branch recovery before implementation can continue.

## Suggested fix

Add a shared cleanup-scope gate across the affected workflows:

1. In `grilling`, make "simplify", "remove", "clean branch", "restore", and "make it match the base" mandatory ambiguity triggers when the working tree or branch contains more than the obvious feature. Ask one focused scope question before any edit or restore operation.
2. Require the question to distinguish the task-owned diff from pre-existing work. Recommended wording: "Should I change only the files, classes, and methods required by this feature, while preserving every other file and all pre-existing uncommitted content?"
3. In `plans`, require a scope ledger for multi-file cleanup or restoration work. Record the exact base ref, task-owned files/classes/methods, frozen areas, pre-existing dirty paths, untracked paths, and explicit deletion permissions.
4. In `doing-code-review`, `receiving-review`, and `review-loop`, state that review findings are evidence to assess, not authorization to broaden the plan. Findings outside the accepted scope become backlog items unless the user explicitly expands scope.
5. In `done`, capture the dirty-tree and untracked-file baseline before session changes and refuse to stage paths that were already present unless the user explicitly includes them.
6. Add a lightweight validator or checklist that compares `base..HEAD`, `HEAD..working-tree`, and the untracked manifest before permitting a cleanup commit.

The existing backlog item `2026-09-05-plans-scope-extension-requires-grill-with-docs.md` covers plan-authoring scope extensions. This item should extend that work to cleanup operations, review authorization, and preservation of pre-existing content without duplicating its plan-specific acceptance criteria.

## Acceptance criteria

- Cleanup and restoration requests with ambiguous boundaries cannot proceed without a focused user scope confirmation.
- A cleanup plan identifies task-owned and frozen files, classes, methods, and hunks, plus the exact base ref.
- Pre-existing modified and untracked paths are recorded before edits and are not deleted, restored, or committed implicitly.
- Review loops do not broaden implementation scope from findings alone.
- Done-time staging can distinguish session changes from the initial dirty-tree baseline.
- Tests or self-checks cover a dirty working tree containing unrelated modified and untracked content.

## Why not fixed now

This is a cross-skill workflow contract change. It needs coordinated edits to the clarification, planning, review, and commit workflows, plus a small mechanical preservation check. It was recorded separately so it can be designed and reviewed as one safety change.
