---
name: architect-pyramid
description: "technical-architect 角色的输出编排器 - 将 C4 结构视图、ADR 决策记录和 arc42 约束映射到统一产物金字塔。管理金字塔结构、交叉引用规则和交接约定。在 c4-diagramming、adr-authoring 和 arc42-context 之后加载。"
---

# 架构师金字塔

`technical-architect` 角色的输出编排器。它接收结构视图（C4）、决策记录（ADR）和上下文/约束文档（arc42），并将其组装为一个产物金字塔。

## 金字塔输出结构

```
<project>/
├── 00-index.md
├── 01-summary/
│   ├── system-context.md          ← C4 第 1 层（系统上下文图）
│   └── quality-tree.md            ← arc42 Canvas/质量属性
├── 02-analysis/
│   ├── structural-views/
│   │   ├── container.md           ← C4 第 2 层（容器图）
│   │   └── components.md          ← C4 第 3 层（组件图）
│   ├── architecture-decisions/
│   │   └── ADR-001.md             ← 活跃 ADR（每项决策一份）
│   ├── constraints-and-context.md ← arc42 第 1-2 节（目标、约束）
│   └── solution-strategy.md       ← arc42 第 4 节
└── 03-dossiers/
    ├── code-level-detail.md       ← C4 第 4 层（代码图）
    ├── adr-superseded.md          ← 已取代 ADR
    └── arc42-supplemental.md      ← arc42 第 5-12 节（风险、部署、术语表）
```

## 交叉引用规则

1. **C4 视图引用 ADR**：每张容器图和组件图都链接到解释其结构依据的 ADR。
2. **ADR 引用 arc42 约束**：每份决策日志都链接到驱动决策的 arc42 质量属性或约束。
3. **arc42 约束引用 C4 视图**：每条约束都链接到展示其实现方式的 C4 图。
4. **每一层都有 `SOURCES` 部分**：使用带说明的绝对路径，而不是脚注。
5. **识别 ADR 生命周期**：C4 视图只能将 `accepted` ADR 作为权威依据；指向 `proposed` ADR 的链接应标记为暂定；ADR 被取代后，C4 视图必须重新链接到替代项。完整生命周期表见 `references/dimension-boundaries.md`。

## 相关方法：架构即代码（AaC）仓库约定

产物金字塔适用于 **Agent 驱动的架构工作**：使用方是另一个 Agent，或金字塔作为任务工作区下的分析交付物。产物根目录取 Kanban 任务工作区（`worktree:` / `dir:`）、项目约定目录（如 `docs/ai-rnd/<project>/`）或 `${ARCHITECT_ARTIFACTS_DIR:-./architecture}`，**不要**只写入会被清理的临时目录。

对于需要在 Git 仓库中维护**长期存在、由工具渲染的架构文档**的团队，AaC 社区形成了一套基于 Structurizr 的约定，在单一仓库中组合 C4 + ADR + arc42，并通过 Docker 预览。

### 映射：金字塔 → AaC 约定

| 金字塔层 | 金字塔文件 | AaC 约定 |
|---|---|---|
| L1（摘要） | 01-summary/system-context.md | `model/system.dsl`（通过 Structurizr 生成 C4 第 1 层） |
| L1（摘要） | 01-summary/quality-tree.md | `src/10_quality_requirements.adoc`（arc42） |
| L2（分析） | 02-analysis/structural-views/container.md | `model/system.dsl`（通过 Structurizr 生成 C4 第 2 层） |
| L2（分析） | 02-analysis/architecture-decisions/ADR-NNN.md | `adr/NNNN-title.md`（adr-tools 格式） |
| L2（分析） | 02-analysis/constraints-and-context.md | `src/01_introduction.adoc` + `02_constraints.adoc` |
| L3（档案） | 03-dossiers/code-level-detail.md | `model/system.dsl`（通过 Structurizr 生成 C4 第 4 层） |
| L3（档案） | 03-dossiers/arc42-supplemental.md | `src/05`-`12`（其余 arc42 章节） |

### 使用时机

| 场景 | 建议 |
|---|---|
| Agent 驱动分析、单次协作、不使用 Docker | **产物金字塔**：无工具依赖、可移植、Agent 原生 |
| 团队在仓库中维护文档并希望本地预览 | **AaC 约定**：使用 Structurizr Lite 执行 `docker compose up`，通过 CI 发布 |
| 混合场景：Agent 生成初始文档，团队长期维护 | 先生成金字塔 → 团队采用后迁移到 AaC 结构 |

完整资料见 `c4-diagramming` 技能中的 `references/architecture-as-code-ecosystem.md`。

## 交接约定

对任何调用方的响应都是 `00-index.md` 的绝对路径，而不是摘要或自然语言交接，只是一个路径。

```
metadata={"artifact": "<absolute-artifacts-root>/<slug>/00-index.md"}
```

## 内容

- `references/pyramid-handoff-convention.md` - 看板 API、`delegate_task`、质量门检查清单
- `references/dimension-boundaries.md` - 事实归属文件、交叉引用规则、ADR 生命周期状态与识别表、不可变文档与活文档模型说明

## 规范参考

- Magnus Hedemark，《Clanker Technical Architect: First on the Scene with Progressive Disclosure》- https://magnus919.com/2026/05/clanker-technical-architect-first-on-the-scene-with-progressive-disclosure/
