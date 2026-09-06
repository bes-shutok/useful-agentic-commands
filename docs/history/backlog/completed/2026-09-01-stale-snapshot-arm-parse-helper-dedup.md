# Strict-audit stale-snapshot family: extract a shared skipped-malformed parse helper

Status: done
Completion: Completed by docs/plans/completed/2026-09-02-summarizer-hardening-round-2.md (executed + reviewed 2026-09-04/05).
Workflow: backlog
Source: docs/reviews/2026-09-01-summarizer-publish-lock-hardening-code-review-r4.md, round r4, finding F1, design-simplicity worker

## Problem

In `scripts/summarize_review_stats.py`, the `strict_audit_stale_snapshot` selftest family extracts `availability.skipped_malformed` from published reports in two arms (`skipped2` around :3044-3055 and `skipped4` around :3131-3142) using the same twelve-line guarded-parse idiom: `_read_or_empty`, `json.loads` in try/except `ValueError`, `isinstance` dict check, `.get("skipped_malformed")`. A future report-shape change updated in one copy leaves the other asserting the stale shape, so the two arms silently diverge in what they pin.

## Suggested fix

Extract a local helper beside `_read_or_empty` and use it from both arms:

```python
def _skipped_malformed_of(path) -> object:
    raw = _read_or_empty(path)
    if not raw:
        return None
    try:
        avail = json.loads(raw.decode("utf-8")).get("availability", {})
    except ValueError:
        return None
    return avail.get("skipped_malformed") if isinstance(avail, dict) else None
```

Then `skipped2 = _skipped_malformed_of(out2)` and `skipped4 = _skipped_malformed_of(out4)`.

## Note (factual correction preserved from the same review round)

The completed plan's Task 1 arm-(c) parenthetical (docs/plans/completed/2026-09-01-summarizer-publish-lock-hardening.md) misstates the fixture mechanics: `_reject_symlink` raises the builtin `PermissionsError` (an `OSError` subclass, scripts/summarize_review_stats.py:161-169), not a module-specific summarizer error class. The characterization fixture is correct as written; the plan text is frozen history and was not reworded (r4 finding F2, dropped).
