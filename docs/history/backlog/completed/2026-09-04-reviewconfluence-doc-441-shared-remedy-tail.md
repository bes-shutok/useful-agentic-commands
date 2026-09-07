# Backlog: shared remedy tail between review-confluence-doc 4.4.1 and documentation.md consolidation shape

Status: done
Workflow: backlog
Source: 2026-09-04-sot-unification-living-docs-and-grill-escalation branch, code review r3 finding F3 (regenerated at r1 as F5/F7, r2 as F2)
Severity: Low (future-reword divergence risk only)
Scope: agents/skills/review-confluence-doc/SKILL.md, agents/skills/review-agents/documentation.md

## Problem

The first bullet of `review-confluence-doc` section 4.4.1 ("Duplicated normative prose (SOT consolidation)") ends with a near-verbatim tail ("...name the canonical owner and replace peer copies with audience-specific pointers or deltas") that closely mirrors the closing clause of the "Consolidation finding shape" sentence in `review-agents/documentation.md` Living-doc gates ("...names the proposed canonical owner from the documentation hierarchy and replaces peer copies with audience-specific pointers or deltas"); the two differ only by replace/replaces inflection, so either copy can silently drift from the other. Only the `review-confluence-doc` copy is pinned validation vocabulary: the plan validation block pins `"replace peer copies with audience-specific pointers or deltas"` against `review-confluence-doc/SKILL.md` only; the `documentation.md` sentence is unpinned. The defect regenerated across review rounds r1 (F5/F7), r2 (F2), and r3 (F3): each attempt to shrink or reword the overlap either bumped a pin constraint or regressed as a new finding. A future reword of the canonical remedy text in `documentation.md` would silently diverge from the consumer copy in 4.4.1 unless this item is fixed first.

## Exact location

- agents/skills/review-confluence-doc/SKILL.md, section "#### 4.4.1 Duplicated normative prose (SOT consolidation)", first bullet's closing tail
- agents/skills/review-agents/documentation.md, "### Living-doc gates" subsection, "Consolidation finding shape" check sentence ending

## Suggested fix

De-duplicate the remedy wording in a future pass: make `documentation.md` Living-doc gates the canonical home of the consolidation remedy phrasing and reduce the 4.4.1 bullet's overlap to a pointer-style reference ("per `review-agents/documentation.md` Living-doc gates"), then re-pin the affected validation span (only the `review-confluence-doc` copy is pinned). This cannot be done in the current plan's lifetime: the plan's validation block pins the current span verbatim and the plan is about to be archived; fixing here would re-pin a span in an archived-plan validation block and risks another regeneration cycle (fix-risk rule 2 in receiving-review).

## Why not fixed now

Deferred per receiving-review sibling-doc-restatement backlog-by-default bound combined with fix-risk triage: the finding regenerated in three consecutive rounds on files touched by prior fixes, and the shared tail is pinned validation vocabulary in both files. Decision made by the r3 address pass (2026-09-04); see docs/reviews/2026-09-04-2026-09-04-sot-unification-living-docs-and-grill-escalation-code-review-r3.md finding F3.
