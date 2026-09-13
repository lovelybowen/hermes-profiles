# 通知拓扑（exception-only）

Hermes 网关的 Kanban notifier 是平台默认行为，不是本流程的要求；按本仓库的 exception-only 原则对它做**减法配置**。本参考定义订阅集、级联剥离规则与部署核对清单。不改 Hermes 工程代码——所有手段都是现成的订阅 / cron 原语。

## 订阅集（intake 决策后由编排层维护）

| 卡类型 | 订阅 | 模式 | 推送内容 |
|---|---|---|---|
| 需求根卡（intake 根 / Flow 根） | 有 | notify+wake（网关自动订阅默认） | 终态事件 + 最终结果首行 |
| 人工决策卡（`human-decision-handoff.md` 产生的待裁决卡，含 DA 审批卡 `decomposition-approval.md`） | 有 | `notify`（被动一行） | `blocked`（等待裁决）与终态 |
| 过程卡（实现 / QA / review / 研究 / 调试 / 综合等） | **无** | — | 零 |

「人工裁决」「需求根卡最终结果」两个例外条款由订阅集直接覆盖；「崩溃 / 超时 / 放弃」由共享技能 `kanban-exception-watchdog` 的低频巡检兜底（过程卡零订阅后，其失败终态无订阅可推）。

## 平台行为与对应规则

1. **自动订阅（`kanban.auto_subscribe_on_create`，默认 true）**：gateway 会话内建卡时 originating chat 自动订阅该卡。PM 在聊天里建 intake 根卡正是期望行为——**保持 true，不要关**。
2. **订阅级联复制（平台行为，无配置开关）**：worker 通过 `kanban_create` 建子卡时复制所属任务的订阅，与自动订阅开关无关。根卡订阅因此会扩散到整张任务图。**规则：编排者每建一张过程卡，立即剥掉级联订阅**——`hermes kanban --board <slug> notify-list --json <task-id>` 枚举，对每条执行 `hermes kanban notify-unsubscribe <task-id> --platform <p> --chat-id <c>`（CLI 不支持批量，逐条执行；terminal 工具集循环即可）。
3. **决策卡降级为 notify**：决策卡需要人看见，但不需要唤醒 agent 生成回复。建卡后按 2 剥掉级联来的 notify+wake，再 `notify-subscribe <决策卡id> --platform <p> --chat-id <c> --delivery-mode notify` 重订为被动模式。
4. **多网关投递是 profile-owned**：每个 gateway 只投递自己 profile 的订阅。订阅必须在 PM 上下文建立（PM 的 TG 会话内建卡自动订阅即满足；手动补订用 `hermes -p product-manager kanban notify-subscribe ...`），否则会落到不持有研发群 bot 的 gateway 上静默投递失败。
5. **过程卡 `needs_input` / `capability` 类 block**：不进订阅集、不推聊天。需要人裁决的问题升格为决策卡（转录，不是聊天提问）——这保持审批通道唯一。

## 部署核对清单（TG 拓扑：default 日常 bot + PM 研发入口 bot，专家无 bot）

- [ ] 只有 PM 的 gateway 设 `kanban.dispatch_in_gateway: true`（单 dispatcher；default 与其他 gateway 显式 false）
- [ ] PM config **不设** `kanban.auto_subscribe_on_create: false`
- [ ] `kanban.orchestrator_profile` 显式为 `orchestrator`
- [ ] 专家 profile 不配置任何 messaging 平台凭据（无 bot，由 dispatcher 拉起）
- [ ] PM 的研发群已建一条 `kanban-exception-watchdog` no-agent cron（见该技能 SKILL.md）
- [ ] 演练后抽查：`hermes kanban notify-list` 中除根卡 / 决策卡外无其他订阅

## 停止语义与通知

停止请求（`active → stop_requested → draining → settled`）由 orchestrator 接收并在 Kanban 记录；停止本身不推聊天，但「停止后下游自动解锁」若发生属 SEB / 共享写级异常，走 watchdog 与人工通道，不得静默。
