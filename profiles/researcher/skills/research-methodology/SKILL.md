---
name: research-methodology
description: "专业研究方法论 - 新闻调查、行业分析、技术验证和学术式系统研究。参考资料定义来源评估、竞争假设分析（ACH）、综合、访谈处理、信号检测和复现标准。"
version: 1.1.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [research, journalism, industry-analysis, source-evaluation, verification]
---

# 研究方法论

面向子 Agent 的专业研究过程，根据研究类型分为三条路径：

- **新闻调查** - 调查性内容、一手来源研究、依赖大量来源的叙事工作
- **行业分析** - 市场研究与战略、信号检测
- **学术/综合研究** - 在深度最重要时开展系统化深度研究

三条路径共享同一生命周期（界定范围 → 收集 → 评估 → 分析 → 综合 → 报告），但证据标准、速度和输出格式不同。

## 研究生命周期

```
界定范围 → 收集 → 评估 → 分析 → 综合 → 报告
```

## 参考文件

### 研究路径

| 路径 | 参考文件 | 加载时机 |
|-------|-----------|-------------|
| **新闻调查** | `references/journalistic-research.md` | 调查性内容研究：一手来源、访谈、文档、系列管理、发布前核验 |
| **行业分析** | `references/industry-analysis.md` | 行业分析研究：信号检测、企业证据、竞争情报、案例研究标准 |
| **学术/综合研究** | `references/research-lifecycle.md` | 系统化深度研究：问题范围、检索策略、纳入/排除标准 |

### 共享方法论

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/source-evaluation.md` | 判断来源是否可信：CRAAP 测试、三角验证、可靠性分级 |
| `references/structured-analytic-techniques.md` | 评估相互竞争的解释：ACH、驱动力、事前分析、指标 |
| `references/synthesis-patterns.md` | 把多个来源的发现组合为综合结论 |
| `references/technical-verification.md` | 通过复现检验技术主张：基准测试、API 行为、配置 |

### 资产

| 资产 | 产出 |
|-------|-----------------|
| `assets/research-brief.md` | 包含发现、置信度评估、证据表和开放问题的结构化简报 |
| `assets/research-log.md` | 可追溯的检索、来源和决策记录 |

## 发布前质量门

对于包含事实性主张的任何内容，返回报告前必须加载相应研究路径的验证协议：

- **新闻调查：** `references/journalistic-research.md` 中的七步发布前协议
- **行业分析：** `references/industry-analysis.md` 中的七步研究协议
- **技术验证：** `references/technical-verification.md` 中的五步复现协议
