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
| `references/requirements-intake.md` | 收到自然语言需求、需要形成可确认的基线 revision，或收到未就绪基线时 |
| `references/delivery-governance.md` | 分解实现类工作、分配工作区、设定质量门顺序或判定某个动作是否需要审批时 |

持久化决策可使用 `scripts/decision_bridge.py`；它只记录单次决策并在批准后解锁绑定任务，不执行 push、merge 或 deploy。
