#!/usr/bin/env python3
"""One-off: generate distribution.yaml for all 8 profiles.

Descriptions come from each profile.yaml's `description` field (single source).
env_requires mirrors the current .env.example (DEEPSEEK_API_KEY, required).

NOTE: this generator is kept in scripts/ for future re-generation, but the
committed distribution.yaml files are the source of truth.
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = REPO_ROOT / "profiles"

ENV = [{"name": "DEEPSEEK_API_KEY", "description": "DeepSeek API key（模型访问，见 config.yaml model.provider）", "required": True}]

for profile_dir in sorted(PROFILES_DIR.iterdir()):
    if not profile_dir.is_dir():
        continue
    meta = yaml.safe_load((profile_dir / "profile.yaml").read_text(encoding="utf-8")) or {}
    manifest = {
        "name": profile_dir.name,
        "version": "1.0.0",
        "description": meta.get("description", ""),
        "hermes_requires": ">=0.12.0",
        "author": "lovelybowen",
        "license": "MIT",
        "env_requires": ENV,
    }
    out = profile_dir / "distribution.yaml"
    out.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"wrote {out.relative_to(REPO_ROOT)}")
