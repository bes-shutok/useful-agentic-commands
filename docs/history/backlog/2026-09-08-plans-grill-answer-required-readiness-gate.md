# Backlog: block plan readiness until grill questions are answered

Status: open
Workflow: backlog
Origin: User feedback during CRM-691 plan authoring on 2026-09-08
Severity: Medium
Scope: `agents/skills/plans/SKILL.md`, `agents/skills/grilling/SKILL.md`, `agents/skills/grill-with-docs/SKILL.md`, and plan-review readiness checks

## Problem

The plan flow can ask a material grill question, continue when the user says a generic phrase such as “go on,” and then treat the unanswered decision as an assumption. This creates a shared-understanding gap: the plan may look execution-ready while a product or scope decision is still owned by the user.

The phrase “go on” is especially ambiguous after a question. It can mean “continue asking questions” or “proceed with your recommendation.” In the triggering CRM-691 session it was interpreted as permission to continue plan authoring, while the user intended the interview to continue.

## Exact location

- `agents/skills/grill-with-docs/SKILL.md`, interview workflow and integration with `plans`.
- `agents/skills/grilling/SKILL.md`, one-question-at-a-time behavior and generic-acknowledgement rule.
- `agents/skills/plans/SKILL.md`, Phase 1 confidence gate, requirements buffer, and readiness transition.
- The plan-review readiness validator or equivalent gate that certifies a plan as ready.

## Suggested fix

Introduce an explicit grill-question state in the requirements buffer. Each material question should remain `open` until the user gives an answer that addresses that question or explicitly rejects the recommended option.

When an open question exists:

1. A generic acknowledgement, “go on,” or request to continue must resume the interview with the next question, not accept the recommendation.
2. The plan may be edited only for non-decision facts or question framing; it may not be marked execution-ready.
3. The plan-review gate must return `ready=no` while any material question or scope-extension decision is open.
4. After the user answers, record a one-line decision receipt with the answer, source, date, and affected plan section before asking the next question.
5. Only after all material questions are answered should the workflow request shared-understanding confirmation and permit `ready=yes` review.

Question-economy requirement (user direction, 2026-09-08): the interview must only ask questions whose answers are genuinely unclear. Everything the workflow can safely infer or that is already decided must NOT be asked; instead, all such clear assumptions are collected and shown to the user in one consolidated list at the end of the interview (before readiness), so the user can spot and veto any wrong assumption in a single pass.

Use an explicit opt-in phrase if a user truly wants to proceed with the recommendation without answering, for example: “accept the recommendation for this question.” Do not infer that opt-in from “sure,” “okay,” “go on,” or a response to an adjacent question.

Recommended state flow:

```text
OPEN QUESTION -> USER ANSWER -> RECORDED RECEIPT -> NEXT QUESTION
OPEN QUESTION -> GENERIC ACKNOWLEDGEMENT -> ASK/RESTATE SAME QUESTION
ANY OPEN QUESTION -> PLAN REVIEW -> ready=no
ALL QUESTIONS CLOSED + SHARED UNDERSTANDING CONFIRMED -> PLAN REVIEW -> eligible for ready=yes
```

Add regression fixtures covering:

- “go on” after a recommended question: asks the next question and leaves the original question open;
- “accept the recommendation”: records the recommendation as the user decision;
- an answer to a different question: does not close the unanswered question;
- review of a plan with one open question: cannot produce `ready=yes`;
- all receipts present: readiness can proceed to the normal fresh-review gate.

## Acceptance criteria

- A plan cannot be certified `ready=yes` while a material grill question or scope-extension decision is open.
- The workflow distinguishes question continuation from decision acceptance.
- Generic acknowledgements never close an unlisted material decision.
- Every closed grill question has a durable decision receipt in the requirements buffer or plan artifact.
- The user can explicitly accept a recommended answer without retyping it, using a documented opt-in phrase.
- The behavior is covered by deterministic workflow fixtures, including the CRM-691 “go on” scenario.
- The change does not skip the existing fresh plan-review panel or alter branch/push authorization.
- Only genuinely unclear decisions are asked; all clear/safely-inferable assumptions appear in one consolidated assumptions list at the end of the interview, and no clear assumption is asked as a question.

## Coverage / grouping

- Not covered by `docs/plans/2026-09-08-execute-plan-fresh-review-coverage-gaps.md` — that plan explicitly excludes this item (different skill family: plan authoring, not execution review).
- `docs/history/backlog/2026-09-08-plans-trunk-branch-confirmation.md` IS already covered there (Task 8) — do not re-join.
- Join candidate for one authoring plan: `docs/history/backlog/2026-09-07-plans-step14-meta-rule-grilling-duplication.md` (Low; same plans+grilling surface, same duplication-of-grilling-rules theme).

## Why not fixed now

This is a shared workflow and readiness-gate change, not part of the CRM-691 implementation plan. The current session records the issue as backlog work so the plan can remain blocked until the user answers the active grill question.

