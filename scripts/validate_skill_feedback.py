#!/usr/bin/env python3
"""Validate skill_feedback entries (the skill-reflection loop payload).

The loop itself is manual (see skills/skill-feedback-loop/SKILL.md), so the
machine-checkable part is the payload format. This script validates one or
more YAML files, each containing a single `skill_feedback` mapping (or a list
of them) as written into a Kanban task comment:

    skill_feedback:
      skill: <skill-name>                  # must exist in the shared pool
      file: <optional file reference>
      type: missing | wrong | improvement | systemic
      scenario: <one line: task + context>
      problem: <what is missing/wrong/suboptimal>
      proposal: <rule change, PR-ready>
      evidence: <task id + handoff fields>

Checks:
- schema: required fields present, non-empty strings
- type: must be one of the allowed enum values
- skill: must exist in the shared skill pool (unless --no-pool-check)
- duplicates: across all given files, (skill, file, normalized problem) must
  not repeat — the same feedback must not be submitted twice

Usage:
    python3 scripts/validate_skill_feedback.py feedback1.yaml [feedback2.yaml ...]
    cat feedback.yaml | python3 scripts/validate_skill_feedback.py -

Exit code 0 = all entries valid and unique; 1 = validation errors.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # GBK consoles
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_POOL = REPO_ROOT / "skills"

# Single source of truth for the skill_feedback schema. validate_profiles.py
# imports this to keep the GitHub Issue Form template in sync with it.
REQUIRED_FIELDS = ("skill", "type", "scenario", "problem", "proposal", "evidence")
OPTIONAL_FIELDS = ("file",)
ALLOWED_TYPES = ("missing", "wrong", "improvement", "systemic")


def pool_skill_names() -> set[str]:
    """Names of skills present in the shared pool (flat + one legacy sublevel)."""
    names: set[str] = set()
    if not SKILLS_POOL.is_dir():
        return names
    for skill_md in SKILLS_POOL.rglob("SKILL.md"):
        names.add(skill_md.parent.name)
    return names


def _normalize(text: str) -> str:
    """Collapse whitespace for duplicate fingerprinting."""
    return re.sub(r"\s+", " ", text).strip().lower()


def fingerprint(entry: dict[str, Any]) -> str:
    basis = "|".join(
        _normalize(str(entry.get(field, "")))
        for field in ("skill", "file", "problem")
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def validate_entry(
    entry: Any,
    source: str,
    pool: set[str] | None,
    errors: list[str],
) -> dict[str, Any] | None:
    """Validate one skill_feedback mapping; append problems to *errors*."""
    if not isinstance(entry, dict):
        errors.append(f"{source}: entry must be a YAML mapping, got {type(entry).__name__}")
        return None

    valid = True
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{source}: missing or empty required field {field!r}")
            valid = False

    ftype = entry.get("type")
    if isinstance(ftype, str) and ftype.strip() and ftype.strip() not in ALLOWED_TYPES:
        errors.append(
            f"{source}: type {ftype!r} not in {list(ALLOWED_TYPES)}"
        )
        valid = False

    ffile = entry.get("file")
    if ffile is not None and not isinstance(ffile, str):
        errors.append(f"{source}: optional field 'file' must be a string")
        valid = False

    skill = entry.get("skill")
    if isinstance(skill, str) and pool is not None and skill.strip() and skill.strip() not in pool:
        errors.append(
            f"{source}: skill {skill!r} not found in shared pool {SKILLS_POOL} "
            "(typo, or the skill has not been added yet — use --no-pool-check to bypass)"
        )
        valid = False

    return entry if valid else None


def load_entries(path: Path, errors: list[str]) -> list[tuple[str, dict[str, Any]]]:
    """Load skill_feedback entries from one YAML file (mapping or list)."""
    source = str(path)
    try:
        text = sys.stdin.read() if source == "-" else path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
    except Exception as exc:  # noqa: BLE001 - CLI validator reports path + failure
        errors.append(f"{source}: unreadable/invalid YAML: {exc}")
        return []

    raw_entries: list[Any]
    if isinstance(data, dict) and set(data.keys()) == {"skill_feedback"}:
        raw_entries = data["skill_feedback"] if isinstance(data["skill_feedback"], list) else [data["skill_feedback"]]
    elif isinstance(data, list):
        raw_entries = data
    else:
        errors.append(
            f"{source}: expected a `skill_feedback:` mapping (or a list of them), "
            f"got {type(data).__name__}"
        )
        return []

    pool = pool_skill_names()
    entries: list[tuple[str, dict[str, Any]]] = []
    for idx, raw in enumerate(raw_entries, start=1):
        label = f"{source}#{idx}" if len(raw_entries) > 1 else source
        entry = validate_entry(raw, label, pool, errors)
        if entry is not None:
            entries.append((label, entry))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="YAML file(s), or - for stdin")
    parser.add_argument(
        "--no-pool-check",
        action="store_true",
        help="skip checking that `skill` exists in the shared pool",
    )
    args = parser.parse_args()

    errors: list[str] = []
    all_entries: list[tuple[str, dict[str, Any]]] = []
    seen: dict[str, str] = {}

    for name in args.files:
        path = Path(name)
        all_entries.extend(load_entries(path, errors))

    for label, entry in all_entries:
        fp = fingerprint(entry)
        if fp in seen:
            errors.append(
                f"{label}: duplicate of feedback in {seen[fp]} "
                "(same skill + file + problem already submitted)"
            )
        else:
            seen[fp] = label

    if errors:
        print(f"✗ skill_feedback validation failed ({len(errors)} problem(s)):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"✓ {len(all_entries)} skill_feedback entr{'y' if len(all_entries) == 1 else 'ies'} valid and unique")
    return 0


if __name__ == "__main__":
    sys.exit(main())
