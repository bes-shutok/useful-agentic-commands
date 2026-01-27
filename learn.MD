Documentation cleanup + learning extraction — single run

Goal
In a single run:
• Extract lessons from task communication.
• Place knowledge at the correct scope (human, feature, LLM instruction, LLM example, or temporary).
• Clean and consolidate documentation into canonical topics.
• Enforce documentation rules retroactively across the entire corpus.
• Update the LLM instruction rules with high-quality, enforceable rules only.

⸻

A. Extract lessons from communication
1.	Review all communication available in this task context, including:
• discussions
• decisions
• corrections
• constraints
• misunderstandings, false assumptions, and rework
2.	Identify:
• concrete mistakes
• wrong assumptions (human or tooling)
• missing or misleading documentation
• recurring friction points
3.	For each lesson, classify it as exactly one of:
• Human best-practice guidance
• Feature- or system-specific knowledge
• Enforceable LLM instruction rule
• LLM-only examples or playbooks
• Temporary artifact (summaries, review notes, investigation logs)

⸻

B. Hard placement rules (no discretion)
4.	Temporary artifacts (strict)
• Any document that is a summary, review, analysis, investigation, notes, draft, or worklog is a temporary artifact.
• Temporary artifacts may only be created under .github/tmp/.
• Do not create temporary artifacts in the repository root or any other location.
• Temporary artifacts must be deleted or explicitly promoted at the end of the run.
5.	BEST_PRACTICES scope (strict)
Only include content in .github/docs/BEST_PRACTICES.md if all conditions are met:
• understandable without system internals
• useful to a human reader without incident context
• not written to correct LLM reasoning
• not generic troubleshooting advice
• not feature-specific or subsystem-specific

If any condition fails, the content must not be in BEST_PRACTICES.
6.	Feature-specific knowledge (human-facing)
• Lessons that depend on system internals (metrics behavior, Redis keys, thresholds, detection logic, etc.) must live in canonical feature documentation under .github/docs/.
• Prefer adding to an existing canonical document.
• If no suitable canonical document exists, creating a new canonical document is allowed and required to achieve compliance.
• Do not place feature knowledge in BEST_PRACTICES.
7.	LLM-only examples and playbooks
• Place LLM-only examples under .github/docs/examples/.
• Split examples by feature/domain so only relevant context is loaded.
• Each file must clearly start with:
“LLM examples — not human documentation”.
• LLM-only examples must not be copied into BEST_PRACTICES.
• LLM-only examples must not be embedded in the LLM instruction rules.
8.	LLM-only lessons (rules)
• Lessons whose purpose is to prevent incorrect LLM assumptions must be encoded as enforceable LLM instruction rules.
• LLM reasoning guidance must never appear in BEST_PRACTICES.

⸻

C. LLM rule qualification gate (mandatory)

Before adding anything to the LLM instruction rules, apply all checks below.
If any check fails, rewrite the item or discard it.
9.	Rule vs fact test
• Rules must prescribe or constrain behavior.
• Descriptive statements about frameworks, libraries, or system behavior are not rules.
10.	Generalization test
• Rules must apply to multiple situations.
• Statements tied to a single line of code, header, Redis command, or investigation outcome must be generalized or dropped.
11.	Preventive value test
• Rules must clearly prevent a future mistake or mis-assumption.
• If removal would not increase risk, drop the rule.
12.	Actionability test
• Rules must say what to do or not do.
• Background explanations and “FYI” knowledge are forbidden.
13.	Rewrite-or-drop rule
• If a candidate fails any test:
• attempt to rewrite it into a concise, enforceable rule
• if still weak or trivial, discard it

⸻

D. Update human-facing documentation
14.	Update .github/docs/BEST_PRACTICES.md only with lessons that passed the scope rules:
• concise
• human-readable
• explanatory, not prescriptive
• no investigation narratives
• no internal implementation details

⸻

E. Clean and consolidate documentation
15.	Review documentation in:
• .github/docs/
• .github/docs/examples/
• .github/tmp/

Remove duplication, normalize structure, and consolidate topics.
16.	Topic unification rules
• exactly one canonical document per topic
• subtopics must be sections, not separate files
• overview documents may link to canonical docs instead of duplicating content
17.	Temporary document promotion
• promote only if content is long-lived and broadly useful
• merge into existing canonical docs when possible
• create new canonical docs when required for compliance
• eliminate duplication after promotion
18.	Scope enforcement
• exclude test artifacts and test result summaries
• keep test documentation only if general and long-lived
• .github/docs/ must never reference .github/tmp/

⸻

F. LLM instruction rules structure
19.	From communication lessons and documentation decisions, extract only enforceable rules.
20.	Update the LLM instruction rules using this exact structure:

Section 1: Reusable engineering rules (Java/Kotlin ecosystem)
• applies to any Java/Kotlin project
• correctness, testing hygiene, verification discipline, refactoring safety
• must not reference repository-specific paths or environment details

Section 2: Repository style and conventions (look-alike guidelines)
• rules for consistency in this repository only
• examples:
• test naming conventions (method_givenX_shouldY)
• // Given, // When, // Then comment style
• assertion style preferences
• avoid generic best practices unless explicitly framed as “match existing style”

Section 3: Repository constraints (hard boundaries)
• rules that restrict what is allowed in this repository
• examples:
• do not create new modules unless explicitly requested
• where shared constants must live
• do not change unrelated code

Rule placement test:
• reusable anywhere → Section 1
• consistency only → Section 2
• restriction/limit → Section 3
• when unsure, default to Section 1

⸻

G. Environment and privacy gate (mandatory)
21.	Do not add developer-specific or machine-specific details to any .github/** file.
• forbid absolute local paths (/Users/..., /home/..., C:\...)
• forbid usernames, machine names, IDE workspace paths
• all file references must be repository-relative
22.	If a rule depends on local setup or assistant runtime limits:
• rewrite it into a repo-agnostic constraint, or
• discard it

⸻

H. Retroactive compliance pass (mandatory)
23.	Apply all documentation rules to the entire corpus, not only new changes.
• fix pre-existing violations with minimal, safe edits
24.	Enforce no .github/tmp references globally
• scan all .github/docs/**
• rewrite references using neutral wording (e.g. “temporary documentation folder”)
25.	Enforce BEST_PRACTICES scope retroactively
• identify internal-heavy sections
• move content to canonical feature docs or remove it
• replace with short, non-duplicating pointers if needed

⸻

I. Final validation
26.	Verify:
• no new markdown files exist outside .github/docs/, .github/docs/examples/, and .github/tmp/
• .github/docs/ contains no .github/tmp references
• no developer-specific paths or environment details exist
• no duplication between BEST_PRACTICES and feature docs
• every topic has exactly one canonical home