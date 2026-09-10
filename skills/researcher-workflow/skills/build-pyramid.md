---
name: build-pyramid
description: >-
  渐进披露产物金字塔的组装方法。在缺口评估确认研究达到饱和后加载。
  读取 layer-3-detailed/ 中收集的材料，生成分层输出：摘要（第 1 层）、
  分析集合（第 2 层）和详细档案（第 3 层）。每一层都附带说明并链接到下一层。
compatibility: Hermes Agent
metadata:
  tags: [research, pyramid, artifacts, writing, synthesis]
  spec-version: "1.0"
---

# 构建金字塔

## 使用时机

阶段 3（评估缺口）确认研究达到饱和后加载此技能。所有已收集材料都位于 `/tmp/researcher-workflow/<mission-slug>/layer-3-detailed/`。本阶段将这些材料转化为渐进披露金字塔。

## 金字塔结构

```
layer-1-summary/
└── README.md              ← 管理摘要（单一文件，高层概览）

layer-2-analysis/
├── 01-market-analysis.md   ← 主题分析文件
├── 02-risk-assessment.md   ← 每个主要主题一个文件
├── 03-competitive-landscape.md
└── ...

layer-3-detailed/
├── 01-gather-pass-1.md     ← 原始研究日志
├── 02-gather-pass-2.md     ← 每轮研究一个文件
├── gap-brief-1.md          ← 缺口评估记录
├── source-quality-assessment.md
└── ...
```

金字塔顶部窄小（摘要密度高），底部宽广（内容详细且全面）。

## 执行步骤

### 1. 阅读全部已收集材料

读取 `layer-3-detailed/` 中的所有文件，完整理解已有发现。

### 2. 构建第 3 层 - 详细档案（已有内容）

阶段 2 的研究日志已经存放在这里。评审这些日志并按合理顺序组织，使用数字作为文件名前缀来标明阅读顺序。新增 `_index.md`，用一句话说明列出全部档案：

```markdown
# 详细档案：<任务标题>

## 可用文件

- `01-gather-pass-1.md` - 首轮研究，覆盖<广度范围>
- `02-gather-pass-2.md` - 针对<特定缺口>的后续研究
- `source-quality-assessment.md` - 对所有来源进行 CRAAP 评估
- `gap-brief-1.md` - 被判定为范围外的缺口
```

### 3. 构建第 2 层 - 分析集合

针对研究中的每个主要主题编写一份聚焦的分析文件。每份分析文件应当：

- 陈述主张或发现。
- 概述支持性证据。
- 说明相互冲突的证据或不确定性。
- 链接到第 3 层的具体档案以提供细节。

链接格式（绝对路径加说明）：

```
参见 [/tmp/researcher-workflow/<mission-slug>/layer-3-detailed/01-gather-pass-1.md]，
其中记录了形成此项发现的初步调查。
```

### 4. 构建第 1 层 - 管理摘要

在 `layer-1-summary/` 中编写唯一的 `README.md`。这是约束最严格、信息密度最高、提炼程度最高的文件。结构如下：

```markdown
# 研究摘要：<标题>

## 一段话结论
<决策者最需要知道的一件事>

## 关键发现
- <发现 1> → [查看分析](</analysis/01-market-analysis.md>)
- <发现 2> → [查看分析](</analysis/02-risk-assessment.md>)

每项发现都应链接到相关分析文件，并简要说明其中内容。

## 置信度评估
- **高置信度：** <拥有充分且经过三角验证证据的主张>
- **中置信度：** <证据合理但不完整的主张>
- **低置信度：** <证据薄弱或相互冲突的主张>

## 范围外事项
- <缺口评估期间经判断后搁置的事项>

## 如何深入阅读
- 如需市场背景和竞争格局 → 加载 `layer-2-analysis/`
- 如需完整来源日志和缺口评估 → 加载 `layer-3-detailed/`
```

### 5. 确保链接有效

完成所有层级后，验证第 1 层和第 2 层中的每个交叉引用都能解析到磁盘上的实际文件。断裂链接会使渐进披露失效。

## 转换信号

满足以下条件时进入阶段 5（交付）：
- 三个层级均已编写完成。
- 交叉引用链接已经验证。
- 文件使用数字前缀组织，并提供 `_index.md` 导航。

## 工具使用

- 使用终端读取和综合文件。
- 使用 `write_file` 创建产物文件。
- 不使用 Web 研究工具，此时正在构建产物，而不是收集资料。
