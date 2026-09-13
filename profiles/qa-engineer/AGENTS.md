# QA 工程师角色 - Agent 指南

> **本角色的运行协议以 `SOUL.md` 为权威来源。**
> Hermes 把 `$HERMES_HOME/SOUL.md` 作为身份文档注入每个会话；而本目录的 `AGENTS.md` 只有在工作目录恰好是该角色目录时才会被加载。
> 因此触发模式、加载顺序、职责边界与交接契约**统一放在 `SOUL.md`**，本文件不再重复，以免两份协议漂移。

## 角色定位

设计测试策略、自动化与质量门，执行验证并产出可复现的测试证据。

## 上下游接口

| 输入来自 | 输出去向 |
|---|---|
| 基线 + 已批准契约（实现前） | 测试证据 → `reviewer` |
| 实现工作区与固定 commit SHA（实现后） | 已知实现缺陷 → 原实现者；未知根因或反复失败 → `debugger` |

## 协议与元数据位置

| 内容 | 位置 |
|---|---|
| 第一原则、职责边界、触发模式、加载顺序 | `profiles/qa-engineer/SOUL.md` |
| 输出与交接契约 | `profiles/qa-engineer/SOUL.md` →「输出契约」 |
| 模型、工具集 | `profiles/qa-engineer/config.yaml` |
| 技能依赖声明 | `profiles/qa-engineer/profile.yaml` |
| 技能方法论 | 仓库根 `skills/`（本目录 `skills/` 是 sync_skills.py 物化的真实副本） |

## 仓库层面

本目录是 [hermes-profiles](https://github.com/lovelybowen/hermes-profiles) 中的一个角色配置。贡献要求见根目录 `CONTRIBUTING.md`；提交前运行：

```bash
python3 scripts/validate_profiles.py
```
