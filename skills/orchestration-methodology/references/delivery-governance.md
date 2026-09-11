# 交付治理：风险驱动路由、工作区隔离、质量门与审批矩阵

编排者在分解和路由实现类工作时遵循的治理规则。目标：让每项工作按**风险等级**路由到正确的工作区、角色和门禁；让并行实现互不干扰；让每道质量门有可验证的输入；让不可逆动作停在人类责任人手里。

**风险分类与门禁判定在 intake 一次性完成，下游继承**（见 `gate-topology.md`）。本文件负责把该判定落到**工作区路由（workspace routing）**与执行纪律上。

## 1. 风险驱动路由（intake 决策一次，下游继承）

`orchestrator` 在 intake 依据已确认基线判定每项工作的 **T 类**（T0–T6）与**风险等级**（R-none / R-low / R-moderate / R-high / R-critical），据此选定 **G0/G1/G2**，并同时决定**工作区路由**、**参与角色**与 **QA 门**。T 类/风险等级的定义与门禁进入/退出条件以 `gate-topology.md` 为唯一权威出处；本节只把它映射到工作区与角色。

| 风险等级 | 典型 T 类 | 工作区路由（见 §2） | 参与角色 | 门禁 | QA 门 |
|----------|-----------|---------------------|----------|------|-------|
| **R-none** | T0 答问 / T1 讨论研究 | **R0** `scratch`（只读，不写文件） | 仅 `orchestrator`，直接回答 | **G0** | 否 |
| **R-low** | T2 文档 | **R0'** `dir:<工作线绝对路径>`（非 git 资产）或 **R2** worktree（git 仓库内文档） | 作者 + `reviewer`（可抽样） | **G1** | 否 |
| **R-moderate** | T3 配置 | **R2** Flow 级复用；非代码配置走 **R1/R1'** | 按拓扑的 engineer + `qa-engineer` + `reviewer` | **G1**；影响生产 / 密钥 / CI → **G2** | 视影响面 |
| **R-moderate** | T4 普通代码 | **R2** Flow 级 worktree 复用；命中 **S1–S4** 任一 → **R3** per-task | engineer（按系统拓扑）+ `qa-engineer` + `reviewer` | **G1 + QA 门** | 是 |
| **R-high** | T5 高风险代码 / 架构 | **R3** per-task worktree（强制隔离） | 条件性 `researcher` / `technical-architect` + engineer + `qa-engineer` + `reviewer` + `Risk Approver` | **G2** | 是 |
| **R-critical** | T6 安全 / 合规 | **R3** per-task worktree + 最小权限 / 密钥隔离 | 同上 + `Risk Approver` | **G2** | 是 |

规则：

- **取更严者。** 当 T 类与风险等级指向不同门禁或不同隔离强度时，取更严的一侧。
- **信息不足保守升级。** 无法判定改动面、爆炸半径或是否并发写时，工作区按 **R4** 保守升级、门禁按 **G2**，不猜。
- **下游继承、不得各自重判。** 分解出的子任务沿用 intake 的门禁模式与工作区档位；确需变更由 `orchestrator` 出具新判定并记录原因（对齐 `gate-topology.md` 硬规则 1）。
- **跳过必须记录。** G0/G1 的判定、风险等级、依据与所跳过的工作区/角色，一并写入 orchestrator 交接消息（对齐「跳过专家要记录原因」）。
- **只读任务不得落到写工作区。** R-none/R0 是默认；即使 board 配了 `default_workdir`，只读任务的 path 也不得被填（机制保证，见 §2.4）。

## 2. 工作区隔离与 workspace kind 决策

### 2.1 工作区类型

| 任务类型 | 工作区 | 完成后 |
|---|---|---|
| 代码实现（后端 / 前端 / 缺陷修复） | 独立 Git worktree，一任务一 worktree | 保留 |
| 代码评审 | 只读被评审的 worktree | — |
| 设计、研究、文档 | 项目约定目录（如 `docs/ai-rnd/<slug>/`） | 保留 |
| 一次性分析 | Kanban `scratch` 工作区 | **删除**（必须显式声明产物） |

规则：

- **禁止两个实现任务共用同一个工作区。** 并行实现必须各自持有 worktree。
- 实现类任务不得直接改动主分支，也不得改动其他任务的工作区。
- Kanban `scratch` 工作区在任务完成时被删除。产物必须先通过 `kanban_complete(artifacts=[...])` 声明，否则视为未交付。
- `dir:<绝对路径>` 与 `worktree` 工作区在完成后保留。

### 2.2 路由规则（R0–R5）

把 §1 的风险等级落到具体建卡参数：

| 规则 | 触发条件 | 决策 | 必须同时写入建卡参数 |
|------|----------|------|----------------------|
| **R0** | 无写操作：讨论、研究、规划、只读审查、证据核对、汇总 | `scratch` | 显式 `workspace_kind="scratch"`（防 board 默认值污染） |
| **R0'** | R0 且中间产物须跨任务留存 | `dir:<Flow 目录>` | `workspace_kind="dir"`, `workspace_path=<绝对路径>` |
| **R1** | 串行、低冲突的**非 git** 资产修改 | `dir:<工作线目录>` | 同上；一「工作线」一目录，跨任务复用 |
| **R1'** | 并行写非 git 资产 | `dir:<每写者子目录>` | 同上；body 内声明文件所有权 |
| **R2** | 代码修改，同 Flow 内串行、无重叠并行、非破坏性 | `worktree`（**Flow 级复用**） | 首卡：`workspace_kind="worktree"` + `workspace_path`（或 board `default_workdir`）+ `branch_name="wt/<flow-root-id>"`；后续卡：**逐字相同的 path + branch** |
| **R3** | 代码修改 + S1/S2/S3/S4 任一 | `worktree`（**per-task**） | `workspace_kind="worktree"`；path 显式 `<repo>/.worktrees/<task-id>` 或省略（board 锚点）；`branch_name="wt/<task-id>"` 或项目分支 |
| **R4** | 是否写 / 是否并发 / 是否重叠 / 仓库状态**未知** | **保守升级**：只读→`scratch`；写→`worktree` | 升级后按 R2/R3 参数 |
| **R5** | 选了 `worktree` 但既无 `workspace_path` 又无 board `default_workdir` | **不建卡**，先补锚点 | — |

### 2.3 隔离信号（S1–S4）

**S1** 与其他任务并行且可能触碰重叠文件；**S2** 需要独立分支（PR 发布、按 SHA 独立评审、provenance 追溯）；**S3** 破坏性/不确定性实验（rebase、依赖大升级、重构、迁移、批量改写）；**S4** 需独立工作树使失败不污染主工作树。

**保守升级的方向**：按**隔离强度**升级，而不是按「持久性」升级。`dir` 是三者中**唯一共享可变**的工作区，隔离最低；因此「信息不足」绝不能落到 `dir`。

### 2.4 安全约束（不可绕过）

- **`dir` 绝不用于代码。** 共享可变的工作区只承载非 git 资产；代码一律走 `worktree`。
- **Flow 级复用必须逐字传同 path + branch**，并校验实际 checkout 分支；否则机制会静默回退成「各写各的」，隔离看似成立、实为失效。
- **同一共享工作线的多个写者用硬 DAG 父边串行**，天然保证任一时刻只有 1 个写者；无工作区级锁（`claim_lock` 是任务级）。
- **R5 硬失败在建图阶段**，不要留到 dispatcher `spawn_failed`。
- 人类显式 `--workspace` / `workspace_kind=` 覆盖路由建议，但应在任务注释记录理由。

### 2.5 Linux Codex 执行

工程 Profile 在 Kanban 提供的本地独立 worktree 中调用 Hermes 自带 `codex` 技能。工作区、Codex 当前目录、Git branch 和测试环境必须属于同一 Linux worktree；跨角色交接使用 task id、branch、commit SHA 和 repo-relative artifact。需要机器解析时可额外使用 Codex 的 `--json` 输出，但不依赖自定义 Runner。

## 3. 分支与提交约定

```
task/<task-id>-<short-slug>
```

- 分支从基线 revision 对应的提交切出。
- 交接证据必须包含 `commit`（完整 SHA）与 `changed_files`。
- `reviewer` 只评审这个 SHA，不评审「当前工作区」。
- 一个实现任务可以多次提交；交接时给出最终 SHA。
- 交接给 `reviewer` 的证据必须同时携带 `evidence_level`（L0 / L1 / L1+L2 / Full）与 `seb_integrity`（passed / failed / not_required）；缺任一项即视为证据不足，按 §6.2 处理，不得建 reviewer 卡。

## 4. 质量门顺序

```
实现完成
  → qa-engineer 执行验证（自动化测试、lint、构建、契约检查）
      ├─ 已知实现缺陷     → 原实现者
      └─ 未知根因 / 反复失败 → debugger → 原实现者
  → reviewer 对固定 SHA 独立评审
      ├─ 需修改 → kanban_request_changes(reason=...) → 原实现者
      └─ 通过   → 人类批准阶段
```

- QA 与 Reviewer 是两道独立的门，不能合并成一次检查。门禁强度（G0/G1/G2）与拓扑表达见 `gate-topology.md`。
- 门禁结论必须是二元的（通过 / 失败），并附原始命令与原始输出。
- `reviewer` 不修复代码；`qa-engineer` 不做最终裁定。
- `debugger` 的修复完成后，受影响的验证必须由 `qa-engineer` 重新执行。
- 参与角色按 §1 的风险等级路由：`researcher` / `technical-architect` 条件性参与，`debugger` 仅在根因未知或反复失败时参与。

## 5. 审批矩阵

| 操作 | 默认权限 |
|---|---|
| 在任务 worktree 内读 / 写文件 | Agent 可执行 |
| 运行测试、lint、构建、本地脚本 | Agent 可执行 |
| 本地 `commit` 到任务分支 | Agent 可执行 |
| `push` 到远端 | **需要人类批准** |
| 创建 / 更新 PR | Agent 可执行，但必须回传可访问链接 |
| 合并 PR | **需要人类批准** |
| 部署到测试环境 | **按 `Delivery Owner` 策略** |
| 部署到生产 | **需要人类批准** |
| 修改数据库、基础设施、密钥 | **需要 `Risk Approver` 批准** |
| 接受残余风险 / 例外 | **需要 `Risk Approver` 批准** |
| 修改已确认需求基线 | **需要 `Intent Owner` 批准** |

人类责任人不是可调度的 Hermes Profile：`Intent Owner`（业务价值与语义）、`Delivery Owner`（技术范围与交付取舍）、`Risk Approver`（高风险例外与残余风险）。

## 6. 交接消息中的治理字段

```yaml
status: completed | blocked | review_required | needs_decision
evidence:
  evidence_level: L0 | L1 | L1+L2 | Full
  commit: <完整 SHA>
  baseline: <revision / SHA>
  changed_files: [<path + blob_sha + 增删行数>]
  commands: ["<cmd> -> exit <code>, stdout_sha256:<hash>"]
  seb: <SEB 路径或内联块>
  seb_integrity: passed | failed | not_required
  sampling: <抽样的最高风险项>
  confidence: full | reduced
  uncovered: [<未覆盖项>]        # confidence: reduced 时必填
  tests: "原始命令 + 结果"
  worktree: <path>
  branch: task/<id>-<slug>
  gate: G0 | G1 | G2
  task_class: T0..T6
  risk: R-none | R-low | R-moderate | R-high | R-critical
risks: [...]
decisions_required: [...]
```

`decisions_required` 中每一项都要写清：需要谁裁决、裁决什么、不裁决的后果。

### 6.1 与 `reviewer` 交接的证据要求

`evidence_level` 与 SEB 的定义、最小字段、复用前置条件与完整性核验流程以共享技能 `artifact-pyramids/references/evidence-levels-and-seb.md` 为**唯一权威出处**；本节只规定 orchestrator 在**建 reviewer 卡之前**必须保证什么。

- **档位由 intake 一次性下发、下游继承。** `evidence_level`（L0 / L1 / L1+L2 / Full）在 intake 随 T 类 / 风险等级一并判定，写入任务卡与交接消息；`reviewer`、engineer、`qa-engineer` 不得各自重选档位，发现档位不足只能按 6.2 上报升级。
- **建卡前校验证据包完整性。** 建 reviewer 卡前，被交接物必须携带本节 YAML 中的 `evidence_level`、`commit`、`changed_files`（含 `blob_sha`）、`commands`（含 `exit_code` / `stdout_sha256`）、`seb`、`seb_integrity`。任一必需字段缺失 → 证据不足，按 6.2 处理，**不得**以「先让 reviewer 看看」为由建卡。
- **完整性核验由 reviewer 执行，orchestrator 不代替。** 核验与抽样的执行属 `reviewer` 的工程技能，本文件不修改其实现；orchestrator 的职责是保证被交接的固定 SHA 与 SEB 一致，且不得把「文档写了规则」表述为「运行时已自动核验」。
- **`L0` 例外。** `L0` 档位不生成金字塔、不要求 SEB；仅需变更文件清单加至少一条可复核命令及其 exit code，无改动时给出显式「无改动」声明。

### 6.2 证据不足时的阻塞与降级

发现档位不足或 SEB 缺失 / 不一致时按下列处置，**降级的是置信度，不是门禁要求**：

| 情形 | orchestrator 处置 |
|---|---|
| 应 `Full` 却完全无 SEB | **阻断**：不建 reviewer 卡、不进入批准阶段；以 `status: blocked` 式交接，列出缺失字段与补齐责任角色 |
| `commit` / `baseline` / `changed_files` 等 SEB 必需字段缺失 | **阻断复用**：退回原生产者补齐，不得以「部分核验通过」放行 |
| 实际产物低于 intake 下发的 `evidence_level` | 退回原生产者升档补齐；**不得自行降档**（降档只允许发生在 intake 决策点） |
| `commit` 不同或 `baseline` 漂移 | 停止复用并触发全量复算，退回受影响分支重跑 |
| blob / 产物 hash 不一致 | 判定证据被篡改或工作树已变 → 全量复算 + 按 `Risk Approver` 升级风险 |
| 预算耗尽（超出档位轮次 / 秒数） | 只允许**部分裁决**：标 `confidence: reduced` 并列出 `uncovered`；不得伪装通过 |
| 非必需字段缺失（`env`、`schema_version`） | 允许继续，但标 `seb_incomplete: true` 并写入结论 |

处置后的重路由仍遵循 §4 质量门顺序与 `workflow-monitoring.md` 的门禁恢复表。

## 7. 平台边界（不得伪装完成）

下列能力在平台源码中**不存在**，本文件只做**文档纪律**，不得声称已在运行时生效；需要时另立平台卡：

- **`kanban.workspace_routing` 配置键不存在** —— `config_defaults.py` 的 `"kanban"` 默认 schema 与 `/root/.hermes/config.yaml` 的 `kanban:` 段都没有该键。**因此本文件描述的 workspace routing 目前完全由 `orchestrator` 建卡参数纪律实现，运行时没有开关、没有 shadow 模式、没有 `dir` 白名单机制。** 不得把「规则已写入文档」描述为「路由已启用」。
- 门禁**自动超时降级**（把超时自动转为「部分裁决 + `confidence: reduced`」）不存在。
- 运行中 worker **取消 / 中断**不存在（kanban 工具集与 CLI 子命令均无 cancel/stop/kill）。
- **声明式可选 / 条件门禁原语**不存在（`kanban_create` 只有 `parents` 硬父边，无 `optional` / `condition` / `gate` 字段）。

逐条源码证据与关联缺口见平台缺口报告 `/root/kanban-evidence/t_aaacca5c/02-analysis/02-platform-gaps.md`。

SOURCES

```
/root/hermes-profiles/skills/orchestration-methodology/references/gate-topology.md
 -> §1 一次性分类纪律、§2 T0–T6 定义、§3 风险等级、§4 决策矩阵：本文件 §1 的上游权威出处
/root/hermes-profiles/skills/orchestration-methodology/SKILL.md
 -> 编排生命周期与门禁拓扑导航
/root/hermes-profiles/skills/orchestration-methodology/references/specialist-routing.md
 -> §1「参与角色」列引用的专家触发条件
/root/hermes-profiles/skills/artifact-pyramids/references/evidence-levels-and-seb.md
 -> 证据档位 L0/L1/L1+L2/Full 与 SEB 复用 / 完整性核验的唯一权威出处；§3、§6.1、§6.2 的依据
/root/kanban-evidence/t_6dcddd85/02-analysis/02-routing-policy.md
 -> §2 R0–R5 路由规则、§2.3 S1–S4 隔离信号、§2.4 安全约束的原始设计
/usr/local/lib/hermes-agent/hermes_cli/config_defaults.py
 -> kanban 默认 schema（无 workspace_routing 键），§7 平台边界的证据
/root/kanban-evidence/t_aaacca5c/02-analysis/02-platform-gaps.md
 -> 六类平台缺口逐条源码证据
```
