#!/usr/bin/env python3
"""Persist R&D decisions and optionally unblock the bound Kanban task.

The Feishu adapter can call this same interface after validating the card
operator. The script deliberately does not execute delivery commands.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ACTIONS = {"baseline_approve", "push", "merge", "deploy", "risk_accept"}
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def store_dir() -> Path:
    return Path(os.environ.get("HERMES_DECISION_DIR", "~/.hermes/decisions")).expanduser()


def decision_path(decision_id: str) -> Path:
    if not ID_RE.fullmatch(decision_id):
        raise ValueError("invalid decision id")
    return store_dir() / f"{decision_id}.json"


def read_decision(decision_id: str) -> dict:
    path = decision_path(decision_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"decision not found: {decision_id}") from exc
    if not isinstance(data, dict):
        raise ValueError("decision record is not an object")
    return data


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def parse_expiry(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def create(args: argparse.Namespace) -> int:
    if args.action not in ACTIONS:
        raise ValueError(f"unsupported action: {args.action}")
    if not args.approver:
        raise ValueError("at least one approver is required")
    decision_id = args.decision_id or f"dec-{uuid.uuid4().hex[:16]}"
    path = decision_path(decision_id)
    if path.exists():
        raise ValueError(f"decision already exists: {decision_id}")
    record = {
        "decision_id": decision_id,
        "task_id": args.task_id,
        "baseline_revision": args.baseline_revision,
        "commit_sha": args.commit_sha,
        "requested_action": args.action,
        "allowed_approvers": sorted(set(args.approver)),
        "expires_at": args.expires_at,
        "status": "pending",
        "created_at": now(),
        "decision": None,
    }
    write_atomic(path, record)
    print(json.dumps(record, ensure_ascii=False))
    return 0


def update(args: argparse.Namespace, status: str) -> int:
    record = read_decision(args.decision_id)
    if record.get("status") != "pending":
        raise ValueError(f"decision is not pending: {record.get('status')}")
    if parse_expiry(str(record["expires_at"])) <= datetime.now(timezone.utc):
        raise ValueError("decision has expired")
    if args.approver not in set(record.get("allowed_approvers") or []):
        raise ValueError("approver is not authorized for this decision")

    if status == "approved" and record.get("task_id"):
        hermes = shutil.which("hermes")
        if not hermes:
            raise ValueError("hermes executable is unavailable; task remains blocked")
        reason = f"Decision {record['decision_id']} approved action {record['requested_action']}"
        result = subprocess.run(
            [hermes, "kanban", "unblock", str(record["task_id"]), "--reason", reason],
            check=False, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise ValueError(f"Kanban unblock failed: {detail}")

    record["status"] = status
    record["decision"] = {
        "selected_action": record["requested_action"],
        "decided_by": args.approver,
        "decided_at": now(),
        "rationale": args.rationale or None,
    }
    write_atomic(decision_path(args.decision_id), record)
    print(json.dumps(record, ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_create = sub.add_parser("create")
    p_create.add_argument("--decision-id")
    p_create.add_argument("--task-id", required=True)
    p_create.add_argument("--baseline-revision", required=True)
    p_create.add_argument("--commit-sha")
    p_create.add_argument("--action", required=True, choices=sorted(ACTIONS))
    p_create.add_argument("--approver", action="append", required=True)
    p_create.add_argument("--expires-at", required=True)
    p_create.set_defaults(handler=create)
    for command, status in (("approve", "approved"), ("reject", "rejected")):
        p = sub.add_parser(command)
        p.add_argument("decision_id")
        p.add_argument("--approver", required=True)
        p.add_argument("--rationale")
        p.set_defaults(handler=lambda args, s=status: update(args, s))
    p_show = sub.add_parser("show")
    p_show.add_argument("decision_id")
    p_show.set_defaults(handler=lambda args: print(json.dumps(read_decision(args.decision_id), ensure_ascii=False)) or 0)
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"decision_bridge: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
