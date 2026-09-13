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

**例外：L0 快速通道的简化基线。** 走 L0 快速通道（`gate-topology.md` §4.1：单文件 ≤30 行、无依赖、未命中高风险清单的 T2/T4）的任务，基线最低只需三项：

| 字段 | 内容 |
|---|---|
| 原始请求 | 用户原话或 intake 卡原文，不得加工 |
| 验收标准 | 一条可判定命令或一个可观察行为 |
| 项目锚点 | 项目 / board / workspace 路径 |

七字段中的角色 / 场景 / 流程 / 业务规则在此前提下由原始请求隐含；一旦发现任一字段实际影响判定（例如点击行为涉及计费、权限），立即退出快速通道，回退七字段基线并按 §6 重新分类。

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
6. 完成一次性风险分类：判定 T0–T6 与 G0/G1/G2，决策与依据写入 intake 记录（见 `gate-topology.md`）
7. 交 Intent Owner 确认
8. 确认后冻结 revision，进入分解；非豁免任务（G0 与 L0 快速通道除外）的分解计划按 `references/decomposition-approval.md` 过 DA 门人工审批后方可路由建卡
```

## 3.1 基线存放与跨机器引用

基线正文存放在项目仓库的约定目录，例如 `docs/ai-rnd/<baseline-id>/baseline.yaml`；消息只携带 `baseline_id`、`revision`、`content_hash` 和仓库相对路径。任何本地或远程 worker 都不把机器绝对路径当成共享引用。

## 4. Revision 与变更

- 基线变更必须产生**新 revision**，不原地改写历史 revision。
- 每个实现任务记录其依据的 revision；变更后只重跑受影响分支。
- 与基线冲突的发现（研究、调试、架构）走 `references/human-decision-handoff.md`：由编排者准备决策包，不得自行改写基线。

## 5. 收到未就绪基线时

- 不要「先做着看」，也不要自行假设缺失的业务规则。
- 返回 `status: blocked`，在 `decisions_required` 中列出缺失字段以及需要谁裁决。
- `researcher` 可以继续收集外部证据，但必须记录其服务的候选 revision。

## 6. 一次性风险分类与门禁判定

基线冻结后、进入分解与路由之前，`orchestrator` 在 intake 完成**一次**风险分类，之后下游全部继承：

- 判定每项工作的 **T 类**（T0–T6）与**风险等级**（R-none / R-low / R-moderate / R-high / R-critical），据此选定 **G0/G1/G2**。
- 同时下发该项工作的 **证据档位 `evidence_level`**（L0 / L1 / L1+L2 / Full），随 T 类 / 风险等级一并写入任务卡与交接消息，并对下游 reviewer / QA 继承生效；档位阈值与 SEB 规则见共享技能 `artifact-pyramids/references/evidence-levels-and-seb.md`。
- 分解出的子任务沿用同一门禁模式与证据档位，**不得各自重新判定**；确需变更由 `orchestrator` 出具新判定并记录原因。
- 信息不足时保守升级到 **G2** 与更高证据档位，不猜。

完整分类表、决策矩阵、每道门禁的进入 / 退出条件与回滚规则见 `gate-topology.md`；证据不足时的阻塞 / 降级处置见 `delivery-governance.md` §6.2。

### 6.1 intake 记录块（一次性下发：卡面与交接同值）

intake 判定必须以**可机器解析的固定字段块**同时写入**任务卡 body（卡面）**与 **orchestrator 交接消息**，两处**同值同义**：

```yaml
task_class: T0 | T1 | T2 | T3 | T4 | T5 | T6
risk: R-none | R-low | R-moderate | R-high | R-critical
gate: G0 | G1 | G2
evidence_level: L0 | L1 | L1+L2 | Full
reason: <改动面 / 不可逆性 / 爆炸半径 的一句话依据>
evidence: <基线 revision 或 content hash>（+ 判定所依据的交接物路径）
```

- **六个字段全部必填。** 缺任一字段视为 intake 未完成，不得进入分解与路由。
- **取值逐字取自令牌表**（`gate-topology.md` §3/§4 与 `artifact-pyramids/references/evidence-levels-and-seb.md` §1），不得自造同义词、不得追加说明文字。
- **只写进对话不算下发。** 卡片 body 若缺该字段块，下游按「未收到 intake 判定」处理：停止实现并按保守档位升级上报，不得自行补判。
- **子卡继承同一字段块。** 确需变更由 `orchestrator` 出具新判定并记录原因；下游任何角色不得各自重判（对齐 `gate-topology.md` 硬规则 1）。

### 6.2 intake 检查清单

分解与路由前逐项勾选；未勾选即视为 intake 未完成：

- [ ] 基线含 7 项必备字段，revision / content hash 可稳定定位
- [ ] `task_class` 已判定，且与「改动面 × 不可逆性 × 爆炸半径」描述一致
- [ ] `risk` 已判定；T 类与风险等级指向不同门禁时取**更严**者
- [ ] `gate` 已选定；父子边拓扑与之一致（G1 不含 reviewer 硬父边，G2 含）
- [ ] `evidence_level` 已按 §1 阈值判定，且不低于升级触发器给出的下限
- [ ] `reason` 写明改动面 / 不可逆性 / 爆炸半径，不是复述结论
- [ ] `evidence` 指向可定位的基线 revision / content hash
- [ ] 六个字段已写入**卡片 body**，且与交接消息同值同义
- [ ] G0 / G1 的跳过决策与依据已随交接消息保留
- [ ] 信息不足处已保守升级（门禁→G2，档位→更高档），未自行猜判
- [ ] 子卡继承同一字段块，无子卡重判；若由上游 Flow 分解而来，字段块与父卡一致或已记录变更原因
