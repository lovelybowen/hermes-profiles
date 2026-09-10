# 工作流监控与恢复

使用本协议监控已路由工作、恢复受阻任务，并判断工作流何时可以进入综合阶段。这是工作流状态监控，不会分配生产运维或基础设施责任。

## 工作流台账

使用以下字段跟踪每个子任务：

| 字段 | 必需内容 |
|---|---|
| Task | 稳定标识和范围明确的问题 |
| Baseline | 需求基线的稳定标识、URI、revision 或 content hash |
| Profile | 负责当前尝试的角色 |
| Inputs | 该角色可以依赖的产物路径和决策 |
| Completion criterion | 可观察、能判断任务完成的条件 |
| Downstream consumer | 下一步需要结果的角色或人 |
| Status | `queued`、`ready`、`running`、`blocked`、`rework`、`passed` 或 `skipped` |

只有全部声明输入都存在时，任务才能变为 `ready`。只有完成标准和所有已配置质量门都满足时，才能标记为 `passed`。

## 门禁恢复

重新路由受阻结果前，先进行分类：

| 阻断原因 | 路由目标 |
|---|---|
| 证据缺失或没有支持 | `researcher` |
| 架构或契约冲突 | `technical-architect` |
| 已知实现缺陷 | `backend-engineer` 或 `frontend-engineer` |
| 根因未知或技术故障反复发生 | `debugger` |
| 测试覆盖缺失或质量门不足 | `qa-engineer` |
| 业务价值、优先级或语义判断 | 按 `human-decision-handoff.md` 交给 `Intent Owner` |
| 技术范围、交付取舍或拓扑选择 | 按 `human-decision-handoff.md` 交给 `Delivery Owner` |
| 高风险动作、例外或残余风险 | 按 `human-decision-handoff.md` 交给 `Risk Approver` |
| 基线缺失、模糊或相互冲突 | `Intent Owner`，受影响分支保持 `blocked` |

返工后，重新执行所有受变更影响的下游检查。行为性代码变更通常先返回 `qa-engineer`，再进入 `reviewer`。架构变更则先返回受影响的工程师，随后再通过这些质量门。Agent 不修改已确认需求基线；改变业务语义的决定必须由 `Intent Owner` 发布新的基线 revision。

## 重试规则

1. 首次受阻时，把确切缺口、支持证据和完成标准返回给责任角色。
2. 保留已接受产物，只重新运行受影响分支及其下游质量门。
3. 同一质量门第二次失败时，重新分解任务。在再次尝试前检查简报是否模糊、角色分配是否错误、是否存在隐藏依赖或未知根因。
4. 不得把受阻输出当作已通过结果进行综合。只有人类决策负责人明确接受并将其列为风险时，才能保留未解决事项。

## 工作流完成条件

满足以下条件时，工作流可以进入综合阶段：

- 每个必需子任务都已 `passed`，或明确说明原因后 `skipped`；
- 每个已配置 QA 或评审门都已通过；
- 已接受风险和未解决决策都明确其人类负责人；
- 编排者能够将每项结论追溯到支持它的产物。
- 本地构建或测试证据没有被表述为生产部署或运行证据。
