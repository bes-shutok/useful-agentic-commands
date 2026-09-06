# Backlog: review-driven test false-green fixes need a completeness checklist

Status: done
Workflow: backlog
Source: 2026-09-01 execute-plan Phase 3 reflection (project and ticket ids
elided); user direction to backlog the “finding-scoped InOrder / fresh-load
fix without a one-shot helper” failure mode
Severity: Medium (testing / review harness; causes fractal non-blocking
findings across rounds)
Anchors: `agents/skills/execute-plan/SKILL.md` (address-review scope),
`agents/skills/receiving-review/SKILL.md`, testing lens in
`agents/skills/review-agents` / doing-code-review worker prompts,
`agents/skills/unit-test-runner` (patterns only; no project tests)
Decision: user-requested playbook backlog, 2026-09-01
See also: `2026-09-01-execute-plan-five-review-cap-vs-focused-churn.md`
(Phase 3 backlog-by-default for sibling unit gaps)

## Problem

When review finds a **false-green** unit (example shapes: outcome-only asserts;
`times(N)` without order; shared mutable fixture leaking first-pass state),
address-review typically hardens **that one test**.

The same production invariant often has a **family** of units (success,
conflict, empty, multi-op, sibling variants). The next focused testing round
discovers the next member of the family still lacks the witness. Severity
gets promoted because “this is the only guard for X,” even though X is
already pinned elsewhere.

There is no skill rule that says: for `testing#always-passes` (or equivalent)
on a **shared production pattern**, prefer **one completeness task**:

- extract a shared assertion helper / fixture factory, **or**
- enumerate the unit family and migrate all members in one address pass,

instead of shipping finding-scoped one-offs that regenerate.

## Suggested fix

1. **Testing lens / receiving-review:** when staging or fixing
   `testing#always-passes` against a shared production path, require either:
   - a **family checklist** (list sibling tests that must gain the same
     witness), or
   - a **shared helper** adoption plan,
   before marking the finding fixed.
2. **Address-review partner default:** “fix this false-green” means fix the
   **family** or add helper + migrate callers; do not close after one method
   unless the family list is explicitly deferred to backlog as one item.
3. **Phase 3 exit:** missing InOrder/fresh-load on unit B, when unit A already
   pins the same lock-before-classify (or equivalent) production path, is
   **backlog by default** unless it is the sole witness for that path
   (see exit-policy table in the five-review-cap backlog).
4. **Optional:** small shared testing guideline blurb under playbook coding /
   testing guidance: prefer assertion helpers for cross-cutting concurrency
   witnesses; avoid copy-paste InOrder blocks that drift.

## Why not now

Needs a concrete checklist template in review-staging or receiving-review and
agreement that multi-test migrations are in scope for a single address pass.
Implement in a playbook PR; not a product-repo-only fix.

## Non-goals / hygiene

- No project class names, test method names, or module paths.
- Does not require every codebase to adopt one named helper; it requires
  **family completeness** (helper **or** enumerated migration) when reviews
  drive false-green fixes.
