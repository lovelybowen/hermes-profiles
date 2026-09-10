---
name: researcher-workflow
description: >-
  面向 R&D 专家子 Agent 的非交互式深度研究管线。当 orchestrator 分配外部事实、
  技术选型或证据缺口调查时使用。研究员接收带需求基线引用的简报、推导范围、
  使用 Hermes 原生研究工具（groktocrawl 为可选增强）开展多轮研究、评估是否存在
  需要递归调查的缺口，并在任务工作区中生成分层产物金字塔。
compatibility: Hermes Agent - 为非交互式子 Agent 运行而设计
metadata:
  tags: [workflow, bundle, research, subagent, pipeline, progressive-disclosure]
  spec-version: "1.0"
---

# 研究员工作流

用于系统化调查 R&D 证据缺口并以渐进披露形式输出产物的五阶段工作流，供编排者调度研究员专家子 Agent 时使用。研究结果只能补充证据；与已确认需求基线冲突时必须交回 `Intent Owner`。

```
接收任务 → 收集 → 评估缺口 → [递归] → 构建金字塔 → 交付
```

## 参考文件

本技能是索引；五个阶段的方法论细节位于 `references/`，按需加载。

| 阶段 | 参考文件 | 触发条件 |
|-------|-----------|---------|
| 接收任务 | `references/receive-mission.md` | 编排者分配研究简报，将其重述为明确范围 |
| 收集 | `references/research-gather.md` | 使用原生研究工具开展多轮收集 |
| 评估缺口 | `references/evaluate-gaps.md` | 评估已收集材料，决定递归深度 |
| 构建金字塔 | `references/build-pyramid.md` | 组装渐进披露产物文件 |
| 交付 | `references/deliver-findings.md` | 返回结构化交接消息与层级说明 |
| 流程全貌 | `references/decision-map.md` | 需要五阶段管线与递归分支的整体视图 |
| 工具选择 | `references/tool-governance.md` | 需要决定用原生工具还是可选增强 |
| 来源溯源 | `references/generated-from.md` | 需要了解本技能的生成来源 |

## 加载方式与导航

```python
skill_view('researcher-workflow')                       # 1. 本索引
# 然后按当前阶段加载对应参考文件：
skill_view('researcher-workflow', file_path='references/receive-mission.md')
skill_view('researcher-workflow', file_path='references/research-gather.md')
skill_view('researcher-workflow', file_path='references/evaluate-gaps.md')
skill_view('researcher-workflow', file_path='references/build-pyramid.md')
skill_view('researcher-workflow', file_path='references/deliver-findings.md')
```

先判断当前阶段，再加载对应的参考文件并遵循其指令。每个阶段文件都记录自身的转换信号。

## 管线启发式规则

- **入口：** 始终从阶段 1（接收任务）开始，不能直接进入其他阶段。
- **递归：** 阶段 3（评估缺口）可以回到阶段 2（收集）进行定向补充。这是唯一的非线性路径。
- **工具纪律：** 默认使用 Hermes 原生工具（`web_search`、`web_extract`、browser）。`groktocrawl` 为可选增强，仅在 `command -v groktocrawl` 确认可用、且任务需要其独有能力（大规模全站抓取、强反自动化页面）时启用。完整选择表与回退链见 `references/tool-governance.md`，用 `skill_view(name="researcher-workflow", file_path="references/tool-governance.md")` 加载。
- **产物位置：** 输出写入 `<artifacts-root>/<mission-slug>/`，其中 `<artifacts-root>` 为 Kanban 任务工作区，或独立运行时的 `${RESEARCH_ARTIFACTS_DIR:-./research}`。**不要**把产物只留在会被清理的临时目录；Kanban 任务必须通过 `kanban_complete(artifacts=[...])` 显式声明产物。每一层都通过附带说明的链接指向下一层，使使用方能够选择所需深度。
- **状态：** 阶段之间不保留持久状态。每个阶段文件读取任务简报和产物目录来确定上下文。

## 易错点

### `delegate_task` 超时恢复

收集阶段使用 `delegate_task` 创建子 Agent 并行研究，这些子 Agent 有 600 秒的硬超时限制。当单个整体研究任务超时时，将其拆为最多三个并行子任务，每个任务覆盖不同的方法、来源或角度。一次实际会话中，三个并行任务有两个成功，第三个仍然超时。

并行子任务也超时时，第二级回退方案是不再委派，直接对每个已知规范 URL 单独取证：`web_extract <url>`，纯文本端点用 `curl`；若环境中确实存在 `groktocrawl`，`groktocrawl scrape <url>` 同样可用。注意自动综合路径不可靠：即使服务正常，`groktocrawl agent` 与 `groktocrawl search` 也可能返回空结果（`agent` 有时返回“unable to find any relevant web pages”，`search` 可能尚未配置）。常见架构方法论来源如下：
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions - Michael Nygard 的 ADR 原始文章
- https://docs.arc42.org/ - 列出全部 12 个章节的 arc42 模板文档
- https://arc42.org/canvas - arc42 Canvas（完整模板的压缩版本）
- https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf - Kruchten 1995 年的原始论文
- https://c4model.com - Simon Brown 的 C4 模型

核心恢复原则：子 Agent 超时不代表研究问题失效。应缩小每个子 Agent 的范围（每个 Agent 处理更少来源），并直接抓取特定 URL（`web_extract` / `curl` / 可用的 `groktocrawl scrape`）来补齐缺口，而不是重新委派同一个任务包。
