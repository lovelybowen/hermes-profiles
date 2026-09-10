---
name: mermaid-diagrams
description: "与平台无关的 Mermaid.js 绘图方法，涵盖流程图、时序图以及通过 Structurizr 或流程图变通方式实现的 C4 图。生成有效的 Mermaid 语法，通过 mmdc CLI 或 CDN 渲染，并在输出前验证。可移植到 CLI、Markdown、HTML、PDF 和任何 Agent 上下文。"
---

# Mermaid 图表

面向架构文档的可移植 Mermaid.js 绘图方法，不依赖任何博客平台、主题或渲染引擎。图表可以通过 CLI 渲染、嵌入 Markdown，或作为 HTML 片段提供。

## 使用时机

在以下场景加载此技能：
- 创建 C4 结构视图，正式产物使用 Structurizr DSL，内联 Markdown 使用流程图变通方式。
- 为交互流程生成时序图。
- 为流程文档设计流程图。
- 生成需要同时在 Agent 和人类使用场景中渲染的图表。

如果只需要静态 ASCII 架构图，或目标平台要求专用主题渲染，则不要加载此技能。

## PDF 输出 - 必须预渲染

Mermaid 代码块（```mermaid```）无法在 Pandoc → HTML → Puppeteer PDF 管线中渲染，因为该管线生成不执行 JavaScript 的静态 HTML。

**任何用于 PDF 输出的图表都必须：**
1. 将图表创建为独立的 `.mmd` 文件。
2. 预渲染为 SVG：`npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg --width 800`。
3. 把原始 SVG 内容直接嵌入 Markdown，不要使用 `<img src="data:...">`。
4. 从 SVG 标签中移除硬编码的 `max-width` 像素值。
5. 使用纵向的 `flowchart TD`，不要使用横向的 `flowchart LR`，参见 `references/portrait-layout.md`。
6. 在每张整页图表前后添加分页 `div`。

不要在将由 Pandoc 处理的 Markdown 中保留 ```mermaid 代码块，否则会渲染成原始等宽文本。

包含 Puppeteer 设置、SVG 样式修复和 QA 检查清单的完整管线见 `references/pdf-rendering-pipeline.md`。

## 支持的图表类型

| 类型 | 使用场景 | 文件 |
|------|----------|------|
| 流程图 | 业务流程、C4 变通图、决策树 | `references/flowchart.md` |
| 时序图 | 交互协议、API 调用、Agent 交接 | `references/sequence.md` |
| C4 | 架构上下文视图和容器视图 | `references/c4-mermaid.md` |
| C4 流程图转换 | 将 C4 图转换为兼容 GitHub 的标准流程图 | `references/c4-to-flowchart.md` |
| 纵向布局 | 面向 PDF 或打印的绘图，包括优先 TD、分页和整页图表 | `references/portrait-layout.md` |
| PDF 渲染管线 | 从 `.mmd` → SVG → HTML → PDF 的完整管线及 QA 检查清单 | `references/pdf-rendering-pipeline.md` |
| mmdc 间距配置 | 通过 `nodeSpacing`、`rankSpacing`、`padding` 控制复杂打印图表的布局密度，防止标签重叠 | `references/mmdc-spacing-config.md` |

## C4 模型指引

Mermaid 提供实验性的原生 C4 语法（`C4Context`、`C4Container`、`C4Component`），但 **GitHub 和大多数 Markdown 渲染器并不支持**。GitHub 内置的 Mermaid 渲染器未包含 C4 插件，因此 C4 语法块会显示为原始代码而不是图表。应改用以下方法之一：

1. **流程图变通方式（兼容 GitHub）：**把 C4 图转换为标准 `flowchart` 语法，以子图表示边界，为 Person/System/Container/Db 使用带样式的节点框，为 Rel 使用带标签的边。完整转换模式见 `references/c4-to-flowchart.md`。
2. **Structurizr DSL：**用于正式 C4 图。通过 Structurizr CLI 渲染，或导出为 Mermaid SVG。适合不存放在 GitHub Markdown 中的正式架构文档。
3. **混合方式：**在架构师的产物金字塔中使用 Structurizr DSL 生成 C4，同时在 Markdown 报告中放入基于流程图的近似版本，以便内联阅读。

### C4 → 流程图转换模式

C4 元素到标准 `flowchart` 的完整映射表（`Person` / `System` / `System_Ext` / `Container` / `Db` / `Boundary` / `Rel`）与三个层级的实例见 `references/c4-to-flowchart.md`。

## 参考文件

上表列出全部参考文件；其中 `references/rendering-and-pitfalls.md` 覆盖渲染命令与语法验证、主题变量、GitHub 兼容性表和反模式清单，是遇到渲染或语法问题时的入口。

## 脚本

| 脚本 | 用途 |
|---|---|
| `scripts/validate-mermaid.sh` | 验证 `.mmd` 文件是否存在语法错误 |
