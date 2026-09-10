---
name: research-gather
description: >-
  只使用 groktocrawl 套件开展系统化多轮研究收集。禁止使用 web_search 和
  web_extract 工具。遵循确定的回退链：agent → search → scrape → browser。
  作为子 Agent 被调度时，运行此技能以执行 researcher-workflow 的研究阶段。
compatibility: Hermes Agent
metadata:
  tags: [research, gathering, groktocrawl, web-extraction]
  spec-version: "1.0"
---

# 收集研究资料

## 使用时机

完成阶段 1（接收任务）后加载此技能，此时 `SCOPE.md` 已存在，产物目录也已就绪。这是把研究问题转化为已收集材料的执行阶段。

## 工具禁令

**不要使用 `web_search` 或 `web_extract` 工具。** 它们不足以支持系统化研究且经常失效。所有 Web 研究必须通过 groktocrawl 套件进行：

| 需求 | groktocrawl 命令 | 原因 |
|------|---------------------|-----|
| 多来源研究与综合 | `groktocrawl agent "<prompt>"` | 自动完成搜索、抓取和综合 |
| 用于发现资料的 Web 搜索 | `groktocrawl search "<query>" --limit N --json` | 返回结构化搜索结果 |
| 单个页面内容 | `groktocrawl scrape <url>` | 提取干净的 Markdown |
| 大量使用 JS 或具有反自动化保护的页面 | `groktocrawl browser` 套件 | 使用支持 JS 渲染的无头浏览器 |
| 二进制文件（PDF、图像） | `groktocrawl download <url>` | 下载文件 |
| 发现站点中的 URL | `groktocrawl map <url>` | 广度优先发现路由 |
| 全站内容提取 | `groktocrawl crawl <url>` | 递归深度优先抓取 |

## 执行步骤

### 1. 阅读范围

读取 `/tmp/researcher-workflow/<mission-slug>/SCOPE.md`，理解研究问题、范围边界和已知未知项。

### 2. 加载研究方法论

如果尚未加载，则加载共享方法论参考资料：

```
skill_view(name="research-methodology", file_path="references/source-evaluation.md")
skill_view(name="research-methodology", file_path="references/synthesis-patterns.md")
```

### 3. 执行首轮研究

使用 `groktocrawl agent` 获得最广泛的覆盖：

```bash
groktocrawl agent "研究以下问题：<SCOPE.md 中重述的问题>。重点关注：<研究方法部分列出的领域>。综合关键发现，识别相互冲突的主张，并标记缺口。"
```

将输出保存为带时间戳的研究日志：

```bash
cat > /tmp/researcher-workflow/<mission-slug>/layer-3-detailed/01-gather-pass-1.md << 'EOF'
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

针对每个已识别缺口，使用合适的 groktocrawl 命令：

- **轻度缺口**（需要快速核实事实）：`groktocrawl search "<specific query>" --limit 3`
- **中度缺口**（需要单篇文章）：`groktocrawl scrape <url>`
- **深度缺口**（需要综合）：`groktocrawl agent "<focused prompt>"`
- **JS 渲染内容：** groktocrawl 浏览器套件

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

每轮研究都应在 `/tmp/researcher-workflow/<mission-slug>/layer-3-detailed/` 中生成带日期的文件，由此构成金字塔底层，即保存原始发现的详细档案。
