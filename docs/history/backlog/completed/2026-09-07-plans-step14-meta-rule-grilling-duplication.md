# Backlog: plans Step 1.4 meta-rule restates grilling triggers

Status: done
Workflow: backlog
Completed: 2026-09-09 via docs/plans/2026-09-08-plans-grill-answer-state-machine.md (executed, archived to docs/plans/completed/)
Grouping: to be joined with docs/history/backlog/2026-09-08-plans-grill-answer-required-readiness-gate.md into ONE authoring plan (same plans+grilling surface, 2026-09-08 user direction)
Source: docs/reviews/2026-09-07-plans-facts-do-not-resolve-design-ambiguity-code-review-r1.md (overflow entry, design-simplicity, Low, architecture#duplicated-concept)
Severity: Low
Scope: agents/skills/plans/SKILL.md; agents/skills/grilling/SKILL.md

## Problem

The plans skill Step 1.4 confirmation meta-rule (agents/skills/plans/SKILL.md, the HTML comment after the Step 1.4 block, around line 204) restates two rules that the grilling skill already owns canonically: the generic-acknowledgement rule (`a broad acknowledgement (sure, ok, confirmed) confirms only the material decisions explicitly named in this block` vs grilling's `No generic acknowledgement confirms a material choice:` block) and the lifecycle-verb trigger (`an ambiguous lifecycle verb (skip, leave, drop, defer, preserve) must already have been restated as a concrete tree action` vs grilling's `Lifecycle-verb clarification trigger:` block). Two prose sources of truth for the same two rules can drift when one is updated.

- Exact location: `agents/skills/plans/SKILL.md:204` (meta-rule comment inside the Step 1.4 confirmation template); peer sources at the two trigger blocks appended in `agents/skills/grilling/SKILL.md`.

## Suggested fix

Options considered (design choice, not yet decided):

1. Cross-reference: shrink the plans meta-rule clauses to a pointer at the grilling skill's trigger blocks (sibling-doc-restatement class; canonical home stays grilling). Risk: the Step 1.4 confirmation is deliberately self-contained at confirmation time (the authoring agent may not have the grilling skill loaded), so a pointer weakens the confirmation-time gate.
2. Keep both and accept the duplication as confirmation-time self-containment, adding a bidirectional Integration Points note so a future grilling edit knows to mirror the plans meta-rule.

The trade-off to resolve: cross-reference (single source, pointer drift risk) vs confirmation-time self-containment (duplicate prose, manual sync). Not a mechanical fold; needs an explicit decision.

## Why not fixed now

The plans meta-rule text is prescribed verbatim by plan Task 3 of docs/plans/2026-09-07-plans-facts-do-not-resolve-design-ambiguity.md, so the executing plan could not edit it; the review round staged the concern as a budget-capped overflow entry and the address-r1 pass deferred it per the sibling-doc-restatement backlog class (standing instruction: backlog-deferral default for overflow findings). Deferred by the address-r1 sub-agent 2026-09-07.

## Acceptance

- A decision recorded on cross-reference vs self-containment (with the grilling skill's owner).
- If cross-reference: plans meta-rule clauses replaced by a pointer; grilling trigger blocks remain canonical; both skills' Integration Points updated.
- If self-containment kept: a sync note added to both files naming the mirrored clauses so a future edit knows to update the peer.
