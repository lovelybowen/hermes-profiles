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

| C4 元素 | 流程图对应形式 | 示例 |
|-----------|---------------------|---------|
| `Person()` | `[label]`（标准矩形） | `U[人类用户]` |
| `System()` | 带样式的 `[label]` | `GP[GroktoPlan]` 配合 `style GP fill:#...` |
| `System_Ext()` | 子图外的 `[label]` | `GIT[Git 提供商]` |
| `Container()` | `[包含技术栈的标签]` | `KG[知识图谱<br/>Python + pgvector]` |
| `Db()` | `[(label)]`（圆柱形） | `LS[(实时状态数据库)]` |
| `System_Boundary{}` | `subgraph System["标题"] ... end` | 嵌套子图 |
| `Container_Boundary{}` | `subgraph Service["标题"] ... end` | 单个子图 |
| `Rel()` | `-- label -->` 或 `-.->` | `AR -- gRPC --> GA` |
| `UpdateLayoutConfig()` | 省略，使用 `flowchart LR` 或 `TB` | 在头部设置方向 |

三个 C4 层级的完整示例见 `references/c4-to-flowchart.md`。

### GitHub 兼容性参考

| 图表类型 | GitHub 是否渲染 | 说明 |
|-------------|----------------|-------|
| `flowchart`（TD/LR/BT/RL） | ✅ | 用于所有 C4 变通图 |
| `sequenceDiagram` | ✅ | |
| `classDiagram` | ✅ | |
| `stateDiagram-v2` | ✅ | |
| `erDiagram` | ✅ | |
| `gantt` | ✅ | |
| `pie` | ✅ | |
| `quadrantChart` | ✅ | |
| `requirementDiagram` | ✅ | |
| `gitgraph` | ✅ | |
| `mindmap` | ✅ | |
| `timeline` | ✅ | |
| `zenuml` | ✅ | |
| `sankey` | ✅ | |
| `xychart` | ✅ | |
| `block` | ✅ | |
| `packet` | ✅ | |
| `C4Context` | ❌ | 需要 C4 插件，会显示为原始代码 |
| `C4Container` | ❌ | 需要 C4 插件，会显示为原始代码 |
| `C4Component` | ❌ | 需要 C4 插件，会显示为原始代码 |
| `C4Deployment` | ❌ | 需要 C4 插件，会显示为原始代码 |
| `C4Dynamic` | ❌ | 需要 C4 插件，会显示为原始代码 |

## 渲染

### CLI（mmdc）- 用于 PDF/SVG/PNG 输出

```bash
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.pdf
```

需要 Puppeteer 和 Chromium（约 1.7GB）。使用 Docker 镜像进行隔离渲染：
```bash
docker run --rm -v $(pwd):/data ghcr.io/mermaid-js/mermaid-cli mermaid-cli -i /data/diagram.mmd -o /data/diagram.svg
```

### CDN（HTML）- 用于内联 Web 渲染

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true});</script>
<div class="mermaid">
flowchart LR
  A-->B
</div>
```

### 验证

```javascript
// Node.js 验证
import { parse } from 'mermaid';
try {
  parse('flowchart LR\n  A-->B');
  console.log('Valid');
} catch (e) {
  console.error('Invalid:', e.message);
}
```

## 脚本

| 脚本 | 用途 |
|--------|---------|
| `scripts/validate-mermaid.sh` | 验证 `.mmd` 文件是否存在语法错误 |

## 主题

Mermaid 使用带有可定制主题变量的 `base` 主题。在图表顶部通过 `%%{init: {'theme':'base', 'themeVariables': { ... }}}%%` 设置。

主要主题变量：
- `primaryColor`, `primaryTextColor`, `primaryBorderColor`
- `secondaryColor`, `tertiaryColor`
- `lineColor`, `fontFamily`, `fontSize`
- `background`（外部背景）、`mainBkg`（元素背景）

## 反模式

| 反模式 | 修复方法 |
|-------------|-----|
| 流程图中错误使用关键字大小写 | Mermaid 关键字区分大小写，必须使用语法规定的形式。 |
| 连线短横线后紧跟 `o` 或 `x` 且没有空格 | `-->o` 需要空格，应写成 `--o `，或使用明确的节点形状。 |
| 圆括号内使用不合适的引号 | 使用 `("quoted text")`，不要使用 `('quoted text')`。 |
| 图表过宽（超过 100 个节点） | 拆分为多个子图，或使用 ELK 布局。 |
| 混用制表符和空格 | 只使用空格，子图缩进两个空格。 |
| 长标签没有换行 | 在节点中使用 `<br/>` 或竖线 `|` 换行。 |
| 以数据 URI 嵌入 SVG | 改用原始 `<svg>` 标签，CSS 无法覆盖数据 URI 的 `max-width`。 |
| 为 PDF 保留 Markdown 中的 Mermaid 代码块 | 先预渲染为 SVG，Pandoc 会把 ```mermaid 渲染为原始文本。 |
