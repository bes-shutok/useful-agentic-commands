# AI playbook

Ubiquitous language for agent workflow and planning in this repository.

## Language

**Executable plan task**:
A checklist item the default executor can finish now from the target repo and local tooling, without a blocked shared environment or another team's deploy.
_Avoid_: release gate (as a checkbox), rollout step, staging verification task

**Repository implementation**:
Work in the target repository that the default executor can complete and verify now with available local tooling. It becomes an executable plan task by default.
_Avoid_: external prerequisite, release gate

**External prerequisite**:
Work owned outside the current repo or ticket that must exist before a Ship-when condition can be met (another service, ticket, or team).
_Avoid_: implementation task, local verify

**Release gate**:
A Ship-when condition that needs deployed, cross-team, or human-owned evidence. It may appear in plan prose; it must not become a checklist item unless the user confirms an exception. An admitted exception must record a bound receipt (exact confirmation text or stable message reference, specific checklist item, target or environment, confirmation time or session), a meaningful `why executable now`, and observable `completion evidence` in the plan file. External prerequisites are never exception-admissible.
_Avoid_: Done-when check, executable plan task

**Done when**:
The executable success criteria for the implementation phase (local quality dimensions and repo-verifiable checks).
_Avoid_: Ship when, release complete

**Ship when**:
Narrative release dependencies that remain after the implementation phase. No checkboxes; optional Jira tracking only after the user confirms ticket creation.
_Avoid_: Done when, plan archive meaning production-ready

**Completed history artifact**:
A finished plan under `{plans_completed_dir}`, a completed review digest, or non-mirror docs under `docs/history/context/` (and legacy `docs/context/`). Treat as immutable historical context of considerations at the time.
_Avoid_: living guideline, editable draft

**Confluence mirror**:
A wiki snapshot under `docs/history/context/confluence/` that may refresh to match the external page. Not a process-outcome reinterpretation of a completed plan.
_Avoid_: completed history artifact (for immutability rules)

**Review iteration cap**:
The total count of review rounds in one execute-plan Phase 3 loop, counting full-panel and focused rounds alike, stated as the `max_review_rounds` budget (default 5) in the execute-plan Review end condition table. Counting, stop, and standing-instruction semantics are owned by execute-plan Step 3.5.
_Avoid_: full-panel cap (counts only all-five-worker rounds), `max_full_panel_rounds`

**Sibling-doc restatement**:
A living document that restates a cross-cutting rule whose canonical home already states it correctly. During execute-plan Phase 3 addressing, a peer on a shipped doc surface converts to a pointer on the canonical home in the same pass; only a non-shipped or legacy peer defers as one pointer-cleanup backlog item instead of being fixed as a new finding that extends the loop (see `receiving-review`).
_Avoid_: independent contract bug, per-surface docs drift

**Duplicate unit witness**:
A test finding that demands an assertion for a production-path invariant another test demonstrably pins (the pinning test is named and fails when the invariant is violated; for example call order asserted on one unit, now demanded of a sibling unit). During execute-plan Phase 3 addressing, it is deferred to backlog as one family-completeness item instead of being fixed round after round. A pin that cannot be reproduced as a failure under a violated-invariant mutation disqualifies the class and reverts the finding to the fix-everything default (see `receiving-review`).
_Avoid_: per-test always-passes fix
