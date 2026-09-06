# Backlog: plan-readiness-migration plan authoring r5 residuals

Status: open (NOT covered by the prose-residue sweep; its Assumptions scope these two items out — fold at the plan doc's next legitimate touch)
Workflow: backlog
Source: docs/plans/2026-09-05-plan-readiness-migration.md plan review r5 (two Low, non-blocking findings; deferred at the 5-round cap per the two-regenerating-classes rule, prose class)
Severity: Low
Scope: docs/plans/2026-09-05-plan-readiness-migration.md (fold into the plan at its next legitimate touch, or apply during execution)

## Items

1. `implementation#task-gate-scope-ambiguity`: Task 5's interim gate says "the Validation Commands doc-grep section passes", which is correct as written, but an executor running the FULL Validation block at Task 5 hits the em-dash loop's `test -f` fail on the Task 7 backlog file (it does not exist until Task 7). Fold: one sentence in Task 5 restricting the interim run to the doc-grep lines plus the forbidden-README check, with the em-dash loop and full block reserved for Task 8.

2. `documentation#anchor-text-mismatch`: Task 2's Integration Points anchor text `reports ready=yes in its ## Summary` omits the backticks that the host sentence carries in agents/skills/review-plan/SKILL.md, and the prescribed clause replacement leaves the host sentence mildly ungrammatical. The clause is locatable (unique substring) and no validation gate pins the sentence's exact wording. Fold: backtick-accurate anchor plus a full-sentence replacement block.

## Why not fixed now

The authoring loop reached its 5-round cap; both findings are prose/wording class, the known regenerating family, and the certification round (r5) reported ready=yes with zero blocking findings at digest 281a4f1968145ea3b65e674a34f95d0036f6162e18bce704cb52f4e3127f5644.
