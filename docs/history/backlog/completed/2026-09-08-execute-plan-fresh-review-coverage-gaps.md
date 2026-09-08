# Backlog: execute-plan fresh-review and boundary-witness gaps

Status: done
Workflow: backlog
Origin: Post-execution independent branch review found blocking defects and release-gate risks after execute-plan had reported a clean final verification. The incident exposed a reusable review-cycle gap, not a product-specific problem.
Severity: High
Scope: `agents/skills/execute-plan/SKILL.md`, `agents/skills/doing-code-review/SKILL.md`, review-panel and review-staging guidance, and generic workflow regression fixtures

## Problem

The execute-plan review loop can reach a clean result after an initial full review, a receiving-review fix pass, and a targeted final verification even though a later independent full-branch review finds defects on the same current digest.

The triggering shape contained these generalized failure classes:

1. A filtered or compacted batch preserved the downstream relative index in the returned item instead of restoring the original input index. Tests asserted list position and payload identity, but not the returned index value.
2. A pure converter test registered the required nullable-value serializer manually, while the live custom HTTP client constructed its own default serializer. The integration test checked status and request count, but not the actual outbound body.
3. A downstream protection boundary was explicitly owned by a later work item. The implementation was correctly left out of scope, but the review did not retain the missing boundary as a visible release gate tied to the deployed default.
4. A normative strict-mode documentation example used a value that the runtime contract rejects. Documentation checks verified anchors and prose, but did not replay or semantically inspect examples.

Some residuals were not missed: production metrics, broader boundary witnesses, and working-directory portability had already been found and deliberately deferred. The workflow did not make that distinction sufficiently visible when it reported completion.

## Root causes

### 1. Verification framing replaced independent review

The post-fix pass was treated as final verification of previously reported findings. That framing narrows attention to known issues and encourages confirmation of the selected fixes. It does not force a fresh traversal of sibling paths, changed wiring, public examples, or release configuration.

The execute-plan text says that later reviews should be fresh, but the run contract and artifacts do not mechanically prove that the final pass was adversarial, whole-diff, and independent of the previous finding list.

### 2. The failure-mode matrix was too coarse

The matrix recorded that a mutating path was tested, but a test name or a positional assertion could be treated as evidence for a stronger invariant than it actually proved. It did not require each row to identify the discriminating observation that would fail for the most likely implementation mistake.

For boundary-heavy changes, endpoint coverage is not enough. The evidence must cover the transformation chain:

```text
external input -> classification -> internal command -> downstream wire body -> downstream result -> public response
```

### 3. Unit fixtures hid production wiring

Tests constructed converters and object mappers directly, so they proved a local serializer configuration rather than the serializer used by the real client. The workflow did not require an outbound-wire witness whenever a custom client, message converter, generated model, or module registration changed.

### 4. Scope triage dropped release risk with implementation scope

“Owned by another task” was treated as a reason not to stage an implementation finding. That is correct for code ownership but incomplete for release safety. A boundary can be out of scope to implement and still be a blocking ship condition that must remain in the handoff and final report.

### 5. Documentation review was structural, not executable

The contract-docs lens checked changed prose and required anchors, but the workflow had no mandatory check that normative examples are compatible with the runtime classifier, validator, or schema. A sample can therefore look complete while being rejected by the documented mode and header combination.

### 6. Clean status was stronger than the evidence

The exit condition counted unresolved blocking findings, but did not require every changed mutator and boundary claim to have a discriminating witness. A panel can return no blocker because it never tested the relevant distinction.

## Generalized lesson

**Principle:** A clean review is a current-digest acceptance claim, not confirmation that previously known findings were fixed.

**Shape trigger:** A feature changes a public API, a batch transformation, generated or nullable models, a custom downstream client, a security or rollout boundary, or normative documentation, and the final review is narrower than the first review or is framed around prior findings.

**Rule:** After any source mutation, the next review must independently re-traverse the complete current diff. For every changed mutator and boundary, require a failure-mode row with a concrete discriminating witness. Separate implementation ownership from release ownership: an out-of-scope boundary may be deferred for implementation but must remain an explicit ship gate when the current artifact can cross it.

**Evidence rule:** “Covered”, “validated”, “unchanged”, or “already fixed” is not closure evidence by itself. The reviewer must cite the executable assertion, observed wire body, response invariant, configuration guard, or decision receipt that would fail if the defect were present.

## Proposed solution

### A. Make the final review mechanically fresh

Update execute-plan so that:

1. A review after any accepted fix is labeled `fresh-adversarial`, never `final verification` only.
2. Its prompt explicitly says that prior findings are context, not a review filter, and requires a first-principles scan of the complete current diff.
3. A change involving a public API, cross-service call, generated model, serializer, security boundary, rollout flag, or normative documentation automatically receives the correctness, testing, contract-docs, and risk lenses. Use the full five-worker panel when several of those signals are present.
4. The staging metadata records the reviewed digest, review mode, changed-risk signals, workers actually launched, and whether any prior finding list was supplied as a filter. Missing or contradictory metadata prevents a clean exit.
5. The final clean round must be after the last fix commit and must not be replaced by a unit-only or verification-only pass.

### B. Strengthen the mutator and boundary witness ledger

Require one row per public mutator and each directly affected downstream boundary. Each row must name:

- input partitions, including absent, explicit-null, valid, invalid, safe, protected, and filtered cases where applicable;
- the internal representation and any index, identity, or ordering transformation;
- the actual downstream wire boundary and serializer configuration;
- downstream success, partial failure, malformed response, and no-call behavior;
- rollout or compatibility modes and the deployed default;
- normative documentation examples that describe the path;
- the exact discriminating assertion or structural guard that proves each claim.

“Test exists” is not sufficient. For example, a compacted batch row must assert the returned item index, not only the list slot; a nullable-model row must inspect the actual outbound JSON, not only a manually configured converter; and a documentation row must replay or semantically validate strict and compatibility examples.

### C. Add a release-gate ledger for deferred boundaries

When a plan explicitly assigns a boundary to another owner, the review must record:

- the missing capability and its owner;
- the current code path and configuration that would be unsafe without it;
- the deployment mode that is permitted before completion;
- the exact condition that makes the future path shippable;
- whether the item is an implementation blocker, a release blocker owned elsewhere, or a nonblocking follow-up.

Out-of-scope implementation must not become invisible risk. The ledger is a handoff artifact, not authorization to expand the current plan.

### D. Make contract examples executable or semantically checked

For changed normative examples, add a lightweight validation path that checks the example against the active schema/classifier/mode rules. Where full execution is impractical, require a structured example inventory with the expected mode, headers, protected fields, and expected result class. A successful documentation review must prove that examples are not merely syntactically valid.

### E. Turn this incident into harness evaluations

Add generic replayable cases for:

1. a filtered batch whose downstream indexes must be remapped;
2. a nullable generated model whose standalone client mapper is misconfigured;
3. a deferred downstream security boundary with an unsafe strict default;
4. a strict documentation example containing a value classified as protected;
5. a review whose prior pass found only nonblocking residuals but whose current digest contains a sibling defect;
6. a false-clean pass with a matrix row that cites a test name but no discriminating assertion.

Grade the trace as well as the final answer: confirm the fresh panel was launched, the full current digest was supplied, the witness ledger was populated, release gates were retained, and the workflow refused a clean result when evidence was missing.

## Acceptance criteria

- `execute-plan` requires a fresh adversarial current-digest review after every source-mutating review-fix pass and cannot substitute verification-only framing for that review.
- Review selection automatically covers correctness, testing, contract-docs, and risk for public-boundary, custom-client, security-boundary, rollout, and normative-documentation changes; full-panel selection is used when multiple signals are present.
- Review staging includes a freshness/review-mode record, a discriminating-witness ledger, and a separate release-gate ledger.
- The mutator matrix rejects rows that cite only a test name, list position, status code, or manual fixture when the risk is an index, wire-serialization, downstream-response, or mode-preservation invariant.
- A filtered-batch regression case asserts original output indexes and ordering across rejected-item positions.
- A live or equivalent outbound-wire regression case proves nullable absent/null/present serialization through the production client configuration.
- A release-gate regression case proves that an implementation boundary owned elsewhere remains visible as a ship condition rather than being silently dropped as out of scope.
- A documentation regression case rejects a normative example that conflicts with its declared mode or field classification.
- The workflow-level evals grade both worker coverage and evidence quality, and a missing witness prevents a clean terminal result.
- The backlog item remains generic and contains no ticket IDs, repository names, service names, internal URLs, secret names, user identities, or machine-specific paths.

## Not part of this backlog item

- Do not change product code or retrofit a feature-specific implementation.
- Do not make every nonblocking test gap a release blocker.
- Do not force all deferred cross-owner work into the current plan.
- Do not rewrite historical review artifacts; preserve them and use this item to improve future runs.
- Do not rely on stronger models, more workers, or larger prompts as the primary fix without a measurable witness and trace-evaluation improvement.
