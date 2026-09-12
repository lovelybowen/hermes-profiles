# Mermaid 图的纵向布局

为 PDF、打印或纵向屏幕（GitHub、GitLab、移动端）生成图时，使用 `flowchart TD`（自顶向下），而不是 `flowchart LR`（从左到右）。这样会垂直堆叠图，使其铺满纵向页面，而不是缩小后挤在段落之间。

## 强制 Dagre 引擎输出纵向布局

Mermaid 默认的 dagre 布局引擎会针对紧凑性进行优化，因此即使使用 `flowchart TD`，也经常生成较宽的图。以下两种技巧可以可靠地强制输出纵向布局：

### 技巧 1：使用带 `direction TB` 的包裹 Subgraph

将**所有**节点和边包裹在一个带有 `direction TB` 的 subgraph 中。这会将布局引擎限制在纵向容器内：

```mermaid
flowchart TD
  subgraph C["图标题"]
    direction TB
    A[节点 A]
    B[节点 B]
    C[节点 C]
    A --> B
    B --> C
  end
```

在测试中，这会将一张容器图从 2271×1100（横向）转换为 641×928（纵向）。

### 技巧 2：不可见链式边（`~~~`）

当同一层级的节点仍然横向展开时，添加不可见链式边以强制垂直堆叠：

```mermaid
flowchart TD
  subgraph C["堆叠图"]
    direction TB
    A[节点 A]
    B[节点 B]
    C[节点 C]
    D[节点 D]

    A --> B
    A ~~~ C
    B ~~~ D
  end
```

`~~~` 边不可见，但会告知 dagre“这些节点必须位于不同行”。将 dagre 原本会并排放置的所有节点通过这种边串联起来。

### 拆分复杂图

包含超过 12-15 个节点或密集交叉连接的图无法转为纵向。将其拆分成多张子图，每张包含 5-10 个节点。

| 原图（横向） | 拆分方式 | 纵向结果 |
|---------------------|------------|-----------------|
| 20 节点组件图（1261×799） | 4 张子图（每张 5 个节点） | 全部达到 281×661 或更好 |
| 10 节点架构模式图（913×580） | 2 张子图（每张 5-6 个节点） | 分别为 367×799 和 368×532 |

## QA：ViewBox 尺寸检查

交付前，从每个已渲染 SVG 中提取 `viewBox`，并验证宽度 < 高度：

```bash
python3 -c "
import re
with open('diagram.svg') as f:
    c = f.read()
vb = re.search(r'viewBox=\"([^\"]*)\"', c)
w, h = float(vb.group(1).split()[2]), float(vb.group(1).split()[3])
if w > h:
    print(f'LANDSCAPE: {w:.0f}x{h:.0f} — FIX')
"
```

只检查文本模式 `flowchart LR` 并不充分——Mermaid 的 dagre 引擎可能根据 TD 输入生成横向输出。

## PDF 嵌入规则

- **始终以内联 base64 方式嵌入 SVG**——原始 SVG 标签经过 Pandoc 后 CSS 会损坏（尤其是 `@keyframes`）。使用 `<img src="data:image/svg+xml;base64,...">`。
- **绝不使用文件系统路径**——`<img src="/tmp/...svg">` 会在 PDF 生成期间失效。只有 base64 data URI 能通过 Pandoc → HTML → Puppeteer 流程。
- **所有 `<img>` 标签都设置 `width:100%`**——`style="width:100%;height:auto;max-width:100%;display:block;margin:0 auto;"`

## 纵向图规则

1. 用于 PDF 或纵向屏幕的架构图**始终使用 `flowchart TD`**
2. 每张整页图**前后分页**：
   ```html
   <div style="page-break-before: always;"></div>
   <img src="data:image/svg+xml;base64,...">
   <div style="page-break-after: always;"></div>
   ```
3. **保持 viewBox 高于宽。**已渲染 SVG 的 viewBox 必须满足高度 > 宽度。
4. **每行最多 4 个节点，每张图最多 12-15 个节点。**将复杂图拆成子图。
5. **使用少于 30 个字符的短标签。**多行使用 `<br/>`。使用缩写：“scraper-svc”而不是“Web Scraping Service”。
6. **时序图最多 4 个参与者。**参与者更多会生成较宽布局，应拆成多张图。
7. **在 TD 内，仅对包含 2-3 个节点的链使用 `direction LR`。**
8. **打印时使用浅色背景**——深色主题会浪费 PDF 打印墨粉。
9. **通过 mmdc 以 `--width 800` 渲染**，以适配 A4/Letter。
10. **节点形状：数据库使用 `[()]`，服务使用 `[text]`。**

## 验证检查清单

- [ ] 使用 `flowchart TD`，而非 `LR`
- [ ] 已应用带 `direction TB` 的包裹 subgraph
- [ ] 每张图前后都有分页 div
- [ ] SVG 以 base64 内联（无原始 SVG 标签，无文件系统路径）
- [ ] 每个已渲染 SVG 的 viewBox：宽度 < 高度
- [ ] 节点标签少于 30 个字符
- [ ] 打印使用浅色背景
- [ ] 每张时序图最多 4 个参与者
- [ ] 没有 ASCII 字符图——所有图都已渲染为 Mermaid SVG
