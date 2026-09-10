*本文件是 `researcher-workflow` 技能的参考文件，加载方式：*
*`skill_view('researcher-workflow', file_path='references/research-gather.md')`*

# 收集研究资料

## 使用时机

完成阶段 1（接收任务）后加载此技能，此时 `SCOPE.md` 已存在，产物目录也已就绪。这是把研究问题转化为已收集材料的执行阶段。

## 工具选择

默认使用 **Hermes 原生工具**；`groktocrawl` 仅在 `command -v groktocrawl` 确认可用、且任务需要其独有能力时启用。完整选择表与回退链见 `references/tool-governance.md`。

| 需求 | 首选（原生） | 可选增强（groktocrawl） |
|------|---------------|--------------------------|
| 发现资料 | `web_search` | `groktocrawl search "<query>" --limit N --json` |
| 单个页面内容 | `web_extract <url>` | `groktocrawl scrape <url>` |
| JS 渲染 / 反自动化页面 | browser 工具套件 | `groktocrawl browser` |
| 纯文本端点（`.md`/`.txt`/`.json`/`.yaml`） | `curl` | — |
| PDF / 图像 | `web_extract`（含 PDF）或 `curl` + `pdftotext` | `groktocrawl download <url>` |
| 全站内容提取 | 逐页 `web_extract` | `groktocrawl crawl <url>` |
| 多来源自动综合 | 自行综合（`synthesis-patterns.md`） | `groktocrawl agent "<prompt>"` |

## 执行步骤

### 1. 阅读范围

读取 `<artifacts-root>/<mission-slug>/SCOPE.md`，理解研究问题、范围边界和已知未知项。

### 2. 加载研究方法论

如果尚未加载，则加载共享方法论参考资料：

```
skill_view(name="research-methodology", file_path="references/source-evaluation.md")
skill_view(name="research-methodology", file_path="references/synthesis-patterns.md")
```

### 3. 执行首轮研究

先做广度覆盖：用 `web_search` 找来源，用 `web_extract` 逐篇取证。若环境中存在 `groktocrawl`，可用 `groktocrawl agent "<prompt>"` 加速首轮综合，但不要把它当作唯一入口。

```bash
# 原生路径（默认）
web_search "<SCOPE.md 中重述的问题>"
web_extract <候选 URL 列表>
```

将输出保存为带时间戳的研究日志：

```bash
cat > <artifacts-root>/<mission-slug>/layer-3-detailed/01-gather-pass-1.md << 'EOF'
# 第 1 轮收集：<日期>

## 查阅的来源
- <列出 URL 及各自提供的内容>

## 关键发现
- <按研究问题组织发现>

## 冲突主张
- <来源存在分歧之处>

## 潜在缺口
- <看起来缺失或证据薄弱的内容>
EOF
```

### 4. 补齐特定缺口（定向后续调查）

针对每个已识别缺口，使用合适的工具：

- **轻度缺口**（快速核实事实）：`web_search "<specific query>"`
- **中度缺口**（需要单篇文章）：`web_extract <url>`
- **深度缺口**（需要综合）：多篇 `web_extract` + `synthesis-patterns.md` 方法
- **JS 渲染内容：** browser 工具套件（或可用的 `groktocrawl browser`）

### 5. 评估来源质量

对每个来源应用 `source-evaluation.md` 中的 CRAAP 测试：
- **时效性：** 对当前研究问题而言是否足够新？
- **相关性：** 是否真正回答了问题？
- **权威性：** 作者是谁，具备什么资质？
- **准确性：** 证据是否可靠且可验证？
- **目的：** 此来源为何存在，是否带有偏见？

在研究日志中标记低质量来源。不要丢弃它们，而应记录其局限，使后续综合能够加以考虑。

## 转换信号

满足以下条件时进入阶段 3（评估缺口）：
- 首轮研究完成并已保存到产物目录。
- 至少完成一轮定向后续调查。
- 研究日志中已经记录缺口。
- 已经评估来源质量。

如果首轮研究已经明显达到主题饱和，也可以进入下一阶段，即不存在重要缺口。

## 保存内容

每轮研究都应在 `<artifacts-root>/<mission-slug>/layer-3-detailed/` 中生成带日期的文件，由此构成金字塔底层，即保存原始发现的详细档案。
