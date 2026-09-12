---
name: arc42-context
description: "arc42 模板 - 约束与上下文文档，覆盖第 1-4 节（利益相关方、质量目标、约束、解决方案策略）和补充章节（架构、风险、部署、术语表）。将 arc42 章节映射到产物金字塔层（Canvas→L1、第 1-4 节→L2、第 5-12 节→L3）。technical-architect 角色需要记录系统上下文和约束时使用。"
---

# arc42 上下文

arc42 模板用于记录系统约束、上下文和质量属性。它补充仅靠结构视图（C4）和决策记录（ADR）无法表达的上下文维度，即约束和质量属性。

## arc42 到金字塔的映射

| arc42 章节 | 金字塔层 | 路径 |
|--------------|--------------|------|
| Canvas/质量树 | L1（摘要） | 01-summary/quality-tree.md |
| 第 1-2 节：目标、约束 | L2（分析） | 02-analysis/constraints-and-context.md |
| 第 4 节：解决方案策略 | L2（分析） | 02-analysis/solution-strategy.md |
| 第 5-8 节：架构 | L3（档案） | 03-dossiers/arc42-supplemental.md |
| 第 9-12 节：风险、部署、术语表 | L3（档案） | 03-dossiers/arc42-supplemental.md |

没有 arc42，Agent 只能看到解决方案，无法看到界定有效方案的边界。L2 中的第 1-4 节提供约束范围，L3 中的第 5-12 节提供详细实现上下文。

## 内容

- `references/arc42-sections-1-4.md` - 各章节的详细指南和示例表格
- `references/arc42-to-pyramid-mapping.md` - 约束→L2、Canvas→L1，以及精简/必要/详尽模式

## 规范参考

- arc42 — https://arc42.org/
- Magnus Hedemark，《Clanker Technical Architect: First on the Scene with Progressive Disclosure》- https://magnus919.com/2026/05/clanker-technical-architect-first-on-the-scene-with-progressive-disclosure/
