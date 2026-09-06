# Validator pass r4 deferred: space-before-semicolon typo in python_guidelines guideline 12

Status: done (executed via plan 2026-09-05-validator-pass-r4-deferred-residuals, branch 2026-09-06-validator-pass-r4-residuals)
Workflow: backlog
Source: docs/reviews/2026-09-02-validator-pass-code-review-r4.md F5 (quality#typo); deferred per fix-risk stop with the rest of the r4 round

## Problem

The em dash cleanup in `projects/.ai-playbook/python_guidelines.md` (guideline 12) left "silently skipped ;" with a stray space before the semicolon; the other replacements in the same pass have none.

## Suggested fix

Drop the space before the semicolon.
