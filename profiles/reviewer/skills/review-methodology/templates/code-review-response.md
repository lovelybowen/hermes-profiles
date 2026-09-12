# 代码评审回复

## 概览
**PR:** #N
**标题：**[PR 标题]
**变更文件：**N
**`evidence_level`：**`L0` / `L1` / `L1+L2` / `Full`
**核验深度：**[按 `evidence_level` 选定：`L0` 快速扫描 / `L1` 单模块直接验证 / `L1+L2` 跨模块核对 + 关键路径抽样 / `Full` 全量复算；定义见 `references/evidence-level-verification.md`]

## 发现

### 🔴 严重（合并前必须修复）

**1. [标题]**
文件：`path/to/file.py:L42`
[问题是什么，以及为何阻塞合并]
```python
# 当前代码
problematic_line()
```
**修复：**[具体建议]

### 🟡 应修复

**1. [Title]**
File: `path/to/file.py:L100`
[可以改进的内容]
**建议：**[具体建议]

### 💡 建议

**1. [Title]**
File: `path/to/file.py:L200`
[细节级观察]

### ❓ 问题

**1. [Title]**
File: `path/to/file.py:L50`
[我不理解此代码路径的内容]

## 摘要

**总体结论：**批准 / 请求修改 / 评论
**主要优点：**[PR 做得好的地方]
**主要关注点：**[合并前需要关注的内容]
