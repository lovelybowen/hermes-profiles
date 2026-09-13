---
name: kanban-exception-watchdog
description: "Kanban 异常终态兜底巡检：用 no-agent cron 扫描失败终态卡并仅在有异常时推送，支撑 exception-only 通知拓扑。"
version: 1.0.0
author: lovelybowen
license: MIT
metadata:
  hermes:
    tags: [kanban, cron, watchdog, notifications, exception-only]
---

# Kanban 异常终态兜底巡检

在 exception-only 通知拓扑下，过程卡（实现 / QA / review 等）**不持有聊天订阅**——它们的失败终态（`gave_up`、连续 spawn 失败、`crashed` / `timed_out` 汇聚后的 blocked）按平台默认行为**不会推送任何聊天**。Hermes notifier 原语没有按事件类型过滤的能力（订阅级联无法关闭），因此「崩溃 / 超时 / 放弃不得静默」这条流程底线由本技能的**低频兜底巡检**承担，而不是靠订阅配置。

## 最小规则（加载即生效）

1. **只兜底，不替代。** 根卡与人工决策卡自带通知订阅，会自我推送；本巡检只覆盖**零订阅的过程卡**的失败终态。脚本会自动跳过仍持有订阅的任务，不要为此关闭该跳过。
2. **空输出 = 静默。** 巡检脚本无异常时 stdout 为空，no-agent cron 不投递任何消息。不允许为了「确认它在跑」改成每次都发——那正是本技能要消灭的噪音。
3. **只读看板。** 巡检不写 Kanban 状态、不重试任务、不解锁卡片；处置动作永远回到编排协议（`orchestration-methodology` 的监控与恢复规则）。
4. **部署为 no-agent cron**，挂在 product-manager 的 gateway 上（PM 是研发入口通道，持有研发群投递权）。不要挂 LLM job——巡检内容完全由脚本确定，无推理成分。

## 部署（一次性）

cron 脚本必须位于 `$HERMES_HOME/scripts/`（no-agent 模式的硬约束）。技能的 `scripts/kanban_exception_watchdog.py` 已随 profile 安装在技能目录内，复制一份并注册 cron：

```bash
# 1. 复制脚本到 PM 的 HERMES_HOME/scripts/（Windows 为 D:\hermes\profile 按实际安装位置）
HERMES_HOME_PM=~/.hermes/profiles/product-manager   # 按部署实际路径调整
mkdir -p "$HERMES_HOME_PM/scripts"
cp <技能目录>/scripts/kanban_exception_watchdog.py "$HERMES_HOME_PM/scripts/"

# 2. 注册 no-agent cron（在 PM 上下文执行，使其投递到 PM 的研发群）
hermes -p product-manager cron create "every 30m" \
  --no-agent \
  --script kanban_exception_watchdog.py \
  --deliver telegram \
  --name "kanban-exception-watchdog"
```

`--deliver telegram` 投递到 PM 的 home channel；如需定向研发群，按 cron 交付文档指定目标 chat。

## 行为细节

- **检测签名**：`status == blocked` 且 `last_failure_error` 非空。这是 dispatcher 对 gave_up / 失败耗尽 / 崩溃超时回收后的统一落点；普通人工 block（决策卡、needs_input）没有该字段，天然不触发。
- **去重**：状态文件 `<HERMES_HOME>/kanban_exception_watchdog_state.json` 记录已报告任务与错误文本指纹；错误变化（重试后再次失败）视为新事件重报，任务恢复后条目自动清理。
- **多 board**：缺省扫描全部非归档 board；`--board <slug>` 可限定。多项目部署建议按项目 board 各挂一个 job。
- **健康语义**：hermes CLI 调用失败 → 脚本非零退出 → cron 投递错误告警。坏掉的 watchdog 不允许静默。
- **窗口**：默认只报告最近 168 小时内到达异常态的卡（`--max-age-hours` 可调），防止状态文件丢失后旧事件洪水。

## 参考文件

| 参考文件 | 加载时机 |
|---|---|
| `scripts/kanban_exception_watchdog.py` | 巡检脚本本体（部署 / 审计时阅读） |
