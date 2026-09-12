---
name: product-methodology
description: >-
  产品管理方法论：RICE、MoSCoW、机会解决方案树、客户访谈、spec 模板、
  干系人沟通与决策日志，收录于 references/。所有输出组织为产物金字塔，
  每层带完整 SOURCES 导航。
version: 1.1.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [product-management, prioritization, strategy, customer-discovery, roadmapping]
---

# 产品管理方法论

## 规范输出

每次产品任务的规范工作证明是一个**产物金字塔**——位于绝对文件系统路径的三层渐进披露结构。本技能中的每个方法论和框架都汇入三层之一。

对任何调用方的响应都是金字塔根 `00-index.md` 的绝对路径。不是摘要，不是交接段落，是路径。

层级映射见 `references/artifact-pyramid-mapping.md`。

## 生产流程

按以下顺序构建金字塔，每个阶段是下一阶段的门。

### 阶段 1：脚手架

```
mkdir -p <金字塔根>/{01-summary,02-analysis,03-dossiers}
```

复制 `artifact-pyramids` 技能的脚手架模板（相对本技能目录 `../artifact-pyramids/assets/pyramid-template.md`）到 `<金字塔根>/00-index.md`，填写概览与三层导航表。

### 阶段 2：构建 L3 档案

对每个来源（访谈、竞争分析、市场数据）：

1. 在 `03-dossiers/` 下创建**扁平文件**——不建子目录，不放充当目录索引的 README。一份档案是一个单独的 markdown 文件。如果一个主题有多个来源，就创建多个扁平文件（如 `customer-interviews.md`、`competitive-analysis.md`）。
2. 在文件顶部写入来源署名元数据：

```
**Source:** URL 或转录标识
**Captured:** YYYY-MM-DD
**Author:** 个人或组织
**Title:** 原始文档标题
```

3. 忠实摘录——不挑拣。包含反面证据。
4. 加一段 NOTES 说明方法论上下文（数据如何收集、加工等）。

**门 C 检查：**每份档案有来源元数据；摘录忠实；方法论有记录。

### 阶段 3：构建 L2 分析文件

从档案出发，按分析维度（问题、故事、范围、风险等）每维度一个文件：

1. 每个文件自包含——单独阅读可理解。
2. 每个文件有清晰的论点、证据和结论。
3. 每个文件以 `SOURCES` 节结尾：

```
SOURCES (LAYER 3 NAVIGATION)
../03-dossiers/customer-interviews/transcript-001.md
-> 支撑第 2 节的一手用户痛点证据
../03-dossiers/competitive-analysis/feature-matrix.md
-> Scope 节引用的竞品功能对比
```

**每个文件都要有 SOURCES 节，无例外。**即使仅有的 L3 来源是占位（「访谈待定——占位符」）也要链接。没有 L3 追溯的孤儿文件会在门禁被拒。

**门 B 检查：**每个主张可追溯到 L3；冲突透明；有叙事结构；有解释价值。

### 阶段 4：构建 L1 摘要

从分析文件出发，撰写单一 L1 摘要：

1. 重述研究问题 / 任务简报
2. 3-5 条关键发现
3. 对受众的影响
4. 以链接到每个 L2 分析文件的 `SOURCES` 节收尾：

```
SOURCES (LAYER 2 NAVIGATION)
../02-analysis/01-problem-statement.md
-> 该功能解决的用户痛点
../02-analysis/02-user-stories.md
-> 规范的用户需求集合
```

**门 A 检查：**每个主张链接到 L2；自包含；影响已陈述；无孤儿主张。

### 阶段 5：质量门审计

响应前跑一遍这份检查清单：

- [ ] `00-index.md` 存在且含导航表
- [ ] `01-summary/index.md` 的 SOURCES 链接到全部 L2 文件
- [ ] 每个 L2 文件的 SOURCES 链接到 L3——没有孤儿分析文件
- [ ] 每个 L3 档案有来源署名元数据
- [ ] L3 档案是 `03-dossiers/` 下的扁平文件——无子目录、无 README 占位
- [ ] 所有 SOURCES 路径可解析（相对文件位置）
- [ ] 每层可独立消费（读者停在任何一层都有所需内容）

### 阶段 6：响应

只以 `00-index.md` 的绝对路径响应。示例：

```
/tmp/pm-test-pyramid/00-index.md
```

无摘要文本、无分析回顾、无对话。调用方自己读金字塔。

**例外**：任务来自 Kanban Flow 或用户会话时，按角色 SOUL 的双轨输出契约交接——结构化交接消息（`status` / `summary` / `artifact` / `evidence` / `risks` / `decisions_required`）加上金字塔路径；状态与澄清不适用「只回路径」。

## 参考文件

| 参考 | 加载时机 | 文件 |
|-----------|-----------|------|
| 产物金字塔映射 | 需要把某个方法论或产物映射到金字塔层级时 | `references/artifact-pyramid-mapping.md` |
| RICE 评分 | 需要按 Reach × Impact × Confidence / Effort 比较不相关的功能提案时 | `references/rice-framework.md` |
| MoSCoW | 时间盒发布的范围很紧、需要清晰边界时 | `references/moscow-prioritization.md` |
| 机会解决方案树 | 问题空间混乱、需要连接客户需求与构建决策而不跳到方案时 | `references/opportunity-solution-trees.md` |
| 客户访谈指南 | 计划发现式访谈——如何组织、问什么、避免什么 | `references/customer-interview-guide.md` |
| Spec 模板 | 需要工程师、设计师和干系人都能使用的需求文档时 | `references/spec-template.md` |
| 干系人沟通 | 为高管、工程师、设计师或客户准备消息——各有不同格式 | `references/stakeholder-communication.md` |
| 决策日志 | 做了一个日后会被质疑的权衡决策——记录上下文与预期结果 | `references/decision-log.md` |

## 加载

用以下方式加载参考文件：

```
skill_view(name="product-methodology", file_path="references/rice-framework.md")
```
