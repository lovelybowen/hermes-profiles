# PDF 渲染流水线

将架构文档（含 Mermaid 图的 Markdown）转换为 PDF 的完整流水线，确保图正确渲染并铺满整页。

本参考资料记录了一次经过六轮 PDF 迭代才修复全部缺陷的经验：ASCII 图未转换、Mermaid 代码块未渲染、SVG 受 `max-width` 限制、data URI 图像未铺满页面，以及 Pandoc 将 SVG CSS 解析为数学公式。

## 流水线概览

```bash
# 第 1 步：将所有 Mermaid 图预渲染为 SVG
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg --width 800

# 第 2 步：将 SVG 嵌入 Markdown（不要使用 data URI img 标签）
# 在 Markdown 文件中内联使用原始 <svg> 标签

# 第 3 步：通过 Pandoc 将 Markdown 转换为 HTML
pandoc report.md -f markdown -t html5 --embed-resources --standalone \
  -o report.html --metadata title="Title" \
  --syntax-highlighting=none -f markdown-raw_tex

# 第 4 步：移除 HTML 中 SVG 标签的 max-width 约束
sed -i '' 's/max-width: [0-9]*\.[0-9]*px/max-width: 100%/g' report.html

# 第 5 步：为所有 img 标签添加 width:100%（涵盖 data-URI SVG）
# 添加 style="width:100%;height:auto;max-width:100%;display:block;margin:0 auto;"

# 第 6 步：通过 Puppeteer 生成 PDF
node generate-pdf.js
```

## 关键规则

### 规则 1：预渲染，不要直接提供代码块

Mermaid 代码块（```mermaid```）无法在 Pandoc → HTML → Puppeteer 流水线中渲染。Pandoc 会将其转换为静态 `<pre>` 区块，而 Puppeteer 不会执行 JavaScript 来渲染它们。

**始终如此：**先通过 mmdc 预渲染为 SVG，再嵌入 SVG。

### 规则 2：以原始标记嵌入 SVG，而非使用 data URI

当 SVG 以 `<img src="data:image/svg+xml;base64,...">` 形式嵌入时，页面级 CSS 无法覆盖 SVG 内部的 `max-width` 和 `viewBox`。图像会保持其原生尺寸。

**首选：**将原始 `<svg>...</svg>` 标记直接插入 Markdown 或 HTML。这样页面级 CSS（`width:100%`、`max-width:100%`）即可控制缩放。

**回退方案（img 标签）：**如果使用 `<img>` 标签，应在 `<img>` 元素本身显式添加 `style="width:100%;height:auto;max-width:100%;display:block;"`。不要依赖 SVG 内部 CSS。

### 规则 3：移除 SVG 的 max-width 约束

Mermaid 生成的 SVG 带有硬编码的 `max-width` 值：
```html
<svg style="max-width: 881.07px; ..."> 
```
这些值会覆盖尝试应用的任何 `width: 100%`。将所有实例替换为 `max-width: 100%`。

```bash
# 对于内联 SVG：
sed -i '' 's/max-width: [0-9]*\.[0-9]*px/max-width: 100%/g' report.html

# 对于 base64 data URI，max-width 位于 base64 编码内部
# 无法通过 sed 修复。避免使用 data URI。
```

### 规则 4：纵向方向（使用 TD 而非 LR）

所有用于 PDF 的图都必须使用 `flowchart TD`（自顶向下），而不是 `flowchart LR`（从左到右）。参见 `portrait-layout.md`：
- 每个 subgraph 行最多 4 个节点
- 标签少于 30 个字符
- 时序图最多 4 个参与者
- `viewBox` 必须满足高度 > 宽度

### 规则 5：整页图前后分页

```html
<div style="page-break-before: always;"></div>

<!-- 图内容置于此处 -->

<div style="page-break-after: always;"></div>
```

### 规则 6：Pandoc TeX/SVG 冲突

Pandoc 会将包含 `[id=` 模式的 CSS 选择器解释为 TeX 数学公式，从而生成如下警告：
```
[WARNING] Could not convert TeX math ="-arrowhead"] path{fill:#333...
```

当 SVG 已预渲染并以 `<svg>` 或 `<img>` 标签嵌入时，这些警告**无害**，不会影响输出。使用 `--syntax-highlighting=none -f markdown-raw_tex` 参数尽量减少问题。

## Puppeteer 设置

```javascript
const puppeteer = require("/Users/magnus/.npm/_npx/d2654f9a588e9579/node_modules/puppeteer");

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"]
  });
  const page = await browser.newPage();

  const htmlPath = "file:///tmp/report.html";
  await page.goto(htmlPath, { waitUntil: "networkidle0", timeout: 30000 });
  await page.evaluate(() => new Promise(r => setTimeout(r, 2000)));

  await page.pdf({
    path: "/tmp/output.pdf",
    format: "Letter",
    printBackground: true,
    margin: { top: "0.5in", bottom: "0.5in", left: "0.5in", right: "0.5in" }
  });
  await browser.close();
})();
```

Puppeteer 可作为 `@mermaid-js/mermaid-cli` 的依赖从上述路径使用，但**没有**全局安装。

## PDF 输出 QA 检查清单

向用户发送任何 PDF 前，验证以下**所有**项目：

- [ ] 没有 ASCII 字符图（搜索制表字符：┌ ┐ └ ┘ ├ ┤ ┬ ┴ ─ │）
- [ ] 没有原始 ```mermaid 代码块（搜索 '```mermaid'）
- [ ] 所有 SVG 均已预渲染（不依赖 CDN JavaScript 执行）
- [ ] SVG 铺满页面宽度（检查 HTML 中 svg/img 标签是否设置 `width:100%`）
- [ ] SVG 中没有硬编码的 `max-width` 像素值（检查 'max-width: Npx'）
- [ ] 流程图使用 TD 而不是 LR（搜索 'flowchart LR'）
- [ ] 每张整页图前后均有分页（搜索 'page-break'）
- [ ] PDF 文件大小 > 100KB（图已渲染）
- [ ] 视觉验证：生成 PDF 前在浏览器中打开 HTML
