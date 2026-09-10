# researcher-workflow - Agent 加载指引

## 阶段参考文件

| 阶段 | 参考文件 |
|-------|-----------|
| 1 | `references/receive-mission.md` |
| 2 | `references/research-gather.md` |
| 3 | `references/evaluate-gaps.md` |
| 4 | `references/build-pyramid.md` |
| 5 | `references/deliver-findings.md` |

## 加载方式

先加载索引技能：
```python
skill_view('researcher-workflow')
```

然后按需加载各阶段参考文件：
```python
skill_view('researcher-workflow', file_path='references/<phase-file>.md')
```

> 注意：Hermes 只索引名为 `SKILL.md` 的文件，且 `skill_view` 不支持 `父/子` 路径。
> 因此阶段文档必须放在 `references/` 并通过 `file_path` 加载，不能作为「子技能」按名字加载。

## 禁止事项

- 默认使用 Hermes 原生 `web_search` / `web_extract` / browser；`groktocrawl` 仅在 `command -v groktocrawl` 确认可用且必要时启用（见 `references/tool-governance.md`）。
- 不要跳过阶段 1（`receive-mission`），需要先将 orchestrator 的简报转化为研究范围。
- 不要把产物只留在会被清理的临时目录：Kanban 任务通过 `kanban_complete(artifacts=[...])` 显式声明，独立运行写入 `${RESEARCH_ARTIFACTS_DIR:-./research}/<mission-slug>/`。
