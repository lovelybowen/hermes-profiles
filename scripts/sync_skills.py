#!/usr/bin/env python3
"""Materialize per-profile skill copies from the shared skill pool.

The repo keeps ONE authoritative copy of every skill under ``skills/``. Each
profile under ``profiles/<role>/`` declares its dependencies in
``profile.yaml`` (``skills.required``). This script copies each declared
skill into ``profiles/<role>/skills/<name>/`` as REAL files.

Why real files instead of symlinks: the Hermes distribution installer
(``hermes profile install``) hard-rejects symlinks anywhere in the payload,
and Windows clones with ``core.symlinks=false`` degrade symlinks into plain
text files containing the target path — both break installation.

Usage:
    python3 scripts/sync_skills.py            # materialize all profiles
    python3 scripts/sync_skills.py --check    # verify copies match the pool (CI)
    python3 scripts/sync_skills.py orchestrator   # one profile only
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_POOL = REPO_ROOT / "skills"
PROFILES_DIR = REPO_ROOT / "profiles"
PLUGINS_POOL = REPO_ROOT / "plugins"

# Profile -> extra top-level dirs to materialize from the shared pools.
# Keys are profile names; values map destination dir name -> source pool dir.
# (Currently only orchestrator bundles a plugin; plugin.yaml references are
# resolved at runtime relative to the profile's own plugins/ dir.)
PROFILE_EXTRA_COPIES: dict[str, dict[str, Path]] = {
    "orchestrator": {"plugins": PLUGINS_POOL},
}


def find_skill_source(name: str) -> Optional[Path]:
    """Locate the authoritative copy of skill *name* in the shared pool.

    The pool has one flat level (``skills/<name>/``) plus one legacy category
    sublevel (``skills/architecture/<name>/``).
    """
    direct = SKILLS_POOL / name
    if (direct / "SKILL.md").is_file():
        return direct
    for child in sorted(SKILLS_POOL.iterdir()):
        if child.is_dir():
            candidate = child / name
            if (candidate / "SKILL.md").is_file():
                return candidate
    return None


def declared_skills(profile_dir: Path) -> list[str]:
    meta = profile_dir / "profile.yaml"
    if not meta.is_file():
        return []
    data = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
    skills = ((data.get("skills") or {}).get("required")) or []
    return [str(s) for s in skills]


def _remove_existing(path: Path) -> None:
    """Remove a materialized copy, a symlink, OR a Windows-degraded text file
    (a clone with core.symlinks=false turns a mode-120000 blob into a regular
    file whose content is the link target)."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _same_content(fa: Path, fb: Path) -> bool:
    """Compare file contents, ignoring CRLF/LF differences.

    Windows checkouts with core.autocrlf=true renormalize line endings
    on checkout, so a byte-exact compare reports false diffs between a
    pool file and a faithfully copied materialized copy."""
    try:
        a = fa.read_bytes()
        b = fb.read_bytes()
    except OSError:
        return False
    if a == b:
        return True
    crlf = b"\r\n"
    return a.replace(crlf, b"\n") == b.replace(crlf, b"\n")


def trees_equal(a: Path, b: Path) -> bool:
    """Deep compare two directory trees (names + file contents)."""
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files or cmp.common_funny:
        return False
    if any(not _same_content(a / f, b / f) for f in cmp.diff_files):
        return False
    return all(trees_equal(a / sub, b / sub) for sub in cmp.common_dirs)


def sync_profile(profile_dir: Path, check_only: bool = False) -> list[str]:
    """Materialize (or verify) one profile's skill copies. Returns problems."""
    problems: list[str] = []
    role = profile_dir.name
    skills_root = profile_dir / "skills"
    skills_root.mkdir(exist_ok=True)

    wanted = declared_skills(profile_dir)
    if not wanted:
        problems.append(f"{role}: profile.yaml declares no skills.required")
        return problems

    # 1. Every declared skill exists in the pool and is materialized.
    for name in wanted:
        src = find_skill_source(name)
        if src is None:
            problems.append(f"{role}: declared skill '{name}' not found in shared pool {SKILLS_POOL}")
            continue
        dst = skills_root / name
        if check_only:
            if dst.is_symlink():
                problems.append(f"{role}: {dst.relative_to(REPO_ROOT)} is a symlink — run sync_skills.py")
            elif not dst.is_dir():
                problems.append(f"{role}: missing materialized copy of '{name}' — run sync_skills.py")
            elif not trees_equal(src, dst):
                problems.append(f"{role}: copy of '{name}' differs from pool — run sync_skills.py")
        else:
            _remove_existing(dst)
            shutil.copytree(src, dst)

    # 2. No undeclared leftovers (stale copies or old symlinks/text files).
    declared = set(wanted)
    for entry in sorted(skills_root.iterdir()):
        if entry.name.startswith("."):
            continue  # runtime state (.hub, .usage.json, ...) — gitignored
        if entry.name not in declared:
            rel = entry.relative_to(REPO_ROOT)
            if check_only:
                problems.append(f"{role}: undeclared skill copy {rel} — remove it or declare it")
            else:
                _remove_existing(entry)

    # 3. Extra top-level copies (plugins etc.).
    for dest_name, pool in PROFILE_EXTRA_COPIES.get(role, {}).items():
        dst_root = profile_dir / dest_name
        if not pool.is_dir():
            problems.append(f"{role}: extra copy source {pool} does not exist")
            continue
        for src in sorted(pool.iterdir()):
            if not src.is_dir():
                continue
            dst = dst_root / src.name
            if check_only:
                if dst.is_symlink():
                    problems.append(f"{role}: {dst.relative_to(REPO_ROOT)} is a symlink — run sync_skills.py")
                elif not dst.is_dir():
                    problems.append(f"{role}: missing {dst.relative_to(REPO_ROOT)} — run sync_skills.py")
                elif not trees_equal(src, dst):
                    problems.append(f"{role}: copy {dst.relative_to(REPO_ROOT)} differs from pool")
            else:
                dst_root.mkdir(exist_ok=True)
                _remove_existing(dst)
                shutil.copytree(src, dst)

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("profile", nargs="?", help="limit to one profile (default: all)")
    ap.add_argument("--check", action="store_true",
                    help="verify materialized copies match the pool; exit 1 on drift")
    args = ap.parse_args()

    if not SKILLS_POOL.is_dir():
        print(f"error: shared skill pool not found at {SKILLS_POOL}", file=sys.stderr)
        return 2

    profiles = sorted(p for p in PROFILES_DIR.iterdir() if p.is_dir())
    if args.profile:
        profiles = [PROFILES_DIR / args.profile]
        if not profiles[0].is_dir():
            print(f"error: no such profile: {args.profile}", file=sys.stderr)
            return 2

    problems: list[str] = []
    for profile_dir in profiles:
        problems += sync_profile(profile_dir, check_only=args.check)

    if args.check:
        if problems:
            print(f"✗ {len(problems)} problem(s):")
            for p in problems:
                print(f"  - {p}")
            return 1
        print(f"✓ all {len(profiles)} profile(s) match the shared skill pool")
        return 0

    if problems:
        print(f"✗ sync failed with {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"✓ materialized skill copies for {len(profiles)} profile(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
