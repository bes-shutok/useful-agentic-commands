# Backlog: derive mutual-exclusivity message with the terminal "and" restored

- **Status:** done (executed via plan 2026-09-05-validator-pass-r4-deferred-residuals, branch 2026-09-06-validator-pass-r4-residuals)
- **Origin:** execute-plan Phase 3 review r6 (summarizer-hardening round 2), finding F1 (correctness-completeness, quality#message-regression-cosmetic)
- **File:** `scripts/validate_review_staging.py` `main()` source-flag wiring

## Problem

The r5 F4 fix made the mutual-exclusivity `parser.error` text table-derived (`", ".join(...)`), which dropped the Oxford "and": the message changed from "--source-plan, --source-rfc, and --source-doc are mutually exclusive" to "--source-plan, --source-rfc, --source-doc are mutually exclusive". No consumer keys on the "and" (Case E asserts only the "mutually exclusive" substring and rc 2), so this is a cosmetic wording regression only.

## Suggested fix

Render the flag list with a terminal "and", still table-derived:

```python
flags = [f for f, _d, _k in _SOURCE_FLAG_TABLE]
text = ", ".join(flags[:-1]) + ", and " + flags[-1] + " are mutually exclusive"
```

Byte-identical to the pre-c341e07 text and stays single-registration with the table.
