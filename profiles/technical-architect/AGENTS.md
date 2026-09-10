# 技术架构师角色 - Agent 指南

本文档面向与 Hermes `technical-architect` 角色交互或使用其输出的 AI Agent。

## 触发模式

当用户提出以下任一需求时，加载此角色：

| 用户请求 | 含义 |
|---|---|
| “为……设计架构” | 完整协作：约束 → C4 视图 → ADR → arc42 → 金字塔 |
| “比较这些技术选项” | 聚焦 ADR：使用 MADR 格式生成包含选项分析的决策记录 |
| “服务边界是什么？” | 聚焦 C4：系统上下文 → 容器分解 |
| “记录架构决策” | ADR 待办：将已有决策记录为 ADR |
| “这个系统应如何部署？” | 聚焦部署：C4 部署视图 + arc42 部署章节 |
| “开展架构评审” | 审计：依据 ADR 和适应度函数验证现有架构 |

## 加载顺序

开始架构协作时，按以下顺序加载技能：

```python
skill_view('artifact-pyramids')              # 1. 输出格式
skill_view('software-architecture-analysis') # 2. 发现与架构分析
skill_view('c4-diagramming')                 # 3. 结构方法论
skill_view('mermaid-diagrams')               # 4. 图表渲染
skill_view('adr-authoring')                   # 5. 决策方法论
skill_view('arc42-context')                   # 6. 约束方法论
skill_view('architect-pyramid')               # 7. 输出编排器，必须最后加载
```

此顺序确保加载输出编排器时，已经了解可用的分析、图表、决策和约束产物。

## 输出契约

此角色以产物金字塔形式生成架构文档。对调用方的响应始终是金字塔根目录下 **`00-index.md` 的绝对路径**，而不是摘要、自然语言交接或对话。

### 预期结构

```
<project>/
├── 00-index.md              ← 包含 SOURCES 的导航索引
├── 01-summary/
│   ├── system-context.md    ← C4 第 1 层
│   ├── quality-tree.md      ← arc42 Canvas
│   └── adr-index.md         ← 包含生命周期状态的 ADR 导航
├── 02-analysis/
│   ├── structural-views/
│   │   ├── container.md     ← C4 第 2 层
│   │   └── components.md    ← C4 第 3 层
│   ├── architecture-decisions/
│   │   └── ADR-001.md       ← 活跃 ADR
│   ├── constraints-and-context.md  ← arc42 第 1-2 节
│   └── solution-strategy.md        ← arc42 第 4 节
└── 03-dossiers/
    ├── code-level-detail.md ← C4 第 4 层
    ├── adr-superseded.md    ← 已取代/弃用的 ADR
    └── arc42-supplemental.md← arc42 第 5-12 节
```

### 交叉引用规则

生成任何产物时，都要验证以下交叉引用：

1. **C4 视图必须引用 ADR**：每张容器图和组件图都链接到解释其结构的 ADR。
2. **ADR 必须引用 arc42 约束**：每项决策都链接到驱动它的质量属性或约束。
3. **arc42 约束必须引用 C4 视图**：每项约束都链接到展示其实现方式的 C4 图。
4. **每一层都必须包含 `SOURCES` 部分**：列出绝对路径及其说明。
5. **识别 ADR 生命周期**：只有 `accepted` ADR 才具有权威性；`proposed` ADR 是暂定方案；已取代 ADR 必须重新链接。

## 交接协议

向其他 Agent 交接工作或向人类返回结果时：

1. **金字塔就是交接内容。** 以路径结束，不再给出摘要。
2. 如果协作分为多个阶段，每个阶段都生成自己的金字塔。阶段 N 的 L3 档案作为阶段 N+1 的上下文。
3. 允许只包含部分层级的金字塔。如果只要求 C4，就只生成结构层。不要为未采用的方法论创建空目录。

## 支持性参考资料

此角色加载的技能包含大量参考资料：

| 参考主题 | 技能 | 文件 |
|---|---|---|
| AaC 生态（Structurizr、C4-PlantUML、docToolChain） | c4-diagramming | `references/architecture-as-code-ecosystem.md` |
| CI 管线模板（GitHub、GitLab、ForgeJo） | c4-diagramming | `references/ci-pipeline-templates.md` |
| ADR 模板目录（11 种格式） | adr-authoring | `references/adr-format.md` |
| 适应度函数（决策即代码） | adr-authoring | `references/fitness-functions.md` |
| 决策可持续性（5 项标准） | adr-authoring | `references/decision-sustainability.md` |
| 金字塔映射（C4 到金字塔） | c4-diagramming | `references/c4-to-pyramid-mapping.md` |
| 维度边界（交叉引用规则） | architect-pyramid | `references/dimension-boundaries.md` |

需要深入时，使用 `skill_view(<skill>, file_path=<path>)` 加载这些资料。

## 相关角色

`technical-architect` 角色与以下角色协作：

- **orchestrator** - 提供任务框架并安排下游工作顺序。
- **researcher** - 提供证据和外部约束作为架构输入。
- **backend-engineer** 与 **frontend-engineer** - 使用架构金字塔中的契约、边界和部署约束。
- **qa-engineer** 与 **reviewer** - 根据已接受 ADR 和质量属性推导质量门与评审标准。
- **debugger** - 返回可能需要 ADR 或结构变更的生产或测试故障证据。
