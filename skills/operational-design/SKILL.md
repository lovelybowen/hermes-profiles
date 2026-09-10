---
name: operational-design
description: >-
  面向流程设计、组织规模化、运营指标、合规与审计、供应商管理和团队拓扑的方法论。
  涵盖价值流映射、BPMN、瓶颈分析、从 10 人到 100 人再到 1000 人的规模化、KPI 设计、
  平衡计分卡、SOC 2、ISO 27001、GDPR 就绪、RFP 流程、SLA 设计、供应商评分卡、
  团队拓扑、康威定律和邓巴数。
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags:
      [
        operations,
        process-design,
        scaling,
        compliance,
        vendor-management,
        team-topologies,
      ]
---

# 运营设计

用于设计和扩展运营、管理合规、选择并管理供应商以及衡量运营健康的方法论。该技能作为独立可选能力保留，只有任务明确涉及运营流程时才加载。

## 领域模型

| 领域 | 覆盖内容 | 产物 |
|--------|--------|----------|
| **流程设计** | 价值流映射、BPMN、瓶颈分析、工作流优化 | 流程图、VSM 当前/未来状态 |
| **规模化框架** | 10 人到 100 人再到 1000 人的转变、组织设计、授权模式 | 规模化计划、组织设计 |
| **运营指标** | KPI 设计、平衡计分卡、领先与滞后指标 | 运营仪表板 |
| **合规与审计** | SOC 2、ISO 27001、GDPR 就绪、审计准备 | 合规路线图、控制矩阵 |
| **供应商管理** | RFP 流程、SLA 设计、供应商评分卡、关系分级 | 供应商管理框架 |
| **组织模式** | 团队拓扑、康威定律、邓巴数、管理跨度 | 团队设计、沟通模型 |

## 加载时机

任务涉及以下内容时加载此技能：

- 映射和优化业务流程（价值流、BPMN）
- 规划组织跨增长阶段的规模化
- 设计运营 KPI 和平衡计分卡
- 准备 SOC 2、ISO 27001 或 GDPR 合规
- 执行 RFP 或供应商选择流程
- 设计 SLA 和供应商评分卡
- 使用团队拓扑重组团队
- 分析瓶颈和吞吐量约束
- 设计授权和管理跨度模型

## 加载顺序

```
skill_view('operational-design')                    # 本技能：方法论索引
skill_view('artifact-pyramids')                      # 输出契约
skill_view('operational-design', file_path='references/process-design.md')
skill_view('operational-design', file_path='references/scaling-frameworks.md')
skill_view('operational-design', file_path='references/operational-metrics.md')
skill_view('operational-design', file_path='references/compliance.md')
skill_view('operational-design', file_path='references/vendor-management.md')
```

## 参考文件

| 参考主题 | 加载时机 | 文件 |
|-----------|-----------|------|
| 流程设计 | 需要映射、分析或优化业务流程 | `references/process-design.md` |
| 规模化框架 | 规划组织增长或重组 | `references/scaling-frameworks.md` |
| 运营指标 | 设计 KPI、仪表板或平衡计分卡 | `references/operational-metrics.md` |
| 合规与审计 | 准备 SOC 2、ISO 27001 或 GDPR 合规 | `references/compliance.md` |
| 供应商管理 | 执行 RFP、设计 SLA 或评估供应商 | `references/vendor-management.md` |

## 设计原则

1. **流程先于自动化。** 自动化糟糕流程只会更快地产生糟糕结果。选择工具前先映射并优化工作流。
2. **规模是不连续函数。** 适用于 10 人的组织会在 50 人、200 人和 1000 人时失效，每个阶段都需要不同运行模型。面向下一阶段设计，而不是当前阶段。
3. **以领先指标为先。** 滞后指标说明已经发生什么，领先指标预示将要发生什么。优秀的运营仪表板应平衡两者。
4. **合规是系统，而不是项目。** SOC 2 认证不是一次性工作。合规需要嵌入式控制、持续监测和定期测试。
5. **供应商是合作伙伴，而不是乘客。** 最便宜的供应商往往总成本最高。对供应商关系的投入应与业务关键程度相称。
6. **结构追随战略。** 团队拓扑应由工作所需沟通模式（康威定律）驱动，而不是由便于管理的汇报关系驱动。

## 相关技能

- `artifact-pyramids` - 输出契约规范
