# 分解审批门（DA 门）：分解计划的人工审批

orchestrator 完成任务分解之后、建立任何下游执行卡之前，分解计划必须经人类审批。本文件是 DA 门的唯一权威出处：触发与豁免、审批计划 schema、三分支状态机、修订循环、取消路径与平台边界都以此为准。`SKILL.md` 的编排生命周期、`gate-topology.md` 的门禁纪律、`SOUL.md` 的编排纪律条目均指向本文件，不在别处复述规则细节。

**核心纪律：先审后建卡。** 审批对象是「计划」，不是「已在执行的工作」。除豁免类（§1）外，未获批准前不得创建任何实现 / QA / review / 研究 / 调试卡——这让「拒绝并取消」退化为归档审批卡 + settle 根卡，无需清理下游卡片（平台没有 cancel 原语，见 `delivery-governance.md` §7）。

## 1. 触发与豁免

| 任务类别 | DA 门 | 依据 |
|---|---|---|
| T0 / T1（G0：答问、讨论、研究） | **豁免** | 无分解建卡，门不存在 |
| L0 快速通道（`gate-topology.md` §4.1：单文件 ≤30 行、无依赖、未命中高风险清单的 T2/T4） | **豁免** | 保持快速通道速度；事后抽样审计仍适用 |
| 其余全部（非 L0 的 T2/T3/T4、T5、T6，含信息不足保守升级的 G2） | **必须** | 分解计划先审后建卡 |

豁免必须记录：豁免任务在交接消息中注明 `da_gate: exempt` 与豁免依据（`G0` 或 `L0-fast-path`），对齐「跳过必须记录」。

**重分解同样过门。** 监控期间的重新分解（同一质量门第二次失败、研究员带回改变局面的发现等，见 `workflow-monitoring.md` 重试规则 3）产生新计划，plan_rev 递增后重新提审——门只放行被批准的那一版计划，不是第一版。

## 2. 时序（全部为现有原语）

```
1. intake 完成（六字段块写入卡面）+ 分解完成，产出审批计划（§3 schema）
2. 根卡 comment 附计划摘要（可追溯锚点）
3. 创建审批卡：kanban create，assignee=orchestrator，body=完整审批计划 + 审批协议段
4. kanban block <审批卡> "awaiting plan approval rev<N>" --kind needs_input
   （reason 位置参数在 --kind 之前；每张审批卡只 block 一次，见 §7）
5. python scripts/decision_bridge.py create --task-id <审批卡> --parent-task-id <根卡> \
     --action plan_approve --approver <delivery-owner> --approver <发起用户> \
     --expires-at <ISO8601> --plan-rev <N>
6. 按人工决策卡拓扑处理订阅（notification-topology.md）：剥掉级联订阅，
   将 PM 研发群以 --delivery-mode notify 重订到审批卡——blocked 事件推送一行到聊天，
   即「通过消息告知」的触发点；计划全文在审批卡 body（kanban show / Kanban UI 查看）
```

审批界面（rd-approval 插件 `/decision`，或直接调 decision_bridge.py）：

```
/decision show <decision-id>
/decision approve <decision-id> --approver <id> [--rationale <text>]
/decision reject <decision-id> --approver <id> --rework <重做建议>     → 修订循环（§4.2）
/decision reject <decision-id> --approver <id>                         → 取消本次任务（§4.3）
```

`plan_approve` 加入 decision_bridge 的 action 闭集合；批准与拒绝都由 bridge 解锁审批卡（`kanban unblock`），唤醒 orchestrator worker 执行后续语义动作。bridge 仍然只记录决策 + 解锁，不执行归档、建卡或交付动作。

## 3. 审批计划 schema（写入审批卡 body）

```yaml
plan_id: <decision-id>
plan_rev: 1                      # 每轮修订 +1
root_task: <根卡 id>
baseline:
  revision: <revision 或 content hash>
intake:                          # 既有六字段块，与卡面同值同义
  task_class: T0..T6
  risk: R-none..R-critical
  gate: G0|G1|G2
  evidence_level: L0|L1|L1+L2|Full
  reason: <一句话依据>
  evidence: <基线定位>
steps:                           # 简要执行流程：每个环节由哪个 profile 做什么
  - seq: 1
    profile: researcher
    does: 调研 X 的依赖与兼容性
    output: 研究金字塔
    depends_on: []
  - seq: 2
    profile: backend-engineer
    does: 实现 Y 服务切片
    output: 变更 + SEB
    depends_on: [1]
skipped_experts:                 # 对齐「跳过专家要记录原因」
  - profile: debugger
    reason: 根因已知，无需根因分析
da_gate: pending                 # pending | approved | rework | cancelled
```

要求：每个 step 的 `profile` 取自已安装角色，`does` 一句话说清做什么，`output` 可验证；`steps` 与后续建卡一一对应（批准后不得增删环节，需变更即重走 §1 重分解）。

## 4. 三分支状态机

```
                ┌────────────────────────────────────────────┐
                │  DA 门：审批卡 blocked（needs_input），      │
                │  blocked 事件推聊天一行，计划全文在卡 body    │
                └──────────────┬─────────────────────────────┘
        approve                │                reject
   ┌─────────────────────┐─────┴──────┬──────────────────┐
   ▼                     ▼            ▼                  ▼
bridge unblock      bridge unblock              bridge unblock（无 --rework）
建下游卡，进入执行    （携带 --rework）            orchestrator 执行取消：
审批卡 complete      orchestrator 按建议修订       comment 拒绝记录 → 归档审批卡
（--summary 记批准）  计划（plan_rev+1），写回      → 根卡 complete（--result 注明
                     审批卡 body + comment，       rejected/cancelled）→ 根卡终态
                     重新 block + 新 decision，    推送告知用户任务已取消
                     回到 DA 门（新一轮推送）
```

判别规则（显式，不猜意图）：**携带 `--rework` → 修订循环；不携带 `--rework`（无论是否写了 `--rationale`）→ 取消。** `--rationale` 只作记录，不改变分支。帮助文案与审批卡协议段必须写明：想让它改就填 `--rework`，想取消就不填。

### 4.1 通过（approve）

1. bridge 校验 approver / 过期 / 单次使用后 `kanban unblock` 审批卡。
2. 被唤醒的 orchestrator 校验 decision 记录（`show` 回读 status=approved），按已批准计划建下游卡与依赖边（含 worktree 锚点、订阅剥离等既有纪律）。
3. 审批卡 `kanban complete`，`--summary` 记录 decision id 与批准人；`da_gate: approved` 写回 body。
4. Flow 进入监控（`workflow-monitoring.md`）。

### 4.2 拒绝 + 重做建议（reject --rework）→ 修订循环

**一轮修订 = 一张新审批卡**（平台限制：同一张卡第 2 次同 kind block 触发 `block_loop_detected` 直接进 triage，且 triage 恢复走 `specify` 会用 LLM 改写卡面，破坏计划 body——见 §7）。因此修订不重用旧卡，而是链式开新卡：

1. bridge unblock 旧审批卡；decision 记录 `status: rejected`、`decision.rework: <建议原文>`。
2. 被唤醒的 orchestrator 读回 rework 建议，按建议修订计划，`plan_rev + 1`。
3. **旧审批卡 `kanban complete`**（`--result` 注明 `superseded by rev N+1（decision <id>）`），comment 留存被拒版本与建议原文；**新建审批卡 N+1**（body = 新计划，comment 链回指旧卡 id），block + 新 decision，回到 DA 门，新一轮 blocked 推送（注明「第 N+1 版计划待审批」）。
4. 修订循环**不设硬上限**：终止权在人类（随时可空 reject 取消）。
5. 若 rework 建议指向业务语义（改需求而非改计划），不修订计划——按 `human-decision-handoff.md` 交 `Intent Owner`，当前审批卡保持 blocked（本轮 decision 已消耗，业务语义变更冻结由 Intent Owner 裁决后另起）。

审批链可追溯性：`decision.parent_task_id`（根卡）+ 卡间 comment 回指 + decision 记录的 `plan_rev`，三者构成完整修订历史。

### 4.3 拒绝（无 --rework）→ 取消本次任务

1. bridge unblock；decision 记录 `status: rejected`、`rework: null`。
2. 被唤醒的 orchestrator 执行取消清单：
   - 审批卡 comment 拒绝记录（decision id、拒绝人、时间）；
   - `kanban archive <审批卡>`；
   - **初次分解被拒**（无活跃下游卡）：根卡 `kanban complete --result "已取消：分解计划未获批准（decision <id>）"`。根卡终态经既有订阅推回聊天，用户得知任务已取消。
   - **重分解被拒**（已有活跃下游卡）：根卡转入停止语义 `active → stop_requested → draining → settled(stopped)`（见根 AGENTS「停止语义」与 `notification-topology.md`），活跃下游卡随 draining 收尾。
3. 取消后同一需求再次发起 = 新 intake（新根卡），不复用已取消的 decision。

## 5. 责任人与有效期

- **默认审批人**：`Delivery Owner` + 发起会话用户（两者任一可裁决；`allowed_approvers` 同时列入）。
- **默认有效期**：`expires_at` = 建卡时刻 + **72h**。到期后 bridge 拒绝 approve/reject（decision is not pending / has expired 语义），流程停在 blocked。
- **过期恢复 = 重新提审**：orchestrator 以同版计划新建 decision（新 id、新的 72h），comment 注明「前次 decision 过期」。无自动超时降级、无自动取消（平台缺口，§7）。

## 6. 通知

DA 审批卡按**人工决策卡**拓扑处理（`notification-topology.md` 订阅集）：剥级联订阅 + PM 研发群被动 `notify` 重订。修订循环每轮 +1 条 blocked 推送，属 exception-only 的「人工裁决」例外条款。取消路径依赖根卡终态推送（根卡订阅来自 PM 会话建卡），无需额外订阅。

## 7. 平台边界（不得伪装完成）

- **无自动超时降级**：审批过期后流程挂起，恢复靠重新提审；不要声称存在自动降级或自动取消。
- **无运行中取消原语**：取消语义由「先审后建卡」+ 归档/settle 组合实现；重分解取消依赖停止协议的状态机纪律，而非平台 cancel。
- **同 kind block 循环检测（实测）**：同一张卡第 2 次同 kind block 即触发 `block_loop_detected`（limit=2）转入 `triage`，triage 态下 block / unblock / promote 均被拒；唯一出口 `specify` 会用 LLM 重写卡面（实测将审批卡标题改写为实现任务标题）。**因此修订循环必须一轮一卡（§4.2），每张审批卡只 block 一次**；不要试图在同一张卡上多轮 block/unblock。
- **`block` 的 reason 是位置参数**：`kanban block <id> "reason" --kind needs_input`——reason 必须在 `--kind` 之前，顺序颠倒会被 argparse 拒绝（实测）。
- **decision_bridge 在 Windows 上的既有缺陷已修复**：`os.fchmod` 不存在（POSIX-only）曾使任何写入直接崩溃；`os.replace` 需重试以容忍 AV/索引器短暂锁文件（WinError 32）。

## SOURCES

```
references/human-decision-handoff.md
 -> 决策包与 Feishu/Kanban 实现约定（DA 门复用其决策卡机制与审批人校验）
references/notification-topology.md
 -> 人工决策卡订阅拓扑（DA 审批卡的剥订阅 + 被动 notify 重订）
references/gate-topology.md
 -> §4.1 L0 快速通道（豁免依据）；§1 一次性分类纪律（DA 门在其后、建卡前）
scripts/decision_bridge.py
 -> plan_approve action、reject 解锁与 --rework 判别的实现
plugins/rd-approval/__init__.py
 -> /decision 审批界面（approve / reject --rework / reject）
```
