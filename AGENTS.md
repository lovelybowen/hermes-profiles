# Hermes R&D 角色配置集 - Agent 指南

本文档帮助 AI Agent 理解如何使用本仓库中的 R&D 角色配置。

## 仓库结构

```
hermes-profiles/
├── skills/                          ← 共享技能池（实际文件）
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
│   ├── operational-design/
│   ├── orchestration-methodology/
│   ├── qa-methodology/
│   ├── research-methodology/
│   ├── researcher-workflow/
│   ├── review-methodology/
│   ├── software-architecture-analysis/
│   └── systematic-debugging/
├── profiles/                        ← Agent 角色配置（通过符号链接引用技能）
│   ├── backend-engineer/
│   ├── debugger/
│   ├── frontend-engineer/
│   ├── orchestrator/
│   ├── qa-engineer/
│   ├── researcher/
│   ├── reviewer/
│   └── technical-architect/
├── .github/ISSUE_TEMPLATE/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 角色配置的工作方式

本仓库只保留服务于 R&D 生命周期且具有独立上下文、方法论或质量边界的角色。业务价值、交付取舍和风险接受由人类责任人承担，不包装为 Hermes Profile。

每个角色配置都是一个目录，包含以下文件：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | 身份文档：第一原则、方法论、输出契约 |
| `profile.yaml` | 元数据：描述、必需技能和推荐技能 |
| `README.md` | 面向人的使用指南 |
| `AGENTS.md` | 面向 Agent 的触发模式与交接协议 |

角色配置不直接包含技能文件。每个角色的 `skills/` 目录都包含指回仓库根目录共享 `skills/` 池的**相对符号链接**，因此每个技能只需保留一份即可服务所有角色。

## 技能约定

共享池中的技能遵循渐进披露原则：
- `SKILL.md` 是精简索引，包含触发条件和加载说明
- 方法论细节位于 `references/`，通过 `skill_view(name, file_path=path)` 按需加载
- 技能应能在原生 Hermes 安装中工作，不依赖 council、cashew 或其他 Agent 专用基础设施

## 符号链接规则

- 所有符号链接都必须使用**相对路径**，不能使用绝对路径
- 从 `profiles/<name>/skills/` 出发，目标为 `../../../skills/<skill-name>`
- 从 `profiles/<name>/skills/<category>/` 出发，目标为 `../../../../skills/<category>/<skill-name>`（也可让分类目录本身成为符号链接）
- 符号链接由 Git 以模式 `120000` 跟踪，在 macOS/Linux 上执行 `git clone` 后可正确重建

## 贡献流程

1. 从 `main` 创建分支。
2. 添加或修改角色配置文件。
3. 添加新技能时，先将技能目录放入 `skills/`，再从角色配置创建符号链接。
4. 使用 `test -e` 确认所有符号链接都能解析。
5. 创建 PR，并清楚说明角色职责及其所需技能。

## 验证角色配置

提交 PR 前，请检查：

- [ ] `SOUL.md` 存在，并说明第一原则和输出契约
- [ ] `profile.yaml` 存在、YAML 有效且列出必需技能
- [ ] `README.md` 存在，并包含安装、快速开始和技能参考
- [ ] `AGENTS.md` 存在，并包含触发模式、加载顺序和交接说明
- [ ] `skills/` 中的所有符号链接都能解析到共享池中的真实文件
- [ ] 符号链接不包含绝对路径
- [ ] 不复制技能文件，而是使用指向共享池的符号链接

## 相关仓库

- https://github.com/groktopus/artifact-pyramids - 产物金字塔规范
- https://github.com/architecture-decision-record/architecture-decision-record - ADR 社区标准
