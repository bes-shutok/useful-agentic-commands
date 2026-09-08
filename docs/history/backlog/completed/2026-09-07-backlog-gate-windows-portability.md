# Backlog: backlog-gate hardening r5 Windows-portability residuals

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-06-backlog-gate-hardening-code-review-r5.md (two Low, non-blocking findings; deferred at the 5-round cap: out-of-platform scope, both fail-closed or partial on an unsupported host)
Severity: Low
Scope: scripts/check_backlog_inbox_location.py

## Items

1. `security#hot-dirs-windows-sep-split`: on Windows, a `backlog_hot_dirs` entry with native backslash separators (`docs\maintenance`) passes validation but `scan_repo` builds `hot_dir_parts` with `h.split("/")`, so the configured dir is silently inert (partial rule-1 disable without warning). Fix: build segment tuples portably (`tuple(Path(h.replace("\\", "/")).parts)` or normalize separators before splitting).

2. `quality#cross-drive-relpath-crash`: on Windows, a `backlog_dir`/`backlog_completed_dir` value resolving to a different drive makes `os.path.relpath` raise an uncaught `ValueError` (crash instead of the documented warn-and-fallback; fails closed). Fix: wrap the relpath in `try/except ValueError` treating it as the degenerate case, or test resolved containment before deriving `rel`.

## Why not fixed now

Deferred at the r5 cap of the execute-plan review budget: both require a Windows host to verify empirically (none available), the repo's gate runs on darwin/Linux, and both failure modes are fail-closed (uncaught crash / single-dir coverage loss with the rest of the gate intact). Fix during the next Windows-support or cross-platform pass over the gate script.
