# Summarizer read path ancestor-swap dirfd gap (read_private_file)

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-04-2026-09-02-summarizer-hardening-round-2-code-review-r3.md, round r3, finding F2, risk worker (concurrency origin)

## Problem

`read_private_file` opens the full path string (`os.open(str(path), O_RDONLY | O_NOFOLLOW | O_CLOEXEC)`), so `O_NOFOLLOW` guards only the FINAL component; the `_reject_symlink` pre-check is likewise final-component-only. A local attacker with write permission on an ANCESTOR directory of the private path can swap in a symlink after the pre-check and redirect the read; attacker-chosen bytes would be returned as baseline manifest content. The sibling create/tighten helpers pin the parent with an `O_DIRECTORY | O_NOFOLLOW` dirfd and dirfd-relative opens, exactly to close this parent-swap window; the read path did not get the same treatment. On the standard call paths the 0700 tightening of the private tree blocks the attacker, so only non-standard private paths outside the tightened tree are exposed.

## Location

`scripts/summarize_review_stats.py`, `read_private_file` (the `os.open(str(path), flags)` call, ~line 341).

## Suggested fix

Mirror the create helpers: open the parent with `os.open(str(path.parent), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC)` (with the r2 F2 errno translation), then open the final component dirfd-relative: `os.open(path.name, O_RDONLY | O_NOFOLLOW | O_CLOEXEC, dir_fd=parent_fd)`, translating ELOOP/ENOTDIR-family errnos to the existing `PermissionsError` message. Add a selftest bypass arm staging a symlinked ancestor with `_reject_symlink` patched to a no-op, pinning the refusal.

## Severity

Medium (concurrency default), reachability theoretical on standard paths (guarded today by the 0700 tightening of `~/.ai-playbook/` and the private tree).

## Why not fixed now

The certified plan's Task 5 (docs/plans/2026-09-02-summarizer-hardening-round-2.md) prescribes the exact current mechanism (`os.open(str(path), O_RDONLY | O_NOFOLLOW | O_CLOEXEC)`), so a dirfd restructure would deviate from the certified plan's prescribed fix; per the round-3 disposition (same class as the deferred r1 F4 delta-formula finding) the change ships with a future plan rather than in-run. Recorded by the round-3 triage agent on user-directed disposition (defer F2).
