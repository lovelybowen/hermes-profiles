---
name: adr-authoring
description: "架构决策记录 - 捕获决策、记录依据、分析替代方案并跟踪后果。将 ADR 映射到产物金字塔（导航索引→L1、活跃 ADR→L2、已取代 ADR→L3）。technical-architect 角色需要记录架构决策时使用。"
---

# ADR 编写

架构决策记录用于捕获设计依据。ADR 补充仅有结构视图（C4）所缺失的时间维度，即决策随时间的演变。

## ADR 到金字塔的映射

| ADR 状态 | 金字塔层 | 路径 |
|-----------|--------------|------|
| 导航索引 | L1（摘要） | 01-summary/adr-index.md |
| 活跃 ADR | L2（分析） | 02-analysis/architecture-decisions/ADR-NNN.md |
| 已取代 ADR | L3（档案） | 03-dossiers/adr-superseded.md |

没有 ADR，Agent 只能看到结构快照，无法重建形成该结构的决策路径。L2 中的活跃 ADR 提供决策依据，L3 中的已取代 ADR 保留被拒绝替代方案的历史。

## ADR 生命周期

ADR 经历六个阶段，每个阶段都有门禁标准：

```
发起 → 研究 → 评估 → 实施 → 维护 → 退役
```

| 阶段 | 状态 | 金字塔层 | 使用方 |
|-------|--------|--------------|----------|
| 发起 | `proposed` | L2（02-analysis/） | 评估中的工程师 |
| 研究 | `proposed` | L2（02-analysis/） | 评估中的工程师 |
| 评估 | `proposed` | L2（02-analysis/） | 作出决定的工程师 |
| 实施 | `accepted` | L2（02-analysis/） | 实施者、评审员 |
| 维护 | `accepted` | L2（02-analysis/） | 新团队成员、审计人员 |
| 退役 | `deprecated`/`superseded` | L3（03-dossiers/） | 历史研究者 |

所有有效 ADR（`proposed` + `accepted`）都保留在 L2。只有已取代或弃用的 ADR 才移至 L3。被拒绝的拟议 ADR 应以 `rejected` 状态移至 L3，并注明原因。

### 替代生命周期：AWS ADR 流程

AWS Prescriptive Guidance 定义了带有结构化评审流程的补充生命周期，适合相较活文档更偏好正式不可变性的团队。

**状态：** `proposed → accepted | rejected | superseded`

**关键区别：** AWS 将已接受 ADR 视为严格不可变。变更决策需要创建新 ADR 并取代旧 ADR。社区 ADR 仓库的团队协作建议更倾向使用带日期更新的可变活文档。请选择适合团队文化的模型。

**AWS 评审流程：**

1. **提议** - 任何团队成员都可以创建状态为 `proposed` 的 ADR，作者即 ADR 负责人。
2. **评审会议** - 预留专门时间并采用结构化格式：
   - **静默阅读 10-15 分钟** - 每位成员阅读 ADR 并添加评论
   - **宣读评论** - 负责人逐条宣读评论，团队讨论
   - **行动项** - 为发现的问题指定负责人并跟踪至解决
3. **决策** - 有三种结果：
   - **接受** → 负责人添加时间戳、版本和利益相关方列表；状态变为 `accepted`，此后不可变。
   - **返工** → 状态保持 `proposed`；负责人解决行动项并重新安排评审。
   - **拒绝** → 负责人记录拒绝原因，防止未来重复争议；状态变为 `rejected`，文件移至 L3。
4. **取代** - 新决策使已接受 ADR 失效时，创建新 ADR。新 ADR 被接受后，将旧 ADR 状态改为 `superseded` 并移至 L3。

```
[识别需求] → [起草（proposed）] → [静默阅读 10-15 分钟] → [讨论]
                      ↓                     ↓                     ↓
                 [返工/复审] ← [需要返工]                  [接受] → [不可变]
                                                           [拒绝] → [L3]
```

## 模板选择

| 场景 | 模板 | 章节 |
|------|----------|----------|
| 快速决策、单一依据 | **Nygard** | 状态、上下文、决策、后果 |
| 多选项权衡分析 | **MADR** | 决策驱动因素、考虑的选项、优缺点、链接 |
| 高风险、监管、合规 | **Tyree & Akerman** | 12 个章节：问题、立场、论证、影响等 |
| 供应商/采购决策 | **Business Case** | 评估标准、成本/SWOT、建议 |
| QA/契约驱动环境 | **Planguage** | 标签、要点、优先级、利益相关方、风险 |

包含逐章节指南的完整目录见 `references/adr-format.md`。

## 文件命名约定

使用现在时祈使动词短语、小写连字符和 `.md` 扩展名：

```
001-choose-database.md
002-format-timestamps.md
003-manage-secrets.md
```

状态位于文档头部，而不是文件名中；状态变更不应要求重命名文件。

## 团队协作与治理

- **谁可以创建：** 任何读过 ADR 流程文档的团队成员
- **何时值得创建：** 影响未来“为什么”、跨团队协调、长期可维护性或外部接口的决策
- **何时无需创建：** 范围/时间/风险有限、已有标准覆盖、临时变通方案或 POC
- **每份 ADR 的角色：** 主要联系人、次要联系人、责任团队
- **优先使用活文档：** 使用带日期的更新插入新信息，而不是每次更新都取代 ADR。不可变性在理论上理想，可变性在实践中通常更有效。

完整治理模型和团队协作问题见 `references/adr-format.md`。

## 内容

- `references/adr-format.md`——模板目录（11 种格式：Nygard、MADR、Tyree & Akerman、Business Case、Planguage、Alexandrian、ITD、arc42、EdgeX、Gareth Morgan、NHS Wales）、模板选择决策树、生命周期阶段、文件命名、团队治理、示例参考
- `references/adr-to-pyramid-mapping.md`——active→L2、superseded→L3、使用方路由
- `references/fitness-functions.md`——决策即代码：ArchUnit、ArchUnitTS、AI 辅助适应度函数、金字塔映射（适应度函数 → L3）
- `references/decision-sustainability.md`——接受 ADR 前用于评估其质量的 5 项可持续性准则 + 8 条指引
- `references/project-setup-guide.md`——在新项目中引导 ADR：目录设置、README 索引、CONTRIBUTING.md/AGENTS.md 文档、包含实践示例的 issue 优先 PR 工作流

## 规范参考

- 架构决策记录社区仓库——https://github.com/architecture-decision-record/architecture-decision-record
- Michael Nygard, "Documenting Architecture Decisions" — https://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions
- Magnus Hedemark, "Clanker Technical Architect: First on the Scene with Progressive Disclosure" — https://magnus919.com/2026/05/clanker-technical-architect-first-on-the-scene-with-progressive-disclosure/
