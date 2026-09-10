# R&D 编排者 - Hermes 角色

从已确认需求基线建立研发 Flow，将工作分解并按条件路由给架构、工程、QA、评审、研究或调试角色，最后汇总可追溯证据供人类责任人批准。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/orchestrator ~/.hermes/profiles/
hermes --profile orchestrator
```

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 输出格式 |
| `orchestration-methodology` | 任务分解、专家路由、监控恢复与综合模式 |

## 输入边界

需求基线必须具有稳定标识、revision 或 content hash，并包含角色、场景、流程、业务规则和验收标准。编排者不修改基线、不作出架构决策，也不代替人类接受风险。

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
