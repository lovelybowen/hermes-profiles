"""R&D decision slash command plugin.

The Feishu adapter already routes ordinary slash commands. This plugin adds a
text-only approval surface without changing that adapter or inventing a second
approval state machine.
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional

_HELP = """Usage:
/decision show <decision-id>
/decision approve <decision-id> --approver <feishu-open-id> [--rationale <text>]
/decision reject <decision-id> --approver <feishu-open-id> --rationale <text>

The command never runs push, merge, or deploy itself; approval only records the
bound decision and unlocks its Kanban task.
"""


def _bridge() -> Path:
    # This plugin is normally symlinked from the profile repository into the
    # active HERMES_HOME/plugins directory.
    return Path(__file__).resolve().parents[2] / "skills" / "orchestration-methodology" / "scripts" / "decision_bridge.py"


def _run(args: list[str]) -> str:
    result = subprocess.run(
        [sys.executable, str(_bridge()), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=35,
    )
    output = (result.stdout or result.stderr).strip()
    return output or ("decision command failed" if result.returncode else "decision command completed")


def _handle_slash(raw_args: str) -> Optional[str]:
    try:
        argv = shlex.split(raw_args or "")
    except ValueError as exc:
        return f"Invalid command syntax: {exc}\n\n{_HELP}"
    if not argv or argv[0] in {"help", "-h", "--help"}:
        return _HELP
    if argv[0] not in {"show", "approve", "reject"} or len(argv) < 2:
        return _HELP
    if argv[0] == "show":
        return _run(["show", argv[1]])
    if "--approver" not in argv:
        return "Missing --approver.\n\n" + _HELP
    try:
        approver = argv[argv.index("--approver") + 1]
    except (ValueError, IndexError):
        return "Missing --approver value.\n\n" + _HELP
    bridge_args = [argv[0], argv[1], "--approver", approver]
    if "--rationale" in argv:
        try:
            bridge_args += ["--rationale", argv[argv.index("--rationale") + 1]]
        except (ValueError, IndexError):
            return "Missing --rationale value."
    return _run(bridge_args)


def register(ctx) -> None:
    ctx.register_command(
        "decision",
        handler=_handle_slash,
        description="Approve or reject a bound R&D Kanban decision.",
        args_hint="show|approve|reject <decision-id>",
        argument_mode="mixed",
    )
