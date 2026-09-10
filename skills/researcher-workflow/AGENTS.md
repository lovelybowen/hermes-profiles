# researcher-workflow - Agent 加载指引

## 技能

| 阶段 | 技能名称 | 文件 |
|-------|-----------|------|
| 1 | `researcher-workflow/receive-mission` | `skills/receive-mission.md` |
| 2 | `researcher-workflow/research-gather` | `skills/research-gather.md` |
| 3 | `researcher-workflow/evaluate-gaps` | `skills/evaluate-gaps.md` |
| 4 | `researcher-workflow/build-pyramid` | `skills/build-pyramid.md` |
| 5 | `researcher-workflow/deliver-findings` | `skills/deliver-findings.md` |

## 加载方式

先加载总技能以启用触发检测：
```
skill_view(name='researcher-workflow')
```

然后按需加载各阶段技能：
```
skill_view(name='researcher-workflow/<skill-name>')
```

## 禁止事项

- 不要使用 `web_search` 或 `web_extract` 工具，统一使用 groktocrawl。
- 不要跳过阶段 1（`receive-mission`），需要先将 orchestrator 的简报转化为研究范围。
- 不要清理 `/tmp/` 中的产物，它们会自然过期。
