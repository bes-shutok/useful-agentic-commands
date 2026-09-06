# Phase3 churn control plan: non-blocking certification residuals (r11)

Status: done; plan created 2026-09-02 (docs/plans/completed/2026-09-02-phase3-residue-pass.md, branch 2026-09-02-phase3-residue-pass); executed and archived 2026-09-03.
Workflow: backlog
Source: docs/reviews/2026-09-01-plan-review-phase3-review-churn-control-r11.md (final certification round, ready=yes; residuals deferred per Backlog capture)

## Problem

The certified plan (docs/plans/completed or active phase3-review-churn-control, digest a7168b59) leaves five non-blocking wording/placement residuals from its final review round. None enables a wrong silent exit; all are wording/placement improvements to the prescribed skill edits.

1. **ds-F1 (Medium)**: the cap-row co-hold clauses give no relative order when fix-risk AND reconciliation triggers both hold at the cap (reconciliation detour first then Fix-risk direction, or fix-risk supersedes?). Both orderings still write the session note and ask, so no wrong silent exit. Fix: order the clauses explicitly (reconciliation first, then the Fix-risk direction).
2. **cc-F1 (Low)**: the new Step 3.3 verification gate item 5 scopes items 1-3 to a launched Step 3.3, but item 4's "or in the address log" alternative dangles on the skip path (no address log exists). Fix: scope item 4 alongside 1-3 or reword item 5 to "items 1-4".
3. **cc-F2 (Low)**: a skip-path pass that fixes findings mutates the digest, but Step 3.4's clear-round table is not amended, so it may read "clean" for a stale digest (exit remains safe via Step 3.5's fresh-clean-review requirement). Fix: add a clause noting a mutating skip-path pass makes the round not clean.
4. **testing-F1 (Low)**: the prescribed exit-rule clause "exit coverage additionally follows the exit-hybrid-once rule below" is directionality-dependent but the placement is not pinned, so inserting the rule above the referenced bullet leaves "below" false with all pins green. Fix: prescribe "directly after the post-fix focused-round preference bullet" or pin the placement.
5. **ds-F2 (Low)**: the prescribed counting paragraph chains five rules into one long sentence; split into 4-5 sentences in the skill edit (keeping all pinned spans verbatim).

## Location

- `agents/skills/execute-plan/SKILL.md` (cap row, verification gate, clear-round table, counting paragraph) per the certified plan's Tasks 1-2.
- `agents/skills/review-agents/review-panel-selection.md` (exit rule placement) per Task 3.

## Suggested fix

Apply the five one-clause fixes in a single pass over the certified plan's prescribed texts (they are independent), then re-run the plan's Validation Commands block plus the rule-22 mechanical audit; no behavior re-review needed beyond a spot check of the touched clauses.

## Severity

Medium (1, wording-only ambiguity, both readings ask the user) and Low (4).

## Why not fixed now

The plan certified at digest a7168b59 with zero blocking findings; folding these would change the digest and require another full certification round for wording-only improvements. Deferred per the plan's own backlog-by-default philosophy.

## Dispositions (2026-09-02)

- cc-F2: already satisfied on disk by the churn-control execution squash (Step 3.4 skip-path digest-mutation table row).
- the other four residuals as prescribed into the plan tasks.
