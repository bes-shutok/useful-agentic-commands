# Backlog: single SOT for cross-cutting contract rules (stop sibling-doc fan-out)

Status: done
Workflow: backlog
Source: 2026-09-01 execute-plan Phase 3 reflection (project and ticket ids
elided); user direction to keep one source of truth and make peers reference,
remove, refactor, move to context, or archive; follow-up 2026-09-01: same
process must be part of review and execute-plan so duplication converges over
time (not a one-off product-doc cleanup)
Severity: Medium (documentation / review policy; drives regenerating
contract-docs findings across rounds)
Anchors: `agents/skills/doc-hierarchy/SKILL.md`,
`agents/skills/doc-hierarchy-upkeep/SKILL.md`, company/project documentation
hierarchy guidance, `agents/skills/execute-plan` / `receiving-review` /
`doing-code-review` / contract-docs lens / address-review path,
`agents/skills/review-staging`, `agents/skills/plans` (doc tasks)
Decision: user-requested playbook backlog, 2026-09-01; workflow-embedding
addendum same day
See also: `2026-09-01-execute-plan-five-review-cap-vs-focused-churn.md`
(Phase 3 exit / backlog-by-default)

## Problem

Cross-cutting contract rules (examples of **shape**, not project content:
activation readiness splits; shared error key ownership; Retry-After
predicates; which caller surface is undeployed) are often restated in many
living places at once: wire description, operation blurbs, caller catalogs,
integration notes, architecture indexes, decision log, glossary, operator
guides.

Review then treats each restatement as an independent SOT. Fixing one surface
leaves the next sibling "wrong," so contract-docs findings **fan out**
(N → N+1) across rounds even when the **rule** already converged on one
edited page.

That pattern:

- burns Phase 3 budget on prose synchronization;
- creates contradictory skim paths for humans;
- fights Documentation Hierarchy (Layer 2 should be lean; history/context
  should not compete as live SOT).

User direction: **keep only one SOT**. Everything else should **reference**
that SOT, or be **removed / refactored / moved to context / marked archived**.

### Process gap (why a one-off cleanup is not enough)

Even after a successful product-repo consolidation pass, the **harness** still
defaults to "fix this surface" and "stage the next sibling." Without explicit
steps in **review** and **execute-plan**, the next feature reintroduces
restatements and Phase 3 burns the same budget again. Convergence must be
**incremental and mandatory** in those workflows: each addressed doc-fan-out
finding should shrink living restatement count toward one, not rewrite the
rule into every peer.

## Suggested fix

1. **Skill rule (doc-hierarchy + upkeep + contract-docs lens):** when a
   cross-cutting rule appears in more than one living doc, reviewers and
   authors must designate a **canonical home** (usually one Layer 2 section
   or the wire contract component) and convert peers to short pointers.
2. **Review staging policy:** do not stage Medium+ "source-of-truth-drift"
   on a peer that already points at the canonical section unless the
   **pointer is missing or contradicts** the canonical text. Prefer one
   finding: "peer still duplicates rule; replace with reference."
3. **Address-review default:** when fixing dual-ownership / activation-class
   drift, update the **canonical home first**, then either (a) pointer-only
   edits on peers in the same pass, or (b) backlog peer cleanup; do not
   rewrite the full rule into every catalog row.
4. **Archive / context path:** long alternate wordings and historical
   activation narratives belong under history/context (review-excluded) or
   an explicit archived banner; not as parallel live SOT.
5. **Optional checklist** for contract-docs workers: "list every living
   restatement of this rule; if count > 1, finding is fan-out / missing
   pointer, not N independent contract bugs."

### Workflow embedding (review + execute-plan)

Encode the same process so it runs **every** relevant pass, not only when a
human asks for a SOT cleanup:

| Workflow | Required behavior |
|----------|-------------------|
| **contract-docs / design lens** (`doing-code-review`, panel selection) | Before staging N Medium+ "docs disagree" findings on one rule, list living restatements; if count > 1, stage **one** fan-out finding naming the intended canonical home (or "designate SOT"), not N independent contract bugs. |
| **receiving-review / address-review** | Fix path for doc-fan-out: (1) designate or confirm SOT, (2) update SOT if the rule is wrong, (3) convert peers to pointers or backlog remaining peers as pointer cleanup, (4) do not leave full-rule copies in catalogs "for convenience." |
| **execute-plan Phase 3** | When contract-docs findings are mostly sibling restatements of one already-fixed rule, treat as **fan-out / backlog-by-default** (or one pointer pass), not as regenerating blocking production defects. Do not spend further full/focused panels chasing peer prose after the rule has a clear SOT. |
| **execute-plan implement / plans authoring** | New or changed cross-cutting rules: write the canonical Layer 2 (or wire) section in the owning task; plan `Files:` and exit checks prefer "peers point at SOT" over "update every catalog with full text." |
| **doc-hierarchy-upkeep** | After behavior/contract changes, upkeep checks "did we restate the rule in a second living doc?" and prefers pointer edits. |
| **Convergence metric (soft)** | After a doc-fan-out address pass, living full-rule restatement count for that rule should be **1** (SOT) plus pointers; if still > 1 full copies, either finish pointers in-scope or backlog explicitly as "pointer cleanup," not reopen as N new findings next round. |

Suggested skill touch list (implementation PR later): `execute-plan` Phase 3 /
address guidance; `receiving-review` documentation findings + backlog capture;
`doing-code-review` / contract-docs worker brief; `review-staging` finding
shape for fan-out; `doc-hierarchy` / `doc-hierarchy-upkeep`; optionally
`plans` "cross-cutting rule" authoring note.

## Why not now

Needs agreement on where "canonical home" usually lives (wire vs Layer 2
index) per rule class, a small example edit pattern in shared or company
doc guidance, and concrete skill patches (table above). Implement as a
playbook skill + guideline PR; not tied to one product repo. Product-repo
consolidations remain valid proofs of the pattern but do not replace the
harness change.

## Non-goals / hygiene

- No project names, ticket ids, endpoint paths, or concrete catalog filenames
  that identify a private service.
- Does not delete decision logs; it requires them to **point** at living SOT
  instead of restating operational activation rules as if they were current
  indexes.
- Does not require a single mega-pass that rewrites every peer in one PR;
  incremental pointer conversion across review/execute cycles is the goal.
