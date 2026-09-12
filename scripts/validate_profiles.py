#!/usr/bin/env python3
"""Validate Hermes profile metadata, manifests, and skill wiring.

Checks semantic drift that plain `yaml.safe_load` misses:
- duplicate YAML keys
- profile.yaml structure and declared skills present in the shared skill pool
- distribution.yaml: present, parseable, name matches the profile dir
- NO symlinks anywhere under profiles/ (native or Git mode-120000 text blobs)
- materialized skill copies match the shared pool exactly (delegates to sync_skills)
- skill-feedback Issue Form is a .yml form whose fields match the
  skill_feedback schema in scripts/validate_skill_feedback.py
- version lock: profile content changes require a distribution.yaml version
  bump (scripts/version_lock.json, maintained via --bump-lock)

Why no symlinks: `hermes profile install` hard-rejects symlinked payloads, and
Windows checkouts with core.symlinks=false degrade links to text files. Skill
sharing is done by committing real copies, materialized via sync_skills.py.

Windows note: use `python` (or `py -3`) instead of `python3`, and run from the
repository root. Both interpreters are fine on macOS/Linux CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_skills  # noqa: E402

# Schema single source for the skill-feedback Issue Form check.
import validate_skill_feedback as sfb  # noqa: E402

# stdout may be a GBK console on Windows hosts; force UTF-8 so the check/cross
# marks below never raise UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    if _stream and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

NL = chr(10)
LF_BYTES = bytes([10])
CRLF_BYTES = bytes([13, 10])

# Registry of published distribution versions. Key: "<profile>:<content hash>",
# value: the version the payload was published under. Content changes must come
# with a version bump so `hermes profile update` consumers can detect them;
# the lock turns forgetting that into a validation error instead of silent
# drift. Maintained via: python scripts/validate_profiles.py --bump-lock <p>.
VERSION_LOCK_PATH = Path(__file__).resolve().parent / "version_lock.json"


def _manifest_version(profile_dir: Path) -> str:
    try:
        return str(load_yaml(profile_dir / "distribution.yaml").get("version") or "").strip()
    except ValueError:
        return "?"


def _content_hash(profile_dir: Path) -> Optional[str]:
    """Stable digest over the committable content of one profile directory.

    Covers exactly what Git would commit (`ls-files --cached --others
    --exclude-standard`), so local runtime state and secrets never affect the
    hash. Line endings are normalized (Windows autocrlf) and the manifest's
    own `version:` line is excluded — bumping the version must not change the
    hash, otherwise the lock could never be satisfied after a bump.
    Returns None when Git is unavailable (check silently skipped).
    """
    root = profile_dir.parent.parent
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--",
         profile_dir.as_posix()],
        cwd=root, check=False, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    rels = sorted(ln.replace(chr(92), "/") for ln in result.stdout.splitlines() if ln.strip())
    if not rels:
        return None
    digest = hashlib.sha256()
    for rel in rels:
        path = root / rel
        digest.update(rel.encode("utf-8"))
        data = path.read_bytes()
        if path.name == "distribution.yaml":
            data = LF_BYTES.join(
                ln for ln in data.split(LF_BYTES) if not ln.startswith(b"version:")
            )
        digest.update(data.replace(CRLF_BYTES, LF_BYTES))
    return digest.hexdigest()


def _load_version_lock() -> dict[str, str]:
    if VERSION_LOCK_PATH.is_file():
        try:
            data = json.loads(VERSION_LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def profile_dir_by_name(name: str, profile_dirs: list[Path]) -> Path:
    for profile_dir in profile_dirs:
        if profile_dir.name == name:
            return profile_dir
    raise KeyError(name)


def check_version_lock(
    profile_dirs: list[Path], errors: list[str], bump: str | None = None
) -> None:
    """Profiles whose content hash is not in the lock must bump their version.

    First run on an unlocked repo bootstraps silently (records current hashes).
    `--bump-lock PROFILE` re-records one profile after a version bump,
    `--bump-lock all` re-records every profile whose version was already
    bumped (the common case: a shared-pool change touches many profiles at
    once). Both refuse to re-lock changed content under an unchanged version.
    """
    pre_existing_errors = len(errors)  # version-lock errors must not block re-locking
    lock = _load_version_lock()
    relock_all = bump == "all"
    by_name: dict[str, list[str]] = {}
    for key in lock:
        name, _, digest = key.partition(":")
        by_name.setdefault(name, []).append(digest)

    target: Optional[Path] = None
    if bump is not None and bump != "all":
        try:
            target = profile_dir_by_name(bump, profile_dirs)
        except KeyError:
            errors.append(f"--bump-lock: no such profile {bump!r}")
            return

    # Never record state that OTHER checks already flag; version-lock drift
    # errors themselves must not block re-locking (that is the whole point of
    # --bump-lock), so only compare against pre-existing error counts.
    can_write = len(errors) == pre_existing_errors
    dirty = False
    for profile_dir in profile_dirs:
        name = profile_dir.name
        if name == bump:
            continue  # single-profile mode: handled below
        digest = _content_hash(profile_dir)
        if digest is None:
            continue  # git unavailable — skip silently
        hashes = by_name.get(name, [])
        current = _manifest_version(profile_dir)
        if not hashes:
            if can_write:
                lock[f"{name}:{digest}"] = current
                dirty = True
            continue
        if digest in hashes:
            continue  # content unchanged — locked entry already correct
        locked_versions = {lock[f"{name}:{h}"] for h in hashes if f"{name}:{h}" in lock}
        if current not in locked_versions:
            # Version WAS bumped for this content change — safe to re-lock.
            if relock_all and can_write:
                for h in hashes:
                    lock.pop(f"{name}:{h}", None)
                lock[f"{name}:{digest}"] = current
                dirty = True
            else:
                errors.append(
                    f"profiles/{name}: version bumped to {current!r} (locked: "
                    f"{sorted(locked_versions)}) but the new content hash is not yet "
                    f"recorded — run: python scripts/validate_profiles.py --bump-lock {name}"
                )
        else:
            errors.append(
                f"profiles/{name}: content changed since the version-locked hash, but "
                f"distribution.yaml version is still {current!r} — "
                f"bump the version, then run: "
                f"python scripts/validate_profiles.py --bump-lock {name}"
            )

    if bump is not None and target is not None:
        if not can_write:
            errors.append("--bump-lock: fix the other validation errors first")
            return
        digest = _content_hash(target)
        if digest is None:
            errors.append(f"--bump-lock: cannot hash {bump!r} (git unavailable)")
            return
        old = {k: v for k, v in lock.items() if k.startswith(f"{bump}:")}
        new_version = _manifest_version(target)
        if old and f"{bump}:{digest}" not in old and all(v == new_version for v in old.values()):
            errors.append(
                f"profiles/{bump}: content changed but version is still {new_version!r} — "
                "bump distribution.yaml before running --bump-lock"
            )
            return
        for key in list(old):
            del lock[key]
        lock[f"{bump}:{digest}"] = new_version
        dirty = True

    if dirty:
        VERSION_LOCK_PATH.write_text(
            json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False) + NL,
            encoding="utf-8",
        )


def check_issue_form(root: Path, errors: list[str]) -> None:
    """skill-feedback Issue Form must be a .yml form whose fields match the
    skill_feedback schema (names, required-ness, type enum). GitHub only
    parses Issue Forms from .yml/.yaml templates — a .md template with a form
    body silently renders as raw YAML instead of a fillable form."""
    template_dir = root / ".github" / "ISSUE_TEMPLATE"
    if not template_dir.is_dir():
        return

    sfb_yaml = template_dir / "skill-feedback.yml"
    if not sfb_yaml.is_file():
        errors.append(
            ".github/ISSUE_TEMPLATE/skill-feedback.yml: missing — GitHub only parses "
            "Issue Forms from .yml/.yaml files, so the fillable form cannot live in "
            "a .md template"
        )
        return
    try:
        form = load_yaml(sfb_yaml)
    except ValueError as exc:
        errors.append(str(exc).replace(str(root) + os.sep, ""))
        return

    body = form.get("body")
    if not isinstance(body, list):
        errors.append(f"{sfb_yaml.relative_to(root)}: Issue Form `body` must be a list")
        return

    fields: dict[str, tuple[bool, Optional[list[str]]]] = {}
    for block in body:
        if not isinstance(block, dict):
            continue
        fid = block.get("id")
        if not isinstance(fid, str):
            continue
        required = bool(
            isinstance(block.get("validations"), dict)
            and block["validations"].get("required") is True
        )
        options: Optional[list[str]] = None
        if block.get("type") == "dropdown":
            raw_options = (block.get("attributes") or {}).get("options")
            if raw_options:
                options = [
                    str(o.get("label") or o.get("value") or "") if isinstance(o, dict) else str(o)
                    for o in raw_options
                ]
        fields[fid] = (required, options)

    expected: dict[str, tuple[bool, Optional[list[str]]]] = {
        "skill": (True, None),
        "type": (True, list(sfb.ALLOWED_TYPES)),
        "scenario": (True, None),
        "problem": (True, None),
        "proposal": (True, None),
        "evidence": (True, None),
    }
    for fid, (want_required, want_options) in expected.items():
        got = fields.get(fid)
        if got is None:
            errors.append(
                f"{sfb_yaml.relative_to(root)}: missing form field {fid!r} — keep it in "
                f"sync with the skill_feedback schema in scripts/validate_skill_feedback.py"
            )
            continue
        if got[0] != want_required:
            errors.append(
                f"{sfb_yaml.relative_to(root)}: field {fid!r} required={got[0]}, "
                f"schema says required={want_required}"
            )
        elif want_options is not None and got[1] is not None:
            got_labels = [o.split("（")[0].split(" (")[0].strip() for o in got[1]]
            if got_labels != want_options:
                errors.append(
                    f"{sfb_yaml.relative_to(root)}: field {fid!r} options {got_labels} != "
                    f"schema enum {want_options} (scripts/validate_skill_feedback.py)"
                )


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
    if not text.startswith("---" + NL):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find(NL + "---" + NL, 4)
    if end == -1:
        raise ValueError(f"{path}: frontmatter is not closed with ---")
    body = text[end + 5:].strip()
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
        metadata, separator, path = line.partition(chr(9))
        if separator and metadata.split(maxsplit=1)[0] == "120000":
            links.add(path.replace(chr(92), "/"))
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


def check_compat_matrix(root: Path, profile_dirs: list[Path], errors: list[str]) -> None:
    """Cross-check docs/compatibility-matrix.md against each distribution.yaml.

    The matrix is the human-maintained source of truth for tested Hermes
    versions; the manifest `hermes_requires` is what the installer enforces.
    They must agree: every profile row must exist and carry the same
    hermes_requires spec as its manifest."""
    matrix_path = root / "docs" / "compatibility-matrix.md"
    if not matrix_path.is_file():
        errors.append("docs/compatibility-matrix.md: missing — maintainer compatibility matrix required")
        return
    text = matrix_path.read_text(encoding="utf-8")
    import re as _re

    rows: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        m = _re.match(
            r"^\|\s*([a-z][a-z0-9-]*)\s*\|\s*([\d.]+)\s*\|\s*`([^`]*)`\s*\|", line
        )
        if m:
            rows[m.group(1)] = (m.group(2), m.group(3))
    if not rows:
        errors.append("docs/compatibility-matrix.md: no profile rows parsed — check table format")
        return
    for profile_dir in profile_dirs:
        name = profile_dir.name
        manifest_path = profile_dir / "distribution.yaml"
        try:
            manifest = load_yaml(manifest_path)
        except ValueError:
            continue  # already reported by the manifest check above
        spec = str(manifest.get("hermes_requires") or "").strip()
        version = str(manifest.get("version") or "").strip()
        row = rows.get(name)
        if row is None:
            errors.append(
                f"docs/compatibility-matrix.md: missing row for profile {name!r} — "
                "add it with the same hermes_requires as its manifest"
            )
        else:
            row_version, row_spec = row
            if row_spec != spec:
                errors.append(
                    f"docs/compatibility-matrix.md: hermes_requires for {name!r} is {row_spec!r} "
                    f"but manifest says {spec!r} — keep them in sync"
                )
            if row_version != version:
                errors.append(
                    f"docs/compatibility-matrix.md: 当前版本 for {name!r} is {row_version!r} "
                    f"but manifest says {version!r} — update the matrix row when bumping versions"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--bump-lock",
        metavar="PROFILE|all",
        default=None,
        help="re-record content hash + version in scripts/version_lock.json after a "
        "version bump — one profile, or 'all' for every already-bumped profile",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    profiles_dir = root / "profiles"
    skills_dir = root / "skills"
    errors: list[str] = []

    try:
        git_symlinks = tracked_symlinks(root)
    except ValueError as exc:
        print(f"Profile validation failed:{NL}- {exc}", file=sys.stderr)
        return 1
    if git_symlinks:
        for rel in sorted(git_symlinks):
            errors.append(
                f"{rel}: Git-tracked symlink — payloads must be real files "
                "(run `python scripts/sync_skills.py` — `python3` on macOS/Linux — "
                "and commit the copies)"
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

    # Compatibility matrix agrees with each manifest's hermes_requires.
    check_compat_matrix(root, profile_dirs, errors)

    # skill-feedback Issue Form matches the payload schema.
    check_issue_form(root, errors)

    # Content changes require a distribution version bump.
    check_version_lock(profile_dirs, errors, bump=args.bump_lock)

    if errors:
        print("Profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Profile validation passed: {len(profile_dirs)} profiles, "
        f"{len(shared_skill_names)} shared skills; issue-form + version-lock checks OK."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
