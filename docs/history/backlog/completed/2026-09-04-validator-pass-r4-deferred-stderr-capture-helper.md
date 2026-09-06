# Validator pass r4 deferred: captured-vs-silenced stderr helper for selftests

Status: done (executed via plan 2026-09-05-validator-pass-r4-deferred-residuals, branch 2026-09-06-validator-pass-r4-residuals)
Workflow: backlog
Source: docs/reviews/2026-09-02-validator-pass-code-review-r4.md F1 (simplification#shrink); deferred per fix-risk stop after r3 fold regenerated second-generation findings

## Problem

The `buf = io.StringIO(); with contextlib.redirect_stderr(buf):` two-line prelude is copy-pasted at 13+ selftest sites in `scripts/validate_review_staging.py`, and 6 of them never read the captured buffer (pure silencing). Intent (capture vs silence) is implicit, and each new fence-family fixture must re-copy the wrapper.

## Suggested fix

Add a small `contextlib.contextmanager` helper beside `_check_empty_flag_loud_exit` distinguishing `_stderr_captured() -> StringIO` from `_stderr_silenced()`, and use it at all sites; roughly 20 boilerplate lines collapse.
