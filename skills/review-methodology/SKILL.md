---
name: review-methodology
description: "专业评审方法论 - 代码评审、安全审计、架构评审和看板群体验证。参考资料定义 Google 代码评审标准、OWASP 审计模式和架构评估框架。"
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [review, code-review, security-audit, architecture-review, verification, quality]
    related_skills: [qa-methodology, systematic-debugging, software-architecture-analysis]
---

# 评审方法论

用于代码、安全、架构和 Agent 群输出验证的专业评审标准。

## 步骤 0：读取交接证据（强制前置）

reviewer 在进入任何评审类型之前，先读 Kanban 交接消息 `evidence` 段中的 `evidence_level` 与 SEB 字段，再据此选择核验深度。不得凭「改动看起来小」或「时间紧」自行挑档。

字段名以 `skills/orchestration-methodology/references/delivery-governance.md` §6 为准；档位定义、SEB 最小字段与复用条件的**唯一权威出处**是 `skills/artifact-pyramids/references/evidence-levels-and-seb.md`。reviewer 侧必读字段与对应动作：

- `evidence_level`（`L0 | L1 | L1+L2 | Full`）→ 决定核验深度（见下节）；由 intake 一次性下发、下游继承，不得自行升 / 降档。
- `commit`（完整 SHA）→ **只评审该固定 SHA，不评审「当前工作区」**。
- `baseline` → 与交接 / 需求基线 revision 比对；漂移即停止复用。
- `changed_files[].blob_sha` → 逐文件 `git hash-object` 复算比对（内容寻址锚点，防篡改核心）。
- `commands[].exit_code` + `commands[].stdout_sha256` → 逐条重跑并复算输出哈希；门禁结论二元，非 0 不得记为通过。机器可解析键名是 `exit_code`，不是展示串 `exit <code>`。
- `seb` → SEB 路径或内联块；`seb_integrity`（`passed | failed | not_required`）→ 复用前完整性核验结论。`seb_integrity` 与 `seb_incomplete` 是两个不同令牌，不得合并。
- `sampling` → `L1+L2` / `Full` 抽样的最高风险项；`confidence`（`full | reduced`）+ `uncovered` → 标 `reduced` 时 `uncovered` 必填且逐条可核对。

字段缺失 / 不足时**不盲目全量复算**：按 `references/seb-integrity-and-insufficiency.md` 的处置表路由——应 `Full` 却无 SEB → `kanban_block`（退回补证）；档位低于风险要求 → 退回 orchestrator 升级档位；`commit` 不同 / `baseline` 漂移 / hash 不一致 → 停止复用并全量复算；预算耗尽 → 不得伪装通过，标 `confidence: reduced` 并列 `uncovered`。

## 核验深度（按 `evidence_level`）

档位由 intake 一次性判定、下游继承；reviewer 只执行，不上调也不下调。详细深度定义、抽样规则与命令清单见 `references/evidence-level-verification.md`（引用上游权威定义，不复制全文）。

| `evidence_level` | 核验深度 | 做什么 | 明确不做 |
|---|---|---|---|
| `L0` | 快速扫描 | 变更文件清单；≥1 条可复核命令的 `exit_code`；无改动时给出显式「无改动」声明 | 不启动构建、不启动浏览器；不要求 SEB |
| `L1` | 单模块直接验证 | 仅围绕 `changed_files`：逐文件复算 blob hash、逐条重跑命令并复算 `stdout_sha256`、核对 `exit_code` 与二元结论一致 | 不扩散到未改动模块；不跑全量构建 / 浏览器 |
| `L1+L2` | 跨模块 / 接口影响核对 + 关键路径抽样 | L1 全部，外加接口 / 契约 / 依赖变化的对照证据，并按风险序抽样 ≥1 项且覆盖最高风险类别 | 不逐项全量复算全部改动 |
| `Full` | 全量复算（逐项） | build / browser / diff / SHA 逐项重算；复用前先确认 SEB 复用条件，任一不满足即停止复用并全量复算 | 不以抽样代替；不得把 `Full` 降为 `L1` / `L1+L2` 放行 |

## 评审类型

| 类型 | 参考文件 | 加载时机 |
|------|-----------|-------------|
| **代码评审** | `references/code-review-standards.md` | 评审 PR 或差异：Google 工程实践的 9 个维度及项目专用约定 |
| **安全评审** | `references/security-review.md` | 审计漏洞：威胁建模、漏洞类别、依赖分析、供应链 |
| **架构评审** | `references/architectural-review.md` | 评估设计决策：耦合/内聚、可扩展性、数据流、抽象边界 |
| **群体质量门** | `references/swarm-verification.md` | 评估 Agent 群工作者输出：通过或阻断评审门 |
| **证据档位核验** | `references/evidence-level-verification.md` | 按 `evidence_level`（`L0` / `L1` / `L1+L2` / `Full`）选择核验深度；先读交接证据再选档 |
| **SEB 完整性与证据不足** | `references/seb-integrity-and-insufficiency.md` | 复用他人证据前逐字段核验 `commit` / `baseline` / `blob_sha` / `exit_code` / `stdout_sha256` / `gate_artifacts`；证据不足时的阻塞与退回路由 |

## 模板

| 模板 | 使用时机 |
|----------|-------------|
| `templates/code-review-response.md` | 编写按严重程度组织发现的 PR 评审 |
| `templates/security-finding.md` | 记录包含复现步骤的安全漏洞 |
| `templates/swarm-verdict.md` | 使用证据通过或阻断评审门 |

## 评审思维

无论类型如何，每次评审都遵循相同过程：

0. **读取交接证据** - 先按「步骤 0」读 `evidence_level` 与 SEB 字段，据此确定本次核验深度；缺失 / 不足时按处置表上报，不盲目全量复算。
1. **理解意图** - 变更试图实现什么？先阅读描述、Issue 或简报。
2. **评估正确性** - 是否实现了声明的目标？在考虑风格或优雅程度前先回答这个问题。
3. **评估质量** - 构造是否适合其目的？检查复杂度、可维护性和测试覆盖率。
4. **评估风险** - 可能出现什么问题？检查边界情况、安全、回归和运行影响。
5. **沟通** - 清晰说明发现、严重程度和可执行的后续步骤，不针对个人，也不轻视问题。

在理解意图和正确性之前，不要直接讨论质量或风格。针对错误问题的漂亮方案仍然是错误方案。

## 与 G1 / G2 门禁衔接

门禁模式（G0 / G1 / G2）在 intake 一次性判定、下游继承，reviewer 不得自行改变；拓扑与退出条件见 `skills/orchestration-methodology/references/gate-topology.md`。结论必须**二元**（通过 / 失败）并附原始命令与输出。

- **G1（轻量异步）**：交接须含 `review_status: pending`。reviewer 发现**阻断缺陷**时，不静默修复、不在本卡内改代码，而是在**实现卡**上 `kanban_request_changes(reason=...)` 把结论退回原实现者；由 orchestrator 将受影响的综合产物标记 `superseded` 并重跑受影响分支。
- **G2（同步阻塞）**：reviewer 为下游硬父卡，**保持同步强审**。证据包必须携带 `evidence_level`（T5 / T6 为 `Full`）与 `seb_integrity: passed`、SEB 必需字段齐全；应 `Full` 却无 SEB 或 `seb_integrity: failed` 时**阻断**，不得进入批准阶段。发现阻断缺陷同样走 `kanban_request_changes` 回原实现者，行为性改动先由 `qa-engineer` 重跑受影响验证。
- 措辞或非阻断项 → 通过并附注意事项。群体模式的门禁令牌是 `{"gate": "pass" | "block"}`（见 `references/swarm-verification.md`），勿与 Kanban 的 `review_status` / `kanban_request_changes` 术语混用。

**平台边界（不得伪装完成）：** 档位选择、SEB 核验与按档抽样目前是**文档层纪律**，由 reviewer 手工执行；运行时**没有**「按 `evidence_level` 自动选深度」「自动全量复算」或「自动门禁超时降级」的钩子。不得把「规则已写入文档」表述为「运行时已自动核验」。
