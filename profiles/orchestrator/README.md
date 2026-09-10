# R&D 编排者 - Hermes 角色

从已确认需求基线建立研发 Flow，将工作分解并按条件路由给架构、工程、QA、评审、研究或调试角色，最后汇总可追溯证据供人类责任人批准。

## 入口角色

本角色是整个 AI Native R&D 角色体系的**唯一入口**。用户只与 `orchestrator` 对话；其余 7 个角色由 `orchestrator` 按条件通过 Kanban 任务拉入，不直接接单。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/orchestrator ~/.hermes/profiles/
hermes --profile orchestrator
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`，并额外启用 `kanban`（编排者需要看板路由工具））。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/orchestrator/.env.example profiles/orchestrator/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/orchestrator/SOUL.md` —— 这是权威来源。

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 输出格式 |
| `orchestration-methodology` | 任务分解、专家路由、监控恢复与综合模式 |

## 输入边界

需求基线必须具有稳定标识、revision 或 content hash，并包含角色、场景、流程、业务规则和验收标准。编排者不修改基线、不作出架构决策，也不代替人类接受风险。

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
