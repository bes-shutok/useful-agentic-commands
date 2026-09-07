# Backlog: plans must separate facts from unresolved design decisions

Status: open
Workflow: backlog
Source: user correction during a plan-authoring session, 2026-09-07
Severity: Medium
Scope: `agents/skills/plans/SKILL.md` Phase 1 confidence gate and Step 1.4 confirmation; `agents/skills/grilling/SKILL.md` cleanup trigger; `agents/skills/grill-with-docs/SKILL.md` guidance; plan-authoring regression evaluation

## Problem

The plans workflow correctly requires `grill-with-docs` when a requirement remains low-confidence, but the confidence gate can be applied too optimistically after source verification.

In the triggering case, the user asked for a plan to remove changes above a base revision that were not directly related to a named feature. The agent inspected the branch history, the base revision, the feature specification, and related design material. That evidence identified an apparently unrelated change. The agent then treated the classification as settled and moved to plan confirmation without asking the focused cleanup-scope question required by the grilling workflow.

The unresolved choices included:

1. Which files, commits, and hunks belong to the feature, rather than merely having a related-looking subject or neighboring documentation.
2. Whether the cleanup should create an inverse commit, rewrite history, or only describe a future cleanup.
3. Whether ignored, untracked, or pre-existing local files must be preserved.
4. Whether "directly related" means feature behavior only, supporting tests and documentation, plan history, or process metadata.
5. Whether the proposed cleanup has any dependency on files that appear unrelated.

The source material could establish facts about those items, but it did not select all of the decisions. The agent should have invoked the one-question-at-a-time `grill-with-docs` interview before presenting the plan assumptions or writing the plan artifact.

The same failure pattern also applies to non-cleanup plans. A feature specification can describe the goal and constraints while leaving multiple reasonable implementation boundaries, ownership choices, compatibility modes, error policies, or rollout shapes open. Detailed sources do not make an unselected choice high-confidence.

## Root cause

The workflow collapsed two different activities:

- **Fact lookup:** use the repository, specification, history, or tooling to learn what exists and what has already been decided.
- **Decision resolution:** ask the user to choose between multiple defensible designs when the sources do not uniquely determine the plan.

The phrase "strongly supported by repo evidence" was interpreted as "the sources describe the feature in detail." The required test is stricter: there must be exactly one reasonable interpretation, and choosing another must be unreasonable or cheap to correct.

Cleanup wording was an additional missed trigger. Requests containing remove, revert, restore, clean up, or match-the-base language need a preservation boundary even when the candidate change looks obvious. The agent must distinguish feature-owned changes from pre-existing or unrelated changes before any restore operation.

## Generalized lesson

**Principle:** Process-only; facts do not resolve design ambiguity.

**Shape trigger:** Source documents and repository evidence have been verified, but two or more plausible implementations or cleanup scopes still differ in ownership, affected paths, behavior, invariants, history strategy, preservation rules, or validation evidence.

**Rule:** Source verification resolves facts, not unselected design trade-offs. If competing plan shapes remain and choosing one would materially change the task list or its safety boundary, classify the point as low-confidence and invoke `grill-with-docs` before requirements confirmation or plan-file writing.

**Cleanup rule:** For remove, revert, restore, clean-up, or match-the-base requests, ask the focused scope question before any restore or deletion operation whenever the branch contains more than the obvious feature work or the worktree contains pre-existing changes. The question must establish the task-owned files, frozen files, ignored/untracked preservation, allowed deletion, and history strategy.

**Why:** A specification can define the goal while intentionally leaving implementation boundaries, ownership, compatibility, and rollout decisions open. A branch can contain valid feature work beside unrelated or pre-existing changes. Recording one option as a high-confidence assumption hides the decision from the user and can cause the executor to delete, rewrite, or preserve the wrong material.

## Suggested fix

Update the plans and grilling workflows with the following safeguards:

1. Add a mandatory decision-ambiguity scan after source discovery and before Step 1.4. Separate discovered facts from decisions still requiring a choice.
2. For every proposed task, ask whether another reasonable design would remove, add, move, or materially change that task. If yes, the point is low-confidence regardless of source authority or detail.
3. Treat differences in scope, source-of-truth ownership, module boundary, compatibility mode, error policy, rollout, history strategy, preservation, deletion, or validation as material.
4. For cleanup and restoration requests, require the focused scope question from the grilling workflow before any restore or deletion operation. Recommended wording: "Should I change only the files, classes, and methods required by this feature, while preserving every other file and all pre-existing uncommitted content?" Extend it when needed to cover ignored or untracked files and whether history may be rewritten.
5. Add a `Decision points requiring a grill` subsection to the requirements buffer and Step 1.4 confirmation. Keep it separate from ordinary assumptions and from the scope-extension list. A clean result must say `none remain`; the subsection must not be silently omitted.
6. For cleanup plans, require a cleanup scope ledger containing the exact base ref, task-owned files/classes/methods/hunks, frozen areas, pre-existing dirty paths, untracked paths, ignored paths, explicit deletion permissions, and the selected history strategy. Run the cleanup-scope baseline checker before the first cleanup commit.
7. Add plan-authoring regression cases:
   - a single-boundary feature with one implementation clearly required remains eligible for a high-confidence assumption;
   - a feature with an adjacent boundary, compatibility path, or ownership choice routes to `grill-with-docs`;
   - authoritative sources that describe multiple alternatives still route to the grill;
   - a cleanup request with one apparently unrelated commit beside feature work still asks the scope question;
   - a cleanup request with dirty, untracked, or ignored files records preservation before restore;
   - a source-owned prerequisite is placed under `Ship when`, not converted into an assumption or executable task;
   - an explicit user decision suppresses only the already-resolved question, not unrelated ambiguity.
8. Teach `review-plan` to flag a plan when its tasks implement one of multiple plausible designs, or when a cleanup plan lacks a scope ledger and grill result.
9. Add a structural readiness check that refuses plan finalization when a material ambiguity is identified but the plan has neither a recorded user decision nor a `none remain` grill result.
10. Keep the backlog and regression fixtures generic. Do not copy ticket IDs, repository names, service names, internal URLs, secret names, user identities, absolute paths, or feature-specific payloads into this process item.

## Acceptance criteria

- `plans/SKILL.md` distinguishes fact verification from decision resolution in the confidence gate.
- The workflow has an explicit ambiguity scan with the materiality dimensions above.
- Any material competing interpretation must invoke `grill-with-docs` before Step 1.4 confirmation or plan-file writing.
- Cleanup and restoration requests use a scope question and a cleanup scope ledger before any restore or deletion operation.
- Step 1.4 visibly reports the decision-point result, including `none remain` when no grill is needed.
- The cleanup-scope baseline checker is named as the mechanical guard for dirty, untracked, and authorized-deletion boundaries.
- Regression fixtures prove that authoritative source documents do not suppress grilling when they leave multiple viable designs.
- Review-plan can detect a missing grill result or cleanup ledger when the plan contains a material unresolved choice.
- The existing explicit-scope-extension rule remains intact and is cross-referenced rather than duplicated.
- This backlog entry contains only generic workflow language and no project-specific or sensitive data.

## Not part of this backlog item

- Do not require grilling for factual lookups whose result is directly observable and does not involve a choice.
- Do not make `execute-plan` reopen settled plan decisions during implementation.
- Do not require a grill when the user has already explicitly selected the design and no separate material ambiguity remains.
- Do not change product code or a feature plan as part of this playbook-process fix.
- Do not delete or rewrite completed history artifacts to retrofit this lesson; prevention belongs in forward-looking workflow rules and tests.
