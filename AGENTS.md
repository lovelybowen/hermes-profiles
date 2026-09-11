# Hermes R&D 角色配置集 - Agent 指南

本文档帮助 AI Agent 理解如何使用本仓库中的 R&D 角色配置。

## 仓库结构

```
hermes-profiles/
├── skills/                          ← 共享技能池（真实文件，单一来源）
│   ├── artifact-pyramids/
│   ├── architecture/
│   │   ├── adr-authoring/
│   │   ├── arc42-context/
│   │   ├── architect-pyramid/
│   │   └── c4-diagramming/
│   ├── backend-engineering/
│   ├── debugging-methodology/
│   ├── frontend-engineering/
│   ├── mermaid-diagrams/
│   ├── orchestration-methodology/
│   ├── qa-methodology/
│   ├── research-methodology/
│   ├── researcher-workflow/
│   ├── review-methodology/
│   ├── software-architecture-analysis/
│   ├── systematic-debugging/
│   └── codex-exec-runner/
├── profiles/                        ← Agent 角色配置（技能通过符号链接引用）
│   ├── backend-engineer/
│   ├── debugger/
│   ├── frontend-engineer/
│   ├── orchestrator/
│   ├── qa-engineer/
│   ├── researcher/
│   ├── reviewer/
│   └── technical-architect/
├── scripts/validate_profiles.py
├── .github/ISSUE_TEMPLATE/
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 角色配置的工作方式

本仓库只保留服务于 R&D 生命周期且具有独立上下文、方法论或质量边界的角色。业务价值、交付取舍和风险接受由人类责任人（`Intent Owner` / `Delivery Owner` / `Risk Approver`）承担，不包装为 Hermes Profile。

每个角色配置都是一个目录，包含以下文件：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | **权威运行协议**：第一原则、职责边界、触发模式、加载顺序、输出契约 |
| `config.yaml` | 模型、provider 与工具集（不含密钥） |
| `profile.yaml` | 元数据：描述、必需技能和推荐技能 |
| `README.md` | 面向人的使用指南 |
| `AGENTS.md` | 指向 `SOUL.md` 的索引 + 该角色的上下游接口 |
| `.env.example` | 所需凭据清单（实际 `.env` 被 gitignore） |
| `skills/` | 指向仓库根 `skills/` 池的相对符号链接 |

### 为什么运行协议只放在 SOUL.md

Hermes 把 `$HERMES_HOME/SOUL.md` 作为身份文档注入每个会话。而 `AGENTS.md` 是从**工作目录**向 git 根目录发现的**项目**上下文文件——只有当工作目录恰好是该角色目录时才会被加载。角色的触发模式、加载顺序和交接协议必须每个会话都生效，因此它们放在 `SOUL.md`；`AGENTS.md` 只做索引，避免两份协议漂移。

### 入口

`default` 是外部 ingress，`orchestrator` 是研发准入与编排入口。普通问答可由 default 直接回答；研发请求统一进入 Kanban `triage` intake，由 default 保留原始请求、项目、验收条件和来源标识，并固定交给 `orchestrator`。其余 7 个角色由 orchestrator 按条件通过 Kanban 任务拉入，不直接面向用户接单。

在 Feishu/Cron/Webhook/CLI 多触发源部署中，default 不承担研发编排，而是创建 assignee 为 `orchestrator` 的 intake 任务；`kanban.orchestrator_profile` 必须显式设为 `orchestrator`。

### 角色之间的协调方式

- 编排是**集中式**的：`orchestrator` 分解工作、建立 Kanban 任务与依赖边、按条件路由专家、汇总证据。
- 代码执行在 Linux 本地完成：工程类 Profile 使用 Hermes 自带 `codex` 技能，在 Kanban 独立 worktree 中调用 `codex exec`。
- 交接是**结构化消息**（`status` / `summary` / `artifact` / `evidence` / `risks` / `decisions_required`），不是自然语言散文，也不是单纯一个路径。
- 产物金字塔是**详细交付物**；状态、阻断、澄清和审批请求不生成金字塔。
- 人类责任人不是可调度的 Profile。

## 全局 R&D 流程规则

default 只负责入口协议，不自行决定业务语义、风险接受或交付基线；这些事项由 orchestrator 和人类责任人按 Kanban 记录处理。orchestrator 在 intake 时**一次性**确定任务类型与风险等级，下游继承该决定并在交接中记录依据：

| 风险等级 | 门禁 | Reviewer 拓扑 |
|---|---|---|
| T0 / T1 | G0 | 不创建 reviewer |
| T2 | G1 | reviewer 可选轻量检查，不作为下游父卡 |
| 普通 T3 / T4 | G1 + QA | reviewer 轻量；QA 必须执行验证 |
| T5 / T6、信息不足或高风险 | G2 | 同步 reviewer + 完整质量门 |

G1 交接必须含 `review_status: pending`；发现缺陷时标记综合产物 `superseded` 并回到实现 / QA。

### 证据等级与 SEB

按风险选择证据层级：L0（单文件、≤30 行、无依赖）→ L1（多文件、≤200 行或单模块）→ L1+L2（跨模块、新依赖或接口变化）→ Full（迁移、公开 API、安全、高风险）。

复用 SEB 时必须核对固定 SHA、baseline、改动文件 blob hash、命令 exit code/stdout hash、gate 产物路径、产生者和时间；缺失或不一致即停止复用并升级为全量复算。预算耗尽不得伪装为通过，必须标记 `confidence: reduced` 并列出 `uncovered`。

### 通知

默认 exception-only：普通创建、进展、中间完成、常规重试和内部 reviewer 流转只写 Kanban；仅人工裁决、`needs_input` / `capability`、崩溃 / 超时 / 放弃、风险异常、用户主动询问及需求根卡最终结果推送 Feishu。高风险、P0、SEB 异常或共享写事故不得静默。

### 工作区路由

- 讨论 / 研究 / 规划：显式 `scratch`
- 非代码串行资产：受控 `dir`（**绝不用于代码**）
- 同一 Flow 的低风险串行代码任务：复用 Flow worktree（逐字传递相同 path + branch）
- 并行重叠、独立分支、破坏性实验或失败隔离：per-task worktree

worktree 任务缺少明确 `workspace_path` / branch 锚点时不得建卡；交付物必须通过 Kanban `artifacts` 声明。

### 停止语义

停止请求的权威接收方为 orchestrator，状态机为 `active → stop_requested → draining → settled(stopped)`；停止后不新建或解锁下游，后完成的 reviewer 标记 `post_stop: true`。

### 迁移

流程迁移遵循 `observe → shadow → gray rollout → expand → default`。shadow 只记录建议，不改变实际参数；gray rollout 先覆盖低风险任务，expand 再覆盖普通任务；高风险始终 G2。P0 漏发、SEB 完整性漏检、共享写事故 / 产物丢失、逃逸率或延迟连续超阈值、停止后下游自动解锁，均按主题回滚。

运行中 worker 取消、自动门禁超时降级、声明式门禁原语和事件分类器 / roll-up 目前属于平台缺口，不得声称已实现。

## 技能约定

共享池中的技能遵循渐进披露原则：

- `SKILL.md` 承载四件事：触发条件（`description` + 使用时机）、核心流程或最小可执行规则、参考文件索引，以及必须在加载时就生效的硬约束
- 长步骤、示例、兼容性表与操作细节放入 `references/`，通过 `skill_view(name, file_path=path)` 按需加载
- 判断标准：**`SKILL.md` 加载后应当足以决定接下来加载哪个参考文件**，而不必内联全部细节

## 技能的可达性

Hermes 只索引名为 `SKILL.md` 的文件，且 `skill_view` 不支持 `父/子` 形式的技能名。
阶段文档、阶段明细等**不能**作为「子技能」按名字加载，必须放入 `references/` 并通过 `file_path` 加载。
- 技能应能在原生 Hermes 安装中工作，不依赖 council、cashew 或其他 Agent 专用基础设施
- 研究类技能默认使用 Hermes 原生工具（`web_search` / `web_extract` / browser）；外部工具只能作为**可选增强**，不得作为前置依赖

## 符号链接规则

- 所有符号链接都必须使用**相对路径**，不能使用绝对路径
- 从 `profiles/<name>/skills/` 出发，目标为 `../../../skills/<skill-name>`
- 从 `profiles/<name>/skills/` 指向分类技能时为 `../../../skills/<category>/<skill-name>`
- 符号链接由 Git 以模式 `120000` 跟踪，在 macOS/Linux 上执行 `git clone` 后可正确重建
- 用普通文本文件冒充符号链接（Git 模式 `100644`）**不会被 Hermes 加载**，会导致 `Skills: 0`

## 凭据与运行时状态

Profile 目录通过符号链接直接位于 Git 仓库内，因此 Hermes 的运行时产物会落在仓库目录中。`.gitignore` 已排除：

- 凭据：`profiles/*/.env`、`profiles/*/auth.json`
- 状态：`state.db*`、`sessions/`、`memories/`、`logs/`、`cron/`、`cache/`、`*.lock`
- 其他：`checkpoints/`、`workspace/`、`home/`、`skills/.hub/`

新增任何会在 Profile 根目录产生文件的配置时，同步补充 `.gitignore`。

### 已知上游交互：符号链接技能会被误判为「未安装技能」

Hermes 启动时用 `Path(skills_dir).rglob("SKILL.md")` 判断 Profile 是否已安装技能。Python 的
`rglob` **不会跟随目录符号链接**，因此一个「技能全是相对符号链接」的 Profile 会被判定为空，
Hermes 随后会把自带技能重新播种进来（`.no-bundled-skills` 标记只能把它限制为少量「essential」技能）。

表现：运行过一次 `hermes -p <profile> chat` 后，`profiles/<profile>/skills/` 下会出现真实目录
（如 `autonomous-ai-agents/`）、`.bundled_manifest`、`.hub/`、`.usage.json`。

同一根因的第二个症状：技能文件经符号链接解析后落在 `<repo>/skills/`，不在 Profile 自己的
`skills/` 下，因此每次加载技能都会附带一条非阻断警告
`skill file is outside the trusted skills directory (~/.hermes/skills/)`（`success` 仍为 `true`）。

两者都源自同一件事：**符号链接布局不符合 Hermes 对「技能就位于 `$HERMES_HOME/skills/` 之下」的路径假设**。
改为真实副本安装（仓库仅作分发源）可同时消除这两个症状。

处理：

```bash
./scripts/clean_profile_runtime.sh          # 清理运行时状态
python3 scripts/validate_profiles.py        # 校验（会拦截意外混入的真实技能目录）
```

`.no-bundled-skills` 标记**必须提交**，否则全新克隆第一次运行时会被播种整套自带技能。
在决定「仓库是分发源还是运行目录」之前，把 Profile 目录直接符号链接进仓库并在此运行，
只是开发期的便利做法。


## 贡献流程

1. 从 `main` 创建分支。
2. 添加或修改角色配置文件。
3. 添加新技能时，先将技能目录放入 `skills/`，再从角色配置创建**相对**符号链接。
4. 运行 `python3 scripts/validate_profiles.py`，确认结构与符号链接全部通过。
5. 创建 PR，并清楚说明角色职责及其所需技能。

## 验证角色配置

提交 PR 前，请检查：

- [ ] `SOUL.md` 存在，说明第一原则、职责边界与输出契约
- [ ] `config.yaml` 存在，含模型与工具集，且**不含任何密钥**
- [ ] `profile.yaml` 存在、YAML 有效且列出必需技能
- [ ] `README.md` 存在，并包含安装、配置和技能参考
- [ ] `AGENTS.md` 存在，指回 `SOUL.md` 作为权威协议来源
- [ ] `.env.example` 存在（如该角色需要凭据）
- [ ] `skills/` 中的所有符号链接都能解析到共享池中的真实文件
- [ ] 符号链接为相对路径，且 Git 模式为 `120000`
- [ ] `python3 scripts/validate_profiles.py` 通过
- [ ] `hermes -p <name> skills list` 的启用技能数与 `profile.yaml` 一致

## 相关仓库

- https://github.com/groktopus/artifact-pyramids - 产物金字塔规范
- https://github.com/architecture-decision-record/architecture-decision-record - ADR 社区标准
