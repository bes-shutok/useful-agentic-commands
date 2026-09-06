# Backlog inbox gate: symlinked hot-dir subdirectory bypass (rule 1)

Status: open
Workflow: backlog
Source: docs/reviews/2026-09-03-backlog-inbox-location-gate-code-review-r1.md, round r1, finding F7, risk worker

## Problem

`scripts/check_backlog_inbox_location.py` rule 1 walks the hot dirs with `os.walk(..., followlinks=False)` (the default). A symlinked subdirectory inside a hot dir is therefore not descended, and an untracked token-named backlog-inbox file behind such a symlink is invisible to both rules (rule 2 sees only tracked files). A misfiled inbox file behind a symlinked hot-dir subdirectory bypasses the gate.

## Location

`scripts/check_backlog_inbox_location.py`, `scan_repo` rule-1 loop (`os.walk(hot_path)`).

## Suggested fix

If hardening is wanted: resolve each symlinked directory entry and traverse only when the resolved target stays inside the hot dir (or flag it for manual review). Do NOT enable `followlinks=True` unconditionally; that would let a planted symlink escape the tree (the current traversal-safety property, no escape from the scanned tree, is preserved by the default).

## Why not fixed now

Threat model is accidental agent misfiling, not adversarial symlink planting; no plan workflow creates symlinks inside hot dirs, and safe traversal hardening is invasive relative to that model. Deferred by the r1 address pass (execute-plan Phase 3) per the fix plan: F7 is explicitly a no-fix/backlog finding.
