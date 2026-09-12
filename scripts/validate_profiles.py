#!/usr/bin/env python3
"""Validate Hermes profile metadata, manifests, and skill wiring.

Checks semantic drift that plain `yaml.safe_load` misses:
- duplicate YAML keys
- profile.yaml structure and declared skills present in the shared skill pool
- distribution.yaml: present, parseable, name matches the profile dir
- NO symlinks anywhere under profiles/ (native or Git mode-120000 text blobs)
- materialized skill copies match the shared pool exactly (delegates to sync_skills)

Why no symlinks: `hermes profile install` hard-rejects symlinked payloads, and
Windows checkouts with core.symlinks=false degrade links to text files. Skill
sharing is done by committing real copies, materialized via sync_skills.py.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_skills  # noqa: E402


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def construct_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate key {key!r} at line {key_node.start_mark.line + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        # UniqueKeyLoader subclasses yaml.SafeLoader; yaml.load is used here only
        # to reject duplicate keys while preserving safe construction semantics.
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except Exception as exc:  # noqa: BLE001 - CLI validator should report path + failure
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping, got {type(data).__name__}")
    return data


def extract_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: frontmatter is not closed with ---")
    body = text[end + 5 :].strip()
    if not body:
        raise ValueError(f"{path}: missing body content")
    try:
        # UniqueKeyLoader subclasses yaml.SafeLoader; yaml.load is used here only
        # to reject duplicate keys while preserving safe construction semantics.
        fm = yaml.load(text[4:end], Loader=UniqueKeyLoader)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{path}: invalid frontmatter YAML: {exc}") from exc
    if not isinstance(fm, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return fm


def tracked_symlinks(root: Path) -> set[str]:
    """Return repository-relative paths tracked by Git as symbolic links."""
    result = subprocess.run(
        ["git", "ls-files", "--stage", "--", "profiles"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(f"unable to inspect Git symlink modes: {result.stderr.strip()}")

    links: set[str] = set()
    for line in result.stdout.splitlines():
        metadata, separator, path = line.partition("\t")
        if separator and metadata.split(maxsplit=1)[0] == "120000":
            links.add(path.replace("\\", "/"))
    return links


def declared_skills(profile_yaml: dict[str, Any], profile_path: Path) -> set[str]:
    skills = profile_yaml.get("skills")
    if not isinstance(skills, dict):
        raise ValueError(f"{profile_path}: `skills` must be a mapping")
    declared: set[str] = set()
    for bucket in ("required", "recommended"):
        values = skills.get(bucket, [])
        if values is None:
            continue
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ValueError(f"{profile_path}: `skills.{bucket}` must be a list of strings")
        declared.update(values)
    return declared


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    profiles_dir = root / "profiles"
    skills_dir = root / "skills"
    errors: list[str] = []

    try:
        git_symlinks = tracked_symlinks(root)
    except ValueError as exc:
        print(f"Profile validation failed:\n- {exc}", file=sys.stderr)
        return 1
    if git_symlinks:
        for rel in sorted(git_symlinks):
            errors.append(
                f"{rel}: Git-tracked symlink — payloads must be real files "
                "(run `python3 scripts/sync_skills.py` and commit the copies)"
            )

    shared_skill_names = {p.parent.name for p in skills_dir.rglob("SKILL.md")}

    # Shared skill frontmatter must be valid Hermes-style skill metadata.
    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        try:
            fm = extract_frontmatter(skill_md)
            name = fm.get("name")
            description = fm.get("description")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{skill_md.relative_to(root)}: missing non-empty frontmatter `name`")
            if not isinstance(description, str) or not description.strip():
                errors.append(f"{skill_md.relative_to(root)}: missing non-empty frontmatter `description`")
            elif len(description) > 1024:
                errors.append(f"{skill_md.relative_to(root)}: `description` exceeds 1024 characters")
        except ValueError as exc:
            errors.append(str(exc).replace(str(root) + os.sep, ""))

    profile_dirs = sorted(p for p in profiles_dir.iterdir() if p.is_dir())
    for profile_dir in profile_dirs:
        rel = profile_dir.relative_to(root)
        for required_file in ("SOUL.md", "profile.yaml", "README.md", "AGENTS.md", "distribution.yaml"):
            if not (profile_dir / required_file).is_file():
                errors.append(f"{rel}: missing {required_file}")

        # distribution.yaml: parseable, name == dir, env entries well-formed.
        manifest_path = profile_dir / "distribution.yaml"
        if manifest_path.is_file():
            try:
                manifest = load_yaml(manifest_path)
                mname = str(manifest.get("name") or "").strip()
                if not mname:
                    errors.append(f"{manifest_path.relative_to(root)}: missing 'name'")
                elif mname != profile_dir.name:
                    errors.append(
                        f"{manifest_path.relative_to(root)}: name {mname!r} != directory "
                        f"{profile_dir.name!r} (kanban routing relies on exact profile names)"
                    )
                env = manifest.get("env_requires") or []
                if not isinstance(env, list):
                    errors.append(f"{manifest_path.relative_to(root)}: env_requires must be a list")
                else:
                    for entry in env:
                        if not isinstance(entry, dict) or not str(entry.get("name") or "").strip():
                            errors.append(f"{manifest_path.relative_to(root)}: env_requires entry missing 'name'")
            except ValueError as exc:
                errors.append(str(exc).replace(str(root) + os.sep, ""))

        # profile.yaml structure + declared skills exist in the shared pool.
        profile_yaml_path = profile_dir / "profile.yaml"
        if profile_yaml_path.exists():
            try:
                data = load_yaml(profile_yaml_path)
                declared = declared_skills(data, profile_yaml_path.relative_to(root))
            except ValueError as exc:
                errors.append(str(exc).replace(str(root) + os.sep, ""))
            else:
                missing_from_repo = sorted(declared - shared_skill_names)
                if missing_from_repo:
                    errors.append(
                        f"{profile_yaml_path.relative_to(root)}: declares skills not present in shared pool: "
                        + ", ".join(missing_from_repo)
                    )

        # Native symlinks (not yet committed, or committed from a symlink-capable host).
        for p in profile_dir.rglob("*"):
            if p.is_symlink():
                errors.append(f"{p.relative_to(root)}: symlink — payloads must be real files")

    # Materialized copies match the pool (delegates the deep tree comparison).
    for profile_dir in profile_dirs:
        errors += sync_skills.sync_profile(profile_dir, check_only=True)

    if errors:
        print("Profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Profile validation passed: {len(profile_dirs)} profiles, "
        f"{len(shared_skill_names)} shared skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
