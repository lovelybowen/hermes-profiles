# 需求准入：从自然语言到可确认基线

R&D 流程要求“已确认需求基线”才能开始实现。本文件定义基线如何产生、如何标识、谁批准。

用户的需求一律由 `orchestrator` 接收——它是角色体系的唯一入口，也是本流程的执行者。

**关键边界：Agent 负责整形、一致性检查和候选 revision；业务语义的确认权属于人类 `Intent Owner`。** 编排者可以起草基线，但不能批准基线。

## 1. 基线必须包含什么

| 字段 | 内容 |
|---|---|
| 标识 | 稳定 ID 或 slug |
| revision | 权威 revision 标记或 content hash |
| 角色 | 谁使用系统 |
| 场景 | 在什么情况下使用 |
| 流程 | 关键步骤顺序 |
| 业务规则 | 约束与判定规则 |
| 验收标准 | 可判定的通过条件 |

缺少任一项 → 基线未就绪，实现不得开始。

## 2. 角色分工

| 步骤 | 负责 |
|---|---|
| 从自然语言、会议纪要、文档中抽取需求 | `orchestrator`（唯一需求入口） |
| 澄清歧义、补齐缺口 | `orchestrator` 向用户提问，不自行假设 |
| 外部事实与技术可行性核实 | `researcher`（带候选 revision 引用） |
| 候选基线草案与 revision 计算 | `orchestrator` |
| **确认业务语义并批准基线** | **`Intent Owner`（人类）** |
| 实现范围与交付取舍 | `Delivery Owner`（人类） |

## 3. 流程

```
1. 收集原始输入（对话、纪要、文档、既有基线）
2. 抽取上述 7 项必备字段
3. 标记缺口与歧义 → 向 Intent Owner / 用户提问，不自行假设
4. 需要外部事实的缺口 → 交 researcher，附候选 revision 引用
5. 写出候选基线草案，计算 content hash 作为候选 revision
6. 交 Intent Owner 确认
7. 确认后冻结 revision，进入分解与路由
```

## 4. Revision 与变更

- 基线变更必须产生**新 revision**，不原地改写历史 revision。
- 每个实现任务记录其依据的 revision；变更后只重跑受影响分支。
- 与基线冲突的发现（研究、调试、架构）走 `references/human-decision-handoff.md`：由编排者准备决策包，不得自行改写基线。

## 5. 收到未就绪基线时

- 不要「先做着看」，也不要自行假设缺失的业务规则。
- 返回 `status: blocked`，在 `decisions_required` 中列出缺失字段以及需要谁裁决。
- `researcher` 可以继续收集外部证据，但必须记录其服务的候选 revision。
