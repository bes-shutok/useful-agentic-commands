# Backlog: execute-plan Phase 3 continues past user-expected five-review stop

Status: done
Workflow: backlog
Source: 2026-09-01 execute-plan Phase 3 session (project and ticket ids elided);
user stop + reflection request after long post-fix review churn
Severity: High (process / harness; burns budget and delays archive without a
mandatory reflection gate)
Anchors: `agents/skills/execute-plan/SKILL.md` (Phase 3 counters, full-panel
budget, Step 3.5 continue-or-exit, clear-round quality bar),
`agents/skills/review-loop/SKILL.md` (`max_full_panel_rounds`),
`agents/skills/review-panel-selection` / focused post-fix composition,
`agents/skills/review-reconciliation/SKILL.md`,
`agents/skills/receiving-review/SKILL.md` (fix-risk / regenerating findings)
Decision: user-requested durable playbook backlog, 2026-09-01; skill change
not implemented in the same session
See also:
- `2026-09-01-single-sot-for-cross-cutting-contract-rules.md` (sibling doc fan-out; includes **workflow embedding** so review + execute-plan converge duplication to one SOT over time)
- `2026-09-01-review-test-false-green-completeness-checklist.md` (fractal unit fixes)

## Problem

### What the user reasonably expected

Phase 3 has a **hard limit of five reviews**. After that budget, the agent
should **stop**, surface unresolved themes, and run a **reflection /
convergence** step (what is still regenerating, what to backlog vs fix, whether
to archive) instead of continuing address → done → fresh panel cycles.

### What the skills actually encode

1. The hard cap is on **`full_panel_rounds` (max 5)**, not on total
   `review_round` count. A full-panel round counts only when **all five** base
   workers launch.
2. **Focused / targeted** post-fix panels (subset of workers) **do not**
   increment `full_panel_rounds` and **do not** trip the “ask before a sixth
   full panel” stop.
3. Step 3.5 **Otherwise** says: increment `review_round` and return to
   Step 3.1 with the targeted worker set. Combined with continuous
   execute-plan execution, that is an open loop until blocking-clean **and**
   the clear-round quality bar passes.
4. There is **no mandatory reflection artifact** or user ask when:
   - total review iterations exceed five;
   - several consecutive rounds find **no production Medium+** miss-paths
     but still find docs/test residuals;
   - the same theme regenerates across sibling documents or unit witnesses;
   - focused clears fail the quality bar because risk/design were skipped,
     forcing yet another hybrid round.
5. `review-reconciliation` and fix-risk gates exist for recurrence, but they
   are easy to under-invoke when each new residual looks “fresh” (next sibling
   doc, next unit missing the same InOrder shape) rather than identical text.

### Focused-panel → quality-bar → more rounds trap

Post-fix composition prefers workers that owned the last round’s fixes.
When those owners are only contract-docs and testing:

1. The focused panel skips risk (and often design).
2. Blocking production findings may already be gone.
3. Step 3.4 clear-round quality bar still requires required risk lenses
   (and design coverage of the tip for exit).
4. Quality bar **fails** even though the round was blocking-clean on the
   domains that ran.
5. Step 3.5 schedules another hybrid (design + risk), which can again find
   only Low hygiene or sibling prose, then address/done, then another focused
   docs/test round.

Net: **production was already clean**, but omitted lenses on cheap focused
panels keep the loop alive. Skills do not say “if the last production-clean
risk+correctness round already passed, schedule **one** exit hybrid then
stop,” so the agent keeps optimizing for last-round owners.

### Blocking vs backlog-by-default gap

Step 3.2 treats `blocking: false` as non-blocking for completion, but
continuous address-review partner prompts in practice still say “cheap wins
fix F*” every round. That turns Medium non-blocking residuals into loop
fuel. Skills lack an explicit Phase 3 exit policy table:

| Class | Phase 3 default |
|-------|-----------------|
| Wrong runtime outcome; lock/TOCTOU/integrity; wire status/code/key lies | **Blocking** (must fix or user ask) |
| Sibling prose repeating a rule already correct on the canonical SOT | **Backlog by default** |
| Ticket-tag / activation-label drift when undeployed status is already clear | **Backlog by default** |
| Missing assert on unit B when unit A already pins the same production path | **Backlog by default** (or one completeness task; see sibling backlog) |
| Low YAGNI / rename / dead branch | **Backlog by default** |

Without that table, receiving-review and orchestrator prompts keep fixing
residuals “while we’re here,” which regenerates the next sibling finding.

### What happened in the session (sanitized)

- Early rounds used full or near-full panels and burned part of the full-panel
  budget.
- Later rounds repeatedly used **focused** post-fix panels (often
  docs + tests only, then exit hybrids for omitted lenses).
- Manifest `full_panel_rounds` stayed **below six**, so the agent never hit
  Step 3.5 “ask the user before a sixth full panel.”
- Total review iterations continued well past five (address → done → next
  panel) under continuous-execution rules.
- Production race / integrity findings largely stopped; remaining work was
  residual activation prose, Retry-After sibling wording, and race-unit
  false-green hardening (fractal).
- The user had to **manually stop** and ask for reflection. That reflection
  correctly concluded: production converged; the review loop did not.

### Why this is a skill defect, not only an agent miss

Even a careful agent following the letter of execute-plan can “comply” while
violating the user’s mental model of a five-review hard stop. The gap is
**metric mismatch** (full-panel count vs total iterations), **exit quality bar
interacting badly with focused ownership**, and **missing stop → reflect**
plus **backlog-by-default** before Phase 4 when diminishing returns are
obvious.

## Suggested fix

Update execute-plan (and align review-loop / receiving-review / panel-selection
wording) so the budget matches operator expectation and forces reflection:

1. **Dual counters (both hard):**
   - keep `full_panel_rounds` ≤ 5 (ask before sixth full panel);
   - add `review_round` / iteration cap (proposed default **5**, or **7** if
     focused rounds are cheaper) that **always** stops for user direction
     before another Step 3.1, regardless of panel mode.
2. **Mandatory reflection stop** when any of these fire (write a short
   session note under session tmp; ask the user before continuing):
   - iteration cap reached;
   - two consecutive rounds with zero unresolved **blocking** findings on
     production/runtime paths (docs/test-only residuals do not extend the
     loop by default);
   - same root theme regenerates across rounds (invoke reconciliation, then
     reflect if still churning);
   - clear-round quality bar fails solely because a focused panel omitted
     required lenses.
3. **Exit-hybrid once, then stop:** when a prior round already had
   risk+correctness (or full panel) blocking-clean on production paths,
   schedule **at most one** design+risk exit hybrid for quality-bar coverage;
   do not resume unbounded docs/test-only focused clears afterward.
4. **Phase 3 exit policy table** (blocking vs backlog-by-default) in
   execute-plan Step 3.2 and receiving-review partner scope defaults; cheap
   wins on non-blocking residuals are optional only when the user asks or
   when they share a root cause with a blocking fix in the same address pass.
5. **Clarify operator-facing skill text:** replace ambiguous “at most five
   reviews” with “at most five **full-panel** rounds **and** at most N
   **total** review iterations; then stop and reflect.”
6. **Optional:** after stop, require a one-page convergence checklist
   (production Medium+ empty? residual classes? plan checkboxes disposition?)
   before Phase 4 archive.

## Why not now

Needs an explicit product decision on the total-iteration cap number and on
whether docs/test residuals may ever block Phase 3 exit. This backlog records
the incident class and the proposed skill changes; implement in a dedicated
playbook PR after that decision.

## Non-goals / hygiene

- Do not store project names, ticket ids, service paths, commit SHAs, or
  review staging contents in this file.
- Do not treat this as authorization to weaken the full-panel budget; add the
  total-iteration and reflection gates **alongside** it.
- Sibling-document fan-out and test false-green completeness are separate
  backlogs (see See also); do not fold their full design into this PR unless
  the exit-policy table only points at them.
