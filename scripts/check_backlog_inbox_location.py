#!/usr/bin/env python3
"""Reject backlog-inbox filename shapes outside the resolved backlog home.

Filename-only gate (content is never inspected), case-insensitive on the
basename:

- rule 1: basename contains ``backlog`` OR ``deferred`` AND the path is under
  one of the named hot dirs (``docs/maintenance/``, ``docs/architecture/``,
  ``docs/tmp/``); scanned over a FILESYSTEM walk so untracked and gitignored
  files are seen. Intentional precedence: rule 1 fires BEFORE the backlog-home
  exclusion, so named hot dirs gate regardless of facts state, including when
  a configured backlog home sits under a hot dir.
- rule 2: basename contains BOTH ``backlog`` AND ``deferred`` AND the path is
  outside the backlog home; scanned over tracked files (``git ls-files -z``).

Backlog home resolves from ``.ai-playbook/facts.md`` TOML keys
``backlog_dir`` / ``backlog_completed_dir`` with fallback defaults and a
stderr warning when missing. Two ``docs/tmp/`` carve-outs (path-segment
boundaries / basename prefix only) keep this repo's own conventions green.

Exit 0 when clean, 1 when any violation (each printed as ``<path>: rule <N>``).
The default scan root anchors at the git toplevel of the current directory
and warns on stderr before falling back to the CWD when git is unavailable.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import facts_paths
except ImportError:  # pragma: no cover
    facts_paths = None  # type: ignore

HOT_DIRS = ("docs/maintenance", "docs/architecture", "docs/tmp")
# Derived once so classify_path cannot drift from HOT_DIRS (single source).
HOT_DIR_PARTS = tuple(tuple(h.split("/")) for h in HOT_DIRS)
DEFAULT_BACKLOG_DIR = "docs/history/backlog"
DEFAULT_BACKLOG_COMPLETED_DIR = "docs/history/backlog/completed"
TOKENS = ("backlog", "deferred")


def resolve_backlog_home(repo_root: Path) -> tuple[Path, Path]:
    """Resolve (backlog_dir, backlog_completed_dir) from repo facts TOML.

    Missing, blank, or degenerate (``.`` or any ``..``-prefixed relpath, i.e.
    at or above the repo root) values fall back to the documented defaults
    with a warning on stderr; such a home would make ``is_relative_to`` match
    every path (or escape the repo) and silently disable rule 2. Values are anchored at ``repo_root`` (raw resolution, so
    a repo-relative value is never anchored against the process CWD).
    """
    resolved: list[Path] = []
    if facts_paths is None:
        print(
            "warning: facts parser unavailable (facts_paths.py not "
            "importable); using default backlog home",
            file=sys.stderr,
        )
    for key, default in (
        ("backlog_dir", DEFAULT_BACKLOG_DIR),
        ("backlog_completed_dir", DEFAULT_BACKLOG_COMPLETED_DIR),
    ):
        home: Path | None = None
        raw = (
            facts_paths.resolve_toml_key_raw(repo_root, key)
            if facts_paths is not None
            else None
        )
        if raw is not None and not raw.strip():
            print(
                f"warning: {key} present but empty in "
                f".ai-playbook/facts.md; falling back to {default}",
                file=sys.stderr,
            )
        elif raw is not None:
            p = Path(raw).expanduser()
            home = p if p.is_absolute() else repo_root / p
            rel = os.path.relpath(home, repo_root)
            if rel == "." or rel.startswith(".."):
                print(
                    f"warning: {key} resolves to {rel} of the repo root; "
                    f"falling back to {default}",
                    file=sys.stderr,
                )
                home = None
        if home is None:
            if raw is None and facts_paths is not None:
                print(
                    f"warning: {key} missing from .ai-playbook/facts.md; "
                    f"falling back to {default}",
                    file=sys.stderr,
                )
            home = repo_root / default
        resolved.append(home)
    return resolved[0], resolved[1]


def _tmp_carve_out(path: Path) -> bool:
    """docs/tmp/ carve-outs, segment boundaries / basename prefix only.

    - any path segment below ``docs/tmp`` equal to ``execute-plan`` (session
      log trees named after plan slugs; segment boundary, so
      ``docs/tmp/execute-plan-sibling/`` is NOT covered);
    - basename prefix ``plan-requirements-`` (plans-skill requirements
      buffers; prefix-only, so a directory named
      ``plan-requirements-fake`` does not carve anything out).
    """
    if path.parts[:2] != ("docs", "tmp"):
        return False
    if "execute-plan" in path.parts[2:]:
        return True
    # Lowered so the prefix test matches the case-insensitive token match
    # above (an uppercase-variant buffer is carved out, never flagged).
    return path.name.lower().startswith("plan-requirements-")


def classify_path(rel_path: str, backlog_home: tuple[Path, Path]) -> int | None:
    """Return the fired rule number (1 or 2) for a repo-relative path.

    Only the file BASENAME is token-matched (case-insensitively); directory
    names never fire. Hot-dir membership and the backlog home are matched on
    path-segment boundaries. ``backlog_home`` entries must be repo-RELATIVE
    paths (see scan_repo), so ``is_relative_to`` compares like-for-like parts.
    """
    path = Path(os.path.normpath(rel_path))
    basename = path.name.lower()
    has_backlog = "backlog" in basename
    has_deferred = "deferred" in basename
    if not has_backlog and not has_deferred:
        return None
    under_hot = path.parts[:2] in HOT_DIR_PARTS
    if under_hot:
        if _tmp_carve_out(path):
            return None
        return 1  # hot dir + either token
    if has_backlog and has_deferred:
        if any(path.is_relative_to(home) for home in backlog_home):
            return None
        return 2  # token pair outside the backlog home
    return None


def scan_repo(repo_root: Path) -> list[tuple[str, int]]:
    """Scan both surfaces; return sorted (relative-path, rule) violations."""
    repo_root = repo_root.resolve()
    backlog_home = tuple(
        Path(os.path.relpath(home.resolve(), repo_root))
        for home in resolve_backlog_home(repo_root)
    )
    violations: dict[str, int] = {}

    # Rule 1: filesystem walk of the hot dirs (untracked files included;
    # absent dirs tolerated).
    for hot in HOT_DIRS:
        hot_path = repo_root / hot
        if not hot_path.is_dir():
            continue
        for dirpath, _dirnames, filenames in os.walk(hot_path):
            for filename in filenames:
                absolute = Path(dirpath) / filename
                rel = os.path.relpath(absolute, repo_root)
                rule = classify_path(rel, backlog_home)
                if rule is not None:
                    violations.setdefault(rel, rule)

    # Rule 2: tracked files only.
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        ).stdout
    except OSError as exc:
        # git absent: fail open with a warning; the rule-1 hot-dir walk
        # still covers the incident shape.
        print(f"warning: git ls-files unavailable; rule 2 skipped: {exc}", file=sys.stderr)
        out = b""
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", "surrogateescape") if exc.stderr else str(exc)
        if "not a git repository" in detail:
            # A non-repo directory is a legitimate scan target (rule-1 walk
            # only); same fail-open treatment as git being absent.
            print(
                f"warning: {repo_root} is not a git repo; rule 2 skipped",
                file=sys.stderr,
            )
            out = b""
        else:
            # git exists yet refused (index.lock, corrupt repo): fail closed
            # so a transient git failure cannot silently skip the
            # tracked-tree scan.
            print(f"error: git ls-files failed: {detail}", file=sys.stderr)
            # Report already-collected violations before aborting so the
            # fail-closed exit does not swallow the rule-1 walk's findings.
            for rel, rule in sorted(violations.items()):
                print(f"{rel}: rule {rule}")
            sys.exit(1)
    for raw in out.split(b"\0"):
        if not raw:
            continue
        rel = os.path.normpath(raw.decode("utf-8", "surrogateescape"))
        rule = classify_path(rel, backlog_home)
        if rule is not None:
            violations.setdefault(rel, rule)

    return sorted(violations.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reject backlog-inbox filename shapes outside the backlog home"
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to scan (default: git toplevel of the "
        "current directory, falling back to the current directory when "
        "git is unavailable)",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run fixture checks and exit",
    )
    args = parser.parse_args(argv)

    if args.selftest:
        return run_selftest()

    if args.repo_root is not None:
        repo_root = Path(args.repo_root).expanduser().resolve()
    else:
        # Anchor the default scan surface at the git toplevel, not the CWD,
        # so a subdirectory invocation cannot silently shrink the scan to
        # its own subtree. Fail open to the CWD when git is absent or fails.
        try:
            out = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            repo_root = Path(out).resolve()
        except (OSError, subprocess.SubprocessError):
            print(
                "warning: git rev-parse unavailable; scanning CWD",
                file=sys.stderr,
            )
            repo_root = Path.cwd().resolve()
    violations = scan_repo(repo_root)
    for rel, rule in violations:
        print(f"{rel}: rule {rule}")
    if violations:
        print(
            f"check_backlog_inbox_location: {len(violations)} violation(s)",
            file=sys.stderr,
        )
        return 1
    print("check_backlog_inbox_location: ok")
    return 0


# --------------------------------------------------------------------------- #
# Selftest
# --------------------------------------------------------------------------- #

_CHECK_FAILURES = [0]


def _make_check():
    def check(condition: bool, label: str) -> None:
        if not condition:
            _CHECK_FAILURES[0] += 1
            print(f"selftest FAIL: {label}", file=sys.stderr)

    return check


def _write(root: Path, rel: str, content: str = "fixture\n") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _clean_git_env() -> dict[str, str]:
    """Env copy without ambient GIT_* redirections (GIT_DIR/GIT_WORK_TREE/
    GIT_INDEX_FILE/GIT_COMMON_DIR, GIT_CONFIG_COUNT + GIT_CONFIG_KEY_*/
    GIT_CONFIG_VALUE_* config injection, GIT_OBJECT_DIRECTORY, and
    GIT_ALTERNATE_OBJECT_DIRECTORIES) so fixture repos are isolated from
    whatever the invoking machine exported."""
    _exact = {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_COMMON_DIR",
        "GIT_CONFIG_COUNT",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    }
    _prefixes = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
    return {
        k: v
        for k, v in os.environ.items()
        if k not in _exact and not k.startswith(_prefixes)
    }


def _git(root: Path, *git_args: str) -> None:
    # Pin ambient-config inputs beyond identity: no signing, no global hooks,
    # so machines with commit.gpgsign=true or a core.hooksPath cannot make
    # the selftest fail for unrelated reasons.
    subprocess.run(
        ["git", "-c", "user.email=selftest@example.invalid",
         "-c", "user.name=selftest",
         "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null",
         "-c", "core.excludesFile=/dev/null", *git_args],
        cwd=root,
        check=True,
        capture_output=True,
        env=_clean_git_env(),
    )


def _run_script(
    root: Path,
    *,
    bare: bool = False,
    cwd: Path | None = None,
    env_extra: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    env = _clean_git_env()
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, str(Path(__file__).resolve())]
    if not bare:
        cmd += ["--repo-root", str(root)]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd is not None else None,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _selftest_main_repo(root: Path, check) -> None:
    """Synthetic git repo: violation + allowed fixtures, facts present."""
    repo = root / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")

    # facts with backlog keys (committed so the resolution path is exercised).
    _write(
        repo,
        ".ai-playbook/facts.md",
        "```toml\n"
        'backlog_dir = "docs/history/backlog/"\n'
        'backlog_completed_dir = "docs/history/backlog/completed/"\n'
        "```\n",
    )

    # Rule-1 hot-dir violations (filesystem walk; tracked or not).
    _write(repo, "docs/maintenance/TT-123-deferred-backlog.md")
    _write(repo, "docs/tmp/round-2-backlog-notes.md")
    _write(repo, "docs/architecture/deferred-queue-design.md")
    _write(repo, "docs/maintenance/sub/sub-deferred-backlog.md")
    # Uppercase token: case-insensitive basename match.
    _write(repo, "docs/architecture/BACKLOG-notes.md")

    # Rule-2 violation (both tokens outside the backlog home); committed.
    _write(repo, "docs/plans/2026-09-03-x-deferred-backlog.md")

    # Carve-out discriminators under docs/tmp that MUST FAIL:
    # segment boundary (execute-plan-sibling is not execute-plan) and
    # carve-opt-out (plan-requirements- is a BASENAME prefix, never a
    # substring anywhere in the path).
    _write(repo, "docs/tmp/execute-plan-sibling/evil-backlog.md")
    _write(repo, "docs/tmp/notes/plan-requirements-fake/evil-backlog.md")

    # Allowed fixtures. The pair-token files inside the home guard the
    # rule-2 backlog-home exclusion: removing the exclusion (or breaking it,
    # e.g. absolute-vs-relative parts comparison) fails these assertions.
    _write(repo, "docs/history/backlog/2026-09-03-anything.md")
    _write(repo, "docs/history/backlog/2026-09-03-pair-deferred-backlog-ok.md")
    _write(repo, "docs/history/backlog/completed/2026-08-28-fence-scanner-family.md")
    _write(repo, "docs/history/backlog/completed/2026-08-28-pair-deferred-backlog-ok.md")
    _write(repo, "docs/maintenance/confluence-sync-manifest.json")
    # Asymmetry (intentional): a single token outside every hot dir and
    # without the second token is allowed by rule 2 (``backlog`` absent);
    # only the token PAIR fires outside the hot dirs.
    _write(repo, "docs/reviews/x-deferred.md")

    # Carve-out allowed fixtures under docs/tmp: the requirements-buffer
    # basename prefix with a backlog slug, and a session-log tree named after
    # a plan slug whose file BASENAME itself contains the token (a token-free
    # basename would pass even without the carve-out, since directory names
    # never fire).
    _write(repo, "docs/tmp/plan-requirements-2026-09-03-backlog-gate.md")
    # Uppercase variant: guards the case-insensitive carve-out prefix
    # (removing ``.lower()`` from the prefix test fails this fixture).
    _write(repo, "docs/tmp/PLAN-REQUIREMENTS-2026-09-03-BACKLOG-gate.md")
    _write(
        repo,
        "docs/tmp/execute-plan/2026-09-03-backlog-location-gate/"
        "task-1-backlog-log.md",
    )

    # Single commit with explicit identity so no ambient git config is
    # needed; every rule-2 fixture is committed for `git ls-files` to see.
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")

    # UNTRACKED gitignored violation inside a hot dir: created after the
    # commit and never added, proving the rule-1 filesystem walk sees
    # shadow-tree files a tracked-only scan would miss.
    _write(repo, ".gitignore", "docs/maintenance/untracked-deferred-inbox.md\n")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-q", "-m", "gitignore")
    _write(repo, "docs/maintenance/untracked-deferred-inbox.md")

    expected = {
        "docs/maintenance/TT-123-deferred-backlog.md": 1,
        "docs/tmp/round-2-backlog-notes.md": 1,
        "docs/architecture/deferred-queue-design.md": 1,
        "docs/maintenance/sub/sub-deferred-backlog.md": 1,
        "docs/architecture/BACKLOG-notes.md": 1,
        "docs/plans/2026-09-03-x-deferred-backlog.md": 2,
        "docs/tmp/execute-plan-sibling/evil-backlog.md": 1,
        "docs/tmp/notes/plan-requirements-fake/evil-backlog.md": 1,
        "docs/maintenance/untracked-deferred-inbox.md": 1,
    }
    allowed = [
        "docs/history/backlog/2026-09-03-anything.md",
        "docs/history/backlog/2026-09-03-pair-deferred-backlog-ok.md",
        "docs/history/backlog/completed/2026-08-28-fence-scanner-family.md",
        "docs/history/backlog/completed/2026-08-28-pair-deferred-backlog-ok.md",
        "docs/maintenance/confluence-sync-manifest.json",
        "docs/reviews/x-deferred.md",
        "docs/tmp/plan-requirements-2026-09-03-backlog-gate.md",
        "docs/tmp/PLAN-REQUIREMENTS-2026-09-03-BACKLOG-gate.md",
        "docs/tmp/execute-plan/2026-09-03-backlog-location-gate/task-1-backlog-log.md",
    ]

    code, stdout, stderr = _run_script(repo)
    check(code == 1, f"main repo: expected exit 1, got {code} (stderr: {stderr})")
    reported: dict[str, int] = {}
    for line in stdout.splitlines():
        if ": rule " in line:
            path, _, rule = line.rpartition(": rule ")
            reported[path] = int(rule)
    check(
        reported == expected,
        f"main repo: reported violations {reported} != expected {expected}",
    )
    for path in allowed:
        check(path not in reported, f"main repo: allowed fixture flagged: {path}")

    # Fail-closed branch: git present but refusing (corrupt index). Note a
    # stale .git/index.lock does NOT drive this branch — `git ls-files` is
    # read-only and never takes the index lock — so the fixture corrupts the
    # index bytes instead. The gate must abort (exit 1) with the
    # 'git ls-files failed' error, not fail open. try/finally restores the
    # index so a failed check cannot corrupt later fixtures.
    index = repo / ".git" / "index"
    backup = index.read_bytes()
    index.write_bytes(b"corrupt\n")
    try:
        code, _stdout, stderr = _run_script(repo)
        check(
            code == 1,
            f"main repo (corrupt index): expected exit 1, got {code} (stderr: {stderr})",
        )
        check(
            "git ls-files failed" in stderr,
            f"main repo (corrupt index): fail-closed error missing (stderr: {stderr!r})",
        )
        # F7: already-collected rule-1 violations must still be printed
        # before the fail-closed exit, not swallowed by the git error.
        check(
            "docs/maintenance/TT-123-deferred-backlog.md: rule 1" in _stdout,
            "main repo (corrupt index): collected violations dropped on "
            f"fail-closed exit (stdout: {_stdout!r})",
        )
    finally:
        index.write_bytes(backup)


def _selftest_factsless_repo(root: Path, check) -> None:
    """Facts-less variant: fallback backlog home with a stderr warning."""
    repo = root / "factsless"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(repo, "docs/plans/fallback-deferred-backlog.md")
    # Both tokens inside the FALLBACK home: guards the exclusion on the
    # default-home resolution path (no facts keys).
    _write(repo, "docs/history/backlog/fallback-ok-deferred-backlog.md")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")

    code, stdout, stderr = _run_script(repo)
    check(code == 1, f"factsless repo: expected exit 1, got {code}")
    check(
        "docs/plans/fallback-deferred-backlog.md: rule 2" in stdout,
        f"factsless repo: rule-2 fallback violation missing (stdout: {stdout!r})",
    )
    check(
        "docs/history/backlog/fallback-ok-deferred-backlog.md" not in stdout,
        "factsless repo: fallback backlog-home fixture flagged",
    )
    check(
        "falling back" in stderr,
        f"factsless repo: fallback warning missing on stderr (stderr: {stderr!r})",
    )


def _selftest_blank_key_repo(root: Path, check) -> None:
    """Blank ``backlog_dir`` value must NOT disable the rule-2 exclusion.

    A present-but-empty key previously anchored the home at the repo root
    itself, making ``is_relative_to`` match every path (silent rule-2
    bypass). It must instead warn and fall back to the default home, so a
    committed both-token violation outside that home still fails.
    """
    repo = root / "blankkey"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(
        repo,
        ".ai-playbook/facts.md",
        "```toml\n"
        'backlog_dir = ""\n'
        'backlog_completed_dir = "docs/history/backlog/completed/"\n'
        "```\n",
    )
    _write(repo, "docs/plans/blank-key-deferred-backlog.md")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")

    code, stdout, stderr = _run_script(repo)
    check(code == 1, f"blank-key repo: expected exit 1, got {code} (stdout: {stdout!r})")
    check(
        "docs/plans/blank-key-deferred-backlog.md: rule 2" in stdout,
        f"blank-key repo: rule-2 violation missing (stdout: {stdout!r})",
    )
    check(
        "present but empty" in stderr,
        f"blank-key repo: empty-key warning missing (stderr: {stderr!r})",
    )


def _selftest_degenerate_home_repo(root: Path, check) -> None:
    """Degenerate ``..`` home (F5): warn + default, rule 2 still fires.

    Also guards the widened above-root arm (F2) via the shared helper below
    with an escaping ``../..`` value: without the ``rel.startswith("..")``
    guard the rule-2 exclusion dies and the committed pair-token violation
    is silently allowed.
    """

    def run_case(name: str, backlog_value: str) -> None:
        repo = root / name
        repo.mkdir()
        _git(repo, "init", "-q")
        _write(
            repo,
            ".ai-playbook/facts.md",
            "```toml\n"
            f'backlog_dir = "{backlog_value}"\n'
            'backlog_completed_dir = "docs/history/backlog/completed/"\n'
            "```\n",
        )
        _write(repo, "docs/plans/degenerate-deferred-backlog.md")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "init")

        code, stdout, stderr = _run_script(repo)
        check(code == 1, f"{name}: expected exit 1, got {code} (stdout: {stdout!r})")
        check(
            "docs/plans/degenerate-deferred-backlog.md: rule 2" in stdout,
            f"{name}: rule-2 violation missing (stdout: {stdout!r})",
        )
        check(
            "of the repo root" in stderr and "falling back" in stderr,
            f"{name}: degenerate-home warning missing (stderr: {stderr!r})",
        )

    run_case("dotdot", "..")
    run_case("aboveroot", "../..")
    run_case("dot", ".")


def _selftest_hot_dir_home_repo(root: Path, check) -> None:
    """Backlog home under a hot dir (F6): rule 1 precedence witness.

    Documented precedence says rule 1 fires BEFORE the backlog-home
    exclusion; a configured home inside ``docs/tmp`` must not exempt a
    token-named file there.
    """
    repo = root / "hotdirhome"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(
        repo,
        ".ai-playbook/facts.md",
        "```toml\n"
        'backlog_dir = "docs/tmp/backlog"\n'
        'backlog_completed_dir = "docs/history/backlog/completed/"\n'
        "```\n",
    )
    _write(repo, "docs/tmp/backlog/pair-deferred-backlog.md")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")

    code, stdout, stderr = _run_script(repo)
    check(code == 1, f"hot-dir home: expected exit 1, got {code} (stdout: {stdout!r})")
    check(
        "docs/tmp/backlog/pair-deferred-backlog.md: rule 1" in stdout,
        f"hot-dir home: rule-1 precedence violation missing (stdout: {stdout!r})",
    )


def _selftest_toplevel_anchor_repo(root: Path, check) -> None:
    """Bare invocation from a subdirectory (F3): toplevel anchoring.

    Run with cwd INSIDE the fixture repo (``<repo>/docs``) and no
    ``--repo-root``; a violation outside that subdirectory must still be
    reported. A regression to CWD-anchoring (``Path.cwd()``) shrinks the
    scan to ``docs/`` and misses the top-level pair-token file.
    """
    repo = root / "anchored"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(repo, "docs/placeholder.md")
    _write(repo, "plans/toplevel-deferred-backlog.md")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")

    code, stdout, _stderr = _run_script(repo, bare=True, cwd=repo / "docs")
    check(code == 1, f"toplevel anchor: expected exit 1, got {code} (stdout: {stdout!r})")
    check(
        "plans/toplevel-deferred-backlog.md: rule 2" in stdout,
        "toplevel anchor: violation outside the cwd subtree missing "
        f"(stdout: {stdout!r})",
    )


def _selftest_git_absent_repo(root: Path, check) -> None:
    """PATH stripped of git (F8): fail-open warnings + rule-1-only scan.

    Bare invocation with cwd at the fixture repo and PATH pointing at an
    empty directory: both git probes fail with OSError, so the run must
    warn for rev-parse and ls-files and still report the rule-1 hot-dir
    violation (exit 1), exercising the CWD-fallback warning of the
    default-root resolution.
    """
    repo = root / "gitabsent"
    repo.mkdir()
    empty_bin = root / "emptybin"
    empty_bin.mkdir()
    _write(repo, "docs/maintenance/untracked-backlog-inbox.md")

    code, stdout, stderr = _run_script(
        repo, bare=True, cwd=repo, env_extra={"PATH": str(empty_bin)}
    )
    check(code == 1, f"git absent: expected exit 1, got {code} (stdout: {stdout!r})")
    check(
        "docs/maintenance/untracked-backlog-inbox.md: rule 1" in stdout,
        f"git absent: rule-1 violation missing (stdout: {stdout!r})",
    )
    check(
        "git rev-parse unavailable; scanning CWD" in stderr,
        f"git absent: rev-parse fallback warning missing (stderr: {stderr!r})",
    )
    check(
        "git ls-files unavailable" in stderr,
        f"git absent: ls-files fail-open warning missing (stderr: {stderr!r})",
    )


def _selftest_clean_tree(root: Path, check) -> None:
    """Clean tree (allowed fixtures only, no git): exit 0."""
    clean = root / "clean"
    _write(clean, "docs/history/backlog/2026-09-03-clean.md")
    _write(clean, "docs/maintenance/confluence-sync-manifest.json")
    _write(clean, "docs/reviews/x-deferred.md")
    _write(clean, "docs/tmp/plan-requirements-2026-09-03-backlog-gate.md")
    code, _stdout, stderr = _run_script(clean)
    check(code == 0, f"clean tree: expected exit 0, got {code}")
    check(
        "rule 2 skipped" in stderr,
        f"clean tree: 'rule 2 skipped' warning missing (stderr: {stderr!r})",
    )


def run_selftest() -> int:
    import tempfile

    _CHECK_FAILURES[0] = 0
    check = _make_check()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for _name, fn in (
            ("main_repo", _selftest_main_repo),
            ("factsless_repo", _selftest_factsless_repo),
            ("blank_key_repo", _selftest_blank_key_repo),
            ("degenerate_home_repo", _selftest_degenerate_home_repo),
            ("hot_dir_home_repo", _selftest_hot_dir_home_repo),
            ("toplevel_anchor_repo", _selftest_toplevel_anchor_repo),
            ("git_absent_repo", _selftest_git_absent_repo),
            ("clean_tree", _selftest_clean_tree),
        ):
            fn(root, check)

    if _CHECK_FAILURES[0]:
        print(
            f"check_backlog_inbox_location: --selftest FAILED "
            f"({_CHECK_FAILURES[0]})",
            file=sys.stderr,
        )
        return 1
    print("check_backlog_inbox_location: --selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
