import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "kanban_exception_watchdog.py"
PY = sys.executable


def run(argv):
    return subprocess.run([PY, str(SCRIPT)] + argv, capture_output=True, text=True,
                          encoding="utf-8", timeout=120)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="wd_test_"))
    tasks_file = tmp / "tasks.json"
    subs_file = tmp / "subs.json"
    state = tmp / "state.json"

    # fake hermes：按 argv 输出 tasks / subs JSON
    fake_py = tmp / "fake_hermes.py"
    fake_py.write_text(
        "import json, sys\n"
        f"tasks = json.load(open(r'{tasks_file}', encoding='utf-8'))\n"
        f"subs = json.load(open(r'{subs_file}', encoding='utf-8'))\n"
        "if 'notify-list' in sys.argv:\n"
        "    print(json.dumps(subs))\n"
        "elif 'list' in sys.argv:\n"
        "    print(json.dumps(tasks))\n"
        "else:\n"
        "    print('[]')\n",
        encoding="utf-8",
    )
    if os.name == "nt":
        fake_exe = tmp / "fake_hermes.bat"
        fake_exe.write_text(f'@"{PY}" "{fake_py}" %*\r\n', encoding="utf-8")
    else:
        fake_exe = tmp / "fake_hermes"
        fake_exe.write_text(f'#!/bin/sh\nexec "{PY}" "{fake_py}" "$@"\n', encoding="utf-8")
        fake_exe.chmod(0o755)

    now = time.time()
    # t_ok: 带 last_failure_error 的失败卡（应报告）
    # t_sub: 同样失败但持有订阅（应跳过）
    # t_human: 人工 block 无错误字段（应忽略）
    # t_old: 300h 前的老卡（窗口外应忽略）
    tasks = [
        {"id": "t_ok", "title": "impl card", "status": "blocked",
         "last_failure_error": "gave up after 3 failures",
         "created_at": now - 7200, "started_at": now - 3600, "completed_at": now - 600},
        {"id": "t_sub", "title": "root card", "status": "blocked",
         "last_failure_error": "gave up too",
         "created_at": now - 7200, "started_at": now - 3600, "completed_at": now - 600},
        {"id": "t_human", "title": "decision card", "status": "blocked",
         "last_failure_error": None,
         "created_at": now - 7200, "started_at": now - 3600, "completed_at": now - 600},
        {"id": "t_old", "title": "ancient card", "status": "blocked",
         "last_failure_error": "very old error",
         "created_at": 1, "started_at": 2, "completed_at": now - 300 * 3600},
    ]
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")
    subs_file.write_text(json.dumps(
        [{"task_id": "t_sub", "platform": "telegram", "chat_id": "1"}]), encoding="utf-8")

    common = ["--board", "b1", "--hermes", str(fake_exe), "--state-file", str(state),
              "--max-age-hours", "168"]

    # 第一次运行：应只报告 t_ok
    r1 = run(common)
    assert r1.returncode == 0, r1.stderr
    assert "t_ok" in r1.stdout and "gave up after 3 failures" in r1.stdout, r1.stdout
    assert "t_sub" not in r1.stdout, r1.stdout
    assert "t_human" not in r1.stdout, r1.stdout
    assert "t_old" not in r1.stdout, r1.stdout
    assert r1.stdout.startswith("⚠️"), r1.stdout

    # 第二次运行：去重后应静默
    r2 = run(common)
    assert r2.returncode == 0 and r2.stdout.strip() == "", (r2.stdout, r2.stderr)

    # 错误文本变化：视为新事件重报
    for t in tasks:
        if t["id"] == "t_ok":
            t["last_failure_error"] = "gave up after 4 failures"
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")
    r3 = run(common)
    assert "after 4 failures" in r3.stdout, r3.stdout

    # 任务恢复（移出 blocked 列表）：静默 + 状态文件自动清理
    tasks = [t for t in tasks if t["id"] != "t_ok"]
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")
    r4 = run(common)
    assert r4.returncode == 0 and r4.stdout.strip() == "", (r4.stdout, r4.stderr)
    state_data = json.loads(state.read_text(encoding="utf-8"))
    assert "b1/t_ok" not in state_data["reported"], state_data

    print("ALL WATCHDOG TESTS PASSED")


if __name__ == "__main__":
    main()
