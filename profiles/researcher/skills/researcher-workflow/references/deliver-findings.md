*本文件是 `researcher-workflow` 技能的参考文件，加载方式：*
*`skill_view('researcher-workflow', file_path='references/deliver-findings.md')`*

# 交付发现

## 使用时机

阶段 4（构建金字塔）完成后加载此技能。此时产物金字塔的三个层级均已存在，交叉引用链接也已验证。

## 执行步骤

### 1. 验证金字塔完整性

检查所有预期文件是否存在：

```bash
ls -R <artifacts-root>/<mission-slug>/
```

### 2. 向 Orchestrator 报告

返回结构化交接消息（契约见 `researcher` 角色的 `SOUL.md`），而不是散文报告：

```yaml
status: completed
summary: <一到三句话：结论是什么、服务于哪个基线或研发决策>
artifact: <绝对路径>/<mission-slug>/00-index.md
evidence:
  layers:
    l1: <绝对路径>/<mission-slug>/layer-1-summary/README.md
    l2: <绝对路径>/<mission-slug>/layer-2-analysis/
    l3: <绝对路径>/<mission-slug>/layer-3-detailed/
  key_sources: [<关键来源 URL + 核验方式>]
  confidence: {high: [...], medium: [...], low: [...]}
risks: [<未解决的证据缺口>]
decisions_required: [<与基线冲突的发现，需 Intent Owner 裁决>]
```

各层级的详细清单：

**第 1 层 - 管理摘要**
Path: <artifacts-root>/<mission-slug>/layer-1-summary/README.md
适合：决策者 - 结论和关键发现
包含：带置信度评估和深入分析链接的单页摘要

**第 2 层 - 分析集合**
Path: <artifacts-root>/<mission-slug>/layer-2-analysis/
适合：架构师、领域专家 - 按发现组织的主题分析
包含：N 个独立分析文件，每个文件用证据覆盖一个主要主题并链接到详细档案
可用文件：<列出每份分析文件并提供一句话说明>

**第 3 层 - 详细档案**
Path: <artifacts-root>/<mission-slug>/layer-3-detailed/
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

### 3. 保证产物可达

Orchestrator 与下游 Agent 必须能读到这些文件，因此：

- **Kanban 任务：** 在 `kanban_complete(artifacts=[...])` 中显式声明每个产物。`scratch` 工作区在任务完成时会被删除，未声明的文件视为未交付。
- **独立运行：** 写入 `${RESEARCH_ARTIFACTS_DIR:-./research}/<mission-slug>/`，不要只写在 `/tmp`。
- 交付的绝对路径必须指向真实存在的文件；交付前用 `ls -R` 验证。

## 转换信号

这是终止阶段，不再发生后续转换。

## 工具使用

- 使用终端验证文件是否存在。
- 使用标准输出返回交付报告。
