---
name: researcher-workflow
description: >-
  面向 R&D 专家子 Agent 的非交互式深度研究管线。当 orchestrator 分配外部事实、
  技术选型或证据缺口调查时使用。研究员接收带需求基线引用的简报、推导范围、
  通过 groktocrawl 开展多轮研究、评估是否存在需要递归调查的缺口，并在 /tmp/ 中
  生成分层产物金字塔。
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

## 子技能

| 阶段 | 技能 | 触发条件 |
|-------|-------|---------|
| 接收任务 | `researcher-workflow/receive-mission` | 编排者分配研究简报，将其重述为明确范围 |
| 收集 | `researcher-workflow/research-gather` | 只使用 groktocrawl 工具套件开展研究 |
| 评估缺口 | `researcher-workflow/evaluate-gaps` | 评估已收集材料，决定递归深度 |
| 构建金字塔 | `researcher-workflow/build-pyramid` | 组装渐进披露产物文件 |
| 交付 | `researcher-workflow/deliver-findings` | 返回绝对路径引用和层级说明 |

## 导航

研究员角色加载此总技能后，先判断当前阶段，再通过 `skill_view()` 加载对应子技能并遵循其指令。每个子技能都记录自身的转换信号。

## 管线启发式规则

- **入口：** 始终从阶段 1（接收任务）开始，不能直接进入其他阶段。
- **递归：** 阶段 3（评估缺口）可以回到阶段 2（收集）进行定向补充。这是唯一的非线性路径。
- **工具纪律：** 所有 Web 研究都通过 groktocrawl 进行。禁止使用内置 `web_search` 和 `web_extract`，因为它们能力不足且经常失效。完整回退链和依据见 `references/tool-governance.md`，使用 `skill_view(name="researcher-workflow", file_path="references/tool-governance.md")` 加载。
- **产物：** 输出以分层 Markdown 文件写入 `/tmp/researcher-workflow/<mission-slug>/`。每一层都通过附带说明的链接指向下一层，使使用方能够选择所需深度。
- **状态：** 阶段之间不保留持久状态。每个子技能读取任务简报和产物目录来确定上下文。

## 易错点

### `delegate_task` 超时恢复

收集阶段使用 `delegate_task` 创建子 Agent 并行研究，这些子 Agent 有 600 秒的硬超时限制。当单个整体研究任务超时时，将其拆为最多三个并行子任务，每个任务覆盖不同的方法、来源或角度。一次实际会话中，三个并行任务有两个成功，第三个仍然超时。

并行子任务也超时时，第二级回退方案是对剩余来源的已知规范 URL 直接执行 `groktocrawl scrape`。即使服务器正常，`groktocrawl agent` 和 `groktocrawl search` 也可能返回空结果；`agent` 有时返回“unable to find any relevant web pages”，而 `search` 可能尚未配置。可靠的回退方式是分别对每个已知规范 URL 执行 `groktocrawl scrape <url>`。常见架构方法论来源如下：
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions - Michael Nygard 的 ADR 原始文章
- https://docs.arc42.org/ - 列出全部 12 个章节的 arc42 模板文档
- https://arc42.org/canvas - arc42 Canvas（完整模板的压缩版本）
- https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf - Kruchten 1995 年的原始论文
- https://c4model.com - Simon Brown 的 C4 模型

核心恢复原则：子 Agent 超时不代表研究问题失效。应缩小每个子 Agent 的范围（每个 Agent 处理更少来源），并直接使用 groktocrawl 抓取特定 URL 来补齐缺口，而不是重新委派同一个任务包。
