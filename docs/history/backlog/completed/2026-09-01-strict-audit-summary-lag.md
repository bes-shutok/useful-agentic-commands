# Strict-audit exit code and stdout summary lag after a retry-absorbed mutation

Status: done
Completion: Completed by docs/plans/completed/2026-09-02-summarizer-hardening-round-2.md (executed + reviewed 2026-09-04/05).
Workflow: backlog
Source: docs/reviews/2026-09-01-summarizer-publish-lock-hardening-code-review-r1.md, round r1, findings F1 + F8, risk worker

## Problem

After a retry-absorbed sidecar mutation (the exact race `publish_with_recheck` hardens), `cmd_strict_audit`'s exit code and stdout `classes=`/anomaly summary still reflect the pre-race snapshot while the published report is rebuilt from the refreshed buffers. A CI gate keying on the return code gets a verdict computed from pre-race bytes the plan itself declares stale. Related residual (F8): the publish-closure freshness contract ("every caller MUST derive its published payload content from the current ``buffers`` contents at invocation time"; cohort membership may stay pinned to the pre-publish ledger or snapshot) has no mechanical enforcement (`publish_with_recheck` cannot observe what `publish_fn` serialized), so a future caller that pre-serializes bytes outside the closure would pass every existing selftest while reintroducing the stale-snapshot defect.

## Location

`scripts/summarize_review_stats.py`:

- anomaly summary and exit code: `cmd_strict_audit`, after `publish_with_recheck(buffers, _publish)` returns (`anomalies = len(audit) + len(ledger["baseline-missing"]) + len(replaced)` through the `return 0 if anomalies == 0 else 1`);
- the contract text: `publish_with_recheck` docstring (load-bearing contract block).

## Suggested fix (options)

- Attempts-taken signal from `publish_with_recheck` (signature change; needs its own plan): on nonzero retry count, recompute `replaced` over the current buffers (cheap digest compare) or emit a one-line note that the summary reflects the pre-publish ledger.
- Recompute `replaced` after a successful publish (touches frozen `cmd_strict_audit` control flow).
- Note-on-retry: emit a stderr/stdout note whenever at least one retry occurred.
- Caller-fixture tripwire for the contract (F8 debug-mode half): a debug-mode assertion that re-derives input digests after `publish_fn` returns, failing closed when published bytes diverge from the refreshed buffers.
- Extend the report's `availability` block with a parse-drop count (r2 finding F1, risk worker; probe-verified 2026-09-01): a sidecar rewritten to unparseable bytes after the initial read is absorbed by the retry and then silently dropped by the publish-time classification (`_classify_current` counts the drop and excludes the sidecar before classification), so `availability.skipped_malformed` stays 0 even though a cohort vanished. The r2 fold landed the minimal stderr variant (a "dropped N unparseable sidecar(s)" operator note plus an unparseable-at-retry fixture arm), but surfacing the count inside the report itself would touch the frozen `build_effectiveness_report` / frozen control flow, so it rides here with the other frozen-builder options.
- Delta variant (r3 finding F8, risk worker): reserve the "dropped N unparseable" wording for retry-induced drops by emitting the delta between the classification-pass drop count and the pre-publish ledger's `unreadable` class count (`dropped - len(ledger["unreadable"])`); chronically unreadable sidecars would then stop firing the note on every run (they already appear in the stdout `classes=` summary, and the emit-site comment records that the current count includes them). Touches note semantics, so it rides here rather than in the r3 fold.

The cheap documentation half is already landed (r1 triage): the `publish_with_recheck` docstring records both the lag and the cohort-membership caveat, and points new callers at a `strict_audit_stale_snapshot`-modeled fixture.

## Severity

Medium (F1) / Low (F8); reachable only in the race edge case the plan targets; the published report itself is correct.

## Why not fixed now

The durable fixes require a `publish_with_recheck` signature change or touching `cmd_strict_audit` control flow that docs/plans/2026-09-01-summarizer-publish-lock-hardening.md froze (r1 triage decision: fold cheap additive docstring fix, backlog the structural half). Captured so the residue is durably tracked instead of buried in the review staging doc.
