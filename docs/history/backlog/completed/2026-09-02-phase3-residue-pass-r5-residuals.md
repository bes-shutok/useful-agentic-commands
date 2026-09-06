# Backlog: phase3-residue-pass r5 certification residuals (5 deferred non-blocking findings)

Status: done
Workflow: pre-plan (promote via `plans` skill when scheduled; several are one-clause riders on the next pass touching these files)
Source: docs/reviews/2026-09-02-plan-review-phase3-residue-pass-r5.md (certification round, zero blocking, ready=yes at digest fa8b91142892f0da; deferred per the backlog-by-default exit policy since folding at the round-5 cap would have required a sixth round)

## Problem

Five non-blocking findings from the r5 certification round of the phase3-residue-pass plan:

1. **(Low, testing + correctness-completeness)** The plan's authoring-time proof classifies the Task 2g routing-anchor count as RED-today, but the anchor `Class membership in the two backlog-by-default classes` already occurs exactly once on disk, so that count guard is green today and never flips. Fix: move it into the green-today count-guard class (alongside the rule 23 count) in the plan's Validation preamble, or note it when the plan next executes.
2. **(Low, design-simplicity)** The prescribed Step 3.5 cap-row reconciliation branch forward-references "the short session note described in this row" before the otherwise-branch defines it. Wording-only; this cell has regenerated wording every round (r1-r5), so it is a backlog-by-default class member.
3. **(Medium, risk, pre-existing debt)** Verification-gate or timeout re-entries that re-check or re-synthesize without re-running workers advance neither `review_round` nor `re_entry_count`, so a pathologically failing gate can loop with no cap ask. Pre-existing on-disk debt, recorded in the residue-pass plan's Gist with a future budget-change plan as owner. Fix options: cap `re_entry_count` regardless of worker re-runs, or require a user ask after N consecutive uncounted re-entries.
4. **(Low, risk)** The cap-row Fix-risk branch's single-ask guarantee is inherited from Hard Gate 23's stop-and-ask semantics rather than restated locally; drift in `receiving-review` would silently drop the cap-row ask. Optional hardening: add "(a stop-and-ask)" after "Fix-risk direction per Hard Gate 23" or add a maintenance probe.
5. **(Low, contract-docs)** The residue-pass plan's Review Scope lists `docs/maintenance/glossary.md` under the "Production code (skill contract text)" heading; it belongs under Documentation.

## Location

- `docs/plans/2026-09-02-phase3-residue-pass.md` (items 1, 2, 4, 5 are plan-text or its prescribed skill text; item 3 is `agents/skills/execute-plan/SKILL.md` counting semantics)
