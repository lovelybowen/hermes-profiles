#!/usr/bin/env python3
"""Mechanical intake signals for evidence-level routing.

Computes the machine-checkable part of the upgrade triggers defined in
``artifact-pyramids/references/evidence-levels-and-seb.md`` §1.3:

  - number of changed files
  - added/deleted line counts
  - whether dependency manifests / lockfiles are touched
  - whether any changed path matches a high-risk path pattern
  - a suggested evidence level (advisory only)

This is an AUXILIARY signal source for the orchestrator's intake decision.
It does not classify business risk and it does not implement any runtime
gate. Per ``references/intake-fast-path.md`` §3: adopt the mechanical
output (counts, paths), but the business-risk judgement stays with the
orchestrator.

Usage:
    python intake_signals.py --repo <path>                     # uncommitted vs HEAD
    python intake_signals.py --repo <path> --baseline <rev>    # committed range
    python intake_signals.py --repo <path> --baseline <rev> --head <rev>

Output: single JSON object on stdout (exit 0). Errors exit non-zero with a
message on stderr.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Files whose changes imply "new/updated dependency" (upgrade trigger: >= L1+L2).
DEPENDENCY_FILE_RE = re.compile(
    r"(^|/)(package\.json|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|"
    r"pyproject\.toml|requirements\.txt|poetry\.lock|Pipfile|Pipfile\.lock|"
    r"Gemfile|Gemfile\.lock|go\.mod|go\.sum|Cargo\.toml|Cargo\.lock|"
    r"pom\.xml|build\.gradle|build\.gradle\.kts|build\.sbt|mix\.exs|mix\.lock|"
    r"composer\.json|composer\.lock)$"
)

# Path patterns aligned with the high-risk list in gate-topology.md §2 (T5/T6
# triggers) and §8 escalation conditions. A hit forces exit from the fast
# path; the orchestrator then applies full rules.
HIGH_RISK_PATH_RE = re.compile(
    r"\.github/workflows/|(^|/)\.gitlab-ci|(^|/)Jenkinsfile$"
    r"|(^|/)migrations?/|(^|/)db/migrate/|(^|/)db/schema\.rb|flyway|liquibase"
    r"|(^|/)(auth|authorization|permission|rbac|acl)s?/"
    r"|(^|/)(openid|oauth|saml|jwt)(/|\.)"
    r"|(^|/)(billing|payment|invoice|charge)s?/"
    r"|(^|/)api/(v\d+/)?public/|(^|/)openapi|(^|/)swagger"
    r"|(^|/)\.env|secrets?\.(yaml|yml|json|toml)$|(^|/)credentials?"
    r"|(^|/)pii/|(^|/)privacy/|(^|/)gdpr/|(^|/)hipaa/"
)

# Lines-per-file threshold for L0 (single file, <=30 lines, no deps).
L0_MAX_FILES = 1
L0_MAX_LINES = 30
L1_MAX_LINES = 200


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def changed_entries(repo: Path, baseline: str | None, head: str | None) -> list[dict]:
    """Return [{path, add, del, status}] for the requested diff range."""
    if baseline:
        base = _git(repo, "rev-parse", "--verify", f"{baseline}^{{commit}}")
        tip = _git(repo, "rev-parse", "--verify", f"{(head or 'HEAD')}^{{commit}}")
        name_status = _git(repo, "diff", "--name-status", base.strip(), tip.strip())
        numstat = _git(repo, "diff", "--numstat", base.strip(), tip.strip())
    else:
        # uncommitted: worktree + index vs HEAD, unified
        name_status = _git(repo, "status", "--porcelain=v1")
        numstat = _git(repo, "diff", "HEAD", "--numstat")

    statuses: dict[str, str] = {}
    for line in name_status.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        st, path = parts[0].strip(), parts[1].strip().strip('"')
        if " -> " in path:  # rename target
            path = path.split(" -> ")[-1]
        statuses[path] = st

    entries: list[dict] = []
    for line in numstat.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_s, del_s, path = parts[0], parts[1], parts[2].strip().strip('"')
        add = int(add_s) if add_s.isdigit() else 0  # binary files show "-"
        del_ = int(del_s) if del_s.isdigit() else 0
        entries.append(
            {
                "path": path,
                "add": add,
                "del": del_,
                "status": statuses.get(path, "M"),
            }
        )
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="project repo path")
    ap.add_argument("--baseline", default=None, help="baseline rev (default: HEAD, i.e. uncommitted)")
    ap.add_argument("--head", default=None, help="head rev for committed ranges (default: HEAD)")
    ap.add_argument(
        "--max-files", type=int, default=L0_MAX_FILES, help="L0 max file count"
    )
    ap.add_argument(
        "--max-lines", type=int, default=L0_MAX_LINES, help="L0 max changed lines"
    )
    args = ap.parse_args()

    repo = Path(args.repo)
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git repo: {repo}")

    entries = changed_entries(repo, args.baseline, args.head)
    files = [e["path"] for e in entries]
    total_lines = sum(e["add"] + e["del"] for e in entries)
    dep_hits = [p for p in files if DEPENDENCY_FILE_RE.search(p)]
    risk_hits = [p for p in files if HIGH_RISK_PATH_RE.search(p)]

    # Advisory level per evidence-levels-and-seb.md §1.3
    if risk_hits:
        suggested = "Full-review"  # high-risk list hit: exit fast path, orchestrator judges T5/T6
    elif dep_hits:
        suggested = "L1+L2"
    elif len(files) == 0:
        suggested = "L0"
    elif len(files) <= args.max_files and total_lines <= args.max_lines:
        suggested = "L0"
    elif total_lines <= L1_MAX_LINES:
        suggested = "L1"
    else:
        suggested = "L1+L2"

    payload = {
        "schema_version": 1,
        "repo": str(repo),
        "baseline": args.baseline or "HEAD (uncommitted)",
        "changed_files": len(files),
        "added_lines": sum(e["add"] for e in entries),
        "deleted_lines": sum(e["del"] for e in entries),
        "total_changed_lines": total_lines,
        "files": entries,
        "dependency_files_touched": dep_hits,
        "high_risk_paths": risk_hits,
        "fast_path_eligible": not dep_hits and not risk_hits and len(files) <= args.max_files and total_lines <= args.max_lines,
        "suggested_evidence_level": suggested,
        "advisory_only": True,
        "notes": "mechanical signals only; business risk and final gate/evidence_level stay with orchestrator intake",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
