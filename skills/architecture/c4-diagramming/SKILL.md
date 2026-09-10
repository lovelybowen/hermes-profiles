---
name: c4-diagramming
description: "C4 模型结构视图 - 系统上下文图、容器图、组件图和代码图。将 C4 缩放层级映射到产物金字塔（上下文→L1、容器/组件→L2、代码→L3）。technical-architect 角色需要生成结构架构图时使用。"
---

# C4 图表绘制

C4 模型用于可视化架构结构。它生成四个缩放层级的图，并映射到产物金字塔。

## C4 到金字塔的映射

| C4 层级 | 金字塔层 | 路径 |
|----------|--------------|------|
| 第 1 层：系统上下文 | L1（摘要） | 01-summary/system-context.md |
| 第 2 层：容器 | L2（分析） | 02-analysis/structural-views/container.md |
| 第 3 层：组件 | L2（分析） | 02-analysis/structural-views/components.md |
| 第 4 层：代码 | L3（档案） | 03-dossiers/code-level-detail.md |

C4 与该结构最为匹配：它的四层层级几乎可以直接映射到金字塔的三层，其中 C4 第 2-3 层分别映射为独立的 L2 分析文件。

## 编写格式

### Mermaid（快速绘图的默认选项）

需要在 Markdown 中嵌入单张图时使用。C4-in-Mermaid 的兼容性说明见下方“GitHub 渲染约束”。

### Structurizr DSL（长期项目的推荐选项）

Structurizr DSL 是 Simon Brown 创建的 C4 模型“模型即代码”参考实现。在一个 DSL 文件中定义完整架构模型，并由它生成全部四个 C4 层级，从而确保跨图结构一致性，这是手写 Mermaid 无法保证的。

```
workspace {
    model {
        user = person "Customer"
        system = softwareSystem "Your System" {
            webapp = container "Web Application" "TypeScript, React"
            api = container "API" "Go"
            db = container "Database" "PostgreSQL"
            user -> webapp "Uses"
            webapp -> api "Makes API calls"
            api -> db "Reads/writes"
        }
    }
    views {
        systemContext system { include * autolayout lr }
        container system { include * autolayout lr }
        component api { include * autolayout lr }
        theme default
    }
}
```

**关键能力：**
- `!adrs docs/adr` - 将架构决策记录（adr-tools、MADR、log4brains）导入工作区，与 C4 图一起渲染
- `!docs docs/arc42` - 将 arc42 文档以 Markdown/AsciiDoc 导入
- Structurizr Lite（Docker）- 在 http://localhost:8081 本地预览
- CI 命令：`validate`、`inspect`、`export`（PlantUML、Mermaid、静态站点）

完整资料见 `references/architecture-as-code-ecosystem.md`，包括工具比较、DSL 实用指南、C4-PlantUML 替代方案和统一仓库约定。

## 内容

- `references/c4-levels.md` - 各层级的目的、受众、建模内容和易错点
- `references/c4-to-pyramid-mapping.md` - 上下文→L1、容器/组件→L2、代码→L3（Mermaid + Structurizr DSL 路径）
- `references/c4-to-flowchart.md` - `mermaid-diagrams` 技能中的 C4 → 标准流程图转换模式，用于兼容 GitHub
- `references/architecture-as-code-ecosystem.md` - Structurizr DSL、C4-PlantUML、docToolChain、统一仓库约定、工具比较表
- `references/ci-pipeline-templates.md` - 用于 Structurizr 验证、导出和部署的 GitHub Actions、GitLab CI、ForgeJo（Gitea Actions、Woodpecker）管线模板

## GitHub 渲染约束

GitHub 内置 Mermaid 渲染器**不包含** C4 插件（`@mermaid-js/mermaid`）。任何使用 `C4Context`、`C4Container` 或 `C4Component` 语法的 ````mermaid` 代码块都会在 GitHub 上显示为原始代码，而不是图表。这会影响 Issue、PR 描述、讨论评论和 Markdown 文件。

**规避方法：** 将 C4 图转换为标准 `flowchart` 语法后，再嵌入 GitHub Markdown：
- `Person()` → 带标签的 `[矩形]` 节点
- `System()` / `System_Ext()` → 子图内部或外部的 `[矩形]`
- `Container()` → 带技术栈标签的 `[矩形]`
- `Db()` → `[(圆柱形)]`
- `System_Boundary{}` / `Container_Boundary{}` → `subgraph ... end`
- `Rel()` → `-- 标签 -->` 或 `-.->`
- 移除 `UpdateLayoutConfig()`，改用 `flowchart LR` 或 `TB` 指令

完整转换表和三个 C4 层级的实例见 `skill_view(name='mermaid-diagrams', file_path='references/c4-to-flowchart.md')`。

如果 **DIAGRAMS/ 目录中的 `.mmd` 文件**需要通过 `mmdc` 或在 GitHub 上渲染，也必须使用标准 flowchart 语法。使用 C4 插件语法的文件只能在捆绑该插件的工具中渲染（例如 Mermaid Live Editor、配置了 C4 扩展的 mmdc）。如果将使用 C4 语法的 `.mmd` 文件提交到仓库，GitHub 的文件预览会将其显示为原始文本——应先转换为标准语法，或渲染为 PNG。

## 已提交功能请求

已在 https://github.com/orgs/community/discussions/197898 提交一项 GitHub Community 功能请求，希望捆绑 C4 Mermaid 插件（已关闭——要求通过 Web UI 使用 Apps、API and Webhooks 讨论模板提交）。如果该功能得到实现，GitHub 渲染将不再需要下述 flowchart 转换。

## 规范参考

- Simon Brown, "The C4 Model" — https://c4model.com/
- Magnus Hedemark, "Clanker Technical Architect: First on the Scene with Progressive Disclosure" — https://magnus919.com/2026/05/clanker-technical-architect-first-on-the-scene-with-progressive-disclosure/
- GroktoPlan C4 图（实例）- https://github.com/groktopus/groktoplan/blob/main/TECHNICAL_ARCHITECTURE.md
