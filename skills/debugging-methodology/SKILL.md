---
name: debugging-methodology
description: "系统化调试方法论 - 根因分析、错误复现、隔离技术和验证协议。"
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [debugging, root-cause, reproduction, error-investigation]
---

# 调试方法论

用于调查和解决软件缺陷的系统化过程。

## 调试生命周期

```
复现 → 隔离 → 根因 → 修复 → 验证
```

## 与 `systematic-debugging` 的关系

本技能是**工程过程索引**（生命周期与参考资料入口）；`systematic-debugging` 是**根因协议的权威细则**（四阶段：根因调查 → 模式分析 → 假设与测试 → 实施）。

| 本技能生命周期 | `systematic-debugging` |
|---|---|
| 复现 | 阶段 1：稳定复现、读错误信息、检查近期变更 |
| 隔离 | 阶段 1：多组件证据收集、特征刻画、数据流跟踪 |
| 根因 | 阶段 1 完成检查清单 → 阶段 2 模式分析 → 阶段 3 假设与测试 |
| 修复 | 阶段 4：先建失败用例，再实施单一修复 |
| 验证 | 阶段 4.3：特定回归测试 + 全量测试确认无回归 |

**优先级：** 进入根因阶段后以 `systematic-debugging` 为准；本技能负责提供复现清单、隔离技巧、根因分析框架和性能调试参考资料。两者不一致时以 `systematic-debugging` 为准。

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/reproduction-checklist.md` | 需要复现间歇性或特定环境中的故障 |
| `references/root-cause-analysis.md` | 已隔离症状，需要继续追踪根因 |
| `references/isolation-techniques.md` | 需要在多个组件之间缩小故障范围 |
| `references/performance-debugging.md` | 调查延迟、内存或吞吐量问题 |
