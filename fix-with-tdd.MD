### Copilot Command (TDD with outcome-driven tests, no duplication)

1. Restate the issue in 1–2 sentences based on the provided context.

2. Ask only the minimum questions required to avoid wrong implementation (no coding yet).
    - If assumptions are required, list them explicitly.

3. Before writing any test:
    - Search for existing tests that already cover the same behavior or overlap with the new case.
    - Reuse or extend existing tests instead of creating duplicates whenever possible.

4. Propose a step-by-step TDD plan that includes:
    - Where the relevant existing tests are (or where new tests will live if none exist).
    - The full set of *distinct outcomes* the code can produce (success paths + failure/edge cases).
    - A test matrix mapping **inputs → expected outcomes**.

5. Test design rules (must follow):
    - Prefer outcome-driven tests over feature-specific tests.
    - Avoid duplicated setup and duplicated assertions.
    - If multiple inputs go through the same code path and only vary by parameter (e.g., different metrics), cover them in one test using parameterization/table-driven cases.
    - If outcomes differ (different branches, errors, side effects), use separate tests—one per distinct outcome.
    - Include negative and boundary cases when they change the outcome.
    - Do not add a new test file if an existing one is the right home.

6. Stop and wait for explicit approval of the plan and test matrix.

7. Only after approval:
    - Implement using strict TDD cycles: **Red → Green → Refactor**.
    - Keep changes minimal and focused on the issue.
    - Ensure all tests pass.
    - Refactor tests to remove duplication after the feature works.

8. At the end:
    - List tests added/updated and which outcomes they cover.
    - Summarize code changes at a high level.
    - Provide commands to run the tests locally.