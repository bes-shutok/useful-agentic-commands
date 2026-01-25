### Copilot Command (Outcome-driven TDD, reuse-first, always run tests)

1. Restate the issue in 1–2 sentences based on the provided context.

2. Ask only the minimum questions required to avoid wrong implementation (no coding yet).
    - If assumptions are required, list them explicitly.

3. Mandatory pre-TDD audit (no test writing yet)
    - Search for existing tests that already cover or overlap this behavior.
    - Output a short list:
        - candidate test files + exact test names (or nearest equivalents)
        - what outcome each currently asserts
        - which test(s) you will extend and why
    - Rule: you may create a new test file only if you show there is no suitable home (state where you looked).

4. Define distinct outcomes before writing tests
    - Enumerate the full set of outcomes the code can produce:
        - return values / thrown errors
        - side effects (DB write, event published, metric emitted, log, external call)
        - state changes
    - Outcome rules:
        - Same outcome + same side effects → group as table-driven/parameterized cases in ONE test.
        - Different outcome or side effects → separate tests (one per outcome).

5. Propose a step-by-step TDD plan (stop before coding)
   Include:
    - The exact existing test location you’ll extend (or new home if justified in step 3).
    - A test matrix mapping **inputs → expected outcomes**.
    - Grouping plan:
        - which rows are table-driven (same outcome)
        - which rows require separate tests (different outcomes/side effects)
    - Duplication control:
        - shared setup must be extracted (helper/builder/fixture) or moved into the parameter table
        - repeated assertions must be factored into helpers

6. Hard gate: wait for explicit approval  
   Stop after the plan and test matrix. Do not write or modify code or tests until approved.

7. After approval: strict Red → Green → Refactor with mandatory test runs
   For each cycle:
    - Red:
        - implement or adjust the approved test(s)
        - run the relevant test subset and show the command used
    - Green:
        - minimal code change to pass
        - run the same test subset again and show the command used
    - Refactor:
        - remove duplication in tests and/or production code
        - run the same test subset again and show the command used

8. Completion criteria (cannot claim “done” without this)
    - Run tests and present evidence:
        - run the full relevant suite (module/package), or
        - if agreed, the smallest suite that fully covers the touched behavior
        - show the command(s) and a short result summary
    - If any tests were skipped, list exactly which and why.

9. End summary
    - List tests added or updated and which outcomes they cover (by outcome name from step 4).
    - Summarize code changes at a high level.
    - Provide commands to run:
        - the focused tests
        - the broader test suite