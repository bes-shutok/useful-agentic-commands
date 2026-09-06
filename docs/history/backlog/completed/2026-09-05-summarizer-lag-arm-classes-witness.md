# Summarizer lag-arm ledger-pinned classes check is a weak witness

Status: done
Workflow: backlog
Source: docs/reviews/2026-09-05-2026-09-02-summarizer-hardening-round-2-code-review-r5.md, round r5, finding F2, testing worker

## Problem

The r4-repurposed summary-lag selftest arm asserts `_classes_of(lag_out) == base_classes`, claiming to guard the ledger-pinning contract (the `classes=` summary derives from the pre-publish classification ledger, not the refreshed buffers). But its payload B (raw_findings 5 -> 25) is valid, unique, and in-snapshot, so its class membership is identical to payload A's: both the correct implementation (ledger-pinned counts) and the regressed one (recomputing the ledger/classes summary from the refreshed buffers) print the same classes tail. The check cannot fail under its named regression; the arm's actual discrimination lives entirely in the report-half assertion. This is a duplicate/weak unit witness on a contract already discriminated by the arm's rc/note/report-bucket assertions.

## Location

`scripts/summarize_review_stats.py`, summary-lag selftest arm, the `_classes_of(lag_out) == base_classes` check (~line 3618 at review time).

## Suggested fix

Make the ledger-pinning half discriminating: at the publish gate, have the hook rewrite a SECOND sidecar to bytes that would change a refreshed-ledger class count (e.g. unparseable bytes, which move the sidecar into `unreadable` only in a refreshed-ledger world), then assert the classes tail still equals the pre-race reference. In that world only a refreshed-ledger regression changes the tail, so the check fails under its named regression.

## Severity

Low (testing#always-passes; error-contract/test-witness gap only, no production behavior defect).

## Why not fixed now

Matches the duplicate-unit-witness backlog-by-default class (execute-plan Phase 3): another arm already pins the underlying invariant, so the weak witness defers as one family-completeness item rather than an in-run fix. Deferred by the round-5 triage agent on user-directed disposition (defer F2, fold F1/F3/F4).
