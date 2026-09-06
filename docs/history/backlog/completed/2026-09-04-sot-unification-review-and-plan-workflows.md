# Backlog: enforce one SOT for cross-document content and grill unclear ownership

Status: done (executed via 2026-09-04-sot-unification-living-docs-and-grill-escalation; archived 2026-09-04)
Workflow: backlog
Source: user decision, 2026-09-04

## Problem

Agents can currently repeat the same workflow or contract guidance across
multiple documents instead of selecting one canonical source of truth (SOT)
and leaving concise pointers in peer documents. This creates review churn and
means one behavior change requires edits in several places.

The workflow also does not explicitly give the document-review, planning, and
plan-execution skills a shared escalation path when the correct SOT or content
boundary is unclear.

## Scope

- Update the document-review workflows, including the `contract-docs` review
  lens used by branch and RFC/TDD reviews, to detect duplicated normative prose
  and request consolidation into one appropriate SOT with role-specific
  pointers elsewhere.
- Update `agents/skills/plans/SKILL.md` so low-confidence uncertainty about SOT
  ownership, document roles, or where new content belongs invokes
  `grill-with-docs` one question at a time before the plan is written or
  updated.
- Update `agents/skills/execute-plan/SKILL.md` so the same ambiguity discovered
  during execution or documentation checkpoints pauses for the shared
  `grill-with-docs` workflow instead of allowing duplicated or contradictory
  documentation edits.
- Keep wire-contract SOT, workflow/domain SOT, API examples, glossary, ADR,
  and historical-document roles distinct; the change must not turn every
  documentation reference into a second SOT.

## Expected behavior

When a review or planning task finds the same normative workflow in several
documents, the agent should:

1. identify the appropriate canonical owner from the repository's documentation
   hierarchy;
2. propose moving the full rule to that owner and replacing peer copies with
   audience-specific deltas or links;
3. invoke `grill-with-docs` when ownership, scope, or the intended consolidation
   is genuinely unclear;
4. update glossary terms and architectural decisions inline during the grill;
5. preserve separate SOTs when the content belongs to different authorities,
   such as OpenAPI wire shape versus workflow ownership.

## Suggested validation

- Review a fixture containing duplicated workflow prose and verify the review
  output identifies the duplicate, names a proposed SOT, and distinguishes
  legitimate audience-specific content.
- Exercise `plans` and `execute-plan` with an intentionally ambiguous document
  ownership case and verify they invoke or route to `grill-with-docs` before
  writing the plan or changing documentation.
- Add a clear, high-confidence ownership fixture and verify neither skill
  asks an unnecessary question.
- Run the skill hygiene and realistic-sample checks required by the repository.

## Locations

- Document-review guidance under `agents/skills/doing-code-review/`,
  `agents/skills/review-confluence-doc/`, and
  `agents/skills/doc-hierarchy-upkeep/`.
- `agents/skills/plans/SKILL.md`.
- `agents/skills/execute-plan/SKILL.md`.
- `agents/skills/grill-with-docs/SKILL.md` and related domain-modeling guidance
  as the shared escalation contract.
