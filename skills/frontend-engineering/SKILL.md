---
name: frontend-engineering
description: "前端工程方法论 - 组件架构、状态管理、API 集成、响应式布局、客户端性能和前端测试模式。与框架无关，聚焦 Web 前端实现。"
version: 1.1.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [frontend, web, ui, components, state-management, performance, javascript, typescript, responsive, testing]
    related_skills: [software-architecture-analysis, backend-engineering, qa-methodology, review-methodology]
---

# 前端工程方法论

前端工程负责构建应用面向用户的层级，包括组件、状态管理、API 集成、响应式布局和客户端性能。本方法论连接 UX 设计（用户旅程、线框图、无障碍标准）与评审员（代码质量门）。

## 前端工程师的职责边界

| 负责 | 不负责 |
|---------|--------------|
| 组件实现：UI 组件组合、props/state 接口、渲染模式、生命周期 | 产品意图、用户旅程和已批准的视觉方向，必须作为输入提供 |
| 状态管理：客户端状态架构、数据获取模式、缓存、乐观更新 | API 契约设计，由 `technical-architect` 负责 |
| API 集成：前后端数据流、认证流程（OAuth、JWT）、实时更新 | 测试策略与自动化，由 `qa-engineer` 负责 |
| 响应式设计实现：布局系统、断点、跨设备测试 | 视觉识别与品牌指南，必须作为输入提供 |
| 客户端性能：产物包优化、延迟加载、Core Web Vitals、渲染优化 | 编辑内容与文案，必须作为输入提供 |
| 前端测试：组件测试、集成测试、视觉回归、无障碍测试 | 代码评审与质量门，由 `reviewer` 负责 |
| 构建工具：打包器配置、TypeScript 配置、代码检查、格式化、开发环境 | CI/CD 平台所有权，需要明确的运维负责人 |

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/component-architecture.md` | 设计组件树：组合模式、props/state 接口、生命周期、无障碍基础 |
| `references/state-management.md` | 选择并实现状态管理：客户端与服务端状态、数据获取、缓存、乐观更新 |
| `references/api-integration.md` | 连接前后端：API 客户端设计、认证令牌流、UI 错误处理、实时订阅 |
| `references/responsive-layout-testing.md` | 实现响应式设计（Grid、Flexbox 与容器查询的选择、断点策略、跨设备测试方法）并测试前端代码（Testing Library 组件测试、Playwright/Cypress 集成测试、视觉回归、axe-core 和 Lighthouse CI 无障碍测试、测试数据管理） |
| `references/performance.md` | 优化客户端性能：Core Web Vitals、产物包分析、代码拆分、渲染优化 |

## 本环境实现任务的操作约定（Kanban + Codex）

- **用 `codex exec -s workspace-write --skip-git-repo-check -C <worktree>` 驱动实现**，不要用 `--full-auto`：该标志在 codex-cli 0.154.0 已被移除，会直接报 `unexpected argument` 且不产生任何改动。
- **worktree 内不跑 `npm install`**，改为 `ln -s <主仓>/node_modules node_modules`：Vite/vue-tsc 可正常构建，且 `node_modules` 已被 `.gitignore` 忽略，不会进入提交。
- **卡面写“复用现有 worktree”时先去验证它真的存在**（`git worktree list` + `ls .worktrees`）：worktree 可能随上一轮任务被清理；缺失时创建唯一一棵，并把该偏差写进交接证据的 `known_deviations`，否则下游找不到实现分支。
- **不采信 Codex 的文字结论**：至少复算 `git diff --name-only <baseline> HEAD`、真实执行 `npm run build`（记录 exit code 与 stdout 哈希）、并用构建产物（`vite preview` + 浏览器真实点击）核对交互；把 a11y 快照里的按钮可访问名当验收条目，不靠目测。
- **交接证据按 `evidence-levels-and-seb` 的字段名打包**（`schema_version`/`commit`/`baseline`/`changed_files[].blob_sha`/`commands[].exit_code`+`stdout_sha256`/`gate_artifacts[]`/`producer`/`produced_at`）：字段名不一致会让 reviewer 的 SEB 完整性核验直接失败。

## 核心原则

**组合的单位是组件，而不是页面** - 将组件设计和构建为可复用、可组合的单元。页面由组件组装而成，而不是一个整体式单体。设计良好的组件可以复用于创建者未曾设想的场景。

**让状态与需要它的组件就近放置** - 并非所有状态都应进入全局存储。本地状态留在本地，服务端状态通过获取和缓存管理，只有真正共享的应用状态才属于全局上下文。

**为每种状态设计，而不只考虑顺利路径** - 每个依赖数据的组件至少有加载、空、错误和成功四种状态。覆盖全部状态不是锦上添花，而是构建有韧性用户体验的基础。

**无障碍不是功能，而是要求** - 键盘导航、屏幕阅读器支持、颜色对比度和焦点管理不是增强项，而是实现契约的一部分。

**性能是用户体验问题** - 每一毫秒加载时间、每一次布局偏移和每一个卡顿交互都会消耗用户信任。性能预算、产物包分析和渲染优化是前端工程的一部分，不是事后补救。
