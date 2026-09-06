# Backlog: reword stale "may print it more than once" claim in the unclosed-fence warning

- **Status:** open
- **Origin:** execute-plan r1 code review F4 (branch 2026-09-06-validator-pass-r4-residuals), finding F4 (correctness-completeness, implementation#stale-warning-wording)
- **File:** `scripts/validate_review_staging.py` `parse_markdown_findings` unclosed-fence warning literal (anchor `# unclosed-fence-warning` in the selftest)

## Problem

The unclosed-fence fallback warning kept its pre-change wording when the warning migrated from a raw stderr print to the `warn` callback (plan: docs/plans/2026-09-05-validator-pass-r4-deferred-residuals.md). Its final clause still says "so a full validation run may print it more than once", which is stale: the parser no longer prints at all, the warning now travels through the `warn` callback into `ValidationResult.warnings` and surfaces as `WARN:` lines or JSON entries. The plan's byte-identical-text Design Invariant deliberately forbids changing the wording this run, so the fix is deferred.

## Suggested fix

In a future plan, reword "print it more than once" to describe the actual transport (for example "report it more than once", since a current-v1 validation parses the Findings section twice and yields two `warnings` entries), and update the selftest pins in the same change: the full-text equality pin in the `(# unclosed-fence-warning)` check (added r1 F2) and any other pin of the tail clause. The staging doc is docs/reviews/2026-09-06-2026-09-05-validator-pass-r4-deferred-residuals-code-review-r1.md (F4, round r1); deferred because the plan invariant pins the text byte-identical (user-approved plan scope).
