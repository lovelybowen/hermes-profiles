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

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/reproduction-checklist.md` | 需要复现间歇性或特定环境中的故障 |
| `references/root-cause-analysis.md` | 已隔离症状，需要继续追踪根因 |
| `references/isolation-techniques.md` | 需要在多个组件之间缩小故障范围 |
| `references/performance-debugging.md` | 调查延迟、内存或吞吐量问题 |
