# Backlog: plans skill must grill any scope extension

Status: done
Workflow: backlog
Source: post-mortem on a feature plan that absorbed a neighboring security/auth concern via high-confidence assumptions; execute-plan then shipped the expanded plan faithfully
Severity: High (systematic overscope risk for every plan authored under the current confidence gate)
Scope: `agents/skills/plans/SKILL.md` Phase 1 (requirements discovery, confidence gate, Step 1.2 scope boundaries, Step 1.4 confirmation); cross-link from `grill-with-docs` / `grilling` integration notes if needed

## Problem

The `plans` skill already has a confidence gate: low-confidence points must go through `grill-with-docs`; high-confidence points may be recorded as assumptions and batch-confirmed.

That gate is insufficient for **scope extension**. Agents routinely classify adjacent security, identity, tenancy, rollout, or sibling-service concerns as high-confidence assumptions (basis: "another ticket owns production" or "fail-closed is safer"), then fold verifier stacks, headers, filters, and tests into the same plan. The user may batch-confirm a long assumption list without noticing that the plan now delivers two independent products.

`execute-plan` does not re-open scope; it implements the plan. Review loops optimize against the plan's Review Scope, so they reinforce the expansion rather than cut it. Overscope therefore becomes durable once Phase 1 misclassifies an extension as an assumption.

## Why not fixed now

This is a skill-contract change, not an incidental wording tweak. It needs an explicit Phase 1 hard gate, updated confirmation template, and likely a plan-review check that flags in-plan work for concerns the plan itself marks as owned elsewhere. Captured here so the next `plans` skill edit can land it deliberately.

## Suggested fix

In `plans` Phase 1, add a **scope-extension hard gate** independent of the existing high/low confidence tiers:

1. **Define scope extension:** any proposed plan work that is not required to deliver the stated primary goal (ticket/title/gist), including but not limited to: a second auth or identity mechanism, a cross-cutting header/principal model, a sibling-service contract the ticket does not own, a multi-tenant or multi-market product shape, or any concern the plan already labels as owned by another ticket/feature.
2. **Mandatory path:** before writing or expanding the plan file to include that work, invoke `grill-with-docs` and get an explicit user decision: keep in this plan, split to a separate plan, or defer (OUT / Ship when). Do not record the extension as a high-confidence assumption and batch-confirm it.
3. **Default recommendation in the grill:** split or defer; keep the current plan minimal for the primary goal.
4. **Confirmation block:** Step 1.4 must list every accepted scope extension separately from ordinary assumptions, each with the grill outcome (in / split / defer). A bare `yes` on assumptions must not silently admit extensions that were never grilled.
5. **Contradiction check:** if OUT-of-scope or "owned by ticket X" prose coexists with Tasks/Files that implement that concern, treat as unresolved scope extension; grill or remove the tasks before plan write.
6. Optional follow-up: teach `review-plan` to flag the same contradiction as blocking.

Do **not** teach `execute-plan` to re-grill mid-implementation; keep scope control at plan authoring.

## Acceptance criteria

- `plans` Phase 1 documents the scope-extension hard gate and requires `grill-with-docs` before any such work enters Terms, Assumptions, Tasks, Files, or Review Scope.
- High-confidence assumptions are explicitly forbidden as the vehicle for admitting scope extensions.
- Step 1.4 confirmation distinguishes ordinary assumptions from grilled scope-extension decisions.
- Integration text notes that `execute-plan` remains faithful to the plan and is not the place to discover overscope.
- No consumer-repo or product-specific examples are required in the skill text; keep the rule domain-agnostic.

## Evidence shape (general)

A plan whose primary goal is one boundary (for example encryption at ingress) also ships a second boundary (for example request identity / tenant principal / sibling propagation) justified only by assumption bullets and "owned elsewhere" prose, while Task checklists still implement the second boundary. `execute-plan` then marks those tasks done without further scope questions.
