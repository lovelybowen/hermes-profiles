# researcher-workflow 技能包

由工作流架构工具于 2026-05-31 生成。

此技能包定义 researcher 子 Agent 的工作流：接收 orchestrator 的任务简报，通过非交互式深度研究管线生成渐进披露的产物金字塔。

## 技能

| 技能 | 触发条件 | 执行时机 |
|-------|---------|---------------|
| receive-mission | Orchestrator 分配研究简报 | 入口，将简报重述为结构化范围 |
| research-gather | 范围定义完成后 | 只使用 groktocrawl 执行多轮研究 |
| evaluate-gaps | 首轮收集完成后 | 应用三问模型并决定是否递归 |
| build-pyramid | 研究达到饱和后 | 在 `/tmp/` 中组装分层产物文件 |
| deliver-findings | 金字塔构建完成后 | 将各层路径及说明报告给 orchestrator |

## 加载方式

调度 researcher 角色时会自动加载此技能包。加载特定子技能时使用：`skill_view(name='researcher-workflow/<skill-name>')`

## 核心原则

- **禁止使用 `web_search` 或 `web_extract`。** 所有 Web 研究都使用 groktocrawl。
- **渐进披露。** 金字塔每一层都附带说明并链接到下一层。
- **缺口三问模型。** 是否在范围内？是否改变结论？增加的是深度还是材料数量？
- **由操作系统清理。** `/tmp/` 中的产物会自然过期。
