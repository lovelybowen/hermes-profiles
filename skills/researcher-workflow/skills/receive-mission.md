---
name: receive-mission
description: >-
  R&D 研究任务接收和范围转化。当 orchestrator 分配外部事实、技术选型或证据缺口简报时使用。
  校验需求基线引用，并将简报重述为明确的研究问题、范围边界和深度目标。
  这是 researcher-workflow 技能包的必经入口。
compatibility: Hermes Agent
metadata:
  tags: [research, scope, mission, interpolation]
  spec-version: "1.0"
---

# 接收任务

## 使用时机

当你作为 researcher 子 Agent 收到 R&D 研究简报时加载此技能。必须始终从这里开始，先校验任务引用的需求基线，再将简报转化为结构化范围。

## 执行步骤

### 1. 阅读任务简报

Orchestrator 会传递一份研究简报。研究问题可能层级过高，但需求基线引用和下游用途必须完整；缺失时停止并退回编排者。对可接受的简报提取：

- **核心问题：** 对方最需要知道的一件事是什么？
- **基线引用：** 稳定标识、URI、revision 或 content hash，以及本次研究服务的验收或决策项。
- **受众：** 哪个保留角色或人类利益相关方会使用各个层级？
- **范围边界：** 哪些内容明确在范围内或范围外？
- **深度信号：** 简报要求的是表层扫描还是深入分析？
- **已知上下文：** 研究员对此主题已经了解什么？检查 `SOUL.md`、已加载的方法论技能以及调度时传入的上下文。

### 2. 转化为研究范围

将简报重述为结构化范围文档，写入 `/tmp/researcher-workflow/<mission-slug>/SCOPE.md`：

```markdown
# 研究范围：<标题>

## 收到的任务
<Orchestrator 的原始简报>

## 需求基线引用
- **Artifact ID：** <稳定标识>
- **URI：** <原始位置>
- **Revision / Content Hash：** <至少一个>
- **服务的验收或决策项：** <可追溯标识>

## 重述后的研究问题
- Q1：<主要问题>
- Q2：<次要问题>
- Q3：<第三层问题>

## 范围边界
- **范围内：** <涵盖内容>
- **范围外：** <明确排除的内容>

## 目标受众与深度
- **第 1 层（摘要）：** <阅读者，例如 orchestrator 或人类责任人>
- **第 2 层（分析）：** <阅读者，例如 technical-architect>
- **第 3 层（详细材料）：** <阅读者，例如 reviewer>

## 已知未知项
- <尚不了解且会实质改变整体判断的事项>

## 基线冲突
- <发现与角色、场景、流程、业务规则或验收标准冲突时记录；无则写“无”>

## 研究方法
- <搜索策略：领域、来源类型和搜索查询>
- <预期深度：轻量扫描或深入系统评审>
```

### 3. 建立产物目录

```bash
mkdir -p /tmp/researcher-workflow/<mission-slug>/{layer-1-summary,layer-2-analysis,layer-3-detailed}
```

### 4. 加载研究方法论技能

加载 `research-methodology` 技能，以使用研究生命周期、来源评估和综合参考资料：

```
skill_view(name='research-methodology')
```

下一阶段通常需要共享参考资料 `source-evaluation.md`、`structured-analytic-techniques.md` 和 `synthesis-patterns.md`。

## 转换信号

满足以下条件时进入阶段 2（收集）：
- `SCOPE.md` 文档已经写入。
- 产物目录已经建立。
- `research-methodology` 技能已经加载。
- 需求基线引用完整且没有未交回 `Intent Owner` 的基线冲突。

## 工具使用

- 使用终端执行 `mkdir` 和文件系统操作。
- 本阶段不使用 Web 研究工具，相关工作在下一阶段进行。
