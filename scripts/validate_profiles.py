#!/usr/bin/env python3
"""Validate Hermes profile metadata and skill wiring.

This intentionally checks semantic drift that plain `yaml.safe_load` misses:
- duplicate YAML keys
- profile.yaml structure
- declared skills that do not exist in the shared skill pool
- declared skills that are not reachable through the profile's skills/ symlinks
- invalid shared-skill frontmatter
- broken or absolute symlinks
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


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


def relative_key(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def link_target(path: Path, root: Path, git_symlinks: set[str]) -> str | None:
    """Read a native symlink or Git's text checkout used when core.symlinks=false."""
    if path.is_symlink():
        return os.readlink(path)
    if relative_key(path, root) in git_symlinks and path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return None


def profile_skill_entries(skill_dir: Path, root: Path, git_symlinks: set[str]) -> list[Path]:
    """Find profile skill links, including links nested under a real category directory."""
    entries: list[Path] = []
    for entry in skill_dir.iterdir():
        if link_target(entry, root, git_symlinks) is not None:
            entries.append(entry)
        elif entry.is_dir():
            entries.extend(profile_skill_entries(entry, root, git_symlinks))
        else:
            entries.append(entry)
    return entries


def skill_names_under(path: Path) -> set[str]:
    """Return skill names reachable under a skill root.

    pathlib's rglob does not reliably traverse symlinked directories on every
    platform, so profiles are handled by resolving each skill entry first.
    Category directories such as `architecture/` expose their nested SKILL.md
    names but are not themselves counted as skills.
    """
    names: set[str] = set()
    if not path.exists():
        return names

    roots: list[Path]
    if path.name == "skills":
        roots = [entry.resolve() for entry in path.iterdir() if entry.is_dir()]
    else:
        roots = [path.resolve()]

    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for skill_md in root.rglob("SKILL.md"):
            try:
                fm = extract_frontmatter(skill_md)
            except ValueError:
                # Let shared-skill validation report the detailed error.
                names.add(skill_md.parent.name)
                continue
            names.add(str(fm.get("name") or skill_md.parent.name))
    return names


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


def reachable_profile_skills(profile_dir: Path, root: Path, git_symlinks: set[str]) -> set[str]:
    skill_dir = profile_dir / "skills"
    if not skill_dir.exists():
        return set()
    names: set[str] = set()
    for entry in profile_skill_entries(skill_dir, root, git_symlinks):
        target = link_target(entry, root, git_symlinks)
        if target is None or os.path.isabs(target):
            continue
        resolved = (entry.parent / target).resolve()
        if resolved.is_dir():
            names.update(skill_names_under(resolved))
    return names


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

    shared_skills = skill_names_under(skills_dir)

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

    for profile_dir in sorted(p for p in profiles_dir.iterdir() if p.is_dir()):
        rel = profile_dir.relative_to(root)
        for required_file in ("SOUL.md", "profile.yaml", "README.md", "AGENTS.md"):
            if not (profile_dir / required_file).is_file():
                errors.append(f"{rel}: missing {required_file}")

        profile_yaml_path = profile_dir / "profile.yaml"
        if not profile_yaml_path.exists():
            continue
        try:
            data = load_yaml(profile_yaml_path)
            declared = declared_skills(data, profile_yaml_path.relative_to(root))
        except ValueError as exc:
            errors.append(str(exc).replace(str(root) + os.sep, ""))
            continue

        missing_from_repo = sorted(declared - shared_skills)
        if missing_from_repo:
            errors.append(
                f"{profile_yaml_path.relative_to(root)}: declares skills not present in shared pool: "
                + ", ".join(missing_from_repo)
            )

        reachable = reachable_profile_skills(profile_dir, root, git_symlinks)
        missing_from_profile = sorted(declared - reachable)
        if missing_from_profile:
            errors.append(
                f"{profile_yaml_path.relative_to(root)}: declares skills not reachable from profile skills/: "
                + ", ".join(missing_from_profile)
            )

    for profile_dir in sorted(p for p in profiles_dir.iterdir() if p.is_dir()):
        skill_dir = profile_dir / "skills"
        if not skill_dir.exists():
            continue
        for link in profile_skill_entries(skill_dir, root, git_symlinks):
            target = link_target(link, root, git_symlinks)
            if target is None:
                errors.append(f"{link.relative_to(root)}: expected a Git symbolic link")
                continue
            if os.path.isabs(target):
                errors.append(f"{link.relative_to(root)}: symlink target is absolute: {target}")
            if not (link.parent / target).exists():
                errors.append(f"{link.relative_to(root)}: broken symlink -> {target}")

    if errors:
        print("Profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Profile validation passed: {len(list(profiles_dir.iterdir()))} profiles, "
        f"{len(shared_skills)} shared skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
