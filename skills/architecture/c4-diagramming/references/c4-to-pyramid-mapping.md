# C4 到金字塔的映射

## 映射表

| C4 层级 | 金字塔层级 | Mermaid 路径 | Structurizr DSL 路径 | 使用方 |
|----------|--------------|--------------|----------------------|----------|
| 第 1 层：系统上下文 | **L1**（01-summary/） | 01-summary/system-context.md | `docs/arch/model/system.dsl`（systemContext 视图） | 需要全貌的利益相关方 |
| 第 2 层：容器 | **L2**（02-analysis/） | 02-analysis/structural-views/container.md | `docs/arch/model/system.dsl`（container 视图） | 开发者、集成人员 |
| 第 3 层：组件 | **L2**（02-analysis/） | 02-analysis/structural-views/components.md | `docs/arch/model/system.dsl`（component 视图） | 组件开发者 |
| 第 4 层：代码 | **L3**（03-dossiers/） | 03-dossiers/code-level-detail.md | `docs/arch/model/system.dsl`（code 视图） | 实施人员、代码评审员 |

**关于 Structurizr DSL 路径的说明：**四个 C4 层级均定义在同一个 `system.dsl` 文件中。各层级的 `system.dsl` 路径相同，因为 Structurizr 从一个模型生成所有图表；区别在于渲染的**视图**不同：L1 为 `systemContext`、L2 为 `container`、L3 为 `component`、L4 为 `code`。完整 Structurizr 参考见 `references/architecture-as-code-ecosystem.md`。

## C4 为什么易于映射

C4 是唯一内置深度层级的架构方法论。其四个缩放层级天然对应三个金字塔层级，其中第 2 至 3 层均作为独立 L2 分析文件呈现。没有其他方法论能如此直接映射。

## 核心原则

C4 从根本上说是一种视觉表示法，它向已经理解领域的人传达结构。它不传达决策依据（这是 ADR 的职责）或约束（这是 arc42 的职责）。三种方法论相互补充，而非相互竞争。
