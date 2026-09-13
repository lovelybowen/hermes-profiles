#!/usr/bin/env python3
"""Integration smoke: DA gate three branches against a throwaway Kanban DB.

Pins HERMES_KANBAN_DB + HERMES_DECISION_DIR to fresh temp dirs; touches no
real board. Exercises the real `hermes kanban` CLI path that decision_bridge
invokes (create/block/unblock/archive/complete/comment).
Run: python scripts/test_da_gate_integration.py
"""
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRIDGE = REPO / "skills" / "orchestration-methodology" / "scripts" / "decision_bridge.py"

base = Path(tempfile.gettempdir()) / f"da-gate-int-{uuid.uuid4().hex[:8]}"
(base / "dec").mkdir(parents=True)
base_db = base / "kanban.db"

PASS, FAIL = [], []


def check(ok, label, detail=""):
    (PASS if ok else FAIL).append(label)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"\n        {detail[:300]}" if not ok else ""))


def sh(*args, env=None):
    return subprocess.run(list(args), capture_output=True, text=True, env=env, timeout=60)


def kb(*args, env=None):
    return sh("hermes", "kanban", *args, env=env)


def kb_create(title, env, body=""):
    args = ["create", "--json"]
    if body:
        args += ["--body", body]
    args.append(title)
    r = kb(*args, env=env)
    if r.returncode != 0:
        return None, r
    try:
        data = json.loads(outp(r))
        return data.get("id") or data.get("task_id"), r
    except json.JSONDecodeError:
        return None, r


def bridge(*args, env=None):
    return sh(sys.executable, str(BRIDGE), *args, env=env)


def outp(proc):
    return (proc.stdout or proc.stderr).strip()


FUT = "2030-01-01T00:00:00Z"
PAST = "2020-01-01T00:00:00Z"

# --- shared throwaway board -----------------------------------------------
env = dict(os.environ, HERMES_KANBAN_DB=str(base_db), HERMES_DECISION_DIR=str(base / "dec"))
r = kb("init", env=env)
check(r.returncode == 0, "board init", outp(r))

# --- validation-only branches (must fail before any state change) ------------
r = bridge("create", "--task-id", "t_x", "--baseline-revision", "r", "--action", "plan_approve",
           "--approver", "alice", "--expires-at", FUT, env=env)
check(r.returncode != 0 and "parent-task-id" in outp(r), "create without --parent-task-id rejected", outp(r))

r = bridge("create", "--task-id", "t_x", "--parent-task-id", "t_y", "--baseline-revision", "r",
           "--action", "plan_approve", "--approver", "alice", "--expires-at", PAST,
           "--decision-id", "dec-exp", env=env)
check(r.returncode == 0, "expired-ttl decision created", outp(r))
r = bridge("approve", "dec-exp", "--approver", "alice", env=env)
check(r.returncode != 0 and "expired" in outp(r), "expired decision cannot be approved", outp(r))

root_id, r = kb_create("smoke root", env, body="root card")
check(bool(root_id), f"root card created ({root_id})", outp(r))

gate_id, r = kb_create("DA approval card", env, body="plan_rev: 1")
check(bool(gate_id), f"approval card created ({gate_id})", outp(r))

# --- branch 1: approve ------------------------------------------------------
r = kb("block", gate_id, "awaiting plan approval", "--kind", "needs_input", env=env)
check(r.returncode == 0, "approval card blocked (needs_input)", outp(r))

r = bridge("create", "--task-id", gate_id, "--parent-task-id", root_id, "--baseline-revision", "rev-1",
           "--action", "plan_approve", "--approver", "alice", "--approver", "bob",
           "--expires-at", FUT, "--plan-rev", "1", env=env)
dec1 = json.loads(outp(r))["decision_id"] if r.returncode == 0 else ""
check(bool(dec1), f"decision created ({dec1})", outp(r))

r = bridge("approve", dec1, "--approver", "mallory", env=env)
check(r.returncode != 0 and "authorized" in outp(r), "unauthorized approver rejected", outp(r))
r = bridge("reject", dec1, "--approver", "alice", "--rationale", "方向不对", env=env)
check(r.returncode != 0 and "rework" in outp(r), "bare-rationale reject rejected (ambiguous)", outp(r))
r = bridge("approve", dec1, "--approver", "alice", env=env)
check(r.returncode == 0 and json.loads(outp(r))["status"] == "approved", "approve via bridge", outp(r))
r = bridge("approve", dec1, "--approver", "alice", env=env)
check(r.returncode != 0 and "not pending" in outp(r), "double-decide rejected", outp(r))

r = kb("show", gate_id, env=env)
check("ready" in outp(r) or "todo" in outp(r), "approval card unblocked after approve", outp(r)[:400])

r = kb("complete", gate_id, "--result", f"plan approved ({dec1})", env=env)
check(r.returncode == 0, "approval card completed", outp(r))

# --- branch 2: reject --rework (revision loop) -------------------------------
gate2, r = kb_create("DA approval card v2", env, body="plan_rev: 2")
check(bool(gate2), f"second approval card ({gate2})", outp(r))
kb("block", gate2, "awaiting plan approval rev2", "--kind", "needs_input", env=env)

r = bridge("create", "--task-id", gate2, "--parent-task-id", root_id, "--baseline-revision", "rev-1",
           "--action", "plan_approve", "--approver", "alice", "--expires-at", FUT,
           "--plan-rev", "2", env=env)
dec2 = json.loads(outp(r))["decision_id"] if r.returncode == 0 else ""

r = bridge("reject", dec2, "--approver", "alice", "--rework", "先补性能基准环节", env=env)
rec = json.loads(outp(r)) if r.returncode == 0 else {}
check(r.returncode == 0 and rec.get("decision", {}).get("rework") == "先补性能基准环节",
      "reject --rework records rework text", outp(r))

r = kb("show", gate2, env=env)
check("ready" in outp(r) or "todo" in outp(r), "approval card unblocked after rework reject", outp(r)[:400])

# revision loop = one NEW card per revision (same-card re-block hits block_loop_detected at 2)
r = kb("complete", gate2, "--result", f"superseded by rev3 (decision {dec2})", env=env)
check(r.returncode == 0, "rejected card completed (superseded)", outp(r))
gate3, r = kb_create("DA approval card v3", env, body="plan_rev: 3")
check(bool(gate3), f"third approval card ({gate3})", outp(r))
r = kb("block", gate3, "awaiting plan approval rev3", "--kind", "needs_input", env=env)
check(r.returncode == 0, "new card blocked (loop back to DA gate)", outp(r))

# --- branch 3: bare reject (cancel) ------------------------------------------
r = bridge("create", "--task-id", gate3, "--parent-task-id", root_id, "--baseline-revision", "rev-1",
           "--action", "plan_approve", "--approver", "alice", "--expires-at", FUT,
           "--plan-rev", "3", env=env)
dec3 = json.loads(outp(r))["decision_id"] if r.returncode == 0 else ""

r = bridge("reject", dec3, "--approver", "alice", env=env)
rec = json.loads(outp(r)) if r.returncode == 0 else {}
check(r.returncode == 0 and rec.get("decision", {}).get("rework") is None,
      "bare reject records rework=null (cancel semantics)", outp(r))

r = kb("show", gate3, env=env)
check("ready" in outp(r) or "todo" in outp(r), "approval card unblocked after cancel reject", outp(r)[:400])

kb("comment", gate3, f"cancelled: {dec3}", env=env)
r = kb("archive", gate3, env=env)
check(r.returncode == 0, "approval card archived (cancel path)", outp(r))
r = kb("complete", root_id, "--result", f"已取消：分解计划未获批准（decision {dec3}）", env=env)
check(r.returncode == 0, "root card settled (cancel path)", outp(r))

print(f"\n=== {len(PASS)} passed, {len(FAIL)} failed === scratch: {base}")
sys.exit(1 if FAIL else 0)
