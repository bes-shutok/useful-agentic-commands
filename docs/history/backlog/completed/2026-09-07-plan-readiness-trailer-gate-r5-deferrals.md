# Backlog: plan_readiness trailer gate r5 review deferrals (12 findings)

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-07-plans-facts-do-not-resolve-design-ambiguity-code-review-r5.md (all staged findings + both overflow entries, round 5 fresh full panel, zero blocking)
Severity: 3 Medium, 9 Low (all non-blocking)
Scope: scripts/plan_readiness.py

## Problem

The fifth and final full-panel review round of the plans fact-vs-decision confidence gate execution returned 12 valid non-blocking findings against the decision-points trailer gate (`scripts/plan_readiness.py`) and its selftest family. The full-panel budget was exhausted (5/5), so folding them in-branch would have mutated the reviewed digest and required a sixth full panel, which the budget forbids. Per the standing backlog-deferral default, all 12 were deferred to this item; the digest reviewed by round 5 (77028539b35d5e1ade492e686c53c3cd57748983c351c1e47ac696766f20d91e) carried zero unresolved blocking findings, so the branch is clean; these are residual hardening/cosmetic items for the gate's owner.

## Findings (fix in this order: discrimination first, then parser residuals, then cosmetics)

### A. Selftest discrimination (Medium first)

1. `testing#non-discriminating-arm` (Medium, scripts/plan_readiness.py:1848): `trailer_inside_close_with_info_text_fails`, `trailer_inside_short_close_fails`, and `trailer_after_indent_4_closer_stays_fenced` place the quoted trailer BEFORE the pseudo-closer, so they pass under both the r4 CommonMark closer rules and the pre-r4 lenient closer (verified by replaying the r3 parser). Reshape each arm so a REAL trailer sits AFTER the pseudo-closer, e.g. `"# P\n\n## Assumptions\n\n````\nquoted template\n```\n" + trailer + "none remain.\n````\n"` for the short-close case; analogous shapes for the info-text closer (` ``` note ` line before the real trailer) and the indent-4 closer (`"    ```"` line before the real trailer, genuine bare closer ending the fence).
2. `testing#non-discriminating-arm` (Medium, scripts/plan_readiness.py:1965): `sidecar_date_malformed_exempt` uses `09/10/2026`, which sorts below `2026-09-08` with or without the r4 fullmatch guard, so it pins nothing. Change the malformed value to `2026-09-08T12:00` (shape-invalid, sorts at/above the minimum): exempt with the guard, gated without it.
3. `testing#assertion-weakened-refactor` (Low, scripts/plan_readiness.py:1897): the table refactor dropped the pre-refactor `2026-09-08 in reason` assertion from `gated_missing_trailer_fails`. Restore via a multi-needle convention (e.g. `needle.split("|")` with `all(n in (reason or "") for n in ...)`) or keep that one arm bespoke.
4. `simplification#shrink` (Low, scripts/plan_readiness.py:1893): the arms table never validates the needle/expect_ok pairing; add `assert (needle is None) == expect_ok, suffix` at the top of the loop body.
5. `testing#coverage-gap` (Low, scripts/plan_readiness.py:1786): no tilde-side bare-closer witness; add a fail-arm with `~~~ end` (info-text tilde closer) before a real trailer inside a tilde fence.
6. `testing#coverage-gap` (Low, scripts/plan_readiness.py:1800): no cross-character closer pass-arm; add a pass-arm with a stray `~~~` line inside an open backtick fence followed by a real trailer.

### B. Fence parser residuals

7. `security#fence-parser-line-model-mismatch` (Medium, scripts/plan_readiness.py:217): `_strip_fences` iterates `text.splitlines()` (which splits on CR/VT/FF/U+0085/U+2028/U+2029) but rejoins with `\n`, so an embedded Unicode separator inside a fence-character run fabricates a parser-line closer and exposes quoted trailer text (verified probe). Fix: split on `"\n"` only (`text.split("\n")`), keeping the fail-closed closer model; pin with a U+2028-embedded bare-run arm expecting `missing decision-points trailer`.
8. `quality#fence-parser-commonmark-deviation` (Low, scripts/plan_readiness.py:187): (a) a backtick opener whose info string contains a backtick (```` ```Decision points``` styled text. ````) is accepted as an opener (CommonMark: paragraph), swallowing the rest of the document; (b) `lead` counts a tab as one column (CommonMark expands tabs to 4-column stops). Both directions fail closed. Fix: reject backtick openers with a backtick in the info string; treat a leading tab as indent >= 4; add two pass-arms.

### C. Cosmetics and docstring

9. `simplification#delete` (Low, scripts/plan_readiness.py:262): `DECISION_MARKER_RE` captures `(\S.*?)[ \t]*$`, so `value.strip()`/`value.lstrip()` in `decision_marker_problem` are dead; use `value` directly or comment the regex as the guarantee.
10. `simplification#shrink` (Low, scripts/plan_readiness.py:1908): the three bespoke sidecar-mutation arms repeat identical scaffolding; fold to a `(name, comment, mutate)` table.
11. `simplification#shrink` (Low, scripts/plan_readiness.py:1595): per-arm comments restate the tuple's first element; keep only rationale text.
12. `documentation#prose-outdated-doc` (Low, scripts/plan_readiness.py:205): the `_strip_fences` docstring clause "a longer run never closes a shorter one early in the fail-open direction" states the opposite of the code (`len(m.group(1)) >= fence[1]`) and of the pinned `trailer_inside_short_close_fails` arm; swap the adjectives ("a shorter run never closes a longer one early").

## Why not fixed now

Full-panel budget exhausted at round 5 of the executing plan's Phase 3 (cap 5); any fix would mutate the reviewed digest and require a sixth full panel, which the budget forbids without user direction. The user's standing instruction for this run prescribes the backlog-deferral default at exactly this juncture. Deferred by the execute-plan orchestrator 2026-09-07 (inline receiving-review pass on the Step 3.2 skip path; zero unresolved blocking findings, no address fixes, round 5 stands as the fresh clean review of the current digest).

## Acceptance

- Findings 1-2 land first (the arms must discriminate before any further parser change relies on them).
- Findings 7-8 (parser residuals) land with their pinning arms in the same change.
- Findings 3-6, 9-12 are mechanical and can ride any touching change.
- `python3 scripts/plan_readiness.py --selftest` stays ALL PASS with every existing `selftest#decision_marker/*` name preserved; new arms follow the `selftest#decision_marker/<name>` convention.
