# Researcher 工具治理

研究员默认使用 **Hermes 原生研究工具**，把 `groktocrawl` 当作可选的增强路径。原生工具在任意 Hermes 安装中都可用；`groktocrawl` 需要额外的自托管服务，**不是前置依赖**。

## 工具选择

| 需求 | 首选（原生） | 可选增强（groktocrawl，若可用） |
|---|---|---|
| 发现资料 | `web_search` | `groktocrawl search "<query>" --limit N --json` |
| 读取单页内容 | `web_extract <url>` | `groktocrawl scrape <url>` |
| JS 渲染 / 反自动化页面 | browser 工具套件 | `groktocrawl browser` |
| 纯文本端点（`.md` / `.txt` / `.json` / `.yaml`） | `curl` | — |
| PDF / 图像 | `web_extract`（含 PDF）或 `curl` + `pdftotext` | `groktocrawl download <url>` |
| 全站提取 | 逐页 `web_extract` | `groktocrawl crawl <url>` |
| 多来源自动综合 | 自行综合（`research-methodology/references/synthesis-patterns.md`） | `groktocrawl agent "<prompt>"` |

## 何时启用 groktocrawl

仅在**同时**满足以下条件时使用：

1. 环境中确实存在该可执行文件 —— 先运行 `command -v groktocrawl` 确认；
2. 任务需要原生工具无法提供的能力（大规模全站抓取、强反自动化页面）。

探测不到就**直接使用原生工具**，不要花时间尝试安装或绕行。

## 回退链

```
groktocrawl（若可用且必要）
  → web_search / web_extract / browser（原生，默认路径）
    → curl（纯文本端点）
      → 记录为未解决的证据缺口
```

## 关键约束

- **不要为了用某个工具而降低证据标准。** 换工具是为了拿到证据，不是为了完成调用。
- **记录每次取证的获取方式**（原生还是 groktocrawl），便于复现。
- **抓取失败不等于问题不存在。** 工具失败时记录缺口并交回，不要用常识补位。
- 研究路径与来源评估方法见 `research-methodology` 技能。
