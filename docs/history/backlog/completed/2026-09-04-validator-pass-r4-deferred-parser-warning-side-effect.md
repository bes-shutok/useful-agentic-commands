# Validator pass r4 deferred: surface unclosed-fence fallback structurally instead of stderr print

Status: done (executed via plan 2026-09-05-validator-pass-r4-deferred-residuals, branch 2026-09-06-validator-pass-r4-residuals)
Workflow: backlog
Source: docs/reviews/2026-09-02-validator-pass-code-review-r4.md F2 (simplification#yagni); deferred per fix-risk stop; NOTE: deliberately contradicts the 2026-09-02-validator-pass plan Assumption (warn-level stderr diagnostic), so this is a conscious contract change for a future plan, not a bug fix

## Problem

`parse_markdown_findings` prints the unclosed-fence warning directly to `sys.stderr`, turning a pure parser into a side-effecting one. Every selftest caller parsing an unclosed-fence fixture must wrap the call in `redirect_stderr`, and callers composing parse + readiness + validation cannot silence the warning selectively.

## Suggested fix

Keep the parser silent and surface the fallback event structurally (return it alongside findings, or accept an optional warn callback defaulting to a printer at the CLI boundary) so selftests assert on returned values instead of captured stderr. Migrate the existing warning selftest and the r6 F3 recovery pins in the same change.
