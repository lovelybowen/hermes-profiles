# 渲染、兼容性与反模式

*本文件是 `mermaid-diagrams` 技能的参考文件，加载方式：*
*`skill_view('mermaid-diagrams', file_path='references/rendering-and-pitfalls.md')`*

| 小节 | 内容 |
|---|---|
| 渲染 | mmdc CLI、CDN 内联、语法验证 |
| 主题 | `base` 主题与可定制变量 |
| GitHub 兼容性 | 哪些图表类型在 GitHub 原生渲染 |
| 反模式 | 常见语法陷阱与修复 |

---

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
