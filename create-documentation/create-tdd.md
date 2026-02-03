# Command: Generate Technical Design Document (TDD) – Zero Inference Mode

Create a **Technical Design Document (TDD)** in **Markdown format**.

The **output must be Markdown only**.

You must strictly follow the **original TDD Template structure and section numbering (1–11)**.
You are **not allowed** to rename, reorder, merge, or remove sections.

The goal is to produce a TDD that:
- Explains *how* the feature will be implemented
- Is implementation-oriented (engineering-facing)
- Contains **zero inferred content**

---

## Step 0 – Input Verification (Blocking)

Before writing the TDD, verify that the following inputs are provided **in full**:

### Required Textual Inputs
- PRD (full text)
- High-level Architecture document (full text)
- Relevant service documentation (e.g. User Platform Service), including subfolders

### Required Non-Textual Inputs (if referenced by the documents)
- Architecture diagrams
- Sequence / flow diagrams
- Data model or ER diagrams
- MQ / event flow diagrams
- Tables or graphs referenced by the PRD or architecture

If **any input is missing or incomplete**:
- Stop
- Explicitly list what is missing
- Ask the user to provide it
- Do **not** infer, approximate, or substitute content

---

## Step 1 – Project Type Clarification (Mandatory)

Before section 1, explicitly determine and state:
- Project type (Backend / Frontend / Mobile / DevOps)

If unclear:
- List this as an open question
- Do not assume a default without justification from the PRD or architecture

This decision influences **which subsections are populated**, not the template itself.

---

## Step 2 – Missing Information Declaration (Mandatory)

Before section 1 of the TDD, add a short preface:

### Missing Inputs / Open Questions

List all items required for correctness that are unclear or missing, for example:
- Missing diagrams
- Undefined APIs or contracts
- Unclear service ownership
- Missing error taxonomy
- Undefined rollout or feature-flag strategy

Each item must be explicit and actionable.

---

## TDD Structure (Must Match Template Exactly)

Populate the following sections **without changing their structure**.
If a section or subsection is not applicable, explicitly state **“Not applicable”** and explain why.

### 1. 🧭 Introduction
- Feature name
- Purpose of the document
- Link to PRD
- Stakeholders
- Status and dates

### 2. 🎯 Objectives & Scope
- What is included
- What is out of scope
- Assumptions and constraints (explicit, minimal)
- Platforms or systems impacted
- Multi-region / multi-country support (explicit or TODO)

### 3. 📐 Functional Overview (Optional)
- High-level behavior and flows
- Edge cases explicitly mentioned in PRD
- No speculative behavior

### 4. ⚙️ System Impact Overview
- Systems and components affected
- APIs / endpoints
- Services and domains
- Databases, queues, jobs, third-party systems
- Explicit “NO CHANGES” where applicable

### 5. 🧱 Detailed Technical Design
Populate **only the relevant subsections** based on project type.
Mark others as “Not applicable”.

- 5.1 Backend
- 5.2 Frontend
- 5.3 Mobile
- 5.4 DevOps / Infrastructure
- 5.5 Performance & Load Considerations

All implementation details must be traceable to inputs.
Missing diagrams or specs must be marked as TODOs.

### 6. 🔐 Security & Privacy
- Permissions and access
- PII handling or explicit confirmation of absence
- Compliance and audit considerations

### 7. 📊 Observability & Metrics
- Events, logs, metrics
- KPIs
- Tools
- Explicit TODOs if observability is undefined

### 8. 🧪 Testing Strategy
- Unit tests
- Integration tests
- Manual QA
- Acceptance criteria derived from PRD
- Explicit confirmation where existing logic remains unchanged

### 9. ⚖️ Risks, Trade-offs & Limitations
- Known risks
- Trade-offs made
- Alternatives considered (if stated in inputs)
- Explicit TODOs for unknown risks

### 10. 📅 Timeline & Milestones (Optional)
- Development phases
- Dependencies
- TODOs if dates are unknown

### 11. 📌 Appendix
- Related documents
- Diagrams and schemas
- Payload examples
- Glossary (if needed)
- Placeholders for missing artifacts with exact names

---

## Content Rules (Strict)

- Markdown output only
- Zero inference policy
- Prefer TODO over assumptions
- Be explicit rather than complete
- No meta commentary
- The TDD must complement the PRD and architecture, not restate them

---

## Output Contract

Produce **one** of the following:
1. A complete TDD with no inferred content, or
2. A blocked response listing all missing inputs required to proceed

Markdown only.