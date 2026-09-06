# dirfd-relative open loses full-path context in non-translated OSError diagnostics

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-06-2026-09-05-summarizer-round-3-residuals-code-review-r3.md, round r3, finding F1 (Low, non-blocking), correctness-completeness worker; deferred at orchestrator direction (plan-prescribed re-raise shape)

## Problem

`read_private_file`'s final-component open is dirfd-relative (`os.open(path.name, ..., dir_fd=parent_fd)`), so a non-translated `OSError` message surfaces only the bare final component (for example `[Errno 2] No such file or directory: 'file.json'`) instead of the full path the pre-rewrite `os.open(str(path), flags)` surfaced. The strict-audit baseline path pre-checks `is_file()`, so the common case still reports fully, but any future non-baseline caller of read_private_file (today the only caller is load_baseline, whose strict-audit path pre-checks is_file) would report a bare final component; sidecar content is read by read_byte_buffer, which still opens the full path string and is unaffected. Stderr/log clarity only; no behavioral or contract change.

Pattern: quality#dirfd-open-error-loses-path-context.

## Location

`scripts/summarize_review_stats.py`, `read_private_file` final-component open (~line 351).

## Suggested fix

Wrap the re-raise of non-translated `OSError`s so the message carries the full path (for example `raise OSError(f"{path}: {exc}") from exc` or an equivalent context-bearing wrapper), keeping the plan's message contracts untouched.

## Severity and source reference

Low, non-blocking; plausible-edge reachability, local blast radius. Review doc path above, round r3, finding F1.

## Why not fixed now

Deferred by orchestrator direction (2026-09-06 r3 fix pass): the r3 plan (docs/plans/2026-09-05-summarizer-round-3-residuals.md) prescribes "re-raising other OSErrors" unchanged on this branch, so changing the re-raise would deviate from the certified prescription; recorded as a diagnostics residual.
