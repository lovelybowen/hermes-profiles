---
name: qa-methodology
description: "质量保证方法论 - 测试策略设计、测试自动化模式、回归测试、CI 质量门、测试数据管理和质量指标。以帮助团队放心交付的实践模式为基础。"
version: 1.1.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [qa, testing, quality-assurance, test-automation, regression, CI, quality-gates, flaky-tests, quality-metrics]
    related_skills: [review-methodology, systematic-debugging, backend-engineering, frontend-engineering]
---

# QA 方法论

质量保证旨在让放心交付成为常态。本方法论涵盖测试策略、自动化、回归管理，以及随项目复杂度扩展的质量指标。

## QA 工程师的职责边界

| 负责 | 不负责 |
|---------|--------------|
| 测试策略：测试什么、在哪个层级测试、优先级如何 | 代码评审，由 `reviewer` 负责 |
| 测试自动化：框架选型、测试工具配置、CI 集成 | 缺陷根因分析，由 `debugger` 负责 |
| 回归测试：既能捕获回归又不过度脆弱的测试套件 | 功能实现，由相应开发者负责 |
| 质量门：CI 集成、通过/失败标准、阻断与非阻断规则 | 跨专家工作流排序，由 `orchestrator` 负责 |
| 测试数据管理：夹具、工厂、合成数据 | 生产监控，需要明确的运维负责人 |
| 质量指标：覆盖分析、缺陷密度、MTD | 独立完成裁定，由 `reviewer` 负责 |

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/test-strategy.md` | 为新项目或功能设计测试策略：测试层级、风险分析、优先级、自动化目标 |
| `references/test-automation-gates-metrics.md` | 测试自动化框架选型、CI 集成（并行执行、分片、不稳定测试管理）、质量门设计（通过/失败标准、阻断与建议、演进）和质量指标（覆盖率、缺陷密度、MTTD/MTTR） |
| `references/regression-testing.md` | 构建和维护回归套件：选择标准、优先级、套件演进、误报管理 |

## 核心原则

**未经测试，就视为有缺陷** - 未测试的代码不是可工作的代码，只是尚未发现其失败方式的代码。

**质量是过程的属性，而不是产物的属性** - 在最后阶段测试并不能创造质量。质量需要通过贯穿开发周期的测试策略、自动化和门禁机制设计进去。

**测试行为，而不是实现** - 与实现细节耦合的测试会在重构时失效，与行为耦合的测试则能够经受重构。优先测试系统做什么，而不是怎么做。

**快速反馈更有价值** - 运行 30 秒的测试比运行 30 分钟的测试更常被执行。应根据反馈频率投入相应的测试速度优化。

**不稳定测试比没有测试更糟** - 非确定性失败会让团队养成忽略失败的习惯。一旦发现不稳定测试，就应修复或移除。
