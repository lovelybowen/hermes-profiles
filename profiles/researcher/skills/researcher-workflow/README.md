# researcher-workflow 技能

定义 researcher 角色的五阶段工作流：接收 orchestrator 的任务简报，通过深度研究管线生成渐进披露的产物金字塔。

## 参考文件

`SKILL.md` 是索引，阶段方法论位于 `references/`。

| 参考文件 | 触发条件 | 执行时机 |
|-------|---------|---------------|
| `references/receive-mission.md` | Orchestrator 分配研究简报 | 入口，将简报重述为结构化范围 |
| `references/research-gather.md` | 范围定义完成后 | 使用原生研究工具执行多轮收集 |
| `references/evaluate-gaps.md` | 首轮收集完成后 | 应用三问模型并决定是否递归 |
| `references/build-pyramid.md` | 研究达到饱和后 | 在任务工作区中组装分层产物文件 |
| `references/deliver-findings.md` | 金字塔构建完成后 | 返回结构化交接消息 |
| `references/decision-map.md` | 需要整体视图时 | 五阶段管线与递归分支 |
| `references/tool-governance.md` | 选择取证工具时 | 原生工具与可选增强的选择表与回退链 |

## 加载方式

```python
skill_view('researcher-workflow')
skill_view('researcher-workflow', file_path='references/receive-mission.md')
```

## 核心原则

- **原生优先。** 默认使用 `web_search` / `web_extract` / browser；`groktocrawl` 仅在确认可用且必要时启用（见 `references/tool-governance.md`）。
- **渐进披露。** 金字塔每一层都附带说明并链接到下一层。
- **缺口三问模型。** 是否在范围内？是否改变结论？增加的是深度还是材料数量？
- **产物必须可达。** 写入任务工作区或 `${RESEARCH_ARTIFACTS_DIR:-./research}/<mission-slug>/`；Kanban 任务用 `kanban_complete(artifacts=[...])` 声明。
