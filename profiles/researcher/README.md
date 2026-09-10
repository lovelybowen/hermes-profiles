# R&D 研究员 - Hermes 角色

针对研发工作中的外部事实、技术选型和证据缺口开展调查与三角验证，并产出可追溯的结构化结论。研究结果支持需求基线和技术决策，但不修改已确认的业务语义。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/researcher ~/.hermes/profiles/
hermes --profile researcher
```

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 渐进披露输出格式 |
| `research-methodology` | 证据收集、来源评估、三角验证与核验 |
| `researcher-workflow` | 端到端研究任务工作流与产物生成 |

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
