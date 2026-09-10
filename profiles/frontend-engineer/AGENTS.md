# 前端工程师角色 - Agent 指南

> **本角色的运行协议以 `SOUL.md` 为权威来源。**
> Hermes 把 `$HERMES_HOME/SOUL.md` 作为身份文档注入每个会话；而本目录的 `AGENTS.md` 只有在工作目录恰好是该角色目录时才会被加载。
> 因此触发模式、加载顺序、职责边界与交接契约**统一放在 `SOUL.md`**，本文件不再重复，以免两份协议漂移。

## 角色定位

实现 UI 组件、状态管理、API 集成、响应式布局与客户端性能优化。

## 上下游接口

| 输入来自 | 输出去向 |
|---|---|
| `technical-architect` 的契约与边界 | 实现工作区（worktree）+ commit SHA + 测试证据 → `qa-engineer` → `reviewer` |
| `qa-engineer` 的验证策略 | — |

## 协议与元数据位置

| 内容 | 位置 |
|---|---|
| 第一原则、职责边界、触发模式、加载顺序 | `profiles/frontend-engineer/SOUL.md` |
| 输出与交接契约 | `profiles/frontend-engineer/SOUL.md` →「输出契约」 |
| 模型、工具集 | `profiles/frontend-engineer/config.yaml` |
| 技能依赖声明 | `profiles/frontend-engineer/profile.yaml` |
| 技能方法论 | 仓库根 `skills/`（本目录 `skills/` 是相对符号链接） |

## 仓库层面

本目录是 [hermes-profiles](https://github.com/lovelybowen/hermes-profiles) 中的一个角色配置。贡献要求见根目录 `CONTRIBUTING.md`；提交前运行：

```bash
python3 scripts/validate_profiles.py
```
