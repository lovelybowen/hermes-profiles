# Hermes 角色配置集

这是面向 AI Native R&D 协作的 Hermes 角色配置集。每个角色配置都封装角色身份（`SOUL.md`）、技能依赖和研发能力配置，可作为 Hermes Agent 部署。

这些角色配置具有明确的设计主张，并采用 Hermes 原生模式：
- 产物金字塔输出格式（渐进披露、以路径作为交接内容）
- 基于技能的方法论加载（`skill_view` → 加载参考资料）
- 使用 Hermes 看板开展多 Agent 编排
- 使用 Hermes Profile 系统隔离角色

**角色配置**（`SOUL.md` + `profile.yaml`）是 Hermes 专用内容，通常无法直接用于其他 Agent 运行环境。但 `skills/` 下采用 `SKILL.md + references/` 结构的**技能**方法论遵循 [Agent Skills 开放标准](https://www.agensi.io/learn/agent-skills-open-standard)。Claude Code、Codex CLI、Cursor、Gemini CLI、OpenClaw、GitHub Copilot、Windsurf 等 20 多种编码 Agent 均采用该标准，因此这些技能具有良好的可移植性。

## 仓库结构

```
hermes-profiles/
├── skills/
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
│   ├── operational-design/
│   ├── orchestration-methodology/
│   ├── qa-methodology/
│   ├── research-methodology/
│   ├── researcher-workflow/
│   ├── review-methodology/
│   ├── software-architecture-analysis/
│   └── systematic-debugging/
└── profiles/
    ├── backend-engineer/             ← API 实现、服务逻辑、数据库访问
    ├── debugger/                     ← 根因分析、错误诊断
    ├── frontend-engineer/            ← UI 组件、状态管理、API 集成、性能
    ├── orchestrator/                 ← 任务分解、专家路由
    ├── qa-engineer/                  ← 测试策略、自动化、质量门
    ├── researcher/                   ← 深度调查、证据综合
    ├── reviewer/                     ← 代码/架构评审、质量门
    └── technical-architect/          ← 系统架构：C4 + ADR + arc42
```

角色配置通过符号链接指向共享的 `skills/` 目录，因此每个技能只需保留一份即可供所有角色使用。Git 按引用跟踪这些符号链接，不会复制内容。

## 使用角色配置

```bash
# 克隆仓库
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles

# 将所需角色配置链接到 ~/.hermes/profiles/
# （当前有 8 个角色配置，请选择一个）
ln -s ~/hermes-profiles/profiles/researcher ~/.hermes/profiles/

# 切换角色配置（已包含技能，无需单独安装）
hermes --profile researcher
```

每个角色配置的 `profile.yaml` 都列出其必需技能和 Hermes 专用配置。

## 贡献

请创建 Issue 或 PR。角色配置应满足以下要求：
- 职责单一且清晰
- 服务于 R&D 生命周期，并具有独立的上下文、方法论或质量边界
- 包含说明第一原则与输出契约的 `SOUL.md`
- 明确列出技能依赖
- 采用 Hermes 原生模式（产物金字塔输出、基于技能加载方法论）
- 不依赖 Agent 专用基础设施（如 council、cashew），必须能在原生 Hermes 安装中工作

## 许可证

MIT
