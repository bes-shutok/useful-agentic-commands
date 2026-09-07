# Backlog: done run-start marker r5 review residuals

Status: done
Origin: code review r5 of docs/plans/2026-09-04-done-deliverables-log-dedupe-and-anchors.md (docs/reviews/2026-09-06-2026-09-04-done-deliverables-log-dedupe-and-anchors-code-review-r5.md)
Captured: 2026-09-06 (execute-plan Phase 3 exit; round-5 cap reached, findings valid but unfixed)

## Items

1. **Multi-repo conservative-gating seam (R5-1).** Step 0 writes one run-start marker (starting repo's `{tmp_dir}`); a secondary repo's Step 1.5 gate deterministically hits the no-match arm of the echo-loss fallback, so every `!!` plan there is conservatively gated (safe, named, never skipped, but spurious-refusal noise). Fix direction: one-clause acknowledgment in the skill, or a per-repo marker write at each Step 1.5 gate invocation.

2. **Content-bearing marker identity (R5-3).** Markers are empty files; identity rests on cross-compaction recall of the echoed path. A content-bearing marker (e.g. `date -u +%s` + `$REPO_TOP` + `$$`) with content-match confirmation at Step 1.5/2.62 would make identity verifiable without chat context. All current confusion paths already degrade to conservative gating; this is hardening, not a gap.

3. **Echo-loss fallback naming seam (R5-4).** Step 1.5 back-references "the Step 0 echo-loss fallback", but Step 0 states the rule without that label. One-line fix: name the rule in Step 0 or drop the label in Step 1.5. Cosmetic; the parenthetical restates the effect.

Also folds the probe-coverage follow-ups in `2026-09-06-done-run-start-probe-coverage.md` (r1-r4 literals) whenever a future wording pass touches this area: land the validation pins in the same change.
