# Phase3 churn control r1 code review: residual findings (F6, F7, F14, F15; R-2 entry added in round r2; F-7-from-r3 entry added in round r3; entries 7-9 added in round r4)

Status: done; plan created 2026-09-02 (docs/plans/completed/2026-09-02-phase3-residue-pass.md, branch 2026-09-02-phase3-residue-pass); executed and archived 2026-09-03.
Workflow: backlog
Source: docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r1.md (execute-plan Phase 3, round 1, full panel)

## Problem

Nine entries are recorded here. Entries 1-4 are the round-1 deferred findings (rationale for all four: changes risk pinned-span drift on certified plan text, including its single-use validation block); entry 5 (R-2) was added in round r2, entry 6 (F-7) in round r3, and entries 7-8 (F-9, F-10) in round r4, all deferred for the same pinned-span reason. Entry 9 (F-1) is an out-of-scope note, not a deferral: it needs its own fix outside this plan.

1. **F6 (Medium)** (r1 on-disk staging doc numbers these F6/F7 without a dash), `agents/skills/execute-plan/SKILL.md` ("Class membership in the two backlog-by-default classes defined by"): Routing pointer mixes two concerns in one ~150-word paragraph and embeds a restatement of the owner's evidence rules. Text is verbatim from the certified plan (r11); rewording risks pin drift for a stylistic gain. Backlog as wording-density cleanup.
2. **F7 (Medium)** (r1 on-disk staging doc numbers these F6/F7 without a dash), `agents/skills/review-agents/review-panel-selection.md` ("Before staging multiple findings that one rule's restatement explains"): Fan-out policy placed in "Focused panels" though it is a general staging rule; canonical sibling is "Tiered ownership" Hard rule. Plan pinned "near the focused-panel rules"; relocation is a plan-text change. Backlog as placement follow-up for a future plans/staging change.
3. **F14 (Low)**, `agents/skills/execute-plan/SKILL.md`: Four inherited-wording items: (a) re-entry sentence ordinal-vs-type ambiguity; (b) exit-hybrid "typically design-simplicity and risk" lists a lens the precondition already required, and the full-panel exemption attaches only to the no-production branch; (c) exit-hybrid reset trigger narrower than digest mutation (skip-path pass may not reset the once-only allowance); (d) clean row may close standing_continue before a reconciliation detour. Each is a non-blocking polish/semantics item on certified text; backlog as one item naming all four.
4. **F15 (Low)**, plan `## Validation Commands` block: (a) Group [3] lacks an absence probe for the superseded short-form clean-review row (probe-proven gap); (b) group [6] deny-list omits other runtime names. One-shot gate, shipped text clean; backlog as validation-block hardening for reuse.
5. **R-2 from r2 (Medium)**, `agents/skills/execute-plan/SKILL.md` (skip-path gate item: "On the Step 3.3-skip path, the skip-path receiving-review pass ran"): the skip-path gate item requiring the skip-path receiving-review pass to have run is unsatisfiable on a zero-findings round (no residuals means no pass to have run). Suggested fix: condition the item on residuals existing ("with no residuals, no pass is required"). This modifies certified plan text (Task 2 item 5); deferred for the same reason as the items above. Source: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r2.md`, finding F-10, `blocking: false`.
6. **F-7 from r3 (Low)**, `agents/skills/execute-plan/SKILL.md` (counting paragraph, quoted span "Every launch of a Step 3.1 review panel increments"): the opening universal ("Every launch of a Step 3.1 review panel increments `review_round`") reads as contradicting the first-free-re-entry exception defined later in the same sentence chain. Suggested fix: reword the opening to carve out the exceptions (e.g., "Every launch of a Step 3.1 review panel except a verification-gate or timeout re-entry increments `review_round`"). This is certified plan text (Task 1 counting paragraph, pinned by validation group [1] expect_once spans); deferred for the same reason as the items above. Source: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r3.md`, finding F-7, `blocking: false`.
7. **F-9 from r4 / R-1 (Low)**, `agents/skills/execute-plan/SKILL.md` (quoted span "Step 3.5 treats a standing_continue line whose session key"): the ambiguous-means-absent rule is scoped to Step 3.5 only; at Step 3.1 a resumed loop could honor a stale session-key standing_continue line and launch one over-budget round before the Step 3.5 ask fires (recovery within iteration). Suggested fix: widen scope to "Phase 3 treats ... as absent". This modifies certified plan text (Task 1 counting paragraph); deferred for the same reason as the items above. Source: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r4.md`, finding F-9, `blocking: false`.
8. **F-10 from r4 / DS-3 (Low)**, `docs/maintenance/glossary.md:38-40`: the Review iteration cap entry restates operational detail (proceeds-to-Phase-4, standing-instruction lifecycle) beyond a definition; drift risk vs the owning skill. Suggested fix: trim to definition + owner cite ("counting and stop semantics owned by execute-plan Step 3.5"). This is Task-0-committed plan artifact text; deferred for the same reason as the items above. Source: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r4.md`, finding F-10, `blocking: false`.
9. **F-1 from r4 (out-of-scope note, not a deferral)**, `agents/skills/plans/SKILL.md:454,456`: two rules numbered 22 (breaks number-referenced cites; renderer renumber divergence). OUT OF SCOPE for this plan (plan-excluded file; introduced by earlier branch work codifying UL#263/264, commits 2531e90/1f57764 era); needs its own fix outside this plan. Source: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r4.md`, finding F-1.

## Location

- `agents/skills/execute-plan/SKILL.md` (F6 "Class membership in the two backlog-by-default classes defined by" paragraph; F14 counting paragraph / exit-hybrid rows)
- `agents/skills/review-agents/review-panel-selection.md` (F7 "Before staging multiple findings that one rule's restatement explains")
- `docs/plans/` (active) `2026-09-01-phase3-review-churn-control.md` `## Validation Commands` (F15)

## Suggested fix

Reword/relocate per each finding's review analysis, only alongside a plans-skill change that re-pins affected spans; for F-15, extend the validation block only when it is reused as a template.

## Severity and source reference

- Staging doc: `docs/reviews/2026-09-02-phase3-review-churn-control-code-review-r1.md`, round r1, findings F6 (Medium), F7 (Medium), F14 (Low), F15 (Low) (the r1 on-disk staging doc numbers all four without a dash); all `blocking: false`.

## Why not fixed now

Deferred by the address-review pass (this run): changes risk pinned-span drift on certified plan text, including its single-use validation block, for non-blocking gains. Owner: this backlog item (orchestrator-staged decision, round r1; R-2 entry added in round r2; F-7-from-r3 entry added in round r3; entries 7-9 added in round r4).

## Entries from round r5 (deferrals-only clean round; no digest mutation)

10. (r5 CC-1, Low, agents/skills/review-agents/review-panel-selection.md) Pre-plan line 50 ("Before loop exit, if the clear-candidate round would omit `design-simplicity`, include it in a hybrid pass") carries no at-most-one bound or once-only-reset and sits adjacent to the new exit-hybrid-once rule at line 51; could be read as mandating two hybrid passes. Fix candidate: one-clause scope amendment deferring to the exit-hybrid-once rule. Deferred: fixing mutates the digest at the cap (round 5); wording ambiguity only, behavior converges on one hybrid.
11. (r5 R-1, Low, agents/skills/execute-plan/SKILL.md Step 3.4 row 1) Row 1 "or the pass fixed nothing" drops the digest-mutation qualifier row 4 keeps; the Review end condition freshness gate catches any mismatch at exit, so wording-precision only. Fix candidate: "No (no address pass ran, or the pass neither accepted fixes nor mutated the digest)". Deferred: same cap rationale.
12. (r5 CD-1 + CD-2, Low, docs/history/backlog/*this file* and docs/plans/2026-09-01-phase3-review-churn-control.md) (a) Entry 7's line anchor was stale after the frontmatter line insertion; quoted span remains unique and load-bearing; line numbers dropped. (b) Task-0 checkbox pins commit message `plans: phase3 review churn control plan (Phase-1 artifacts)` which never existed verbatim; artifacts actually landed as 1f57764/f98f7ac after the plan's own review rounds; substance satisfied, rewording risks pin drift. Deferred: both are citation hygiene.

## Dispositions (2026-09-02)

- Entry 4 (F15) and CD-2: frozen-history dispositions (archived plan; the two validation-block hardenings apply when the block is reused as a template; the Task-0 commit-message citation is historical).
- Entry 8 (F-10/DS-3): prescribed into Task 4 (glossary trim).
- CD-1: satisfied by this edit (the entry 7 and entry 12 line-number mentions are dropped here).
- Entries 9, R-2, F-7, F-9, F14, F6, F7, CC-1, and r5 R-1 (entry 11, Step 3.4 row 1): prescribed into the plan tasks above.
