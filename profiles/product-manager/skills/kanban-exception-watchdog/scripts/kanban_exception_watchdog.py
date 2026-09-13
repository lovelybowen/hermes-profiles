#!/usr/bin/env python3
"""Kanban exception watchdog — exception-only 通知拓扑的异常终态兜底巡检。

扫描 Kanban board 上以失败告终、且聊天通道按设计不会被通知到的任务
（过程卡零订阅），输出一份紧凑报告，交给 no-agent cron 原样投递。
stdout 为空 == 无事可报 == cron 静默 tick。

检测签名：status == "blocked" 且 last_failure_error 非空 —— 这是
dispatcher 在 gave_up / 连续 spawn 失败耗尽后留下的状态（crashed /
timed_out 的运行最终也汇聚到这里）。仍持有通知订阅的任务（根卡 /
人工决策卡）会被跳过：它们本来就自我推送，重复报告只会制造噪音。

跨轮去重依靠一个小 JSON 状态文件：同一任务只报告一次；若
last_failure_error 文本变化（如重试后再次失败），视为新事件重报。

hermes CLI 调用失败时以非零退出 —— no-agent cron 对非零退出会投递
错误告警，坏掉的 watchdog 不允许静默失败。

本脚本只读看板（hermes kanban list / notify-list / boards list），
不写任何 Kanban 状态；唯一写入物是状态文件。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

MAX_ERROR_CHARS = 160
DEFAULT_MAX_AGE_HOURS = 168.0  # 状态文件丢失时限制重报范围的兜底窗口


def resolve_hermes(explicit: str | None) -> list[str]:
    """返回调用 hermes CLI 的 argv 前缀。"""
    if explicit:
        return [explicit]
    found = shutil.which("hermes")
    if not found:
        raise SystemExit(
            "kanban_exception_watchdog: PATH 上找不到 hermes（可用 --hermes 指定）"
        )
    if os.name == "nt" and found.lower().endswith((".bat", ".cmd")):
        return ["cmd", "/c", found]
    return [found]


def run_json(prefix: list[str], args: list[str]) -> object:
    proc = subprocess.run(
        prefix + args, capture_output=True, text=True, encoding="utf-8", timeout=120
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"hermes {' '.join(args)} 失败: {detail}")
    out = (proc.stdout or "").strip()
    if not out:
        return None
    return json.loads(out)


def default_state_path() -> Path:
    home = os.environ.get("HERMES_HOME", "~/.hermes")
    return Path(home).expanduser() / "kanban_exception_watchdog_state.json"


def load_state(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("reported"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"reported": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def error_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


def task_age_hours(task: dict, now: float) -> float:
    stamps = [
        task.get("completed_at") or 0,
        task.get("started_at") or 0,
        task.get("created_at") or 0,
    ]
    return (now - max(stamps)) / 3600.0


def scan_board(prefix: list[str], slug: str, max_age_hours: float) -> tuple[list[dict], set[str]]:
    """返回 (异常任务列表, 本 board 有订阅的任务 id 集合)。"""
    tasks = run_json(prefix, ["kanban", "--board", slug, "list", "--status", "blocked", "--json"])
    if not isinstance(tasks, list):
        tasks = (tasks or {}).get("tasks") or []
    subs = run_json(prefix, ["kanban", "--board", slug, "notify-list", "--json"])
    subscribed_ids = {s.get("task_id") for s in (subs or []) if isinstance(s, dict)}

    now = time.time()
    anomalies: list[dict] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        err = (task.get("last_failure_error") or "").strip()
        if not err:
            continue  # 普通人工 block（决策卡等），不是异常终态
        if task.get("id") in subscribed_ids:
            continue  # 根卡/决策卡：自带订阅推送，不重复报告
        if task_age_hours(task, now) > max_age_hours:
            continue
        anomalies.append(task)
    return anomalies, subscribed_ids


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Kanban 异常终态巡检（no-agent cron 用；空输出=静默）"
    )
    parser.add_argument(
        "--board", action="append", default=None,
        help="要扫描的 board slug，可重复；缺省扫描全部非归档 board",
    )
    parser.add_argument("--hermes", default=None, help="hermes 可执行文件路径（默认取 PATH）")
    parser.add_argument(
        "--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS,
        help="只报告最近 N 小时内到达该状态的任务（默认 168）",
    )
    parser.add_argument(
        "--state-file", default=None,
        help=f"去重状态文件路径（默认 <HERMES_HOME>/{default_state_path().name}）",
    )
    args = parser.parse_args(argv)

    prefix = resolve_hermes(args.hermes)
    state_path = Path(args.state_file).expanduser() if args.state_file else default_state_path()

    if args.board:
        boards = [{"slug": s} for s in args.board]
    else:
        boards = run_json(prefix, ["kanban", "boards", "list", "--json"]) or []
        boards = [b for b in boards if isinstance(b, dict) and not b.get("archived")]

    state = load_state(state_path)
    reported: dict = state["reported"]

    lines: list[str] = []
    seen_now: dict[str, str] = {}
    for board in boards:
        slug = str(board.get("slug") or "").strip()
        if not slug:
            continue
        try:
            anomalies, _ = scan_board(prefix, slug, args.max_age_hours)
        except (RuntimeError, subprocess.SubprocessError, ValueError) as exc:
            print(f"kanban_exception_watchdog: 扫描 board {slug} 失败: {exc}", file=sys.stderr)
            return 1
        for task in anomalies:
            tid = str(task.get("id"))
            err = (task.get("last_failure_error") or "").strip()
            digest = error_hash(err)
            seen_now[f"{slug}/{tid}"] = digest
            if reported.get(f"{slug}/{tid}") == digest:
                continue  # 已报告且错误未变化
            title = (task.get("title") or "").strip().replace("\n", " ")
            snippet = err if len(err) <= MAX_ERROR_CHARS else err[: MAX_ERROR_CHARS - 1] + "…"
            lines.append(f"[{slug}] {tid} · {title}\n  {snippet}")

    if lines:
        print(f"⚠️ Kanban 异常巡检：{len(lines)} 个未确认异常终态卡")
        for line in lines:
            print(line)
        print("处理：hermes kanban --board <slug> show <id>；确认后按编排协议重试或关闭。")

    # 只保留本轮仍处于异常态的条目，自动清理已恢复的任务
    state["reported"] = seen_now
    save_state(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
