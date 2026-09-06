# Summarizer: shared parent-dirfd open/close context manager for the four hand-copied scaffolds

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-04-2026-09-02-summarizer-hardening-round-2-code-review-r1.md, round r1, finding F9 (overflow manifest, design-simplicity, Low, non-blocking); deferred at orchestrator direction (fix 8 / defer 2 pass). Scoped up 2026-09-04 (r2 overflow manifest, same worker/pattern): from a shared dirfd flag constant to a shared parent-dirfd open/close context manager.

## Problem

Four hardened helpers in `scripts/summarize_review_stats.py` each hand-copy the same parent-dirfd scaffold: the flag expression `os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC` into a local `dir_flags`, the `os.open(str(path.parent), dir_flags)` with the errno-split OSError translation (r2 F2), and the `finally: os.close(parent_fd)` teardown: `tighten_parent_ai_playbook`, `ensure_private_dir`, `create_private_file_exclusive`, and `_atomic_write_private`. A future edit to one copy (e.g. dropping `O_NOFOLLOW` or `O_CLOEXEC`, or fixing one translation message) leaves the other three stale, silently reopening the symlink-refusal window or drifting the message contract in only some helpers. A shared context manager (e.g. `_pinned_parent(path)`) yielding the pinned fd and owning both the open/translate and the close would make the drift impossible; a bare shared flag constant (the original r1 F9 scope) covers only the flag expression.

## Location

`scripts/summarize_review_stats.py`: the `dir_flags = ...` lines plus the surrounding parent-open/translate/close scaffolds inside `tighten_parent_ai_playbook`, `ensure_private_dir`, `create_private_file_exclusive`, and `_atomic_write_private` (post r2-fix line numbers shift; grep `dir_flags = os.O_RDONLY`).

## Suggested fix

Introduce one shared parent-dirfd open/close context manager (named so the per-helper grep pins can address it) that opens the parent with the pinned flags, applies the r2 F2 errno-split translation, yields the fd, and closes it in a finally; replace the four local scaffolds with it (superseding the constants-only scope of the original r1 F9 item). Constraint: the certified plan's Validation Commands block (docs/plans/2026-09-02-summarizer-hardening-round-2.md) pins per-helper function-body grep ranges (e.g. `sed -n '/^def ensure_private_dir/,/^def [a-z_]*(/p' | grep -q dir_fd`); extracting the scaffold out of the function bodies requires amending that validation block in the same change, so the context manager must be introduced together with an amended Validation Commands block in a future plan, not folded into an execution-pass fix. Optionally add one selftest arm per helper asserting the shared manager is used (grep-based pin or flag-equality check).

## Severity and source reference

Low, non-blocking; drift risk only (behavior currently identical across the four copies). Review doc path above, round r1, finding F9 (recorded in the Overflow manifest); scoped up via the r2 review (docs/reviews/2026-09-04-2026-09-02-summarizer-hardening-round-2-code-review-r2.md) overflow manifest row.

## Why not fixed now

Deferred by orchestrator instruction (2026-09-04 fix pass): the fold conflicts with the plan's pinned per-helper grep ranges over a certified plan artifact, which must not be edited mid-execution; needs a future plan with an amended validation block. The r2 overflow disposition additionally scoped the item up to the full context manager (not just the flag constant) so the future plan extracts the whole scaffold in one pass.
