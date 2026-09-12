---
name: project-context-binding
description: "项目接入约定：新项目如何通过仓库根 AGENTS.md + 独立 Kanban board 接入角色体系，不改动任何 Profile。"
version: 0.1.0
author: lovelybowen
license: MIT
metadata:
  hermes:
    tags: [project-onboarding, agents-md, kanban-boards, multi-project]
---

# 项目接入约定（AGENTS.md 绑定 + 每项目一 board）

角色 Profile 保持**项目无关**：SOUL、技能、门禁语法是通用的 R&D 语言。
项目差异统一落在**项目仓库根目录的 `AGENTS.md`**——Hermes 按工作目录自动发现，
所有在该项目 worktree 内工作的角色都会读到同一份约定。

## 核心不变量

1. **角色不含项目知识。** 项目事实（命令、责任人、拓扑）只存在于项目侧 AGENTS.md；Profile 改动不需要为接入新项目发生。
2. **一项目一 board。** `hermes kanban boards create <slug>` + `set-default-workdir`；跨项目任务不共板。
3. **intake 校验 AGENTS.md。** 必填区缺失即阻塞，交回 Intent Owner，不猜命令、不代填责任人。

## 接入流程（新项目，约 10 分钟）

1. 项目仓库根放 `AGENTS.md`（用 `docs/project-agents-template.md` 模板）：
   构建命令表、责任人映射、仓库拓扑为必填；board、部署边界为可选。
2. `hermes kanban boards create <project-slug>`
3. `hermes kanban boards set-default-workdir <project-slug> <repo 绝对路径>`
4. 跑一次 T2 级文档任务验证闭环（命令表真实可执行、责任人可触达）。

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `docs/project-agents-template.md`（本仓库） | 为新项目起草 AGENTS.md 时 |

## 硬约束

- AGENTS.md 里的命令必须**真实可执行**（orchestrator/QA 会按表执行）；
  填不准就留空并阻塞 intake，不要填猜测值。
- 项目侧 AGENTS.md 与角色 SOUL 冲突时：**项目约定优先于通用纪律的事务性条款**（如分支命名），
  **角色纪律优先于项目便利**（如门禁、证据、审批边界）。
- board 隔离是硬边界：任务、workspace、日志不跨板引用。
