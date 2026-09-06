# Private-path helper symlink TOCTOU (pre-check-only defenses)

Status: done
Completion: Completed by docs/plans/completed/2026-09-02-summarizer-hardening-round-2.md (executed + reviewed 2026-09-04/05).
Workflow: backlog
Source: docs/reviews/2026-09-01-plan-review-summarizer-publish-lock-r1.md, round r1, findings F6 + F9, risk worker

## Problem

The telemetry lock-file symlink TOCTOU (docs/history/backlog/completed/2026-08-28-telemetry-lock-symlink-toctou.md) was closed 2026-09-01 with an `O_NOFOLLOW` lock open, but the same threat model remains reachable at directory and file granularity in the class of private-path helpers that defend symlink swaps with a pre-check only: between the symlink rejection (`_reject_symlink` / `lstat`-style check) and the subsequent open/mkdir/write, a local attacker can swap in a symlink and the operation follows it, breaking the private-dir guarantee.

## Location

All in `scripts/summarize_review_stats.py`:

- `ensure_private_dir` (directory granularity),
- `_atomic_write_private` (directory granularity),
- `tighten_parent_ai_playbook` (directory granularity),
- `read_private_file` (file granularity).

`create_private_file_exclusive` is file-level safe via its exclusive create (`O_CREAT | O_EXCL` refuses to follow an existing symlink) and carries only the parent-directory window shared with the helpers above.

## Suggested fix

Kernel-grade defenses at each granularity: open directories/files with `O_NOFOLLOW` (and `O_CLOEXEC`) or use `openat`-style dirfd-relative paths so the pre-check becomes advisory only; add selftests staging symlinked paths and asserting clean failure. Out of scope for docs/plans/2026-09-01-summarizer-publish-lock-hardening.md, which froze the neighboring helpers.

## Severity

Low/Medium (local attacker with write access to the parent dirs; pre-existing on main).

## Rider (operator UX, from finding F9)

When a raced symlink is hit on the lock path, the failure surfaces as a raw `OSError` traceback (errno `ELOOP`) with no pointer to the lock path; the friendly permission error covers only the static case. Revisit the operator-facing error message together with the dir-level fix.

## Why not fixed now

The 2026-09-01 summarizer publish-lock hardening plan froze all neighboring helpers so its lock-path change stayed minimal (review r1 F6: fixing them in-branch would violate the plan's own freeze). Captured per the repo's backlog-capture rule so the residue is durably tracked instead of buried in the closure record.
