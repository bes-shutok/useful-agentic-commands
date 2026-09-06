# Summarizer-hardening-round-2 plan: r5 review residuals

Status: done (folded by docs/plans/completed/2026-09-05-certified-plan-prose-residue-sweep.md, executed 2026-09-06)
Workflow: backlog
Source: docs/reviews/2026-09-02-plan-review-summarizer-hardening-round-2-r5.md, round r5 (review cap, blind certification), findings F1 + F2, both Low non-blocking, deferred at the round cap (folding at the cap would have required a sixth round on docs/plans/2026-09-02-summarizer-hardening-round-2.md, certified ready=yes at digest 8dddedc95d11d9aeb36250635a4c3b64769bde684eafc057285180a2b1c73810).

## Residuals

1. **F1 (Low, consistency)**: the plan's Task 7 union enumeration names the doc family's source_kind-mismatch case but not the rfc family's identical case (`scripts/validate_review_staging.py:3595`). The "union of today's cases" phrasing preserves the case mechanically; wording only. Fix opportunistically during plan execution or fold into the Task 7 commit message checklist.
2. **F2 (Low, consistency)**: Task 2's "before the anomalies line" note-timing phrasing describes an untestable stdout/stderr interleaving; the control-flow requirement is already clear from the task body. Reword at the next plan touch.

Both were verified non-blocking by the r5 blind panel; the certified digest intentionally does not include them.
