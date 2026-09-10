---
name: artifact-pyramids
description: >-
  对 AI Agent 产物实施渐进披露。将研究输出组织为深度递增的三个层级：摘要
  （关键发现）、分析集合（按维度拆分的文件）和详细档案（来源摘录、原始数据、
  访谈记录），使下游 Agent 和人类只读取所需深度。组织研究输出、构建多 Agent
  研究管线或设计 Agent 协作协议时加载此技能。
license: MIT
compatibility: 与 Agent 无关，概念适用于任何 AI Agent 工作流。脚本要求 Python 3.9+ 和 POSIX shell。
metadata:
  spec-version: "0.0.3"
  source: https://github.com/groktopus/artifact-pyramids
  canonical-article: https://www.groktop.us/artifact-pyramid-progressive-disclosure/
---

# 面向 Agent 化 AI 研究的产物金字塔

渐进披露规定如何向 Agent 提供上下文：启动时提供元数据，激活时提供指令，按需加载资源。**产物金字塔把同一原则应用到 Agent 的产出。**三个层级逐步深入，每层都可以独立使用，并链接到下一层。

## 加载指引

**生成产物金字塔时，必须成套加载以下参考资料，不得零散加载：**

| 参考资料 | 文件 |
|-----------|------|
| 管线阶段 - 层级定义、导航格式、生成流程 | `references/pipeline-stages.md` |
| 输出分类框架 - 与角色无关的内容契约、`00-index` 与 L1 的边界 | `references/output-classification-framework.md` |
| 质量门 - 各层级的验证检查清单 | `references/quality-gates.md` |
| 委派上下文模板 - 约束子 Agent 输出的准确文本 | `references/delegation-context-template.md` |

这四份资料分别定义规范中相互补充且彼此依赖的方面。只加载其中一部分，可能违反内容契约，例如把发现写进 `00-index.md`，或遗漏必需的导航机制。编写任何金字塔文件前都要完整加载这组资料。

下方参考资料表说明各文件的加载时机；上面四份资料在生成金字塔时**始终必需**。其余资料（框架、完整示例、规范文章、思想沿革、来源追溯、复合综合）属于补充材料，在任务需要概念深度或实践范例时加载。

## 金字塔

```
      ┌──────────────┐
      │   L1 摘要    │  一个文件：研究问题、关键发现、
      │    🎯        │  最重要的影响。链接到 L2 文件。
      └──────┬───────┘
      ┌──────┴───────┐
      │   L2 分析    │  按维度拆分文件：市场、竞争、
      │     集合     │  技术可行性、风险。每份可独立使用，
      │   🧩        │  并链接到 L3 档案。
      └──────┬───────┘
      ┌──────┴───────┐
      │   L3 档案    │  来源摘录、原始数据表、访谈记录、
      │    📦        │  方法说明。作为参考资料库，
      └──────────────┘  按需读取。
```

金字塔自顶向下使用，但通过递归缺口分析生成：从摘要开始，嵌入分析文件链接，再编写链接到档案的分析文件，并在每轮之后评估是否仍有缺口。

**层级编号自顶向下。**L1 是提炼程度最高的层级（入口），L3 最为详细（按需读取）。这与 Agent Skills 的输入模型对应：元数据（L1）→ 指令（L2）→ 资源（L3）。

## 导航机制

每一层的每个文件底部都必须带有明确的 `SOURCES` 部分，其中包含绝对路径引用及说明：

```
SOURCES (LAYER 2 NAVIGATION)
research/analysis/market-position.md
 -> 支持第 2 节的竞争对手映射和市场份额分析
research/analysis/technical-feasibility.md
 -> 支持第 3 节的架构评估
research/dossiers/competitor-profiles.md
 -> 竞争对手原始数据档案
```

这些不是脚注，而是供 Agent 使用方使用的**导航机制**。每条说明都回答使用方 Agent 在加载前会提出的问题：*继续深入会看到什么？*

## 参考文件

| 参考资料 | 加载时机 | 文件 |
|-----------|-----------|------|
| 框架与对称性 | 需要完整概念基础，包括不对称问题、多 Agent 路由、DIKW 关系 | `references/artifact-pyramid-framework.md` |
| 管线阶段 | 构建或审计金字塔，需要各层详细定义、导航格式和生成流程 | `references/pipeline-stages.md` |
| 质量门 | 需要验证产物是否符合所在层级的标准 | `references/quality-gates.md` |
| 完整示例 | 希望查看三个层级的完整合成示例 | `references/synthetic-example.md` |
| 规范文章 | 阅读 groktop.us 发布的文章，即定义此概念的第 3 层产物 | `references/canonical-article.md` |
| 思想沿革 | 了解软件架构文档（4+1 视图、C4、arc42、ADR）如何以不同名称独立发现渐进披露，以及产物金字塔在此基础上的泛化 | `references/intellectual-lineage.md` |
| 方法论到金字塔的映射 | 了解专家角色如何按维度边界规则，把领域方法论映射到通用金字塔结构 | `references/methodology-to-pyramid-mapping.md` |
| 输出分类框架 | **与角色无关**，任何专家都可通过三个问题把输出映射到正确层级：谁使用、使用频率、回答什么问题。包含各层内容契约，以消除 `00-index` 与 L1 文件的重复 | `references/output-classification-framework.md` |
| 复合金字塔综合 | 将多个子 Agent 金字塔合并成根级复合金字塔，包括 orchestrator 流程、`SOURCES` 约定和 jobs-finder 管线示例 | `references/composite-pyramid-synthesis.md` |
| 委派上下文模板 | 向子 Agent 委派研究时，需要在上下文中加入准确文本以确保产出金字塔 | `references/delegation-context-template.md` |
| 扁平输出迁移到金字塔 | 把现有扁平 JSON 输出转换为产物金字塔，包括 L1/L2/L3 结构、`00-index` 规则和下游使用方的回退读取 | `references/flat-to-pyramid-migration.md` |
| 嵌套金字塔模式 | 设计随时间生成多条产物流的单一系统（多阶段、多轮次），通过嵌套在单一根金字塔下避免分散 | `references/nested-pyramid-pattern.md` |

## 脚本

| 脚本 | 加载时机 | 文件 |
|--------|-----------|------|
| pyramid-status | 希望审计现有研究目录的结构覆盖情况 | `scripts/pyramid-status.sh` |
| extract-atoms | 已有原始来源文本，需要提取候选原子主张 | `scripts/extract-atoms.py` |

## 模板

| 模板 | 加载时机 | 文件 |
|----------|-----------|------|
| 项目脚手架 | 启动新研究项目并需要索引骨架 | `assets/pyramid-template.md` |
| 产物清单 | 需要跟踪项目各层级中已有的内容 | `assets/artifact-inventory.md` |

## 快速开始

```bash
# 为新研究项目创建包含三个层级目录的脚手架
mkdir -p my-project/{01-summary,02-analysis,03-dossiers}
cp assets/pyramid-template.md ./my-project/00-index.md

# 检查现有项目的结构覆盖情况
scripts/pyramid-status.sh ./my-project

# 从来源文本提取候选原子主张
scripts/extract-atoms.py ./my-project/03-dossiers/source-1.txt
```

## 项目结构

```
my-project/
├── 00-index.md              # 项目脚手架（来自模板）
├── 01-summary/              # L1：一个文件，包含关键发现、影响和 L2 链接
├── 02-analysis/             # L2：按维度拆分的文件（市场、竞争、技术）
├── 03-dossiers/             # L3：来源摘录、访谈记录、原始数据和方法
└── artifact-inventory.md    # 跨层级跟踪（来自模板）
```

数字前缀体现金字塔自顶向下的方向：`01` 使用最频繁，`03` 按需读取。

## 核心原则

1. **渐进披露具有对称性。**同一三层模型既约束 Agent 使用的内容（元数据 → 指令 → 资源），也约束其产出（摘要 → 分析 → 档案）。
2. **每一层都可以独立使用。**orchestrator Agent 只读取 L1 摘要，technical-architect Agent 读取一份 L2 分析文件，reviewer 读取 L3 档案。
3. **导航必须明确。**每个文件都带有包含绝对路径和说明的 `SOURCES` 部分。它不是脚注，而是 Agent 导航机制，用来回答*继续深入会看到什么？*
4. **深度随任务复杂度变化。**简单简报可能只生成 L1 和两份分析文件；竞争格局研究可能需要全部三个层级，且每层包含多个文件。
5. **质量门具有方向性。**材料只有满足目标层级的质量门，才能从 L3（来源）向 L1（摘要）移动。
6. **`03-dossiers/` 必须保持扁平，不得包含子目录。**档案层是扁平参考资料库。使用带轮次或类别前缀的文件名组织，例如 `epoch-1-validation-edit-3.json`，不要使用嵌套目录。`03-dossiers/` 内的子目录违反扁平文件契约，并会破坏 `SOURCES` 导航路径。
7. **根级文件持续修订，底层文件保持固定。**在多轮次或多阶段系统中，`00-index.md`、`01-summary/findings.md` 和 `02-analysis/` 中的轨迹文件会随新数据到来而增长，并重写以反映当前状态。`03-dossiers/` 中的文件以及 `02-analysis/` 下按类别拆分的分析文件只创建一次，不再修改，因为它们代表固定时间点。

## 不适用场景

- 无需保留研究产物的单轮问答。
- 只产生临时输出的任务，例如一次性计算或快速查询。
- 来源材料本身就是最终输出、无需综合的工作流。
