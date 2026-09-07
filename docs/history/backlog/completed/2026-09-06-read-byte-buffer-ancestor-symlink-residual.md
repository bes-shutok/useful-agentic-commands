# read_byte_buffer still opens sidecar content by full path string (ancestor-symlink residual)

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-06-2026-09-05-summarizer-round-3-residuals-code-review-r2.md, round r2, finding F4 (Low, non-blocking), risk worker; deferred at orchestrator direction (out-of-scope frozen path)

## Problem

The pinned-parent guarantee landed by the round-3 residuals plan (docs/plans/2026-09-05-summarizer-round-3-residuals.md) covers `read_private_file` and the four create/tighten helpers via the shared `_pinned_parent` context manager. `read_byte_buffer` (the reader the strict audit actually uses for sidecar content) still opens the full path string with only a final-component pre-check, so an attacker with write access to a sidecar ancestor directory can swap a symlink into an ancestor path and redirect the read. No wrong behavior was introduced by that branch and no docstring overclaims coverage; this is pre-existing code that the plan's Review Scope froze.

Pattern: security#read-byte-buffer-ancestor-residual.

## Location

`scripts/summarize_review_stats.py`, `read_byte_buffer` (~line 548).

## Suggested fix

Route `read_byte_buffer` through a shared pinned-parent open (reuse `_pinned_parent` and open the final component dirfd-relative with `O_NOFOLLOW`), mirroring the `read_private_file` rewrite. Worth doing if sidecar ancestors are ever considered attacker-writable.

## Severity and source reference

Low, non-blocking; plausible-edge reachability, single-service blast radius. Review doc path above, round r2, finding F4.

## Why not fixed now

Deferred by orchestrator direction (2026-09-06 r2 fix pass): `read_byte_buffer` is outside the plan's Review Scope (frozen path); changing it mid-run would deviate from the certified plan.
