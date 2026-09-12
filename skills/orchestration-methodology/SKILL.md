---
name: orchestration-methodology
description: "R&D 编排方法论 - 从已确认需求基线建立 Flow，完成任务分解、专家路由、工作流恢复、证据综合和人类决策交接。"
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [orchestration, multi-agent, workflow, routing, synthesis]
---

# R&D 编排方法论

以已确认需求基线为起点，将研发工作组织为可追溯的专家协作。编排者管理工作流，不修改业务意图、不替专家作出领域决策，也不代替人类接受风险。

## 编排生命周期

```
校验基线 → 分解 → 路由 → 监控 → 综合 → 人类批准
```

## 门禁拓扑（intake 决策一次）

门禁强度在建卡时用父子边（`kanban_create(parents=[...])`）表达，并在 intake 阶段**一次性**决定，下游继承：

| 门禁 | 适用 | 拓扑 |
|------|------|------|
| **G0 跳过** | T0（答问）、T1（讨论/研究） | 不建 reviewer 卡 |
| **G1 轻量异步** | T2、非生产的 T3、T4（+ QA 门） | reviewer 卡 `parents=[实现/QA]`；综合卡 `parents=[QA]`，不含 reviewer；交接须含 `review_status: pending` |
| **G2 同步阻塞** | T5、T6、影响生产的 T3、信息不足的保守升级 | 综合卡 `parents=[..., reviewer]`（硬父卡） |

G1 若在综合完成后发现阻断级缺陷：在实现卡 `kanban_request_changes`，并由编排者把综合产物标记 `superseded` 后重跑受影响分支。完整矩阵、每道门禁的进入/退出条件、风险等级映射与回滚规则见 `references/gate-topology.md`。

## 证据等级与 SEB（intake 决策一次）

证据深度档位 **`evidence_level`（L0 / L1 / L1+L2 / Full）** 与门禁强度一并在 intake **一次性**判定，写入任务卡与交接消息，下游 reviewer / QA **继承、不得各自重选**。编排者把工作交给 `reviewer` 前，必须校验交接证据包含 `evidence_level`、固定 `commit`、`changed_files`（含 `blob_sha`）、`commands`（含 `exit_code` / `stdout_sha256`）与 `seb_integrity`；档位不足或 SEB 缺失 / 不一致时按阻塞或 `confidence: reduced` + `uncovered` 部分裁决处理，**降级的是置信度，不是门禁要求**。

档位阈值、SEB 最小字段、复用前置条件、完整性核验流程与不足处置表以共享技能 `artifact-pyramids/references/evidence-levels-and-seb.md` 为唯一权威出处；orchestrator 侧的交接字段与处置表见 `references/delivery-governance.md` §6。本技能不改动 `reviewer` 的技能实现。

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/task-decomposition.md` | 需要把复杂问题拆为可交给专家的子任务 |
| `references/specialist-routing.md` | 需要为子任务匹配正确的专家角色 |
| `references/workflow-monitoring.md` | 工作流跨越多个角色、质量门阻断，或工作需要重试和重新路由 |
| `references/synthesis-patterns.md` | 需要把多个专家的输出组合成连贯整体 |
| `references/human-decision-handoff.md` | 业务语义、交付取舍或高风险例外需要人类责任人裁决 |
| `references/requirements-intake.md` | 收到自然语言需求、需要形成可确认的基线 revision，或收到未就绪基线时 |
| `references/gate-topology.md` | intake 需要判定 T0–T6 与 G0/G1/G2，或需要门禁拓扑（父边）与缺陷回收纪律时 |
| `references/delivery-governance.md` | 分解实现类工作、分配工作区、设定质量门顺序或判定某个动作是否需要审批时 |
| `references/rehearsal-comparison-metrics.md` | 需要为重复演练做跨轮定量对比：确定指标字段集、从 Kanban DB / 会话日志 / git 取数，或决定对比前的基线证据冻结方式时 |
| `artifact-pyramids/references/evidence-levels-and-seb.md`（共享技能池） | 需要判定 / 继承 `evidence_level`（L0 / L1+L2 / Full）、核验 SEB 完整性，或处理证据不足（阻塞 / 降级）时 |
| 共享技能 `project-context-binding` | intake 涉及新项目接入、项目 AGENTS.md 必填区校验或 board 选择时 |
| 共享技能 `skill-feedback-loop` | 任务执行中发现方法论缺陷，需要形成 skill_feedback 回流时 |

持久化决策可使用 `scripts/decision_bridge.py`；它只记录单次决策并在批准后解锁绑定任务，不执行 push、merge 或 deploy。
