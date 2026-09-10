---
name: orchestration-methodology
description: "R&D 编排方法论 - 从已确认需求基线建立 Flow，完成任务分解、专家路由、工作流恢复、证据综合和人类决策交接。"
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [orchestration, multi-agent, workflow, routing, synthesis]
---

# R&D 编排方法论

以已确认需求基线为起点，将研发工作组织为可追溯的专家协作。编排者管理工作流，不修改业务意图、不替专家作出领域决策，也不代替人类接受风险。

## 编排生命周期

```
校验基线 → 分解 → 路由 → 监控 → 综合 → 人类批准
```

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/task-decomposition.md` | 需要把复杂问题拆为可交给专家的子任务 |
| `references/specialist-routing.md` | 需要为子任务匹配正确的专家角色 |
| `references/workflow-monitoring.md` | 工作流跨越多个角色、质量门阻断，或工作需要重试和重新路由 |
| `references/synthesis-patterns.md` | 需要把多个专家的输出组合成连贯整体 |
| `references/human-decision-handoff.md` | 业务语义、交付取舍或高风险例外需要人类责任人裁决 |
