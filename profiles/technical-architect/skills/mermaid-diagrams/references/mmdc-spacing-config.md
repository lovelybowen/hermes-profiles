# mmdc 间距配置

通过 `mmdc -c config.json` 传入的 JSON 配置文件，用于控制 Mermaid 图表的 PDF 或打印输出渲染。

## 使用场景

复杂流程图、ER 图和时序图在 mmdc 默认间距下会产生重叠标签。此配置增大节点、层级和内边距，生成适合打印的清晰输出。

## 配置文件

保存为 `mermaid-config.json`：

```json
{
  "flowchart": {
    "useMaxWidth": false,
    "htmlLabels": true,
    "padding": 25,
    "nodeSpacing": 60,
    "rankSpacing": 80,
    "curve": "basis"
  },
  "er": {
    "diagramPadding": 30,
    "layoutDirection": "TB",
    "minEntityWidth": 100,
    "minEntityHeight": 40,
    "entityPadding": 20,
    "fontSize": 11,
    "useMaxWidth": false
  },
  "sequence": {
    "diagramMarginX": 50,
    "diagramMarginY": 30,
    "actorMargin": 50,
    "width": 150,
    "height": 65,
    "boxMargin": 10,
    "boxTextMargin": 5,
    "noteMargin": 10,
    "messageMargin": 35,
    "mirrorActors": true,
    "bottomMarginAdj": 10,
    "useMaxWidth": false,
    "rightAngles": false,
    "showSequenceNumbers": false
  },
  "theme": "default",
  "themeVariables": {
    "fontSize": "11px",
    "fontFamily": "Inter, sans-serif",
    "primaryColor": "#f5ede4",
    "primaryTextColor": "#2a2018",
    "primaryBorderColor": "#65413a",
    "lineColor": "#65413a",
    "secondaryColor": "#132345",
    "tertiaryColor": "#e8d9c0",
    "noteBkgColor": "#1a2f5a",
    "noteTextColor": "#eceae5",
    "clusterBkg": "#f5ede4",
    "clusterBorder": "#132345",
    "edgeLabelBackground": "#f5ede4",
    "nodeBorder": "#65413a"
  },
  "maxTextSize": 50000
}
```

## 使用方法

```bash
# 使用自定义间距渲染
mmdc -i diagram.mmd -o diagram.png -c mermaid-config.json

# 使用配置以更高分辨率渲染
mmdc -i diagram.mmd -o diagram.png -c mermaid-config.json -w 2400 --backgroundColor '#f5ede4'
```

## 关键取值

| 设置 | 默认值 | 此配置 | 作用 |
|---------|---------|-------------|--------|
| `nodeSpacing` | 30-40 | 60 | 流程图节点间的水平间距 |
| `rankSpacing` | 50 | 80 | 流程图层级间的垂直间距 |
| `padding` | 15 | 25 | 流程图周围的内部留白 |
| `actorMargin` | 25 | 50 | 时序图参与者之间的间距 |
| `messageMargin` | 20 | 35 | 时序图消息之间的间距 |
| `er.diagramPadding` | 15 | 30 | ER 图实体周围的留白 |

## 渲染后调整大小

使用 `-w 2400` 渲染后，PNG 对 A4 页面会过大，应调整大小以便打印：

```python
from PIL import Image
img = Image.open('diagram.png')
w, h = img.size
MAX_W, MAX_H = 1300, 2100
scale = min(1.0, MAX_W / w, MAX_H / h)
img.resize((int(w * scale), int(h * scale)), Image.LANCZOS).save('diagram.png')
```

这样会生成约 200dpi 的输出，适合带有 2.2cm 页边距的 A4 纵向页面。
