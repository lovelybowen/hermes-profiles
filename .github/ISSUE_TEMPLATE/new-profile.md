---
name: 新角色配置
about: 请求或提议新的 Hermes Agent 角色配置
title: "创建 [profile-name] 角色配置"
labels: enhancement
---

## 概述

这个角色配置承担什么职责？解决什么问题？

## 为什么必须是独立 Profile

说明它具备**独立的上下文、方法论或质量边界**中的哪一项。
如果它只是某个现有角色的提示词变体，或只是人类责任（业务价值、交付取舍、风险接受），
则不应包装为 Hermes Profile。

## 方法论

哪些方法论、框架或运行原则定义了这个角色？
（例如：`technical-architect` 使用 C4 + ADR + arc42，`qa-engineer` 使用测试策略 + 回归测试。）

## 必需技能

列出该角色需要从共享池（`skills/`）加载的技能，以及需要新增的技能。

## 与人类责任人的边界

这个角色**不能**做什么？（例如：不修改已确认基线、不自行接受残余风险、不代替评审员裁定。）

## 相关角色

该角色会与哪些现有角色协作？请检查 `SOUL.md` 中的交叉引用。

## 验证

提交 PR 前逐项确认：

- [ ] `SOUL.md` 说明第一原则、职责边界、触发模式、加载顺序与输出契约
- [ ] `config.yaml` 含模型与工具集，且**不含任何密钥**
- [ ] `.env.example` 列出所需凭据；`.env` 已被 `.gitignore` 排除
- [ ] `.no-bundled-skills` 标记已提交（避免首次运行被播种整套自带技能）
- [ ] 所有技能为**相对符号链接**，Git 模式为 `120000`
- [ ] `python3 scripts/validate_profiles.py` 通过
- [ ] `hermes -p <name> skills list` 的启用技能数与 `profile.yaml` 一致
- [ ] 交接消息包含 `status` / `summary` / `artifact` / `evidence` / `risks` / `decisions_required`
- [ ] 持久成果生成产物金字塔；状态/阻断/审批请求不生成
- [ ] 不把外部私有工具设为前置依赖（原生 Hermes 工具是默认路径）
