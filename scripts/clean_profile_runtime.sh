#!/usr/bin/env bash
# Remove Hermes runtime state that lands inside profile dirs of this repository.
#
# Why this exists: Hermes probes "<profile>/skills" with rglob("SKILL.md"); Python's
# rglob does NOT follow symlinked directories, so a profile whose skills are all
# relative symlinks is misread as "unseeded" and Hermes repair-seeds bundled skills
# into it on every launch. See CONTRIBUTING.md -> "运行时状态".
#
# Run before committing, or when `validate_profiles.py` reports real paths inside
# a profile's skills/ directory.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
echo "cleaning runtime state under profiles/ ..."
find profiles -mindepth 2 -maxdepth 2 -name 'runtime' -type d -prune -exec rm -rf {} + 2>/dev/null || true
python3 - <<'PY'
import pathlib, shutil
removed = []
for skills in sorted(pathlib.Path("profiles").glob("*/skills")):
    for entry in list(skills.iterdir()):
        if entry.is_symlink():
            continue          # the real wiring — keep
        removed.append(str(entry))
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
for marker in ("state.db", "state.db-shm", "state.db-wal", "auth.lock",
               ".skills_prompt_snapshot.json", "gateway.pid", "gateway_state.json"):
    for p in pathlib.Path("profiles").glob("*" + "/" + marker):
        p.unlink(missing_ok=True)
        removed.append(str(p))
print(f"removed {len(removed)} runtime path(s)")
PY
echo "done. then verify with: python3 scripts/validate_profiles.py"
