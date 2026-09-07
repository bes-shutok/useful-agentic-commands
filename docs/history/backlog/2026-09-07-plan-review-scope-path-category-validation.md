# Backlog: validate plan review-scope path categories

Status: open
Workflow: backlog
Source: user correction during an implementation-plan review, 2026-09-07
Severity: Medium
Scope: `agents/skills/plans/SKILL.md` Review Scope contract, `agents/skills/review-plan/SKILL.md` validation, and project-agnostic regression fixtures

## Problem

An implementation-plan edit placed production and test paths beneath the global `Documentation:` subsection of `## Review Scope`. The Markdown remained valid, and the paths were still present in the plan, so a simple completeness check could pass while reviewers received an incorrect category mapping. This can cause implementation files to be treated as documentation and weaken review coverage or task-to-scope traceability.

The relevant structure is the plan's global `## Review Scope` section, where task file paths are grouped under categories such as `Production code`, `Tests`, and `Documentation`.

## Suggested fix

Add a project-agnostic plan validation rule, checklist item, or validator that:

1. Parses the global Review Scope category blocks and classifies each listed path by its declared category.
2. Flags source, test, configuration, resource, and other implementation artifacts listed under `Documentation:` unless an explicit documented exception applies.
3. Detects paths duplicated across categories.
4. Verifies that every task `Files:` path is covered by exactly one appropriate explicit category, or is clearly covered by the plan-related-extension policy.
5. Reports the path, the declared category, and the expected category so the author can correct placement directly.

Keep the rule independent of repository names, programming languages, module names, ticket identifiers, and framework-specific directory conventions. The category policy may use configurable or documented path-kind rules, but it must not encode one consumer repository's file suffixes or layout as the only valid model.

## Acceptance criteria

- A regression fixture with production and test paths accidentally placed under `Documentation:` fails with a precise category-mismatch diagnostic.
- Valid plans containing documentation paths under `Documentation:` pass.
- A fixture with duplicate paths across Review Scope categories fails.
- A fixture proves that task `Files:` paths are not silently omitted from the explicit scope inventory.
- The check distinguishes explicit must-fix paths from plan-related-extension prose and does not reject valid extension-only documentation coverage.
- The plan-authoring and plan-review workflows reference the same category rule, so the contract has one source of truth.
- All examples and fixtures remain project agnostic and contain no product, repository, ticket, or environment-specific identifiers.

## Not part of this backlog item

- Do not change a consumer implementation plan as the durable fix.
- Do not require every documentation file to be listed as an explicit must-fix path when the plan-related-extension policy intentionally covers it.
- Do not infer categories from one repository's exact directory layout without a documented generic rule or configurable convention.
