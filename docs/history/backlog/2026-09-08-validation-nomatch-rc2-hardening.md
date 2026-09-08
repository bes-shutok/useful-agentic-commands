# Backlog: Validation Commands no_match rc-2 hardening (template-level)

Status: open
Origin: Phase 3 code review r1 (F2, Info) of the review-pointer-wiring-polish execute-plan run, 2026-09-08
Source finding: docs/reviews/2026-09-08-review-pointer-wiring-polish-code-review-r1.md

## Finding

In plan Validation Commands blocks, the common `no_match()` helper treats any non-zero grep exit as clean: `if grep -qF -- "$pat" "$f"; then fail; fi`. A grep error other than "no match" (e.g., an unreadable file) would pass as no-match. `test -f` pre-checks close the missing-file case but not other rc-2 causes.

## Remedy

Harden the shared plan template's `no_match` recipe to capture the grep exit status and fail on rc >= 2 (match → fail as forbidden-text-present; rc >= 2 → fail as grep error). Template-level change for future plans; explicitly no action required for the plan that surfaced it (its files are pre-checked and readable).
