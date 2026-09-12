# 门禁拓扑：T0–T6 风险分类与 G0/G1/G2

编排者在 intake 阶段完成一次性风险分类，并用父子边（`kanban_create(parents=[...])`）表达门禁强度。本文件是门禁决策的唯一权威出处：门禁模式在建卡时确定一次，下游**继承**，worker 不得各自重新判定。

## 1. 一次性分类纪律（intake 决策一次）

- intake（需求准入）阶段，`orchestrator` 依据已确认基线判定每项工作的 **T 类**与**风险等级**，并据此选定 **G0/G1/G2**。
- 决策连同依据写入**任务卡 body（卡面）**与交接消息，可机器解析。六个字段**全部必填**：

  ```yaml
  task_class: T0 | T1 | T2 | T3 | T4 | T5 | T6
  risk: R-none | R-low | R-moderate | R-high | R-critical
  gate: G0 | G1 | G2
  evidence_level: L0 | L1 | L1+L2 | Full
  reason: <改动面 / 不可逆性 / 爆炸半径 的一句话依据>
  evidence: <基线 revision / content hash 或交接物路径>
  ```

  取值必须逐字取自 §3/§4 与 `artifact-pyramids/references/evidence-levels-and-seb.md` §1 的令牌表，不得自造同义词或追加说明文字。**缺任一字段即视为 intake 未完成**，不得进入分解与路由；只写进对话而卡面缺失时，下游按「未收到 intake 判定」处理并保守升级。字段模板与检查清单见 `requirements-intake.md` §6.1 / §6.2。
- **下游继承。** 分解出的子任务沿用同一门禁模式，不得各自重新判定——这正是「要不要金字塔 / 要不要 reviewer」出现相反判断的根因。
- **跳过与降级必须有记录。** G0/G1 的决策与依据随 orchestrator 交接消息一并保留（对齐「跳过专家要记录原因」）。
- **信息不足时保守升级。** 无法判定改动面或爆炸半径时按 G2 处理，不猜。

## 2. T0–T6 任务分类

按「改动面 × 不可逆性 × 爆炸半径」分类：

| ID | 类型 | 典型触发 | 改动面 | 不可逆性 | 爆炸半径 | 需要 QA 门 |
|----|------|----------|--------|----------|----------|-----------|
| T0 | 一句话需求 / 澄清 | 「把颜色换成蓝色？」 | 无（回答） | n/a | 无 | 否 |
| T1 | 纯讨论 / 研究 | 方案讨论、调研综合 | 无（知识） | n/a | 无 | 否 |
| T2 | 文档 | README、ADR、runbook | 文本 | 高（git 可回滚） | 低 | 否（可抽样） |
| T3 | 配置变更 | `config.yaml`、`board.json`、CI | 运行时行为 | 中 | 中 | 视影响面 |
| T4 | 普通代码变更 | 小功能 / 修 bug，低爆炸半径 | 代码 | 高（git） | 低–中 | 是 |
| T5 | 高风险代码 / 架构变更 | 鉴权、支付、数据迁移、公开 API、跨服务契约 | 代码 + 契约 | 低 | 高 | 是 |
| T6 | 安全 / 合规 | 密钥、PII、权限、依赖供应链 | 全部 | 低 | 高 | 是 |

## 3. 风险等级 → 默认门禁

| 风险等级 | 含义 | 典型 T 类 | 默认门禁 | QA 门 |
|----------|------|-----------|----------|-------|
| R-none | 无改动面，仅知识 / 答问 | T0, T1 | **G0** | 否 |
| R-low | 文本改动，可回滚 | T2 | **G1** | 否 |
| R-moderate | 运行时配置或局部代码，爆炸半径低–中 | T3, T4 | **G1**（T3 触及生产/密钥/CI → **G2**；T4 加 QA 门） | T4 是 |
| R-high | 跨服务契约 / 迁移 / 鉴权 | T5 | **G2** | 是 |
| R-critical | 安全 / 合规 / 密钥 / PII | T6 | **G2** | 是 |

风险等级只是 T 类到门禁的中间表达；当 T 类与风险等级指向不同门禁时，取**更严**者。

## 4. 决策矩阵（任务类 → 门禁 / 证据 / 预算 / 人工升级）

| 任务类 | 默认模式 | 证据深度 | Reviewer 预算 | QA 门 | 人工升级 |
|--------|----------|----------|---------------|-------|----------|
| T0 一句话需求 | **G0 跳过** | L0 | — | 否 | 语义有歧义时 |
| T1 讨论 / 研究 | **G0 跳过**（作者自检） | L0（可选 L1） | — | 否 | 结论改变基线时 |
| T2 文档 | **G1 轻量异步** | L1 | ≤ 8 轮 / ≤ 180s | 否 | 面向用户的政策文 |
| T3 配置 | **G1**；影响生产 / 密钥 / CI 则 **G2** | L1（接口 / 依赖 / schema 变化 → L1+L2） | ≤ 12 轮 / ≤ 300s | 视影响面 | 影响生产时（`Risk Approver`） |
| T4 普通代码 | **G1 轻量异步 + QA 门** | L1（可复用上游 L1+L2 / Full） | ≤ 12 轮 / ≤ 300s | 是 | 否（除非发现缺陷） |
| T5 高风险代码 / 架构 | **G2 同步阻塞（强化）** | Full（SEB 必需） | ≤ 30 轮 / ≤ 900s | 是 | 是（`Risk Approver`） |
| T6 安全 / 合规 | **G2 同步阻塞（强化）** | Full（SEB 必需 + 威胁建模） | ≤ 30 轮 / ≤ 900s | 是 | 是（`Risk Approver`） |

「证据深度」列取 `evidence_level` 档位（L0 / L1 / L1+L2 / Full），与门禁一样在 **intake 一次性下发、下游继承**。档位阈值、SEB 最小字段、复用前置条件、完整性核验流程与不足处置以共享技能 `artifact-pyramids/references/evidence-levels-and-seb.md` 为唯一权威出处；orchestrator 建 reviewer 卡前必须校验证据包（见 `delivery-governance.md` §6）。

预算数值是**设计目标值**，须经阶段 0–1 校准；未校准前只作软纪律，不得作为自动化门禁超时机制已在运行的证据（该机制属平台缺口，见 §10）。

## 5. 门禁模式的拓扑表达

三种模式今天就能用父边拓扑表达（零平台改造）：

| 模式 | 语义 | 拓扑表达（`kanban_create`） |
|------|------|------------------------------|
| **G0 跳过** | 不建 reviewer 卡 | 不调用 `kanban_create(assignee=reviewer)` |
| **G1 轻量异步** | reviewer 卡存在，但不作下游父卡 | reviewer 卡 `parents=[实现/QA]`；综合卡 `parents=[QA]`（不含 reviewer） |
| **G2 同步阻塞** | reviewer 卡为下游硬父卡 | 综合卡 `parents=[..., reviewer]` |

## 6. 每道门禁的进入与退出条件

### G0 — 跳过

- **进入**：intake 判定 T0/T1（无改动面），或改动可由作者自检覆盖且**无下游行为依赖**。
- **拓扑**：不创建 reviewer 卡。
- **退出（完成）**：产物经 `kanban_complete` 交接，交接消息记录 `gate: G0` 与跳过依据。
- **升级**：语义歧义或结论可能改变基线时，按 `human-decision-handoff.md` 交人类责任人，可升级为 G1/G2。

### G1 — 轻量异步

- **进入**：T2；T3（非生产影响）；T4（普通代码），且具备可判定验收标准与固定 SHA / 产物。
- **拓扑**：reviewer 卡 `parents=[实现卡 或 QA 卡]`；综合卡 `parents=[QA 卡]`，**不含** reviewer 边。
- **交接要求**：G1 交接**必须**携带 `review_status: pending` 与证据包（`evidence_level` + `seb_integrity` + SEB 必需字段）。`seb_integrity` 只有 `passed` / `failed` / `not_required` 三个逐字取值：生产者交接自产证据时为 `not_required`，`reviewer` 完成完整性核验后改填 `passed` / `failed`（语义与填权见 `artifact-pyramids/references/evidence-levels-and-seb.md` §4.1）。G1 下综合卡不被 reviewer 阻塞，因此最终人工批准须等评审落地，或由责任人显式接受残余风险。
- **证据不足**：`seb_integrity: failed`、档位低于 intake 下发值或 SEB 必需字段缺失时**不得建 reviewer 卡**，退回原生产者补齐；预算耗尽只能标 `confidence: reduced` + `uncovered` 部分裁决。处置表见 `delivery-governance.md` §6.2。
- **退出（通过）**：reviewer 通过且无阻断缺陷 → 综合可推进。
- **退出（阻断）**：G1 reviewer 在综合完成后发现阻断级缺陷 → 在实现卡上 `kanban_request_changes`，由 `orchestrator` 将综合产物标记 `superseded` 并重跑受影响分支。
- **预算**：文档 ≤ 8 轮 / ≤ 180s；普通 ≤ 12 轮 / ≤ 300s（目标值）。

### G2 — 同步阻塞

- **进入**：T5/T6；T3 影响生产；G1 发现阻断缺陷且已交付 SHA；或 intake 信息不足的保守升级。
- **拓扑**：综合卡 `parents=[..., reviewer]`，reviewer 为硬父卡。
- **交接要求**：证据包必须携带 `evidence_level`（T5/T6 为 `Full`），SEB 必需字段齐全。生产者交接时 `seb_integrity` 为 `not_required`（自产，尚无复用方核验）；**G2 通过前必须由 `reviewer` 给出 `passed`**（`reviewer` 未给出核验结论、应 `Full` 却无 SEB、或出现 `seb_integrity: failed` 时**阻断**，不得进入批准阶段，处置见 `delivery-governance.md` §6.2）。
- **退出（通过）**：reviewer 结论二元（pass）并附原始命令与输出。
- **退出（阻断）**：`kanban_request_changes` 回原实现者；行为性改动先由 `qa-engineer` 重跑受影响验证。
- **预算**：≤ 30 轮 / ≤ 900s（目标值）。

## 7. 硬规则

1. **一次改动、一次门禁判定。** 门禁模式在 intake 由 `orchestrator` 决定一次，下游继承，不得由各 worker 各自判定。
2. **QA 门与 Reviewer 门分工不重叠。** QA 回答「它是否能工作」（功能性验证）；reviewer 回答「它是否是正确的改动、风险是否可接受」（对抗性判断）。reviewer 默认不重跑 QA 已跑过的功能验证。
3. **G1 的独立缺陷路径。** 见 §6 G1「退出（阻断）」：`kanban_request_changes` + 综合产物标 `superseded`。
4. **只有 G2 允许阻塞下游。** 仅 T5/T6 及「信息不足的保守升级」允许设置硬父边。
5. **跳过必须有记录。** G0/G1 的决策连同依据写入 orchestrator 交接消息。
6. **证据包不足不得进 reviewer 门。** 建 reviewer 卡前必须校验 `evidence_level` 与 SEB 必需字段；档位不足、`seb_integrity: failed` 或字段缺失时先退回原生产者补齐（见 `delivery-governance.md` §6.2），不得用 reviewer 代替证据核验，也不得自行降档。

## 8. 人工升级条件

| 触发条件 | 升级对象 |
|----------|----------|
| 改动触及公开契约、数据迁移、鉴权 / 权限、密钥、资金 | `Risk Approver` |
| 任何 G1 发现为正确性 / 安全缺陷，且已交付 SHA | `Risk Approver` |
| 门禁超时或降级 | `Delivery Owner` |
| reviewer 与 QA 结论冲突 | `Delivery Owner` |
| 收到任何人类停止 / 取消请求 | `Intent Owner`（并立即执行停止协议） |
| 需要接受残余风险 | `Risk Approver` |
| 基线缺失 / 冲突 | `Intent Owner` |

决策包格式见 `human-decision-handoff.md`。

## 9. 回滚（新 Flow 暂按 G2）

回滚规则：**停止新 Flow 的 G0/G1 决策，所有新 Flow 暂按 G2；不回溯修改已有任务的父边。** 已有任务保持既定拓扑，避免历史重排造成状态不一致。

## 10. 平台边界（不得伪装完成）

以下能力在平台源码中**不存在**，本文件只做文档纪律，不得声称已在运行时生效：

- 门禁自动超时降级。
- 运行中 worker 取消 / 中断。
- 声明式可选 / 条件门禁原语（`kanban_create` 无此字段）。

需要这些能力时另立平台卡，由 `Delivery Owner` / 系统 owner 决策。

SOURCES

```
/root/kanban-evidence/t_ab501dbe/02-analysis/02-task-classification-and-gates.md
 -> §1–§7：门禁三模式拓扑表达、T0–T6 分类、决策矩阵、5 条硬规则、人工升级条件的原始出处
/root/kanban-evidence/t_c73d8334/02-analysis/02-task-gate-matrix.md
 -> T0–T6 与 G0/G1/G2 矩阵的原始设计
/root/kanban-evidence/t_c73d8334/02-analysis/02-timeout-stop-escalation.md
 -> 超时与停止协议的详细设计（运行时部分属平台缺口）
/root/.hermes/kanban/attachments/t_567d53e4/implementation-plan.md
 -> 批次 A2 的原始意图与验证方法
/root/kanban-evidence/t_40171dfd/02-analysis/02-item-classification.md
 -> A2 各子项分类（C2 / C3 / C4）与 SOUL.md 受保护说明
/root/hermes-profiles/skills/artifact-pyramids/references/evidence-levels-and-seb.md
 -> §4「证据深度」列（L0/L1/L1+L2/Full）与 §6 门禁交接要求引用的权威出处；SEB 完整性核验与不足处置规则
```
