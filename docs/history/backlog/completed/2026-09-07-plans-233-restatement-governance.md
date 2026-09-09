# Backlog: plans:233 acceptance-mechanics prose restatement governance

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-07-plans-facts-do-not-resolve-design-ambiguity-code-review-r3.md (code review r3, overflow entry, design-simplicity worker, Low, architecture#duplicated-contract-prose)
Severity: Low
Scope: agents/skills/plans/SKILL.md (template line ~233)

## Problem

The plans-skill template line at agents/skills/plans/SKILL.md:233 restates the trailer-gate acceptance mechanics (case/period leniency for the none-remain line, the placeholder vocabulary, the `<` prefix check) that the readiness validator (scripts/plan_readiness.py, `decision_marker_problem`) enforces. Two review rounds give contradictory directions for this prose:

- r2 (contract-docs finding, fixed in 04e32c7): document the acceptance vocabulary where authors read: i.e., in the plans template line itself: so authors are not surprised by gate refusals.
- r3 (design-simplicity overflow finding): the restated mechanics are duplicated contract prose; compress them to a pointer at the validator's contract and keep the template line minimal.

Both directions cannot be applied at once; this is a restatement-governance question (which surface owns the acceptance-mechanics wording), not a defect in either round's fix.

## Suggested fix (design choice, owner decision needed)

Owner decides the governance rule, then applies one direction:

1. Keep r2's placement: the template line stays the author-facing statement of acceptance mechanics, and the validator's docstring points at the template line as the prose contract (current state).
2. Apply r3's compression: the template line carries only the authoring rule plus one pointer ("the readiness gate in scripts/plan_readiness.py defines the exact acceptance mechanics"), and the mechanics live solely in the validator/docstring.

Direction 2 reopens the r2 gap (unexplained gate refusals for authors) unless the pointer is genuinely discoverable; direction 1 leaves the duplicated-contract-prose smell r3 names.

## Why not fixed now

Deferred per the execute-plan r3 address-pass disposition map (overflow item, ADR-0002 class default): the standing instruction fixes all staged findings F1-F9 and backlogs the overflow entry because it contradicts an already-applied r2 fix and needs an owner decision between the two review artifacts. Decision made by the non-interactive address-pass pre-authorization (backlog-deferral default).

## r4 recurrence (2026-09-07, code review round 4)

Source: docs/reviews/2026-09-07-plans-facts-do-not-resolve-design-ambiguity-code-review-r4.md (code review r4, two overflow entries, design-simplicity worker, architecture#duplicated-knowledge).

Third recurrence of the same restatement-governance item:

- agents/skills/plans/SKILL.md:233 (Medium): the acceptance grammar (none-remain leniency, placeholder vocabulary, `<` prefix) is again restated in prose after the r4 F2 fix expanded it to state the hyphen carve-out exactly; the r4 pass could not compress it because the same round pinned that clause's wording against the validator.
- agents/skills/review-plan/SKILL.md:318 (Low, sibling): the sidecar-date exemption mechanics are restated in the review-plan Integration Points clause instead of pointing at `evaluate_readiness`'s own comment; the r4 F4 fix edited one clause in place rather than converting it to a pointer.

Both remain the same class (sibling-doc restatement vs the validator's single-owner contract) and fold into this existing item per the non-interactive backlog-deferral default; no duplicate backlog item created. Status stays open pending the owner governance decision above, which now covers both surfaces.

Landed: Landed via Task 3 (21b9155 + 567f180 pointer compression + validator back-pointer comment); r2-vs-r3 contradiction resolved in r2 favor.
