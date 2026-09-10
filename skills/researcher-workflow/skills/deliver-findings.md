---
name: deliver-findings
description: >-
  researcher-workflow 的交付阶段。通过绝对路径引用以及各金字塔层级的内容说明，
  将发现报告给 orchestrator。这是最终阶段。
compatibility: Hermes Agent
metadata:
  tags: [research, delivery, handoff]
  spec-version: "1.0"
---

# 交付发现

## 使用时机

阶段 4（构建金字塔）完成后加载此技能。此时产物金字塔的三个层级均已存在，交叉引用链接也已验证。

## 执行步骤

### 1. 验证金字塔完整性

检查所有预期文件是否存在：

```bash
ls -R /tmp/researcher-workflow/<mission-slug>/
```

### 2. 向 Orchestrator 报告

返回包含绝对路径的结构化交付报告。输出应让 orchestrator 可以读取符合自身需要的层级，同时让下游 Agent 能够按需深入。

```
## 研究完成：<任务标题>

### 产物金字塔

**第 1 层 - 管理摘要**
Path: /tmp/researcher-workflow/<mission-slug>/layer-1-summary/README.md
适合：决策者 - 结论和关键发现
包含：带置信度评估和深入分析链接的单页摘要

**第 2 层 - 分析集合**
Path: /tmp/researcher-workflow/<mission-slug>/layer-2-analysis/
适合：架构师、领域专家 - 按发现组织的主题分析
包含：N 个独立分析文件，每个文件用证据覆盖一个主要主题并链接到详细档案
可用文件：<列出每份分析文件并提供一句话说明>

**第 3 层 - 详细档案**
Path: /tmp/researcher-workflow/<mission-slug>/layer-3-detailed/
适合：深入调查人员 - 原始发现、来源评估和缺口决策
包含：N 份研究日志、来源质量评估和缺口简报
可用文件：<列出每份档案并提供一句话说明>

### 方法论说明
- 使用 CRAAP 框架评估来源（见 `layer-3-detailed/source-quality-assessment.md`）
- 判定为范围内的缺口：
  - <已补齐的缺口> → 在第 2 轮收集中解决
- 判定为范围外的缺口：
  - <已搁置的缺口> → 记录在 `layer-3-detailed/gap-brief-N.md`

### 置信度摘要
- 高：<列表>
- 中：<列表>
- 低：<列表>
```

### 3. 不要清理

将文件保留在 `/tmp/` 中，操作系统会在文件过期后清理。Orchestrator 和下游使用方 Agent 需要这些文件保持可访问，以便深入阅读。

## 转换信号

这是终止阶段，不再发生后续转换。

## 工具使用

- 使用终端验证文件是否存在。
- 使用标准输出返回交付报告。
