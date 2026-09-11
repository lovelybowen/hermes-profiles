# SEB 完整性与证据不足处置

本文件规定 reviewer 在**复用他人证据（SEB，Structured Evidence Bundle）之前**必须执行的逐字段核验，以及发现证据缺失、不一致、档位不足或预算耗尽时的处置与看板路由。

**唯一权威出处：** `skills/artifact-pyramids/references/evidence-levels-and-seb.md`。档位定义（`L0` / `L1` / `L1+L2` / `Full`）、SEB 最小字段、复用前置条件、完整性核验流程与处置决策表均以该文件为准；本文件只把定义落到 reviewer 的**执行动作与阻塞 / 退回路由**上，**不复制其全文**，避免双源漂移。

档位由 intake 一次性下发、下游继承：reviewer 不重新选档、不得自行降档，发现档位不足只能按第 4 节上报升级。

---

## 1. 触发时机

reviewer 在 `kanban_show` 读取交接之后、选择复核深度（见 `evidence-level-verification.md`）之前，先做两件事：

1. 读交接 `evidence` 中的 `evidence_level` 与 SEB 字段：`seb` / `seb_integrity` / `baseline` / `changed_files` / `commands` / `sampling` / `confidence` / `uncovered`。
2. 按第 2、3 节判定这份证据是「可直接复用」还是「必须全量复算」。

**只有核验通过后，未抽样部分才可直接采信**；核验未通过时不存在「部分采信」。

---

## 2. 复用前逐字段核验

对 SEB 内每个字段做**内容寻址核验**，逐条给出 pass / fail：

| # | 字段 | 核验动作 | 失败判定 |
|---|---|---|---|
| 1 | `commit`（固定 SHA） | 与本次被评审的固定 SHA 逐字符比对；不得用「当前工作区 / HEAD」替代 | 不同 SHA → 停止复用 |
| 2 | `baseline` | 与 intake / 需求基线记录的 revision 比对 | 漂移 → 停止复用 |
| 3 | `changed_files[].blob_sha` | 对每个 path 复算 `git hash-object <path>` 并比对，含「应存在 / 应删除」状态 | 任一不一致 → 停止复用 |
| 4 | `changed_files` 覆盖 | 与 `git diff --name-status <baseline>..<commit>` 逐条对齐 | 有遗漏或多余 → 停止复用 |
| 5 | `commands[].exit_code` | 每条门禁命令的退出码与结论一致；门禁二元，非 0 不得记为通过 | 非 0 却记为通过 → 门禁失败 |
| 6 | `commands[].stdout_sha256` | 复算命令输出哈希并比对 | 不一致或不可复算 → 停止复用 |
| 7 | `gate_artifacts[].path`（门禁产物路径） | 路径可达，且实际 `sha256` 与记录一致 | 不可达 / 不匹配 → 停止复用 |
| 8 | `producer` | 产出该证据的 profile 与 run id 可追溯 | 缺失 → 停止复用 |
| 9 | `produced_at`（时间戳） | 记录存在且为 UTC ISO 8601；**只用于审计排序，不作为失效依据** | 缺失 → 停止复用；时间旧**不**构成拒绝理由 |

**非阻断字段：** `schema_version` / `env` / `task_id` 缺失时按第 4 节「非必需字段」处理，标 `seb_incomplete: true` 后允许继续。

> 字段取值口径、核验步骤（Step 1–7）与命令示例以 `artifact-pyramids/references/evidence-levels-and-seb.md` §2–§3 为准；本节不重复其定义。

---

## 3. 终止规则：缺失或不一致即停止复用

任一必需字段**缺失**或**不一致**时，立即停止复用，并把复核升级为**全量复算**（Full 档动作：build / browser / diff / SHA 逐项重跑）。不得：

- 以「大部分字段都对」放行（不存在部分采信）；
- 以「时间紧 / 改动看起来小」自行降档；
- 静默跳过不一致项。

全量复算完成后，在结论中记录触发核验失败的具体字段与原因。

---

## 4. 证据不足与异常处置表

| 情形 | reviewer 处置 | 路由 |
|---|---|---|
| 应 `Full` 却完全没有 SEB | `kanban_block`，`reason` 以 `evidence insufficient` 开头并列出缺失字段 | **退回补证**，补齐后重跑核验；不得进入批准阶段 |
| SEB 必需字段缺失（`commit` / `baseline` / `changed_files` / `commands` / `gate_artifacts` / `producer` / `produced_at`） | `kanban_block`（证据不足） | 退回补证 |
| 实际档位低于风险要求（如按 T5 / T6、安全、公开 API 应为 `Full`，交接却只给 `L1`） | 不在本卡内自行升档 | **退回 orchestrator 升级档位**（升档只允许发生在 intake 决策点） |
| `commit` 不同 / `baseline` 漂移 | 停止复用并触发全量复算 | **全量复算**；同 SHA 前提已被破坏 |
| blob / 产物 hash 不一致 | 停止复用，判定证据被篡改或工作树已变 | 全量复算 + 按 `Risk Approver` 上报风险 |
| 命令 `exit_code` 非 0 却记为通过 | 判定门禁失败（二元结论） | 退回**实现卡** `kanban_request_changes`，不得放行 |
| 非必需字段缺失（`env` / `schema_version` / `task_id`） | 允许复用，标 `seb_incomplete: true` 并写入结论 | 不阻断 |
| 预算耗尽（超出档位轮次 / 秒数上限） | **不得伪装通过**：只做部分裁决，标 `confidence: reduced` 并逐条列出 `uncovered` | 结论交回 orchestrator，由人类责任人决定是否补预算 |

**降级的是置信度，不是门禁要求。** `Full` 档缺 SEB 时不得降级为 `L1` 放行；唯一允许的降级是 `confidence: reduced` + 显式 `uncovered` 清单。`uncovered` 必须逐条可核对（哪些路径 / 命令 / 结论未覆盖），不得写「其余未验证」这类不可核对表述。

---

## 5. `seb_integrity` 取值与 `seb_incomplete` 的区分

| 令牌 | 取值 / 含义 | 使用场景 |
|---|---|---|
| `seb_integrity` | `passed` / `failed` / `not_required` | 复用前完整性核验的结论；`not_required` 仅用于 `L0`（不要求 SEB） |
| `seb_incomplete` | `true` | 非必需字段缺失时的补充标记，可与 `seb_integrity: passed` 并存 |
| `confidence` | `full` / `reduced` | 标 `reduced` 时必须带 `uncovered` |
| `uncovered` | `[<未覆盖项>]` | 仅 `confidence: reduced` 时必填 |

注意：`seb_integrity: failed` 表示**核验失败**（已触发全量复算），不等同于 `seb_incomplete: true`（字段不全但仍可复用）。两者不得互相替代。

---

## 6. 与 G1 / G2 门禁的衔接

- **G1**：发现阻断缺陷（`blocking`）时，在**实现卡**上 `kanban_request_changes`，把复核结论退回原实现者；不在本卡内静默修复。
- **G2**：保持同步强审；证据不足时按第 4 节 `kanban_block`，不因门禁模式放宽证据要求。
- 选用边界：**证据不足 / 门禁失败 → `kanban_block` 或 `kanban_request_changes`**；**仅措辞或非阻断项 → 通过并附注意事项**（阻断协议见 `swarm-verification.md`）。

---

## 7. 平台边界（不得伪装完成）

- 运行时「自动门禁超时降级」「自动全量复算」**不存在**；本节是**文档层纪律**，核验与抽样目前由 reviewer 手工执行。
- 不得把「规则已写入文档」表述为「SEB 复用已自动化」。
- 不修改 reviewer Profile 之外的技能实现。

---

## SOURCES

```
skills/review-methodology/references/seb-integrity-and-insufficiency.md
 -> 本文件：reviewer 侧 SEB 复用前逐字段核验 + 证据不足处置与看板路由
skills/artifact-pyramids/references/evidence-levels-and-seb.md
 -> 唯一权威出处：L0/L1/L1+L2/Full 层深阈值、SEB 最小字段、复用前置条件、核验流程、处置决策表
skills/review-methodology/references/evidence-level-verification.md
 -> 按 evidence_level 选择复核深度（L0 快扫 / L1 单模块 / L1+L2 跨模块 / Full 全量复算）
skills/review-methodology/references/swarm-verification.md
 -> 质量门通过 / 阻断协议与阻断措辞
skills/orchestration-methodology/references/delivery-governance.md
 -> 交接消息治理字段与 orchestrator 侧证据不足处置（§6）
```
