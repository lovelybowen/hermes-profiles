# 产品经理角色 - Agent 指南

> **本角色的运行协议以 `SOUL.md` 为权威来源。**
> Hermes 把 `$HERMES_HOME/SOUL.md` 作为身份文档注入每个会话；而本目录的 `AGENTS.md` 只有在工作目录恰好是该角色目录时才会被加载。
> 因此第一原则、沟通风格与输出契约**统一放在 `SOUL.md`**，本文件不再重复，以免两份协议漂移。

## 角色定位

撰写 spec、管理路线图、对齐团队，把客户需求翻译为可排序的交付物；产出以产物金字塔交付。

## 上下游接口

| 输入来自 | 输出去向 |
|---|---|
| 用户/干系人的产品请求（问题、约束、期望成果） | 产品金字塔（spec / 优先级 / 决策记录）→ `orchestrator`、`technical-architect` |
| 客户访谈与发现式研究材料 | 干系人简报与状态更新 → 人类干系人 |

## 协议与元数据位置

| 内容 | 位置 |
|---|---|
| 第一原则、沟通风格、输出契约 | `profiles/product-manager/SOUL.md` |
| 模型、工具集 | `profiles/product-manager/config.yaml` |
| 技能依赖声明 | `profiles/product-manager/profile.yaml` |
| 技能方法论 | 仓库根 `skills/`（本目录 `skills/` 是 sync_skills.py 物化的真实副本） |

## 仓库层面

本目录是 [hermes-profiles](https://github.com/lovelybowen/hermes-profiles) 中的一个角色配置。贡献要求见根目录 `CONTRIBUTING.md`；提交前运行：

```bash
python3 scripts/validate_profiles.py
```
