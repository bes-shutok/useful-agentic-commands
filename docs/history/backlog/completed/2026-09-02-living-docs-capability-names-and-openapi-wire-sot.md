# Backlog: living-doc capability names + OpenAPI wire SOT (doc-review residuals)

Status: done (executed via 2026-09-04-sot-unification-living-docs-and-grill-escalation; archived 2026-09-04)
Workflow: backlog
Source: 2026-09-02 grill-with-docs on a company service doc cull (product ticket
ids and repo names elided); extends completed
`2026-09-01-single-sot-for-cross-cutting-contract-rules.md`
Severity: Medium (documentation / review policy; stops regenerating
ticket-churn and catalog-vs-OpenAPI dual-SOT findings)
Anchors: `agents/skills/review-agents/documentation.md`,
`agents/skills/review-agents/consistency.md`,
`agents/skills/review-agents/review-panel-selection.md`,
`agents/skills/doc-hierarchy-upkeep/SKILL.md`,
`agents/skills/doc-hierarchy/company-decisions.md`,
`agents/skills/plans/SKILL.md` (doc task Files:), optionally
`doing-code-review` / `receiving-review` (fan-out already partially landed)
Decision: user-requested playbook backlog, 2026-09-02; prefer backlog over
in-session skill PR while product-repo cull proves the pattern

## Problem

The 2026-09-01 single-SOT backlog embedded **fan-out staging** (one finding
naming a canonical home; peers become pointers). That is necessary but not
sufficient. Two residual failure modes remain:

1. **Ticket keys as living gates.** Layer 1/2 prose still uses issue keys
   ("undeployed until `PROJ-NNNN`"). When the ticket closes or renumbers,
   every living surface churns. Review then stages "stale ticket" or
   "missing ticket tag" findings that are not contract defects.
2. **Caller catalogs as a second wire SOT.** Rich request/response tables in
   maintenance catalogs duplicate OpenAPI. Feature work edits wire + catalog
   (+ BFF/sync peers), so contract-docs findings fan out again even after a
   cross-cutting rule has one Layer 2 home.

Product-repo proof (same day): designate one Layer 2 section for activation
policy; OpenAPI owns wire; peers keep pointer + audience-specific delta;
Layer 1/2 use **capability names** (and RFC/ADR links), not issue keys;
Jira stays in Layer 3 / PRs / workflow tools.

## Suggested fix

1. **`documentation.md` (contract-docs lens):** add phase-2 checks:
   - Living Layer 1/2 must not use issue keys as the primary gate label;
     prefer a durable **capability name** (plus optional RFC/ADR link).
     Issue keys belong in Layer 3, plans, backlog, and tracker workflow.
   - When a catalog restates OpenAPI schemas/enums/status maps, prefer
     finding shape "catalog is second wire SOT; thin-index to OpenAPI"
     over "update the catalog table to match."
2. **`consistency.md` / panel selection:** extend fan-out examples to cover
   "ticket-as-gate" and "OpenAPI vs catalog wire duplicate" as one fan-out
   class, not N sibling edits.
3. **`doc-hierarchy-upkeep` + company-decisions:** upkeep checklist row:
   wire change → OpenAPI first; cross-cutting policy → one Layer 2 home;
   peers → pointer + audience delta only; no new issue-key gates in Layer 1/2.
4. **`plans` authoring:** for contract tasks, `Files:` prefer OpenAPI + one
   prose SOT; do not list every caller catalog as a full-text edit target.
5. **Sync mirrors:** after editing `agents/skills/...`, sync `claude/skills/...`
   (or the repo's established skill mirror path) in the same change set.

## Why not now

- Fan-out policy already landed in `review-panel-selection`,
  `receiving-review`, and `review-staging`; this item is **residuals**, not
  a greenfield rewrite.
- Skill patches need neutral placeholders only (`PROJ-1234`), public hygiene
  scan, and mirror sync; better as a dedicated playbook PR than interleaved
  with a product-repo doc cull.
- Product cull is the concrete example the skill PR should cite (without
  naming private endpoints in the skill body).

## Skill / agent touch list

| Artifact | Change |
|----------|--------|
| `review-agents/documentation.md` | Capability-name citation; OpenAPI-vs-catalog thin-index disposition |
| `review-agents/consistency.md` | Ticket-as-gate and catalog wire-duplicate as SOT drift classes |
| `review-agents/review-panel-selection.md` | Fan-out examples for the two residual classes |
| `doc-hierarchy-upkeep/SKILL.md` | Upkeep checklist rows above |
| `doc-hierarchy/company-decisions.md` | Living-doc citation + wire ownership (if not already covered) |
| `plans/SKILL.md` | Cross-cutting / contract `Files:` guidance |
| `doing-code-review` / `receiving-review` | Only if residual wording still pushes "fix every catalog table" |

Do **not** invent a separate "doc review agent"; extend the existing
`contract-docs` worker lenses.

## Non-goals / hygiene

- No real employer ticket prefixes, private service names, or concrete
  product endpoint paths in skill bodies; use `PROJ-1234` and generic
  capability labels.
- Does not forbid issue keys in Layer 3 plans, backlog, or PR/Jira workflow.
- Does not require deleting caller catalog files; it requires they stop being
  a second wire contract.
