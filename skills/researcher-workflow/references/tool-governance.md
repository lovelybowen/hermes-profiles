# Researcher 子 Agent 工具治理

**所有 Web 研究都必须使用 groktocrawl 工具套件。明确禁止使用内置的 `web_search` 和 `web_extract` 工具。**

| 需求 | 必需工具 |
|------|---------------|
| 多来源研究与综合 | `groktocrawl agent "<prompt>"` |
| 用于发现资料的 Web 搜索 | `groktocrawl search "<query>" --limit N --json` |
| 单个页面内容 | `groktocrawl scrape <url>` |
| 大量使用 JS 或具有反自动化保护的页面 | groktocrawl 浏览器套件 |
| 二进制文件（PDF、图像） | `groktocrawl download <url>` |
| 发现站点中的 URL | `groktocrawl map <url>` |
| 全站内容提取 | `groktocrawl crawl <url>` |

**回退链**（仅当 groktocrawl 确实不可用时）：
1. `curl` - 仅用于纯文本端点（`.md`、`.txt`、`.json`、`.yaml`）。
2. `web_extract` - 最后的选择，存在已知限制。

**原因：** 内置工具不足以支持系统化研究。它们可能返回空结果、遭遇 CAPTCHA 阻拦，也无法处理由 JS 渲染的内容。Groktocrawl 可以自行托管、处理反自动化措施，并返回干净的 Markdown。

**当你发现自己准备使用 `web_search` 或 `web_extract` 时：** 停下来，打开终端并改用 groktocrawl CLI。为获得更高质量，多执行这一步是值得的。
