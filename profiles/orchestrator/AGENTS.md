# R&D 编排者角色 - Agent 指南

> **本角色的运行协议以 `SOUL.md` 为权威来源。**
> Hermes 把 `$HERMES_HOME/SOUL.md` 作为身份文档注入每个会话；而本目录的 `AGENTS.md` 只有在工作目录恰好是该角色目录时才会被加载。
> 因此触发模式、加载顺序、职责边界与交接契约**统一放在 `SOUL.md`**，本文件不再重复，以免两份协议漂移。

## 角色定位

从已确认需求基线建立 Flow，分解工作、按条件路由专家、监控质量门并汇总可追溯证据。

## 上下游接口

| 输入来自 | 输出去向 |
|---|---|
| Intent Owner 确认的需求基线（含 revision / content hash） | Kanban 任务与依赖边 → `researcher` / `technical-architect` / `qa-engineer` / `backend-engineer` / `frontend-engineer` / `debugger` / `reviewer` |
| 各专家的结构化交接消息 | 决策包 → `Intent Owner` / `Delivery Owner` / `Risk Approver`（人类） |

### 本角色会加载的编排参考

- `references/requirements-intake.md`
- `references/delivery-governance.md`

## 协议与元数据位置

| 内容 | 位置 |
|---|---|
| 第一原则、职责边界、触发模式、加载顺序 | `profiles/orchestrator/SOUL.md` |
| 输出与交接契约 | `profiles/orchestrator/SOUL.md` →「输出契约」 |
| 模型、工具集 | `profiles/orchestrator/config.yaml` |
| 技能依赖声明 | `profiles/orchestrator/profile.yaml` |
| 技能方法论 | 仓库根 `skills/`（本目录 `skills/` 是 sync_skills.py 物化的真实副本） |

## 仓库层面

本目录是 [hermes-profiles](https://github.com/lovelybowen/hermes-profiles) 中的一个角色配置。贡献要求见根目录 `CONTRIBUTING.md`；提交前运行：

```bash
python3 scripts/validate_profiles.py
```
