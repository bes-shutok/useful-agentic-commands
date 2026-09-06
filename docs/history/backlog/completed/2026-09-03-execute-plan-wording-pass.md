# Execute-plan wording-pass residuals (re-entry paragraph, cap row, probe guidance)

Status: done — fixed 2026-09-03 on branch 2026-09-02-phase3-residue-pass (F2-F4 folded; F5/F6 closed as recorded guidance, see Dispositions).
Workflow: backlog
Source: residue-pass r1 code review (docs/reviews/2026-09-03-phase3-residue-pass-code-review-r1.md), findings F2-F6; deferred per Backlog capture (plan-verbatim text / template-reuse guidance; tree verified byte-identical or review-validated where applicable)

## Problem

The residue-pass plan landed its skill edits as plan-verbatim text, leaving five wording/coverage Lows that were not folded to avoid mutating the executed digest. None enables a wrong silent exit.

1. **F2**: execute-plan SKILL.md counting paragraph uses distant anaphora ("Such an uncounted re-entry") whose antecedent sits two sentences back. Suggested direction: restate the noun phrase at the point of use in a wording pass.
2. **F3**: the counting paragraph states the counted-re-entry consequences twice (internal redundancy). Suggested direction: state each rule once, matching the paragraph's own split-rule style.
3. **F4**: the Step 3.5 cap-row table cell duplicates the session-note parenthetical in both the reconciliation branch and the otherwise branch. Suggested direction: hoist the parenthetical to cell level or drop one copy.
4. **F5**: plan Task 3a fan-out relocation probes (plan lines 164-169) pin the relocated paragraphs by opening phrase + position/count only; interior content is unpinned, so interior mangling during relocation would pass. Guidance for future template reuse: pin a longer interior span of each relocated paragraph.
5. **F6**: plan Task 2g probes (plan lines 159-161) pin the reversion of the tail but not the second routing paragraph's interior phrases. Guidance for future template reuse: pin multi-sentence replacements beyond their tail/reversion boundary.

## Location

- `agents/skills/execute-plan/SKILL.md` (counting paragraph, Step 3.5 cap row): F2-F4.
- `docs/plans/2026-09-02-phase3-residue-pass.md` Task 3a/2g probe guidance (template-reuse): F5-F6.

## Suggested fix

One wording pass over the counting paragraph and cap-row cell (keeping all pinned spans verbatim per the plan's contracts), plus the two template-reuse guidance notes for the next validation-block reuse.

## Severity

Low (all five).

## Why not fixed now

The skill text is plan-verbatim (pinning contracts) and F5/F6 are guidance for future template reuse with the current tree verified correct; folding them would mutate the executed digest for wording-only gains. Deferred per the receiving-review backlog-by-default path, residue-pass r1.

## Dispositions (2026-09-03)

F2-F4 folded in one wording pass over `agents/skills/execute-plan/SKILL.md` (counting paragraph restructured: counted re-entry consequences stated once, anaphora replaced with an explicit noun phrase, redundant sentence deleted; cap-row cell now says "the same short session note" in the otherwise branch). All validation-command pins re-verified green after the edits. F5/F6 need no live edit: their targets are the archived plan's frozen validation block; the guidance itself (pin longer interior spans / multi-sentence replacements on future template reuse) is the deliverable and stands recorded in this entry.
