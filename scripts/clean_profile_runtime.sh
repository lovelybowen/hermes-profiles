#!/usr/bin/env bash
# Remove Hermes runtime state that lands inside profile dirs of this repository.
#
# Why this exists: Hermes probes "<profile>/skills" with rglob("SKILL.md"); Python's
# rglob does NOT follow symlinked directories, so a profile whose skills are all
# relative symlinks is misread as "unseeded" and Hermes repair-seeds bundled skills
# into it on every launch. See CONTRIBUTING.md -> "运行时状态".
#
# This is the "thorough" edition: it also physically removes every runtime
# artifact Hermes writes under profiles/ (state DBs, caches, logs, sessions,
# memories, evidence DBs, etc.) so the repo can be shipped with only
# non-runtime content. It deliberately PRESERVES:
#   - every symlink (profiles/*/skills/* is the only correct wiring)
#   - secrets (.env, auth.json) and semantic files (SOUL.md, config.yaml,
#     profile.yaml, README.md, AGENTS.md, .env.example, .no-bundled-skills)
#   - the shared skill pool under skills/ (real files, NOT runtime)
#
# Run before committing, or when `validate_profiles.py` reports real paths inside
# a profile's skills/ directory.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
echo "cleaning runtime state under profiles/ ..."
python3 - <<'PY'
import pathlib, shutil

removed: list[str] = []

# Files that are always runtime state inside a profile's root. Never secrets or
# semantic config — those are protected separately below.
RUNTIME_FILES = {
    "state.db", "state.db-shm", "state.db-wal", "state.db-journal",
    "hermes_state.db", "hermes_state.db-shm", "hermes_state.db-wal",
    "response_store.db", "response_store.db-shm", "response_store.db-wal",
    "verification_evidence.db", "projects.db",
    "provider_models_cache.json", "ollama_cloud_models_cache.json",
    "tui-theme-boot.json", "models_dev_cache.json", "models_dev_cache.etag",
    ".skills_prompt_snapshot.json", ".tirith-install-failed",
    "auth.lock", "gateway.pid", "gateway_state.json", "gateway.lock",
    "gateway.sock", "processes.json", "errors.log", ".hermes_history",
    ".update_check", ".install_id.lock",
}

RUNTIME_DIRS = {
    "runtime", "memories", "sessions", "logs", "plans", "workspace", "home",
    "cron", "hooks", "lsp", "pairing", "cache", "image_cache", "audio_cache",
    "document_cache", "browser_screenshots", "checkpoints", "backups",
    "sandboxes", ".worktrees", "bin", "node_modules", "hermes-agent",
}

# Semantic / secret files that must NEVER be removed, even if a broad pattern
# would otherwise match them.
PROTECTED_FILES = {
    "SOUL.md", "config.yaml", "profile.yaml", "README.md", "AGENTS.md",
    ".env.example", ".env", "auth.json", ".no-bundled-skills",
    "CONTRIBUTING.md", "LICENSE", ".gitignore",
}


def remove(path: pathlib.Path) -> bool:
    if path.is_symlink():
        return False  # symlinks are the real wiring — never touch
    try:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
        else:
            return False
        removed.append(str(path))
        return True
    except OSError as exc:
        print(f"  ! skip {path}: {exc}")
        return False


for profile in sorted(pathlib.Path("profiles").glob("*/")):
    # 1. Explicit runtime files / dirs in the profile root.
    for name in RUNTIME_FILES:
        remove(profile / name)
    for name in RUNTIME_DIRS:
        remove(profile / name)

    # 2. Pattern-based sweep: lock files, logs, *_cache dirs, state DB leftovers.
    for entry in list(profile.iterdir()):
        if entry.is_symlink() or entry.name in PROTECTED_FILES:
            continue
        if entry.is_dir():
            if entry.name.endswith("_cache") or entry.name.endswith("-cache"):
                remove(entry)
        else:
            if entry.name.endswith(".log") or ".lock" in entry.name:
                remove(entry)
            if entry.name.startswith(("state.db", "hermes_state.db", "response_store.db")):
                remove(entry)

    # 3. skills/ must contain only relative symlinks into the shared pool.
    #    Any real dir/file here is bundled-skill seeding or runtime state.
    skills = profile / "skills"
    if skills.is_dir():
        for entry in list(skills.iterdir()):
            if entry.is_symlink():
                continue
            remove(entry)

# 4. Shared pool: drop runtime cache dirs (pycache etc.) but keep real skill files.
for runtime_dir in (".hub", ".org", "__pycache__", ".cache", ".tmp"):
    for p in pathlib.Path("skills").rglob(runtime_dir):
        if p.is_dir() and not p.is_symlink():
            remove(p)

print(f"removed {len(removed)} runtime path(s)")
PY
echo "done. then verify with: python3 scripts/validate_profiles.py"
