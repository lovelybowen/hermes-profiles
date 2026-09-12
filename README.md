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
├── profiles/
│   ├── backend-engineer/               ← API 实现、服务逻辑、数据库访问
│   ├── debugger/                       ← 根因分析、错误诊断
│   ├── frontend-engineer/              ← UI 组件、状态管理、API 集成、性能
│   ├── orchestrator/                   ← 基线准入、任务分解、专家路由、质量门监控
│   ├── qa-engineer/                    ← 测试策略、自动化、质量门
│   ├── researcher/                     ← 深度调查、证据综合
│   ├── reviewer/                       ← 代码/架构评审、质量门
│   └── technical-architect/            ← 系统架构：C4 + ADR + arc42
│
│   工程执行：backend/frontend/qa/debugger 在 Linux 本地 worktree 中
│   使用 Hermes 自带 codex 技能调用 codex exec
├── scripts/validate_profiles.py        ← 结构与符号链接校验
├── .gitignore                          ← 排除凭据与运行时状态
├── AGENTS.md / CONTRIBUTING.md
└── README.md
```

角色配置通过符号链接指向共享的 `skills/` 目录，因此每个技能只需保留一份即可供所有角色使用。Git 以模式 `120000` 跟踪这些符号链接，不会复制内容。

每个角色配置包含：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | **权威运行协议**：第一原则、职责边界、触发模式、加载顺序、输出契约 |
| `config.yaml` | 模型、provider 与工具集（orchestrator 额外启用 `kanban`） |
| `profile.yaml` | 元数据与技能依赖声明 |
| `README.md` | 面向人的使用指南 |
| `AGENTS.md` | 指向 `SOUL.md` 的索引 + 上下游接口 |
| `.env.example` | 需要的凭据清单（复制为 `.env` 并填入） |
| `skills/` | 指向仓库根 `skills/` 的相对符号链接 |

## 使用角色配置

```bash
# 克隆仓库
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles

# 将角色配置链接到 ~/.hermes/profiles/（8 个角色，按需链接）
ln -s ~/hermes-profiles/profiles/orchestrator ~/.hermes/profiles/

# 准备凭据（.env 已被 .gitignore 排除，不会进入版本库）
cp ~/hermes-profiles/profiles/orchestrator/.env.example \
   ~/hermes-profiles/profiles/orchestrator/.env
# 编辑 .env，填入模型 API key

# 启动
hermes --profile orchestrator
```

角色的运行协议以 `SOUL.md` 为准；`config.yaml` 里的 `toolsets` 决定工具集，`profile.yaml` 里的 `skills` 是依赖声明（技能通过 `skills/` 符号链接实际生效）。

## 入口

**`default` 是外部 ingress，`orchestrator` 是研发准入与编排入口。** 普通问答可由 default 直接回答；研发请求统一进入 Kanban `triage` intake，由 default 保留原始请求、项目、验收条件和来源标识，并固定交给 orchestrator。default 不直接改代码、不调用工程 Profile。

```
你（需求 / 变更请求）
    ↓
default（Feishu/Cron/Webhook/CLI ingress）
    ↓ Kanban intake
orchestrator                    ← 研发准入、分解、路由、汇总
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

`default` 可以作为 Feishu/Cron 入口：它只创建 assignee 为 `orchestrator` 的 intake 任务；编排和执行仍由 Kanban Flow 完成。

```bash
hermes --profile orchestrator
```

## 工作流

```
自然语言需求
  → default 创建 triage intake（保留原始请求与来源标识）
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
- 明确列出技能依赖，并通过相对符号链接实际生效
- 采用 Hermes 原生模式（产物金字塔输出、基于技能加载方法论）
- 不依赖 Agent 专用基础设施（如 council、cashew），必须能在原生 Hermes 安装中工作

提交前请运行校验：

```bash
python3 scripts/validate_profiles.py
```

## 许可证

MIT
