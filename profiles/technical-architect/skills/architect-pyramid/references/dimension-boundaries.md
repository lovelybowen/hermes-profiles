# 维度边界

定义每类事实应存放在哪个文件，以及文件之间如何交叉引用。

## 文件边界

| 文件 | 包含内容 | 不包含内容 |
|------|----------|-----------------|
| system-context.md | 系统边界、外部参与者、关键交互 | 内部组件细节、决策依据、约束 |
| container.md | 服务边界、数据存储、技术选择 | 组件内部实现、ADR、代码细节 |
| components.md | 模块职责、接口 | 容器拓扑、代码层级细节、ADR 依据 |
| architecture-decisions/ADR-NNN.md | 决策上下文、选项、后果 | 结构描述、约束细节 |
| constraints-and-context.md | 质量目标、约束、利益相关方需求 | 解决方案策略、结构图 |
| code-level-detail.md | 类图、接口定义 | 组件职责、容器拓扑 |

## 金字塔中的 ADR 生命周期状态

ADR 会随着生命周期推进在金字塔中流动：

| 生命周期阶段 | 金字塔层级 | ADR 状态 | 允许的行为 |
|---|---|---|---|
| 发起 → 研究 → 评估 | L2（02-analysis/） | `proposed` | 正在讨论，尚未最终确定 |
| 实施 → 维护 | L2（02-analysis/） | `accepted` | 最终决策，正在使用 |
| 已取代 / 已弃用 / 已拒绝 | L3（03-dossiers/） | `superseded`、`deprecated`、`rejected` | 仅作历史保留 |

**规则：**所有存续 ADR，即 `proposed` 与 `accepted`，均存放在 L2；只有历史 ADR 移至 L3。这样既避免过时或被拒绝的决策干扰活跃分析，也保留完整历史。

**不可变文档与活文档：**物理移动模型，即被取代后从 L2 → L3，假定采用**不可变 ADR**方式：ADR 一旦接受就不再编辑，新 ADR 取代旧 ADR。有些团队偏好**活文档**方式，直接在 ADR 中新增带日期的内容。在这种方式下，ADR 不在层级间物理移动，只修改同一文件内的状态字段，L1 索引反映当前状态。金字塔同时支持两种方式：L3 的 `adr-superseded.md` 在活文档方式下成为仅含状态条目的汇编，而非不可变方式下被移动的文件。项目建立时应选择模式，并在 ADR 索引 README 中记录选择。

## 交叉引用规则

1. **structural-views/*.md → architecture-decisions/：**每个组件都链接到解释其结构的 ADR。
2. **architecture-decisions/*.md → constraints-and-context.md：**每项决策都引用驱动它的质量属性或约束。
3. **constraints-and-context.md → structural-views/：**每项约束都链接到展示其实现方式的 C4 图。
4. **同一维度内不跨层引用：**C4 视图不跨层引用 C4 视图，ADR 不跨层引用 ADR。
5. **生命周期转换必须更新金字塔位置：**ADR 从 `accepted` 转为 `superseded` 时，应从 L2 物理移动到 L3，并更新 L1 的 adr-index.md 以反映新位置。注：此规则适用于不可变模型；在活文档模型中，文件保持原位，仅修改状态。

## ADR 生命周期意识

| 状态 | 引用是否有效 | 使用方 |
|--------|-------------------|----------|
| `proposed` | 是，作为暂定方案由 C4 视图链接 | 评估决策的工程师 |
| `accepted` | 是，作为确定方案由 C4 视图链接 | 实施人员、reviewer |
| `deprecated` / `superseded` | 否，移至 L3，C4 视图重新链接到替代项 | 历史查阅者、质疑者 |
| `rejected` | 否，带拒绝依据移至 L3 | 审计人员 |

当 C4 组件链接到 ADR 时，应在将其视为权威依据前验证 ADR 状态。已取代 ADR 是未采用路径的证据，不代表当前结构。
