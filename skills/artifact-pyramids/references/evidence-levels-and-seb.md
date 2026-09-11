# 证据等级与 SEB：层深阈值与证据复用纪律

本文件定义产物金字塔的**证据深度档位**（L0 / L1 / L1+L2 / Full）与 **SEB（Structured Evidence Bundle，结构化证据包）** 的复用、完整性核验与不足处置规则。

它回答两个问题：

1. 这个任务该生成多深的金字塔？（第 1 节）
2. 别人的证据我能不能直接采信，凭什么？（第 2–4 节）

**层级命名说明：** `L1` / `L2` / `L3` 是金字塔的层级（摘要 / 分析 / 档案）。证据档位 `L0` / `L1` / `L1+L2` / `Full` 描述**生成到哪一层为止**：`L0` 不生成金字塔，`L1` 只到摘要，`L1+L2` 到分析，`Full` 三层齐备。数量前缀不可混用：`L1` 档位只产生 `01-summary/`，不产生 `03-dossiers/`。

---

## 1. 四档层深阈值

### 1.1 档位定义

| 档位 | 适用场景（intake 触发条件） | 最低产物要求 | 最低证据强度 | 默认预算 |
|---|---|---|---|---|
| **L0** | T0 / T1；单文件且 ≤30 行且无依赖的 T2 / T4；纯状态、阻断、澄清、审批请求 | **不生成金字塔**：不创建 `00-index.md`，不创建任何层级目录。只用结构化交接消息（`status` / `summary` / `evidence` / `risks`） | 变更文件清单；至少一条可复核命令及其 exit code；无改动时给出显式「无改动」声明 | 不需要门禁产物 |
| **L1** | 多文件改动；diff ≤200 行；T3；单模块 T4 | `00-index.md` + `01-summary/` 至少 1 个文件。**不创建空层级目录** | 固定完整 commit SHA；`changed_files` 含 blob hash；每条命令的 exit code 与 stdout hash；`SOURCES` 至少 1 条可达引用 | G1 目标 ≤12 轮 / 300s |
| **L1+L2** | 跨模块改动；新增依赖；接口 / 契约变化 | 在 L1 基础上增加 ≥1 份 `02-analysis/` 维度文件；`SOURCES` 上下都完整 | L1 全部，外加接口 / 依赖变化的对照证据（变更前后签名、依赖锁文件、schema 差异） | G1 目标 ≤12 轮 / 300s |
| **Full** | T5 / T6；数据或环境迁移；公开 API；安全相关；高风险清单命中 | 三层齐备：`00-index.md` + `01-summary/` + `02-analysis/`（按维度）+ `03-dossiers/`（原始证据、命令输出、SEB） | L1+L2 全部，外加完整 SEB（第 2 节）、门禁产物路径、质量门 A/B/C 全过 | G2 目标 ≤30 轮 / 900s |

### 1.2 决策顺序

```
intake 一次性分类（T 档 + 高风险清单）
  → 命中 ≥2 条升级触发器？ → 保守升级一档
  → 落档（L0 / L1 / L1+L2 / Full）
  → 写进任务卡与交接消息的 evidence_level，下游继承
```

**只由 intake 决策一次，下游继承。** 工程师、QA、reviewer 不重新选择档位；发现档位不足时按 1.3 上报升级，不自行降档。

### 1.3 进入下一档所需的证据强度（升级触发器）

命中任一条即升档，多条叠加时取最高档：

| 观察到的信号 | 升到 |
|---|---|
| 改动涉及 ≥2 个文件，或 diff >30 行 | ≥ L1 |
| 出现提交、分支、可交付产物 | ≥ L1 |
| diff >200 行，或超出单模块边界 | ≥ L1（超出模块边界时直接 L1+L2） |
| 跨模块调用、接口签名变化、新增 / 升级依赖、配置 schema 变化 | ≥ L1+L2 |
| 迁移、公开 API、安全相关、T5 / T6、高风险清单命中 | Full |
| 档位无法判定 | 保守升一档（与 intake 的保守升级纪律一致） |
| SEB 完整性核验失败（第 3 节） | 升到 Full 并全量复算 |

**降档只允许发生在 intake 决策点。** 下游不得因为「时间紧」「改动看起来小」自行降档。确需降档必须记录理由、通知 orchestrator，并保留原档位的证据要求。

---

## 2. SEB（结构化证据包）：最小字段

SEB 是任务在交接时打包的**可复用证据单元**。目标：下游（reviewer、后续 Flow、复核者）在不动手重跑的前提下，能判定「这份证据是否仍然有效」。

字段清单（最小集；`*` 为必需，缺失即阻断复用）：

| 字段 | 含义 | 说明 |
|---|---|---|
| `schema_version` * | 证据包版本 | 结构变更时必须递增 |
| `task_id` * | 产生该证据的 Kanban 任务 | 复用时的追溯锚点 |
| `commit` * | 被固定评审的完整 commit SHA | 复用必须同 SHA；不得用「当前工作区」替代 |
| `baseline` * | 实现依据的基点 revision / SHA | 与需求基线 revision 对应 |
| `changed_files[]` * | `path` + `blob_sha`（`git hash-object`）+ 增删行数 | 内容寻址，是防篡改的核心 |
| `commands[]` * | `cmd` + `exit_code` + `stdout_sha256` + `cwd` | 门禁结论必须能追到原始命令与原始输出 |
| `gate_artifacts[]` * | `gate` + `path` + `sha256` | 质量门产物必须可达且哈希匹配 |
| `producer` * | 产生者 profile 与 run id | 谁产出的证据 |
| `produced_at` * | 产生时间（UTC、ISO 8601） | 仅用于记录与排序，**不作为失效依据** |
| `env` | OS / 内核 / 运行时版本 | 命令结论依赖环境时补充 |

**内容寻址原则：** SEB 的有效性由 `commit` + `blob_sha` + `sha256` 决定，与产生时间无关。时间只用于审计排序；「证据太旧」不构成拒绝理由，「内容不一致」才是。

---

## 3. SEB 复用条件与完整性核验

### 3.1 何时可以复用（全部满足才可复用）

| # | 前置条件 |
|---|---|
| 1 | 待采信的固定 SHA 与 SEB 的 `commit` **完全一致**（同 SHA） |
| 2 | `baseline` 与 intake / 需求基线记录的 revision 一致 |
| 3 | `changed_files` 覆盖 `git diff --name-status <baseline>..<commit>` 的全部条目，**无遗漏、无多余** |
| 4 | 逐文件复算的 blob hash 与 `changed_files[].blob_sha` 全部一致（含「文件应存在/应删除」状态） |
| 5 | 每条命令的 `exit_code` 与结论一致（门禁必须二元，非 0 不得记为通过） |
| 6 | `gate_artifacts[]` 路径可达且实际 `sha256` 与记录一致 |
| 7 | 命令的前提条件仍成立（cwd、分支、环境未变） |

任一条不满足 → **停止复用**，按 3.3 处置。不存在「部分满足就部分采信」的中间态。

### 3.2 完整性核验流程（reviewer 先核验，再抽样）

```
Step 1 结构核验：必需字段齐全、类型合法
Step 2 锚点核验：commit == 被评审 SHA；baseline == 基线 revision
Step 3 内容核验：对 changed_files 逐一复算 blob hash 并比对
Step 4 产物核验：gate_artifacts 路径存在 + sha256 匹配；命令 stdout hash 复算
Step 5 覆盖核验：changed_files 与 tree diff 完全对应（无遗漏、无多余）
Step 6 抽样：默认只抽最高风险项（风险序：公开 API / 迁移 / 安全 > 跨模块接口 > 单模块逻辑 > 文档）
Step 7 升级：Step 1–5 任一步失败 → 自动升级为全量复算，标记 seb_integrity: failed
```

抽样规模建议 ≥1 项，且必须覆盖最高风险类别。核验（Step 1–5）通过后，未抽样部分可直接采信——**采信的强度来自内容寻址核验，而不是来自抽样比例。**

### 3.3 缺失或不完整的处置（降级 / 阻断）

| 情形 | 处置 |
|---|---|
| 应 Full 却完全没有 SEB | **阻断**：返回 `status: blocked` 风格交接（证据不足），不得进入批准阶段；补齐后重跑核验 |
| `commit` / `baseline` / `changed_files` 等必需字段缺失 | **阻断复用**：要求补齐，不得以「部分核验通过」放行 |
| 非必需字段缺失（`env`、`schema_version`） | 允许复用，但标记 `seb_incomplete: true` 并写进结论 |
| `commit` 不同或 `baseline` 漂移 | **停止复用 + 全量复算**（同 SHA 前提被破坏） |
| blob hash / 产物 hash 不一致 | 判定证据被篡改或工作树已变 → **全量复算 + 风险上报**，不得静默 |
| 命令 exit code 非 0 却记为通过 | 判门禁失败（二元结论），回到实现者 |
| 预算耗尽（超出档位轮次 / 秒数） | 只允许**部分裁决**：标 `confidence: reduced` 并列出 `uncovered`；不得伪装通过 |

**降级的是置信度，不是门禁要求。** Full 档任务缺 SEB 时，不得降级为 L1 放行；只能阻塞或标记不完整。允许的降级只有：`confidence: reduced` + 显式 `uncovered` 清单。

---

## 4. 交接字段与可检索令牌

交接消息的 `evidence` 至少包含：

```yaml
evidence:
  evidence_level: L0 | L1 | L1+L2 | Full
  commit: <完整 SHA>
  baseline: <revision / SHA>
  changed_files: [<path>, ...]
  commands: ["<cmd> -> exit <code>, stdout_sha256:<hash>"]
  seb: <SEB 文件路径或内联块>
  seb_integrity: passed | failed | not_required
  sampling: <抽样了哪些最高风险项>
  confidence: full | reduced
  uncovered: [<未覆盖项>]     # confidence: reduced 时必填
```

稳定可检索令牌（供 grep / 门禁脚本使用）：

```
L0  L1  L1+L2  Full  SEB  seb_integrity  blob_sha  stdout_sha256
confidence: reduced  uncovered  evidence_level
```

---

## 5. 平台边界（不得声称已实现）

本节规则是**文档层的纪律**，不改变任何运行时行为：

- **运行时「自动门禁超时降级」不存在。** 超时后自动降级、自动全量复算、自动升级档案，都需要平台能力，属平台缺口（C4-4）。
- **抽样与核验目前由 reviewer 手工执行**，没有平台钩子强制。
- 本文档不得被引用为「SEB 复用已自动化」的证据；任何「自动降级已生效」的表述都是不实声称。
- 本文件不修改 reviewer Profile 的技能实现（属需人工批准的范围）。

**预算纪律（软目标）：** 普通 G1 ≤12 轮 / 300s；高风险 G2 ≤30 轮 / 900s。超预算只能部分裁决（第 3.3 节），不能无限运行，也不能伪装通过。

---

## 6. 与其他参考资料的关系

| 参考资料 | 本文件如何扩展它 |
|---|---|
| `pipeline-stages.md` | 定义层级**是什么**；本文件定义**生成到哪一层为止**（L0 档位即第 0 层：不生成金字塔） |
| `quality-gates.md` | 定义完成金字塔后的验证；本文件定义**复用他人证据前**的完整性核验 |
| `output-classification-framework.md` | 决定内容放在**哪一层**；本文件决定**要不要建这些层** |
| `methodology-to-pyramid-mapping.md` | 定义角色的领域产物如何映射到层级；本文件定义 `evidence_level` 由 intake 一次性下发并由下游继承 |

## SOURCES

```
references/evidence-levels-and-seb.md
 -> 本文件：L0/L1/L1+L2/Full 层深阈值 + SEB 复用与完整性核验规则
references/pipeline-stages.md
 -> 三层级定义与生成流程（L0 档位在此为「不生成金字塔」）
references/quality-gates.md
 -> 质量门 A/B/C（金字塔内部验证；与 SEB 复用核验互补）
references/output-classification-framework.md
 -> 层级内容契约（决定内容放哪一层）
references/methodology-to-pyramid-mapping.md
 -> 角色方法论到金字塔层级的映射
<skills-root>/orchestration-methodology/references/delivery-governance.md
 -> 交接消息中的治理字段（commit / changed_files / tests / worktree / branch）
<repo-root>/AGENTS.md「证据等级与 SEB」章节
 -> 上级全局约定；本文件是它在 artifact-pyramids 技能内的落地展开
上游 Kanban 任务 t_567d53e4 的 implementation-plan.md「A3」节
 -> 层深阈值、SEB 最小字段、预算纪律的原始意图（附件随任务，不在本仓库内）
```
