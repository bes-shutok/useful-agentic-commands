#!/usr/bin/env python3
"""Fail-closed readiness validator for reviewed plans.

Given a plan path, answers: does the latest review of these exact plan bytes
report ready=yes with zero unresolved blocking findings and a valid sidecar?

Exit 0 only when every readiness condition passes; otherwise prints the FIRST
failed condition and exits 1. Digest, schema, sidecar-path, and review-parsing
rules are IMPORTED from ``validate_review_staging.py`` (same directory); the
digest recipe is never re-implemented here. ``{plans_dir}`` and ``{reviews_dir}``
resolve from the ``.ai-playbook/facts.md`` TOML block via ``facts_paths.py``.

Condition ordering inside ``evaluate_readiness`` is deliberate: local
readability checks (plan path, review artifact, sidecar file, sidecar JSON,
review UTF-8, plan bytes) run first so each gets its own named reason, then
the shared sidecar gate (schema, source_kind, digest), then the verdict line,
then ``is_review_ready``. Several of those readability steps re-state checks
the shared gate would also make; they exist for reason classification, not
duplication.
"""

from __future__ import annotations

import argparse
import glob as globmod
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import facts_paths
import validate_review_staging as vrs

# Sibling compat handshake: the COMPAT_VERSION value of the sibling shared-rule
# module (vrs) that THIS validator shipped against. Checked at every launch
# (gate, sweep, selftest) before any other work; a missing or mismatched
# sibling value means a partially updated deployment.
EXPECTED_SIBLING_COMPAT_VERSION = 1

# Round suffix of a review artifact filename: ``-r<N>.md`` (N >= 1).
# Case-sensitive on purpose: the discovery glob below is lowercase-only, so
# an uppercase ``-R1.md`` artifact is invisible to both (consistent pair).
ROUND_RE = re.compile(r"-r(\d+)\.md$")
# Verdict token inside the review's ``## Summary`` section. TOTAL rule
# (r4 reconciliation directive): a verdict line is ANY line in the section
# containing a word-bounded ``ready=yes`` / ``ready=no`` token — bare,
# bulleted, bolded, behind a ``Verdict:`` / ``Ready for execution:`` label,
# or as a prose tail (``… — ready=yes.``, ``- Blocking findings: 0 —
# ready=yes``, ``Counts: … **ready=yes** — …``). A prose mention IS the
# verdict under the total rule; the fail-open concern that motivated the old
# prefix/label shape-chasing is covered by the OTHER readiness conditions
# (sidecar schema, digest match, ``is_review_ready`` zero-blocking), so the
# grammar no longer tries to distinguish prose from verdict lines. Matching
# stays PER LINE (a token split across two lines never matches) and the LAST
# occurrence in the section wins.
# PRECEDENCE (2026-09-05 plan-readiness-migration): the sidecar ``verdict``
# field ("yes"/"no", written by review-plan) is the PREFERRED verdict source;
# this per-line total rule is the LEGACY fallback for pre-adoption artifacts
# whose sidecar lacks a conforming field. Deleting the legacy grammar is
# TIME-GATED and tracked in the spin-off backlog item
# ``docs/history/backlog/2026-09-05-plan-readiness-legacy-verdict-grammar-deletion.md``
# (eligible only once ``--sweep`` coverage reports covered equal to total).
VERDICT_TOKEN_RE = re.compile(r"\bready\s*=\s*(yes|no)\b", re.IGNORECASE)


def sidecar_verdict(payload: dict) -> str | None:
    """Conforming sidecar ``verdict`` value (``"yes"``/``"no"``), else ``None``.

    Single owner of the conforming-verdict predicate: the readiness verdict
    step and the sweep coverage counter both route through this helper, so
    the yes/no membership test exists exactly once. Any other value (absent,
    dict-valued legacy key, non-yes/no string) yields ``None`` and callers
    fall back to the legacy Summary rule; version-1 records never reach a
    caller with a non-conforming value because the schema gate rejects them
    earlier.
    """
    value = payload.get("verdict")
    return value if value in vrs.VERDICT_VALUES else None


def verdict_tokens(summary: str) -> list[str]:
    """Verdict tokens (``yes``/``no``) per matching line, in document order."""
    tokens: list[str] = []
    for line in summary.splitlines():
        for match in VERDICT_TOKEN_RE.finditer(line):
            tokens.append(match.group(1).lower())
    return tokens


def repo_root(start: Path) -> Path:
    """Return the git toplevel for ``start``, or ``start`` itself on failure."""
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except (subprocess.SubprocessError, OSError):
        pass
    return start.resolve()


def feature_slug(plan_path: Path) -> str:
    """Plan filename stem minus its leading ``YYYY-MM-DD-`` prefix."""
    stem = plan_path.stem
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem, count=1)


def latest_review_round(reviews_dir: Path, slug: str) -> tuple[Path, int] | None:
    """Latest review artifact for ``slug``: highest ``r<N>``, ties by filename.

    Never resolves latest by mtime.
    """
    candidates: list[tuple[int, str, Path]] = []
    for path in reviews_dir.glob(
        f"*-plan-review-{globmod.escape(slug)}-r*.md"
    ):
        match = ROUND_RE.search(path.name)
        if match:
            candidates.append((int(match.group(1)), path.name, path))
    if not candidates:
        return None
    round_no, _, path = max(candidates)
    return path, round_no


def summary_section(content: str) -> str:
    """Text of the ``## Summary`` section (empty when absent)."""
    match = re.search(r"^## Summary\s*$", content, re.MULTILINE)
    if not match:
        return ""
    tail = content[match.end() :]
    return re.split(r"\n## ", tail, maxsplit=1)[0]


def digest_failure_reason(first_error: str, round_no: int) -> str:
    """Classify a shared-gate ``source_digest`` error into a distinct reason.

    ``stale`` is reserved for a digest MISMATCH only (the plan bytes changed
    after the review round). A missing digest or a non-hex placeholder is
    ``invalid or missing``. An unrecognized digest error gets a fallback
    wording that embeds the raw error verbatim, so a silent classification
    collapse (unknown shared-validator wording mapping to the wrong family)
    stays detectable from the printed reason.
    """
    if "is stale" in first_error:
        return (
            f"sidecar source_digest is stale (plan bytes changed after "
            f"review r{round_no}): {first_error}"
        )
    if (
        "missing source_digest" in first_error
        or "must be a lowercase" in first_error
    ):
        return (
            f"sidecar source_digest is invalid or missing (round "
            f"r{round_no}): {first_error}"
        )
    return (
        f"sidecar source_digest failed an unrecognized check (round "
        f"r{round_no}); raw error: {first_error}"
    )


def evaluate_readiness(
    plan_path: Path, plans_dir: Path, reviews_dir: Path
) -> tuple[bool, str | None]:
    """Evaluate the readiness conditions in order.

    Returns ``(ok, reason)``; ``reason`` names the FIRST failed condition only
    and is ``None`` on success.
    """
    plans_dir = plans_dir.expanduser().resolve()
    reviews_dir = reviews_dir.expanduser().resolve()
    resolved = plan_path.expanduser().resolve()

    # 1. Plan path exists, is a file, and resolves under {plans_dir}.
    if resolved.is_dir():
        return False, f"plan path is not a file: {resolved}"
    if not resolved.is_file():
        return False, f"plan file does not exist: {resolved}"
    try:
        resolved.relative_to(plans_dir)
    except ValueError:
        return False, (
            f"plan file resolves outside plans_dir: {resolved} "
            f"is not under {plans_dir}"
        )

    # r6 Z5: a configured-but-missing reviews_dir is a wiring failure with
    # its OWN reason (mirroring the sweep's r5 message), never a misleading
    # "no review artifact" that sends the user down the wrong remedy loop.
    if not reviews_dir.is_dir():
        return False, (
            f"configured reviews_dir does not exist on disk: {reviews_dir}"
        )
    slug = feature_slug(resolved)
    latest = latest_review_round(reviews_dir, slug)

    # 2. A review artifact for the feature slug exists.
    if latest is None:
        return False, (
            f"no review artifact for feature slug {slug!r} "
            f"under {reviews_dir}"
        )
    latest_path, round_no = latest

    # The sidecar and review Markdown are each read ONCE here, purely so a
    # local failure (missing file, bad JSON/UTF-8) can be classified with its
    # own reason; the shared gate below re-reads both internally. The plan
    # digest is computed ONCE and threaded into the shared gate.
    sidecar = vrs.stats_sidecar_path(latest_path)
    if not sidecar.is_file():
        return False, (
            f"missing stats sidecar for latest round r{round_no}: {sidecar.name}"
        )
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, (
            f"malformed stats sidecar (unreadable or invalid JSON): {exc}"
        )
    if not isinstance(payload, dict):
        return False, (
            f"malformed stats sidecar (top-level JSON value is not an object): "
            f"{type(payload).__name__} (round r{round_no})"
        )
    # r5 Y1: a legacy/versionless (or explicit-unsupported) sidecar is
    # REJECTED before the shared gate runs. Pure-legacy payloads take the
    # shared validator's compatibility path, which never reaches the digest
    # or source_kind checks — a fail-open hole in this fail-closed gate.
    # ``is_current_shape`` delegates to the shared classifier
    # (``classify_sidecar_schema``) so the current-vs-legacy definition has a
    # single owner; only current-shape payloads (version-1 or the versionless
    # current markers) carry a verifiable ``source_digest`` contract at all.
    if not vrs.is_current_shape(payload):
        return False, (
            f"sidecar schema is legacy/versionless; a current-shape sidecar "
            f"with a verifiable source_digest is required (round r{round_no})"
        )
    # r6 Z1: the shared gate's source_kind check only fires when the key is
    # DECLARED, so a versionless current-shape sidecar with the key deleted
    # or null bypassed it (empirically exit-0). Enforce the kind locally,
    # unconditionally, with its own named reason; the shared gate below stays
    # the authority for everything else.
    # Deliberate ordering deviation from the plan Assumptions (which
    # prescribe schema, then source_kind, then digest): this local
    # kind-before-schema pre-check runs first so a wrong-kind or kindless
    # sidecar is fail-closed classified with its own named reason instead of
    # surfacing as a generic schema failure. Same pattern as the readability
    # pre-checks above: local reason-classification pre-checks ahead of the
    # shared authority.
    declared_kind = payload.get("source_kind")
    if declared_kind != "plan":
        if declared_kind is None:
            return False, (
                f"sidecar source_kind is missing or not 'plan' (round "
                f"r{round_no})"
            )
        return False, (
            f"sidecar source_kind is {declared_kind!r}, expected 'plan' "
            f"(round r{round_no})"
        )
    try:
        content = latest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, (
            f"cannot read review artifact r{round_no} (not valid UTF-8): {exc}"
        )
    try:
        expected_digest = vrs.compute_source_digest("plan", resolved.read_bytes())
    except OSError as exc:
        return False, f"cannot read plan bytes to compute digest: {exc}"

    # 3. Shared sidecar gate: the SAME validation the staging validator runs
    # (schema validity, then source_kind, then digest — the sequencing the
    # plan Assumptions prescribe), with the "Stats sidecar: skipped" waiver
    # disabled by passing expected_digest and source_kind explicitly. This is
    # the single schema/kind/digest authority; no local duplicate checks. The
    # FIRST error is mapped to a crisp first-failed reason below, preserving
    # the distinct reason families (malformed sidecar, schema, source_kind,
    # stale digest) by classifying the shared validator's error text.
    staging_result = vrs.ValidationResult(path=latest_path)
    vrs.validate_stats_sidecar(
        latest_path,
        content,
        staging_result,
        expected_digest=expected_digest,
        source_kind="plan",
    )
    if staging_result.errors:
        first_error = staging_result.errors[0]
        if "source_kind" in first_error:
            declared = payload.get("source_kind")
            return False, (
                f"sidecar source_kind is {declared!r}, expected 'plan' "
                f"(round r{round_no})"
            )
        if "source_digest" in first_error:
            return False, digest_failure_reason(first_error, round_no)
        return False, (
            f"malformed stats sidecar (schema validation failed) for round "
            f"r{round_no}: {first_error}"
        )

    # 4. Verdict: sidecar ``verdict`` field is DECISIVE when conforming
    # ("yes"/"no" via the single-owner ``sidecar_verdict`` predicate); for
    # ANY other value (absent, or a non-conforming legacy value such as a
    # dict or a non-yes/no string) the legacy Summary total rule runs
    # UNCHANGED (any line with a word-bounded ready=yes/no token; last
    # occurrence wins). Version-1 records with non-conforming values never
    # reach this step (the schema gate rejects them earlier); versionless
    # legacy records keep today's tolerance (r2 F1 fold: the live corpus
    # carries legacy ``verdict`` keys, so a rejecting consumer would newly
    # fail artifacts that pass today).
    verdict_field = sidecar_verdict(payload)
    if verdict_field == "no":
        return False, (
            f"latest review r{round_no} sidecar verdict field reports 'no'"
        )
    if verdict_field != "yes":
        summary = summary_section(content)
        verdicts = verdict_tokens(summary)
        if not verdicts or verdicts[-1].lower() != "yes":
            return False, (
                f"latest review r{round_no} does not report a ready=yes verdict "
                f"line in its ## Summary"
            )

    # 5. is_review_ready() over the same Markdown is True.
    if not vrs.is_review_ready(content):
        return False, (
            f"latest review r{round_no} has unresolved blocking findings "
            f"(is_review_ready is False)"
        )

    return True, None


# Raw "ready=" mention in Summary text (sweep detector; broader than the
# total-rule token on purpose: it must also fire on cross-line or malformed
# shapes the token rule cannot see).
SWEEP_MENTION_RE = re.compile(r"ready\s*=", re.IGNORECASE)


def run_sweep(reviews_dir: Path) -> int:
    """Drift check (r4 X1.4): sweep ``{reviews_dir}`` plan-review artifacts.

    Under the total rule every ``## Summary`` whose text mentions ``ready=``
    must yield at least one verdict token; an anomaly is a file whose Summary
    contains a ``ready=`` mention but whose parse finds no verdict token
    (cross-line split or otherwise malformed). Exit 0 when zero anomalies;
    exit 1 listing them.
    """
    # r5 Y7: a configured-but-missing reviews_dir is a wiring failure with
    # its OWN reason — never a silent zero-artifact pass.
    if not reviews_dir.is_dir():
        print(
            f"sweep FAILED: configured reviews_dir does not exist on disk: "
            f"{reviews_dir}",
            file=sys.stderr,
        )
        return 1
    anomalies: list[str] = []
    total = 0
    covered = 0
    for path in sorted(reviews_dir.glob("*-plan-review-*.md")):
        total += 1
        # Coverage counter (Task 4): a covered artifact's sidecar exists,
        # parses as JSON, and carries a conforming ``verdict`` via the SAME
        # ``sidecar_verdict`` helper the readiness verdict step uses (single
        # owner of the yes/no predicate). Unreadable or malformed sidecars
        # count as NOT covered and are NOT anomalies.
        try:
            sidecar_payload = json.loads(
                vrs.stats_sidecar_path(path).read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, ValueError):
            sidecar_payload = None
        if isinstance(sidecar_payload, dict) and sidecar_verdict(sidecar_payload):
            covered += 1
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            anomalies.append(f"{path.name}: unreadable ({exc})")
            continue
        summary = summary_section(content)
        if SWEEP_MENTION_RE.search(summary) and not verdict_tokens(summary):
            anomalies.append(
                f"{path.name}: ## Summary mentions ready= but the total "
                f"rule finds no verdict token (cross-line or malformed)"
            )
    # Coverage line built ONCE (r1 F5): both post-glob exits print the same
    # variable, so the two messages cannot diverge on future wording edits.
    coverage_line = (
        f"sweep coverage: {covered}/{total} plan-review artifacts carry a "
        "sidecar verdict field; legacy Summary grammar deletion is "
        "eligible only when total is positive and covered equals total"
    )
    if anomalies:
        print("sweep FAILED: verdict anomalies in plan-review artifacts:")
        for line in anomalies:
            print(f"  - {line}")
        print(coverage_line)
        return 1
    print(coverage_line)
    print(
        f"sweep OK: no verdict anomalies across plan-review artifacts under "
        f"{reviews_dir}"
    )
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _check_sibling_compat() -> str | None:
    """Named error when the sibling shared-rule module drifted, else ``None``."""
    declared = getattr(vrs, "COMPAT_VERSION", None)
    if declared is None:
        return (
            "sibling validate_review_staging.py does not declare COMPAT_VERSION; "
            "the deployment is a partial update"
        )
    if declared != EXPECTED_SIBLING_COMPAT_VERSION:
        return (
            f"sibling validate_review_staging.py COMPAT_VERSION {declared!r} "
            f"!= expected {EXPECTED_SIBLING_COMPAT_VERSION!r}; "
            "the deployment is a partial update with divergent "
            "shared-rule semantics"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed reviewed-plan readiness gate"
    )
    parser.add_argument("plan_path", nargs="?", help="Path to the plan file")
    parser.add_argument(
        "--selftest", action="store_true", help="Run fixture checks and exit"
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Sweep {reviews_dir} plan-review artifacts for verdict-parse "
        "anomalies (Summary text contains ready= but the total rule finds "
        "no verdict token); exit 0 when none, exit 1 listing them",
    )
    args = parser.parse_args(argv)

    compat_error = _check_sibling_compat()
    if compat_error is not None:
        print(f"compatibility FAILED: {compat_error}", file=sys.stderr)
        return 1

    if args.selftest:
        return run_selftest()

    root = repo_root(Path.cwd())
    plans_dir_raw = facts_paths.resolve_toml_key_raw(root, "plans_dir")
    reviews_dir_raw = facts_paths.resolve_toml_key_raw(root, "reviews_dir")

    def anchor_at_root(raw: str) -> Path:
        # Tilde-valued facts keys are user-absolute; everything else anchors
        # at the repo ROOT (not the process CWD), so a caller outside the
        # repo root must not false-reject (C1). CWD PREFERENCE (r4 X5): when
        # the raw relative path exists relative to the process cwd, prefer
        # the cwd interpretation BEFORE re-rooting, so a cwd-relative
        # ``..``-containing plan path does not get misleadingly re-rooted at
        # the repo root into a nonexistent path.
        expanded = Path(raw).expanduser() if raw.startswith("~") else Path(raw)
        if expanded.is_absolute():
            return expanded.resolve()
        if expanded.exists():
            return expanded.resolve()
        return (root / expanded).resolve()

    # Single facts resolution (r5 Y5): resolved ONCE here, above the --sweep
    # branch, for both the sweep path (reviews_dir only) and the gate path.
    plans_dir = anchor_at_root(plans_dir_raw) if plans_dir_raw else None
    reviews_dir = anchor_at_root(reviews_dir_raw) if reviews_dir_raw else None

    if args.sweep:
        # --sweep takes no plan operand (r5 Y7): the sweep covers the whole
        # {reviews_dir}; a plan_path alongside it is a caller error.
        if args.plan_path:
            parser.error("plan_path must not be combined with --sweep")
        if reviews_dir is None:
            print(
                "sweep FAILED: cannot resolve reviews_dir from the facts "
                "TOML block",
                file=sys.stderr,
            )
            return 1
        return run_sweep(reviews_dir)

    if not args.plan_path:
        parser.error("plan_path is required (or pass --selftest / --sweep)")

    if plans_dir is None or reviews_dir is None:
        print(
            "readiness FAILED: cannot resolve plans_dir/reviews_dir from the "
            "facts TOML block",
            file=sys.stderr,
        )
        return 1

    # The plan-path argument anchors like relative facts values: CWD
    # PREFERENCE first (a path that exists relative to the process cwd wins,
    # r4 X5), then re-rooting at the resolved repo ROOT (a caller invoking
    # from a subdirectory or outside the repo must not false-reject a valid
    # relative plan path).
    ok, reason = evaluate_readiness(
        anchor_at_root(args.plan_path), plans_dir, reviews_dir
    )
    if ok:
        print("readiness OK: latest review of these plan bytes is ready")
        return 0
    print(f"readiness FAILED: {reason}", file=sys.stderr)
    return 1


# --------------------------------------------------------------------------- #
# Selftest: fixture family through a TEMP tree, never the live repo.
# --------------------------------------------------------------------------- #
def _clear_sidecar(plan_digest: str, source_kind: str = "plan") -> dict:
    """Versionless current-shape clear-review sidecar (schema-passing)."""
    return {
        "panel_mode": "full",
        "selection_reason": None,
        "source_kind": source_kind,
        "source_digest": plan_digest,
        "escalation_reason": None,
        "counts": {"workers_launched": 5, "staged_findings": 0},
        "panel": [
            {
                "worker": worker,
                "lenses": lenses,
                "parent_worker": None,
                "descendant_launches": [],
                "status": "complete",
                "raw": 0,
                "solo": 0,
                "echo": 0,
                "relaunch": False,
            }
            for worker, lenses in (
                ("correctness-completeness", ["quality", "implementation"]),
                ("testing", ["testing"]),
                ("design-simplicity", ["architecture", "simplification"]),
                ("contract-docs", ["documentation"]),
                ("risk", ["security"]),
            )
        ],
        "findings": [],
        "overflow": [],
    }


def _review_markdown(
    verdict: str = "yes",
    blocking_finding: bool = False,
    verdict_line: str | None = None,
) -> str:
    """A realistic plan-review round with a ``## Summary`` verdict.

    ``verdict_line`` overrides the default ``- ready=<verdict>`` bullet to
    exercise other legitimate verdict-line shapes (bare line, trailing
    parenthetical, prose mention).
    """
    findings_body = (
        "### Critical\nNone.\n\n### High\nNone.\n\n"
        "### Medium\nNone.\n\n### Low\nNone.\n"
    )

    if blocking_finding:
        findings_body = (
            "### Critical\nNone.\n\n### High\n\n#### F1. unresolved blocker\n"
            "- **Severity**: High\n"
            "- **Blocking**: true\n"
            "- **Consequence**: plan cannot be executed as written\n"
            "- **Reachability**: expected\n"
            "- **Blast Radius**: single-service\n"
            "- **Confidence**: verified\n"
            "- **Triage**: pending\n\n"
            "#### Comment\n\nThe blocker stands.\n\n"
            "#### Analysis\n\nWorker finding, unrestaged doubt.\n\n"
            "### Medium\nNone.\n\n### Low\nNone.\n"
        )
    summary_verdict = (
        verdict_line if verdict_line is not None else f"- ready={verdict}"
    )
    return (
        "# Plan Review: fixture feature\n\n"
        "## Metadata\n"
        "- Type: Plan Review\n"
        "- Round: r1\n"
        "- Findings: 0\n"
        "- Status: STAGED\n\n"
        "## Summary\n\n"
        "- Counts: Critical 0 | High 0 | Medium 0 | Low 0 | Overflow 0\n"
        "- Blocking findings by id: none\n"
        f"{summary_verdict}\n\n"
        "## Review Statistics\n\n"
        "### Panel\n"
        "| Worker | Lenses | Status | Raw | Solo | Echo | Relaunch | Parent worker |\n"
        "|--------|--------|--------|-----|------|------|----------|--------------|\n"
        "| correctness-completeness | quality, implementation | complete | 0 | 0 | 0 | no | none |\n"
        "| testing | testing | complete | 0 | 0 | 0 | no | none |\n"
        "| design-simplicity | architecture, simplification | complete | 0 | 0 | 0 | no | none |\n"
        "| contract-docs | documentation | complete | 0 | 0 | 0 | no | none |\n"
        "| risk | security | complete | 0 | 0 | 0 | no | none |\n\n"
        "### Counts\n"
        "- Workers launched: 5\n"
        "- Staged findings: 0\n\n"
        "### Triage outcomes\n"
        "Pending triage.\n\n"
        "## Findings\n\n"
        f"{findings_body}\n"
    )


def run_selftest() -> int:
    import os
    import tempfile

    failures = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        if ok:
            print(f"PASS: {name}")
        else:
            failures += 1
            print(f"FAIL: {name}" + (f" - {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plans_dir = root / "plans"
        reviews_dir = root / "reviews"
        plans_dir.mkdir()
        reviews_dir.mkdir()

        def write_clean_state(
            plan_text: str = "# Fixture plan\n\nBody.\n",
            verdict: str = "yes",
            digest_override: str | None = None,
            source_kind: str = "plan",
            blocking: bool = False,
            round_suffix: str = "r1",
            date: str = "2026-09-01",
            slug: str = "fixture-feature",
            verdict_line: str | None = None,
        ) -> tuple[Path, Path]:
            plan = plans_dir / f"{date}-{slug}.md"
            plan.write_text(plan_text, encoding="utf-8")
            digest = digest_override or vrs.compute_source_digest(
                "plan", plan.read_bytes()
            )
            sidecar = _clear_sidecar(digest, source_kind)
            if blocking:
                sidecar["findings"] = [
                    {
                        "id": 1,
                        "severity": "High",
                        "blocking": True,
                        "consequence": "plan cannot be executed as written",
                        "reachability": "expected",
                        "blast_radius": "single-service",
                        "confidence": "verified",
                    }
                ]
                sidecar["counts"]["staged_findings"] = 1
            review = reviews_dir / (
                f"{date}-plan-review-{slug}-{round_suffix}.md"
            )
            review.write_text(
                _review_markdown(
                    verdict=verdict,
                    blocking_finding=blocking,
                    verdict_line=verdict_line,
                ),
                encoding="utf-8",
            )
            review.with_suffix(".stats.json").write_text(
                json.dumps(sidecar), encoding="utf-8"
            )
            return plan, review

        # no_review_files: plan present, no matching review artifact.
        plan, _ = write_clean_state()
        for path in reviews_dir.iterdir():
            path.unlink()
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#no_review_files",
            not ok and reason is not None and "no review artifact" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # missing_sidecar: latest round Markdown present, no .stats.json.
        plan, review = write_clean_state()
        review.with_suffix(".stats.json").unlink()
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#missing_sidecar",
            not ok and reason is not None and "missing stats sidecar" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # malformed_sidecar (invalid JSON arm).
        plan, review = write_clean_state()
        review.with_suffix(".stats.json").write_text("{not json", encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#malformed_sidecar/invalid_json",
            not ok and reason is not None and "malformed stats sidecar" in reason,
            f"ok={ok} reason={reason}",
        )
        # legacy_or_unsupported_sidecar (r5 Y1): an explicit-unsupported
        # schema_version never reaches the shared gate's per-field checks;
        # it is rejected by the current-shape requirement with the named
        # legacy/versionless reason.
        review.with_suffix(".stats.json").write_text(
            json.dumps({"schema_version": 99}), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#legacy_or_unsupported_sidecar/schema_version",
            not ok and reason is not None
            and "legacy/versionless" in reason,
            f"ok={ok} reason={reason}",
        )
        # legacy_or_unsupported_sidecar (r5 Y1a): an EMPTY sidecar object
        # classifies pure-legacy (no version, no current markers) — it used
        # to bypass the digest/source_kind checks entirely (fail-open hole);
        # it must now exit 1 with the named reason even beside a clean
        # review and a matching plan.
        review.with_suffix(".stats.json").write_text("{}", encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#legacy_or_unsupported_sidecar/empty_object",
            not ok and reason is not None
            and "legacy/versionless" in reason
            and "source_digest is required" in reason,
            f"ok={ok} reason={reason}",
        )
        # legacy_or_unsupported_sidecar (r5 Y1b): a versionless legacy
        # payload WITHOUT a source_digest (no panel_mode / counts markers)
        # classifies pure-legacy and must be rejected by the shape gate, not
        # silently waved through with no digest to verify.
        review.with_suffix(".stats.json").write_text(
            json.dumps({"source_kind": "plan", "panel": []}), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#legacy_or_unsupported_sidecar/no_source_digest",
            not ok and reason is not None
            and "legacy/versionless" in reason,
            f"ok={ok} reason={reason}",
        )
        # legacy_or_unsupported_sidecar (r5 Y1c, CRITICAL bypass proof):
        # with a legacy sidecar the gate must reject EVEN when the shared
        # gate alone would pass; and after a would-be-ready state, EDITING
        # the plan bytes must STILL exit 1 (the pre-Y1 build exited 0 both
        # times — the bypass is closed).
        review.with_suffix(".stats.json").write_text(
            json.dumps({"legacy": True}), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#legacy_or_unsupported_sidecar/bypass_closed_initial",
            not ok and reason is not None
            and "legacy/versionless" in reason,
            f"ok={ok} reason={reason}",
        )
        plan.write_text("# Fixture plan\n\nBody edited post-review.\n", encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#legacy_or_unsupported_sidecar/bypass_closed_after_edit",
            not ok and reason is not None
            and "legacy/versionless" in reason,
            f"ok={ok} reason={reason}",
        )
        # malformed_sidecar (schema-failing arm: current shape with bad panel).
        # Digest must MATCH the plan bytes so the failure is schema-shaped.
        bad = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        bad["panel_mode"] = "banana"
        review.with_suffix(".stats.json").write_text(
            json.dumps(bad), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#malformed_sidecar/panel_mode_invalid",
            not ok and reason is not None and "schema validation failed" in reason,
            f"ok={ok} reason={reason}",
        )
        # malformed_sidecar (non-UTF-8 arm): named reason, no traceback.
        review.with_suffix(".stats.json").write_bytes(b"\xff\xfe{not json")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#malformed_sidecar/not_utf8",
            not ok and reason is not None
            and "unreadable or invalid JSON" in reason,
            f"ok={ok} reason={reason}",
        )
        # review artifact itself not valid UTF-8: named reason, no traceback.
        # (Restore a VALID sidecar first so the review read is the failure.)
        review.with_suffix(".stats.json").write_text(
            json.dumps(
                _clear_sidecar(
                    vrs.compute_source_digest("plan", plan.read_bytes())
                )
            ),
            encoding="utf-8",
        )
        review.write_bytes(b"# review \xff\xfe binary\n")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#review_artifact_not_utf8",
            not ok and reason is not None and "not valid UTF-8" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # wrong_source_kind: valid schema, source_kind "code" -> the shared
        # sidecar-gate condition (no ordinal: the shared gate owns the
        # schema/kind/digest sequence; do not renumber against the numbered
        # comments inside evaluate_readiness).
        plan, _ = write_clean_state(source_kind="code")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#wrong_source_kind",
            not ok and reason is not None
            and "source_kind is 'code', expected 'plan'" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # r6 Z1: source_kind bypassable by omission/null on versionless
        # current-shape sidecars (the shared gate only checks a DECLARED
        # kind). Both arms must exit 1 with the named reason.
        plan, review = write_clean_state()
        missing_kind = _clear_sidecar(
            vrs.compute_source_digest("plan", plan.read_bytes())
        )
        del missing_kind["source_kind"]
        review.with_suffix(".stats.json").write_text(
            json.dumps(missing_kind), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#source_kind_key_deleted",
            not ok and reason is not None
            and "source_kind is missing or not 'plan'" in reason,
            f"ok={ok} reason={reason}",
        )
        null_kind = _clear_sidecar(
            vrs.compute_source_digest("plan", plan.read_bytes())
        )
        null_kind["source_kind"] = None
        review.with_suffix(".stats.json").write_text(
            json.dumps(null_kind), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#source_kind_null",
            not ok and reason is not None
            and "source_kind is missing or not 'plan'" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # valid_schema_wrong_digest: schema passes, digest hashes other bytes.
        plan, review = write_clean_state(digest_override="a" * 64)
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#valid_schema_wrong_digest",
            not ok and reason is not None and "stale" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # Digest reason classification (W4, r3): "stale" is reserved for a
        # MISMATCH; missing or non-hex digests get the distinct
        # "invalid or missing" family; an unrecognized shared-validator digest
        # error gets the fallback wording that embeds the raw error.
        plan, review = write_clean_state()
        missing = _clear_sidecar(
            vrs.compute_source_digest("plan", plan.read_bytes())
        )
        del missing["source_digest"]
        review.with_suffix(".stats.json").write_text(
            json.dumps(missing), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#digest_missing_key",
            not ok and reason is not None
            and "invalid or missing" in reason
            and "stale" not in reason,
            f"ok={ok} reason={reason}",
        )

        non_hex = _clear_sidecar("Z" * 64)
        review.with_suffix(".stats.json").write_text(
            json.dumps(non_hex), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#digest_non_hex",
            not ok and reason is not None
            and "invalid or missing" in reason
            and "stale" not in reason,
            f"ok={ok} reason={reason}",
        )

        fallback = digest_failure_reason(
            "current sidecar source_digest failed some future check", 3
        )
        check(
            "selftest#digest_fallback_classification",
            "unrecognized check" in fallback
            and "future check" in fallback,
            f"fallback={fallback!r}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # stale_digest_after_plan_edit + review edited after validation.
        plan, review = write_clean_state()
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#stale_digest_after_plan_edit/initial_pass",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        plan.write_text("# Fixture plan\n\nBody edited.\n", encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#stale_digest_after_plan_edit/plan_edited",
            not ok and reason is not None and "stale" in reason,
            f"ok={ok} reason={reason}",
        )
        # Restore the plan bytes (digest matches again), then edit ONLY the
        # review Markdown after a passing call: the next call must re-read it
        # and fail on the changed verdict.
        plan.write_text("# Fixture plan\n\nBody.\n", encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#stale_digest_after_plan_edit/restored_pass",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        review.write_text(
            _review_markdown(verdict="no"), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#stale_digest_after_plan_edit/review_markdown_edited",
            not ok and reason is not None and "ready=yes" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # ready_no_verdict: ready=no with zero blocking findings.
        plan, _ = write_clean_state(verdict="no")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#ready_no_verdict",
            not ok and reason is not None and "ready=yes" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # verdict_field fixtures (Task 3): consumer precedence, sidecar
        # verdict over Summary grammar. Three RED (precedence not
        # implemented yet) + two GREEN characterization (fallback must
        # survive unchanged).
        plan, review = write_clean_state()
        sc = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        sc["verdict"] = "yes"
        review.write_text(
            _review_markdown(
                verdict_line=(
                    "Counts confirmed in Review Statistics; the verdict "
                    "lives in the sidecar verdict field."
                )
            ),
            encoding="utf-8",
        )
        review.with_suffix(".stats.json").write_text(
            json.dumps(sc), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/sidecar_yes_summary_silent_passes",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        plan, review = write_clean_state(verdict="yes")
        sc = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        sc["verdict"] = "no"
        review.with_suffix(".stats.json").write_text(
            json.dumps(sc), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/sidecar_no_overrides_summary_yes",
            not ok and reason is not None
            and "sidecar verdict field reports" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        plan, review = write_clean_state(verdict="no")
        sc = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        sc["verdict"] = "yes"
        review.with_suffix(".stats.json").write_text(
            json.dumps(sc), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/sidecar_yes_overrides_summary_no",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # legacy_verdict_junk_falls_back (characterization): a
        # non-conforming verdict value neither decides nor fails readiness;
        # the Summary rule runs unchanged.
        plan, review = write_clean_state(verdict="yes")
        sc = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        sc["verdict"] = "maybe"
        review.with_suffix(".stats.json").write_text(
            json.dumps(sc), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/legacy_verdict_junk_falls_back/string_arm",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        plan, review = write_clean_state(verdict="no")
        sc = _clear_sidecar(vrs.compute_source_digest("plan", plan.read_bytes()))
        sc["verdict"] = {"ready": False}
        review.with_suffix(".stats.json").write_text(
            json.dumps(sc), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/legacy_verdict_junk_falls_back/dict_arm",
            not ok and reason is not None
            and "does not report a ready=yes verdict" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # absent_falls_back_to_summary (characterization): no verdict field,
        # Summary decides exactly as today.
        plan, _ = write_clean_state(verdict="no")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_field/absent_falls_back_to_summary",
            not ok and reason is not None
            and "does not report a ready=yes verdict" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # verdict_outside_summary_rejects (r5 Y3): a ready=yes token that
        # appears ONLY in ## Findings is not a Summary verdict; the Summary
        # scoping must not silently widen to the whole document.
        plan, review = write_clean_state(verdict_line="- verdict deferred")
        content = _review_markdown(verdict_line="- verdict deferred")
        content = content.replace(
            "### Low\nNone.\n", "### Low\nNone.\n\nready=yes\n", 1
        )
        review.write_text(content, encoding="utf-8")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_outside_summary_rejects",
            not ok and reason is not None and "ready=yes" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # boundary_violating_mention_rejects (r5 Y4): ``Notready=yes`` is
        # NOT a word-bounded verdict token; as the ONLY Summary mention it
        # must yield no verdict (reject), proving the \b anchors.
        plan, _ = write_clean_state(verdict_line="- Notready=yes")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#boundary_violating_mention_rejects",
            not ok and reason is not None and "ready=yes" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # verdict_line_shapes (r4 reconciliation, corpus-derived): every
        # shape attested in the LIVE corpus under {reviews_dir} (grounded
        # against real lines before writing fixtures), exercised for
        # ready=yes AND ready=no, under the TOTAL rule: any Summary line
        # with a word-bounded ready=yes/no token is a verdict line, last
        # occurrence wins, and a prose mention IS a verdict.
        corpus_shapes = [
            # bare line (2026-09-04-plan-review-review-doc-digest-scope-fix-r5.md:88)
            "ready=yes",
            # bullet, trailing parenthetical (corpus family default)
            "- ready=yes (clean after r7 folds)",
            # bold verdict, no label (2026-09-02-...-r5-residuals-fixes-r4.md:15)
            "**ready=yes**",
            # bold Verdict label + parenthetical (validator-pass r3:53)
            "**Verdict: ready=yes** (zero unresolved blocking findings).",
            # bullet Verdict label, bold value, dash tail (docs-branch-temp-file-hygiene r3:42)
            "- Verdict: **ready=yes** — zero unresolved blocking findings.",
            # bullet Verdict label, plain value (review-doc-digest-scope-fix r4:17)
            "- Verdict: ready=yes after r3 folds",
            # prose tail sentence (fence-close-rules r5:19)
            "Counts: Critical 0 | High 0 | Medium 0 | Low 0. Blocking findings: none. The plan is ready for execution at this digest. Verdict: ready=yes.",
            # Ready for execution label (corpus family)
            "Ready for execution: ready=yes",
            # bullet label + bold value + parenthetical (review-pointer-wiring-polish r2:7)
            "- Ready for execution: **ready=yes** (zero unresolved blocking findings)",
            # bold ready=yes as prose tail after a period (docs-branch-temp-file-hygiene r3:119)
            "Zero unresolved blocking findings. The plan's diagnosis is accurate and every stated witness reproduces. **ready=yes**.",
            # dash tail after Blocking findings count (fence-scanner-consolidation r2:157)
            "- Blocking findings: 0 — ready=yes",
            # Counts prose with bold verdict and dash tail (docs-branch-temp-file-hygiene r2:17)
            "Counts: **0 Critical | 0 High | 0 Medium | 2 Low**. Blocking findings: **none**. Verdict: **ready=yes** — the plan is ready for execution.",
            # prose mention with no label at all: ACCEPTS under the total rule
            "The panel concludes this plan is ready=yes overall.",
        ]
        for idx, line in enumerate(corpus_shapes):
            plan, _ = write_clean_state(verdict_line=line)
            ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
            check(
                f"selftest#verdict_line_shapes/corpus_yes_{idx}",
                ok and reason is None,
                f"line={line!r} ok={ok} reason={reason}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()

        corpus_no_shapes = [
            # bare ready=no (review-doc-digest-scope-fix r3:91)
            "ready=no",
            # bullet ready=no (phase3-review-churn-control r6:283)
            "- ready=no",
            # bold Verdict label, no (r5-residuals-fixes r2:93)
            "Verdict: **ready=no**",
            # bullet Verdict label + reason (validator-pass r1:17)
            "- Verdict: ready=no (one unresolved blocking finding; fold F1 into the plan and re-run a fresh round).",
            # prose tail ready=no
            "Counts: Critical 0 | High 1. Verdict: ready=no.",
            # dash tail after a nonzero blocking count (fence-scanner-consolidation r3:141)
            "- Blocking findings: 1 (F1) — ready=no",
            # Ready for execution label, no
            "Ready for execution: ready=no",
            # bold ready=no as prose tail after a period
            "One blocker stands unresolved against the current digest. **ready=no**.",
        ]
        for idx, line in enumerate(corpus_no_shapes):
            plan, _ = write_clean_state(verdict_line=line)
            ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
            check(
                f"selftest#verdict_line_shapes/corpus_no_{idx}_rejects",
                not ok and reason is not None and "ready=yes" in reason,
                f"line={line!r} ok={ok} reason={reason}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()

        # last-wins across lines: an earlier ready=yes is overridden by a
        # later ready=no in the same Summary (total rule, per line).
        plan, _ = write_clean_state(
            verdict_line="- ready=yes\n- Verdict: ready=no (one blocker re-confirmed)"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_line_shapes/last_line_wins_no",
            not ok and reason is not None and "ready=yes" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # last-wins in the other direction: an earlier ready=no is rescued
        # by a later canonical ready=yes line.
        plan, _ = write_clean_state(
            verdict_line="- Verdict: ready=no (superseded by the fold below)\nVerdict: ready=yes"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#verdict_line_shapes/last_line_wins_yes",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # unresolved_blocking_finding: ready=yes, one blocking:true unresolved.
        plan, _ = write_clean_state(blocking=True)
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#unresolved_blocking_finding",
            not ok and reason is not None and "is_review_ready" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # plan_outside_plans_dir.
        outside = root / "outside-plan.md"
        outside.write_text("# outside\n", encoding="utf-8")
        ok, reason = evaluate_readiness(outside, plans_dir, reviews_dir)
        check(
            "selftest#plan_outside_plans_dir",
            not ok and reason is not None and "outside plans_dir" in reason,
            f"ok={ok} reason={reason}",
        )

        # missing_plan_path.
        ghost = plans_dir / "2026-09-01-ghost.md"
        ok, reason = evaluate_readiness(ghost, plans_dir, reviews_dir)
        check(
            "selftest#missing_plan_path",
            not ok and reason is not None and "does not exist" in reason,
            f"ok={ok} reason={reason}",
        )

        # missing_reviews_dir (r6 Z5): a configured-but-missing reviews_dir
        # on the GATE path gets its own named wiring reason (mirroring the
        # sweep's r5 message), never a misleading "no review artifact".
        wire = plans_dir / "2026-09-01-wire-check.md"
        wire.write_text("# wire check\n", encoding="utf-8")
        ok, reason = evaluate_readiness(
            wire, plans_dir, root / "reviews-gone"
        )
        check(
            "selftest#missing_reviews_dir",
            not ok and reason is not None
            and "configured reviews_dir does not exist on disk" in reason,
            f"ok={ok} reason={reason}",
        )

        # plan_path_is_directory: directory at the plan path gets its own
        # reason, not a misleading "does not exist".
        dir_at_plan = plans_dir / "2026-09-01-not-a-plan.md"
        dir_at_plan.mkdir()
        ok, reason = evaluate_readiness(dir_at_plan, plans_dir, reviews_dir)
        check(
            "selftest#plan_path_is_directory",
            not ok and reason is not None and "not a file" in reason,
            f"ok={ok} reason={reason}",
        )
        dir_at_plan.rmdir()

        # latest_round_selection: r1 clean (newer mtime), r2 not; r2 decides.
        plan, r1 = write_clean_state(round_suffix="r1", date="2026-09-01")
        digest = vrs.compute_source_digest("plan", plan.read_bytes())
        r2 = reviews_dir / "2026-09-02-plan-review-fixture-feature-r2.md"
        r2.write_text(_review_markdown(verdict="no"), encoding="utf-8")
        r2.with_suffix(".stats.json").write_text(
            json.dumps(_clear_sidecar(digest)), encoding="utf-8"
        )
        # Force r1 to have the NEWER mtime; latest must still be r2.
        future = 4102444800.0  # 2100-01-01
        os.utime(r1, (future, future))
        os.utime(r1.with_suffix(".stats.json"), (future, future))
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#latest_round_selection",
            not ok and reason is not None and "r2" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # uppercase_round_suffix_ignored (W10, r3): an uppercase ``-R2.md``
        # artifact is invisible to BOTH the discovery glob and ROUND_RE (a
        # consistent lowercase-only pair), so a clean uppercase r2 must NOT
        # rescue a rejecting lowercase r1.
        plan, _ = write_clean_state(verdict="no", round_suffix="r1")
        digest = vrs.compute_source_digest("plan", plan.read_bytes())
        upper = reviews_dir / "2026-09-02-plan-review-fixture-feature-R2.md"
        upper.write_text(_review_markdown(verdict="yes"), encoding="utf-8")
        upper.with_suffix(".stats.json").write_text(
            json.dumps(_clear_sidecar(digest)), encoding="utf-8"
        )
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#uppercase_round_suffix_ignored",
            not ok and reason is not None and "r1" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # latest_round_selection_tie_break (same-N cross-date): two r1
        # artifacts for one slug with different date prefixes; the tie must
        # resolve by (round, filename) order, NEVER by mtime. The
        # earlier-dated artifact and its sidecar are forced to a year-2100
        # mtime so any mtime participation would flip the winner.
        # Arm 1: later-dated ready=no decides -> not-ok mentioning r1.
        plan, _ = write_clean_state(
            verdict="yes", round_suffix="r1", date="2026-09-01"
        )
        digest = vrs.compute_source_digest("plan", plan.read_bytes())
        later = reviews_dir / "2026-09-02-plan-review-fixture-feature-r1.md"
        later.write_text(_review_markdown(verdict="no"), encoding="utf-8")
        later.with_suffix(".stats.json").write_text(
            json.dumps(_clear_sidecar(digest)), encoding="utf-8"
        )
        earlier = reviews_dir / "2026-09-01-plan-review-fixture-feature-r1.md"
        future = 4102444800.0  # 2100-01-01
        os.utime(earlier, (future, future))
        os.utime(earlier.with_suffix(".stats.json"), (future, future))
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#latest_round_selection_tie_break/later_dated_decides",
            not ok and reason is not None and "r1" in reason,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # Arm 2: inverted polarity — later-dated ready=yes decides -> ok,
        # under the same adversarial mtime on the earlier-dated pair.
        plan, _ = write_clean_state(
            verdict="no", round_suffix="r1", date="2026-09-01"
        )
        digest = vrs.compute_source_digest("plan", plan.read_bytes())
        later = reviews_dir / "2026-09-02-plan-review-fixture-feature-r1.md"
        later.write_text(_review_markdown(verdict="yes"), encoding="utf-8")
        later.with_suffix(".stats.json").write_text(
            json.dumps(_clear_sidecar(digest)), encoding="utf-8"
        )
        earlier = reviews_dir / "2026-09-01-plan-review-fixture-feature-r1.md"
        # r1 F4: this arm owns its adversarial mtime constant instead of
        # reusing arm 1's ``future``; removing or reordering arm 1 must
        # fail only this check, not crash the whole selftest with NameError.
        future = 4102444800.0  # 2100-01-01
        os.utime(earlier, (future, future))
        os.utime(earlier.with_suffix(".stats.json"), (future, future))
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#latest_round_selection_tie_break/inverted_polarity_ok",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        for path in reviews_dir.iterdir():
            path.unlink()

        # glob_metachar_slug: a plan slug containing glob metacharacters
        # (e.g. ``fixture[1]``) must still discover its review artifact —
        # pins the glob.escape in latest_review_round.
        plan, _ = write_clean_state(slug="fixture[1]")
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#glob_metachar_slug",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )
        # And the metachar slug with NO review artifact must reject (the
        # escaped glob must not over-match anything else either).
        for path in reviews_dir.iterdir():
            path.unlink()
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#glob_metachar_slug/no_review_rejects",
            not ok and reason is not None and "no review artifact" in reason,
            f"ok={ok} reason={reason}",
        )

        # accepted_state: exit 0 and no reason output.
        plan, _ = write_clean_state()
        ok, reason = evaluate_readiness(plan, plans_dir, reviews_dir)
        check(
            "selftest#accepted_state",
            ok and reason is None,
            f"ok={ok} reason={reason}",
        )

        # ------------------------------------------------------------------ #
        # CLI fixtures (main() over a temp tree): exit codes, output format,
        # facts resolution, and repo-root anchoring all guarded here.
        # ------------------------------------------------------------------ #
        import contextlib
        import io

        facts_dir = root / ".ai-playbook"
        facts_dir.mkdir()
        (facts_dir / "facts.md").write_text(
            "# facts\n\n```toml\n"
            'plans_dir = "plans"\n'
            'reviews_dir = "reviews"\n'
            "```\n",
            encoding="utf-8",
        )

        def run_cli(plan_arg: Path) -> tuple[int, str, str]:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = main([str(plan_arg)])
            return rc, out.getvalue(), err.getvalue()

        def run_main(argv: list[str]) -> tuple[int, str, str]:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = main(argv)
            return rc, out.getvalue(), err.getvalue()

        prev_cwd = os.getcwd()
        os.chdir(root)  # repo_root() anchors at the process cwd
        try:
            # Sibling compat handshake fixtures: the in-process pair must
            # agree on COMPAT_VERSION, and every CLI mode fails loudly on a
            # mismatched or missing sibling constant.
            declared = getattr(vrs, "COMPAT_VERSION", None)
            check(
                "selftest#sibling_compat/real_pair_match",
                declared == EXPECTED_SIBLING_COMPAT_VERSION
                and _check_sibling_compat() is None,
                f"declared={declared!r}",
            )

            _compat_missing = object()
            _compat_saved = getattr(vrs, "COMPAT_VERSION", _compat_missing)
            try:
                vrs.COMPAT_VERSION = 999
                rc, out, err = run_main(["--sweep"])
                check(
                    "selftest#sibling_compat/mismatch_fails_loud",
                    rc == 1
                    and "compatibility FAILED" in err
                    and "999" in err
                    and "sweep" not in out,
                    f"rc={rc} out={out!r} err={err!r}",
                )
                # r1 F3: gate mode fails loudly on the same mismatch; pins
                # that the handshake runs ahead of the gate path too, not
                # only the sweep path.
                rc, out, err = run_cli(plan)
                check(
                    "selftest#sibling_compat/mismatch_fails_loud/gate_mode",
                    rc == 1
                    and "compatibility FAILED" in err
                    and "readiness" not in out,
                    f"rc={rc} out={out!r} err={err!r}",
                )
                # r1 F3: --selftest mode fails loudly BEFORE the nested
                # selftest dispatch (returns early, so cost is negligible);
                # a refactor moving the check below the dispatch would fail
                # this arm.
                rc, out, err = run_main(["--selftest"])
                check(
                    "selftest#sibling_compat/mismatch_fails_loud/"
                    "selftest_mode",
                    rc == 1
                    and "compatibility FAILED" in err
                    and "ALL PASS" not in out
                    and "PASS:" not in out,
                    f"rc={rc} out={out!r} err={err!r}",
                )
                delattr(vrs, "COMPAT_VERSION")
                rc, out, err = run_main(["--sweep"])
                _ok = (
                    rc == 1
                    and "compatibility FAILED" in err
                    and "does not declare COMPAT_VERSION" in err
                    and "sweep" not in out
                )
                check(
                    "selftest#sibling_compat/missing_constant",
                    _ok,
                    f"rc={rc} out={out!r} err={err!r}",
                )
            finally:
                if _compat_saved is _compat_missing:
                    delattr(vrs, "COMPAT_VERSION")
                else:
                    vrs.COMPAT_VERSION = _compat_saved

            # accepted: exit 0 with the readiness OK line on stdout.
            rc, out, err = run_cli(plan)
            check(
                "selftest#cli/accepted_state",
                rc == 0 and "readiness OK" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )

            # rejected: exit 1 with the readiness FAILED: prefix on stderr.
            plan2, _ = write_clean_state(verdict="no")
            rc, out, err = run_cli(plan2)
            check(
                "selftest#cli/rejected_state",
                rc == 1 and "readiness FAILED:" in err,
                f"rc={rc} out={out!r} err={err!r}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()

            # missing facts: exit 1 with the cannot-resolve reason.
            (facts_dir / "facts.md").unlink()
            rc, out, err = run_cli(plan)
            check(
                "selftest#cli/missing_facts",
                rc == 1 and "cannot resolve plans_dir/reviews_dir" in err,
                f"rc={rc} out={out!r} err={err!r}",
            )

            # nested_cwd (W10, r3): a RELATIVE plan path invoked from a
            # subdirectory of a real git repo anchors at the repo ROOT, not
            # the process cwd.
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "plans"\n'
                'reviews_dir = "reviews"\n'
                "```\n",
                encoding="utf-8",
            )
            plan, _ = write_clean_state()
            subprocess.run(
                ["git", "-C", str(root), "init", "-q"], check=False
            )
            subdir = root / "sub"
            subdir.mkdir()
            os.chdir(subdir)
            rc, out, err = run_cli(Path("plans") / plan.name)
            check(
                "selftest#cli/nested_cwd",
                rc == 0 and "readiness OK" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )

            # cwd_relative_dotdot (r4 X5): a ``..``-containing relative
            # plan path that EXISTS relative to the process cwd prefers the
            # cwd interpretation over repo-root re-rooting (root/../plans
            # does not exist and would false-reject).
            plan, _ = write_clean_state()
            rc, out, err = run_cli(Path("..") / "plans" / plan.name)
            check(
                "selftest#cli/cwd_relative_dotdot",
                rc == 0 and "readiness OK" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )

            # tilde_facts (W10, r3): tilde-valued facts keys expand against
            # HOME (pointed at the temp root here), user-absolute regardless
            # of cwd.
            tilde_plans = root / "tilde-plans"
            tilde_reviews = root / "tilde-reviews"
            tilde_plans.mkdir()
            tilde_reviews.mkdir()
            tplan = tilde_plans / "2026-09-01-tilde-feature.md"
            tplan.write_text("# tilde plan\n\nBody.\n", encoding="utf-8")
            tdigest = vrs.compute_source_digest("plan", tplan.read_bytes())
            treview = tilde_reviews / (
                "2026-09-01-plan-review-tilde-feature-r1.md"
            )
            treview.write_text(_review_markdown(), encoding="utf-8")
            treview.with_suffix(".stats.json").write_text(
                json.dumps(_clear_sidecar(tdigest)), encoding="utf-8"
            )
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "~/tilde-plans"\n'
                'reviews_dir = "~/tilde-reviews"\n'
                "```\n",
                encoding="utf-8",
            )
            prev_home = os.environ.get("HOME")
            os.environ["HOME"] = str(root)
            try:
                rc, out, err = run_cli(tplan)
                check(
                    "selftest#cli/tilde_facts",
                    rc == 0 and "readiness OK" in out,
                    f"rc={rc} out={out!r} err={err!r}",
                )
            finally:
                if prev_home is None:
                    del os.environ["HOME"]
                else:
                    os.environ["HOME"] = prev_home

            # --sweep fixtures (r5 Y2/Y7): anomaly detection, clean pass,
            # CLI plumbing, missing reviews_dir, and plan_path rejection.
            os.chdir(root)
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "plans"\n'
                'reviews_dir = "reviews"\n'
                "```\n",
                encoding="utf-8",
            )
            for path in reviews_dir.iterdir():
                path.unlink()
            # (a) anomaly: Summary's ready= is split across two lines — the
            # sweep mention fires, the per-line total rule finds no token.
            write_clean_state(verdict_line="- ready=\nyes")
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/anomaly_split_ready_returns_1",
                rc == 1
                and "sweep FAILED" in out
                and "2026-09-01-plan-review-fixture-feature-r1.md" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()
            # (b) clean: a plain ready=yes review sweeps to 0.
            write_clean_state()
            rc_sweep = run_sweep(reviews_dir)
            check(
                "selftest#sweep/clean_returns_0",
                rc_sweep == 0,
                f"rc={rc_sweep}",
            )
            # (c) CLI plumbing: main(["--sweep"]) exit 0 with the OK line.
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/main_cli_plumbing",
                rc == 0 and "sweep OK" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            # (c2) r6 Z3: an anomalous *-code-review-*.md file in the sweep
            # tree is NOT swept (glob scoping is plan-review-only); the
            # clean plan-review state still sweeps to 0.
            code_review = reviews_dir / (
                "2026-09-01-code-review-fixture-feature-r1.md"
            )
            code_review.write_text(
                "## Summary\n\n- ready=\nyes\n", encoding="utf-8"
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/code_review_files_not_flagged",
                rc == 0 and "sweep OK" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            # (c3) r6 Z3: an unreadable (non-UTF-8) plan-review artifact in
            # the sweep tree is an anomaly naming the file, rc 1.
            unreadable = reviews_dir / (
                "2026-09-01-plan-review-unreadable-feature-r1.md"
            )
            unreadable.write_bytes(b"# review \xff\xfe binary\n")
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/unreadable_artifact_returns_1",
                rc == 1
                and "sweep FAILED" in out
                and "2026-09-01-plan-review-unreadable-feature-r1.md" in out
                and "unreadable" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            unreadable.unlink()
            # (c4) r6 Z3: mention-vs-token breadth — a Summary line whose
            # ready= mention is NOT a word-bounded token (``Notready=yes``)
            # or carries no yes/no value (``- Blocking findings: ready=``)
            # is an anomaly: the broad mention fires, the token rule cannot.
            breadth = reviews_dir / (
                "2026-09-01-plan-review-breadth-feature-r1.md"
            )
            breadth.write_text(
                "## Summary\n\nVerdict: Notready=yes\n", encoding="utf-8"
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/mention_vs_token_notready",
                rc == 1
                and "sweep FAILED" in out
                and "2026-09-01-plan-review-breadth-feature-r1.md" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            breadth.write_text(
                "## Summary\n\n- Blocking findings: ready=\n", encoding="utf-8"
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/mention_vs_token_no_value",
                rc == 1
                and "sweep FAILED" in out
                and "2026-09-01-plan-review-breadth-feature-r1.md" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            breadth.unlink()
            code_review.unlink()
            # (c5) r6 Z3: a facts.md WITHOUT a reviews_dir key cannot run
            # the sweep at all; rc 1 with the named resolution reason.
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\nplans_dir = \"plans\"\n```\n",
                encoding="utf-8",
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/facts_without_reviews_dir",
                rc == 1 and "cannot resolve reviews_dir" in err,
                f"rc={rc} out={out!r} err={err!r}",
            )
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "plans"\n'
                'reviews_dir = "reviews"\n'
                "```\n",
                encoding="utf-8",
            )
            # (d) r5 Y7: configured reviews_dir missing on disk → exit 1
            # with its OWN reason (never a silent zero-artifact pass).
            reviews_dir.rename(root / "reviews-gone")
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/missing_reviews_dir_returns_1",
                rc == 1 and "does not exist on disk" in err,
                f"rc={rc} out={out!r} err={err!r}",
            )
            (root / "reviews-gone").rename(reviews_dir)
            # (e) r5 Y7: plan_path combined with --sweep is a usage error.
            plan, _ = write_clean_state()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    main(["--sweep", str(plan)])
                except SystemExit as exc:
                    usage_rc = exc.code
                else:
                    usage_rc = 0
            check(
                "selftest#sweep/plan_path_rejected",
                usage_rc == 2 and "must not be combined" in err.getvalue(),
                f"usage_rc={usage_rc} err={err.getvalue()!r}",
            )
            # (f) Task 4: coverage counter over a mixed corpus — one clean
            # artifact whose sidecar lacks the field, one (at a DISTINCT
            # date-prefixed path) whose sidecar carries "verdict": "yes" —
            # prints 1/2; rc 0.
            for path in reviews_dir.iterdir():
                path.unlink()
            write_clean_state()
            _, review_dated = write_clean_state(date="2026-09-02")
            dated_sidecar = review_dated.with_suffix(".stats.json")
            dated_payload = json.loads(
                dated_sidecar.read_text(encoding="utf-8")
            )
            dated_payload["verdict"] = "yes"
            dated_sidecar.write_text(
                json.dumps(dated_payload), encoding="utf-8"
            )
            # r1 F1: third artifact at a distinct date whose sidecar carries a
            # legacy NON-CONFORMING dict verdict; presence is NOT coverage;
            # only the conforming "yes" arm counts, so coverage stays 1/3.
            _, review_legacy = write_clean_state(date="2026-09-03")
            legacy_sidecar = review_legacy.with_suffix(".stats.json")
            legacy_payload = json.loads(
                legacy_sidecar.read_text(encoding="utf-8")
            )
            legacy_payload["verdict"] = {"ready": False}
            legacy_sidecar.write_text(
                json.dumps(legacy_payload), encoding="utf-8"
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/coverage_mixed_corpus",
                rc == 0 and "sweep coverage: 1/3" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()
            # (f2) Task 4: a malformed sidecar (not JSON) counts as NOT
            # covered and is NOT an anomaly; 0/2, rc 0, no crash.
            write_clean_state()
            malformed_review = reviews_dir / (
                "2026-09-02-plan-review-fixture-feature-r1.md"
            )
            malformed_review.write_text(
                "# Plan Review\n\n## Summary\n\n- ready=yes\n",
                encoding="utf-8",
            )
            malformed_review.with_suffix(".stats.json").write_text(
                "not json", encoding="utf-8"
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/coverage_malformed_sidecar_uncovered",
                rc == 0 and "sweep coverage: 0/2" in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            for path in reviews_dir.iterdir():
                path.unlink()
            # (f3) Task 4 (r1 F3 fold): a facts file whose reviews_dir points
            # at a missing directory fails with its OWN error and prints NO
            # coverage line (the early return precedes the glob).
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "plans"\n'
                'reviews_dir = "reviews-absent"\n'
                "```\n",
                encoding="utf-8",
            )
            rc, out, err = run_main(["--sweep"])
            check(
                "selftest#sweep/coverage_absent_on_missing_reviews_dir",
                rc == 1
                and "sweep FAILED" in err
                and "sweep coverage:" not in out,
                f"rc={rc} out={out!r} err={err!r}",
            )
            (facts_dir / "facts.md").write_text(
                "# facts\n\n```toml\n"
                'plans_dir = "plans"\n'
                'reviews_dir = "reviews"\n'
                "```\n",
                encoding="utf-8",
            )
            for path in reviews_dir.iterdir():
                path.unlink()
        finally:
            os.chdir(prev_cwd)

    print()
    if failures:
        print(f"SOME FAIL ({failures})")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
