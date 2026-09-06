# Backlog: strengthen the missing-parent arm's path predicate (parent-vs-child naming)

- **Status:** done
- **Origin:** execute-plan Phase 3 review r6 (summarizer-hardening round 2), finding F2 (risk, security#weak-witness-substring-predicate; duplicate/weak-witness class)
- **File:** `scripts/summarize_review_stats.py` private_permissions selftest family, missing-parent arm

## Problem

The r5 F3 missing-parent arm asserts the helper's PermissionsError message contains `str(missing_parent)`, but for the three child-taking helpers the exercised path is `missing_parent / "child"`, so the parent string is a substring of the child path: a regression that renamed the error to name the child would still pass. The arm cannot mask a real failure (non-PermissionsError escapes; silent success leaves `msg is None`), so this is witness-strength only.

## Suggested fix

Tighten the predicate to exclude the child component, or assert the exact message prefix:

```python
"cannot open parent directory" in msg and str(missing_parent) in msg and "child" not in msg
```

or mirror `_expect_refusal`'s exact-match idiom against `f"cannot open parent directory: {missing_parent}: "`.
