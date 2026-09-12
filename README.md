# Hermes 角色配置集

这是面向 AI Native R&D 协作的 Hermes 角色配置集。每个角色配置都封装角色身份（`SOUL.md`）、技能依赖、运行配置（`config.yaml`），可作为 Hermes Agent 部署。

想快速向团队介绍定位、协作流程、产物金字塔和 Hermes 嵌入方式，请先阅读[对外说明文档](docs/hermes-profiles-guide.md)。

这些角色配置具有明确的设计主张，并采用 Hermes 原生模式：

- 产物金字塔输出格式（渐进披露、以路径作为交接内容）
- 结构化交接契约（状态 + 摘要 + 产物路径 + 证据 + 风险 + 待裁决事项）
- 基于技能的方法论加载（`skill_view` → 加载参考资料）
- 使用 Hermes 看板开展多 Agent 编排（集中式调度，非自由互聊）
- 使用 Hermes Profile 系统隔离角色

**角色配置**（`SOUL.md` + `config.yaml` + `profile.yaml`）是 Hermes 专用内容，通常无法直接用于其他 Agent 运行环境。但 `skills/` 下采用 `SKILL.md + references/` 结构的**技能**方法论遵循 [Agent Skills 开放标准](https://www.agensi.io/learn/agent-skills-open-standard)。Claude Code、Codex CLI、Cursor、Gemini CLI、OpenClaw、GitHub Copilot、Windsurf 等 20 多种编码 Agent 均采用该标准，因此这些技能具有良好的可移植性。

## 仓库结构

```
hermes-profiles/
├── skills/                             ← 共享技能池（真实文件，单一来源）
│   ├── architecture/
│   │   ├── adr-authoring/
│   │   ├── arc42-context/
│   │   ├── architect-pyramid/
│   │   └── c4-diagramming/
│   ├── artifact-pyramids/
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
│   └── systematic-debugging/
├── profiles/                           ← 角色配置（每个可独立安装为 distribution）
│   ├── backend-engineer/               ← API 实现、服务逻辑、数据库访问
│   ├── debugger/                       ← 根因分析、错误诊断
│   ├── frontend-engineer/              ← UI 组件、状态管理、API 集成、性能
│   ├── orchestrator/                   ← 基线准入、任务分解、专家路由、质量门监控
│   ├── qa-engineer/                    ← 测试策略、自动化、质量门
│   ├── researcher/                     ← 深度调查、证据综合
│   ├── reviewer/                       ← 代码/架构评审、质量门
│   └── technical-architect/            ← 系统架构：C4 + ADR + arc42
├── plugins/rd-approval/                ← 审批插件（根级为单一来源，物化进 orchestrator）
├── scripts/
│   ├── sync_skills.py                  ← 按 profile.yaml 依赖物化技能副本
│   ├── validate_profiles.py            ← 结构 / manifest / 副本一致性校验
│   ├── publish.sh                      ← 发布单角色到独立 distribution 仓库
│   └── install-all.sh                  ← 一键安装 / 更新全部 8 个角色
├── docs/hermes-profiles-guide.md       ← 对外说明文档（定位、流程、嵌入方式）
├── .github/workflows/profile-checks.yml ← CI：校验 + README 覆盖检查
├── .gitignore                          ← 排除凭据与运行时状态
├── AGENTS.md / CONTRIBUTING.md / IDEA.md
└── README.md
```

工程执行类角色（backend/frontend/qa/debugger）在 Linux 本地 worktree 中使用 Hermes 自带 codex 技能调用 `codex exec` 完成实现。

仓库根 `skills/` 是技能的**单一来源**；各角色 `skills/` 下的副本由 `scripts/sync_skills.py` 按 `profile.yaml` 的依赖声明从共享池物化为**真实文件**。不再使用符号链接：`hermes profile install` 会硬性拒绝含 symlink 的 payload，且 Windows 克隆（`core.symlinks=false`）会把 symlink 退化为文本文件。修改共享池后必须运行 `python3 scripts/sync_skills.py` 重新物化并提交。

每个角色配置包含：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | **权威运行协议**：第一原则、职责边界、触发模式、加载顺序、输出契约 |
| `config.yaml` | 模型、provider 与工具集（orchestrator 额外启用 `kanban`） |
| `profile.yaml` | 元数据与技能依赖声明（sync_skills 据此物化副本） |
| `distribution.yaml` | Hermes distribution manifest：name（与目录名一致）、version、env_requires |
| `README.md` | 面向人的使用指南 |
| `AGENTS.md` | 指向 `SOUL.md` 的索引 + 上下游接口 |
| `skills/` | 从仓库根共享技能池物化的真实副本 |
| `plugins/` | （仅 orchestrator）rd-approval 插件副本 |

## 使用角色配置

本仓库是**维护源**（monorepo 单一来源）；每个角色发布为独立的 distribution 仓库，安装者用 Hermes 原生命令按需安装：

| 角色 | distribution 仓库 | 职责 |
|---|---|---|
| `orchestrator` | `github.com/lovelybowen/orchestrator-agent` | 研发准入、任务分解、专家路由、质量门监控 |
| `researcher` | `github.com/lovelybowen/researcher-agent` | 深度调查、证据三角验证 |
| `technical-architect` | `github.com/lovelybowen/technical-architect-agent` | 系统架构：C4 + ADR + arc42 |
| `backend-engineer` | `github.com/lovelybowen/backend-engineer-agent` | API 实现、服务逻辑、数据库访问 |
| `frontend-engineer` | `github.com/lovelybowen/frontend-engineer-agent` | UI 组件、状态管理、API 集成、性能 |
| `qa-engineer` | `github.com/lovelybowen/qa-engineer-agent` | 测试策略、自动化、质量门 |
| `debugger` | `github.com/lovelybowen/debugger-agent` | 根因分析、错误诊断 |
| `reviewer` | `github.com/lovelybowen/reviewer-agent` | 代码/架构评审、证据核验 |

```bash
# 安装单个角色
hermes profile install github.com/lovelybowen/orchestrator-agent --alias

# 或一键安装全部 8 个角色
# 方式一：克隆本仓库后执行（适用于任何可见性）
git clone https://github.com/lovelybowen/hermes-profiles.git && cd hermes-profiles
./scripts/install-all.sh
# 方式二：直接管道执行（仅当本仓库为 public 时可用）
curl -fsSL https://raw.githubusercontent.com/lovelybowen/hermes-profiles/master/scripts/install-all.sh | bash

# 准备凭据（安装器已生成 .env.EXAMPLE）
cp ~/.hermes/profiles/orchestrator/.env.EXAMPLE ~/.hermes/profiles/orchestrator/.env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 启动
hermes --profile orchestrator

# 跟进新版本（memories / sessions / 本地 config.yaml 不受影响）
hermes profile update orchestrator
```

> **重要**：8 个角色必须使用 manifest 中的原始名字安装（不要用 `--name` 改名），否则 orchestrator 的 Kanban 按名路由会断链。
>
> 开发期可从本仓库本地直装测试：`hermes profile install ~/hermes-profiles/profiles/orchestrator --name orch-dev`（测试专用名，避免占用正式 profile 名）。

角色的运行协议以 `SOUL.md` 为准；`config.yaml` 里的 `toolsets` 决定工具集，`profile.yaml` 里的 `skills` 是依赖声明（副本由 `sync_skills.py` 物化，随 distribution 一并安装）。

## 入口

**`orchestrator` 是研发流程的唯一入口；`default` 是部署侧的投递通道（ingress），不是研发决策角色。** 所有触发源（Telegram/Feishu、Cron 定时读取需求仓库、Webhook、CLI）产生的研发请求，都以 assignee 为 `orchestrator` 的 Kanban `triage` intake 任务进入流程，保留原始请求、项目、验收条件和来源标识。非研发类操作（日常问答、Hermes 自身维护、配置调整）由 `default` 直接处理，不进 R&D 流程；`default` 不直接改业务代码、不调用工程 Profile。

```
你（需求 / 变更请求，来自 TG / Feishu / Cron / Webhook / CLI）
    ↓
default（部署侧投递通道，只做分流：研发请求 → Kanban intake，其余直接处理）
    ↓ Kanban intake（assignee: orchestrator）
orchestrator                    ← 研发流程唯一入口：准入、分解、路由、汇总
    ├─ 基线未就绪 → 形成候选 revision，交回 Intent Owner 确认
    ├─ researcher               （外部证据不足时）
    ├─ technical-architect      （契约 / 数据模型 / 部署拓扑 / 质量属性受影响时）
    ├─ qa-engineer              （实现前定义验证策略）
    ├─ backend / frontend        （独立 worktree 实现）
    ├─ qa-engineer              （实现后执行验证）
    ├─ debugger                 （根因未知或反复失败时）
    └─ reviewer                 （G2 同步必需；G1 默认轻量）
    ↓
Intent Owner / Delivery Owner / Risk Approver   ← push / 合并 / 部署 / 风险接受
```

其余 7 个角色是**按需参与者**，由 `orchestrator` 通过 Kanban 任务拉入，不直接面向用户接单。

触发源（Telegram/Feishu、Cron 读取需求仓库、Webhook、CLI）通过 `default` 投递：只有基线需求开发会创建 assignee 为 `orchestrator` 的 intake 任务，其余场景 `default` 直接处理；编排和执行仍由 Kanban Flow 完成，`kanban.orchestrator_profile` 必须显式设为 `orchestrator`。启动编排入口的命令见上文「使用角色配置」。

## 工作流

```
自然语言需求
  → default 分流：研发请求创建 triage intake（保留原始请求与来源标识），非研发请求直接处理
  → orchestrator 需求准入：抽取角色/场景/流程/业务规则/验收标准，形成候选 revision
  → Intent Owner 确认基线
  → orchestrator 建立 Kanban 任务图
      ├─ researcher（存在外部证据缺口时）
      ├─ technical-architect（存在架构影响时）
      └─ qa-engineer（实现前形成验证策略）
  → 各工程师在 Linux 独立 worktree 中通过 Hermes 自带 Codex 技能实现
  → qa-engineer 执行验证（已知缺陷回原实现者；未知根因交 debugger）
  → 按风险选择 L0/L1/L1+L2/Full 证据；SEB 完整性失败则全量复算
  → reviewer 对固定 commit SHA 独立评审（G0 无 reviewer，G1 轻量，G2 同步）
  → orchestrator 汇总证据，交人类责任人批准 push / 合并 / 部署
```

工作区和通知也按风险选择：scratch 用于只读讨论/研究/规划，受控 dir 仅用于非代码串行资产，低风险同 Flow 代码任务可复用 Flow worktree，并行/高风险/破坏性实验使用 per-task worktree。默认 exception-only 通知，常规进展留在 Kanban；流程迁移依次经过 observe、shadow、gray rollout、expand、default。停止由 orchestrator 接收并阻止下游新建/解锁；运行中取消、自动超时降级、声明式门禁和事件 roll-up 暂属平台缺口。

治理细节（工作区隔离、分支约定、质量门顺序、审批矩阵）见
`skills/orchestration-methodology/references/delivery-governance.md`；
需求准入见 `skills/orchestration-methodology/references/requirements-intake.md`。

## 贡献

请创建 Issue 或 PR。角色配置应满足以下要求：

- 职责单一且清晰
- 服务于 R&D 生命周期，并具有独立的上下文、方法论或质量边界
- `SOUL.md` 说明第一原则、职责边界与输出契约（运行协议的权威来源）
- `config.yaml` 提供可运行的模型与工具集配置，且不含任何密钥
- 明确列出技能依赖，并运行 `python3 scripts/sync_skills.py` 物化副本后提交
- 采用 Hermes 原生模式（产物金字塔输出、基于技能加载方法论）
- 不依赖 Agent 专用基础设施（如 council、cashew），必须能在原生 Hermes 安装中工作

提交前请运行校验：

```bash
python3 scripts/validate_profiles.py
```

## 许可证

MIT
