# 在新项目中建立 ADR 约定

在尚未使用 Architecture Decision Records 的代码库中建立 ADR 的可复用工作流。

## 快速检查清单

- [ ] 选择模板，默认使用 MADR。
- [ ] 确定目录位置，默认 `docs/adr/`。
- [ ] 编写 README 索引，即 `docs/adr/README.md`。
- [ ] 在 `CONTRIBUTING.md` 中记录约定。
- [ ] 在 `AGENTS.md` 中记录 ADR 位置，AI Agent 需要知道去哪里查找。
- [ ] 如果不存在，将 `.hermes/` 添加到 `.gitignore`。
- [ ] 为已经作出的设计决策创建首批 ADR。
- [ ] 作为单个 PR 提交：Issue → 分支 → ADR 加文档 → PR。

## 分步操作

### 1. 选择模板

| 场景 | 模板 | 章节 |
|------|----------|----------|
| 快速决策、单一依据 | **Nygard** | 状态、上下文、决策、后果 |
| 多选项权衡分析 | **MADR**（默认） | 状态、决策者、日期、上下文、决策驱动因素、已考虑选项、结果、链接 |
| 高风险/监管 | **Tyree & Akerman** | 12 个章节，例如问题、立场、论证、影响 |
| 供应商/采购 | **Business Case** | 评估标准、成本/SWOT 分析 |
| 面向 QA/NFR | **Planguage** | 标签、概要、优先级、利益相关方、风险 |

### 2. 设置目录约定

```text
docs/
└── adr/
    ├── README.md          # 包含状态和链接的索引表
    ├── 0001-title.md      # 第一份 ADR
    ├── 0002-title.md
    └── ...
```

**命名约定：**
- `NNNN-title-with-dashes.md`：连续补零编号，使用祈使动词短语。
- 状态位于文档头部，例如 `Status: accepted`，绝不写入文件名。
- 扩展名使用 `.md` 以便渲染。

**目录命名说明：**部分团队为提高自然语言可读性，偏好使用 `decisions/` 而非 `adr/`。两种名称均可使用同一 ADR 模板格式。

### 3. 编写 README 索引

索引是所有探索决策日志的使用方，包括 AI Agent 的入口，应包含：

- 对 ADR 及其约定的简要说明。
- 包含 ADR 编号、标题和状态的完整表格。
- 指向 `CONTRIBUTING.md` 中 ADR 工作流的链接。

完整示例见 GroktoCrawl 仓库，即 `groktopus/groktocrawl` 中的 `docs/adr/README.md`。

### 4. 在 CONTRIBUTING.md 中记录

增加包含以下内容的章节：

- **约定：**文件命名、状态、不可变性。
- **何时编写 ADR：**新增集成或服务、修改既有模式、在重大替代方案间选择、未来贡献者需要知道“为什么”的决策。
- **工作流：**使用下一个编号创建 ADR → 纳入 PR → 接受后更新索引。

### 5. 在 AGENTS.md 中记录

AI Agent 需要一段指向 ADR 目录的说明：

```markdown
架构决策记录（ADR）位于 `docs/adr/`，记录重大设计选择的上下文和依据。
在进行架构变更前，始终检查 `docs/adr/README.md` 中的 ADR 索引；既有 ADR
可能记录了会影响你的方法的约束或已拒绝替代方案。
```

### 6. Issue 优先的 PR 工作流

1. 创建记录适配器或架构设计的 Issue，即 L1 摘要加 L2 关键决策。
2. 从 main 创建带描述性名称的分支，例如 `feat/adapter-architecture`。
3. 使用 MADR 模板创建 ADR 文件。
4. 在 `CONTRIBUTING.md` 中记录约定。
5. 在 `AGENTS.md` 中增加 Agent 引用。
6. 如缺失，将 `.hermes/` 添加至 `.gitignore`，本地开发产物不应提交。
7. 提交正文包含 `Signed-off-by`（DCO）和 `Refs: #NNN`。
8. 推送并创建引用该 Issue 的 PR，例如 `Closes #NNN`。

## ADR 生命周期（持续使用）

```text
proposed → accepted → [deprecated | superseded by ADR-NNNN | rejected]
```

- **不可变规则：**既有 ADR 在接受后永不编辑。要修改决策时，编写新 ADR 并更新旧 ADR 状态。
- **链接：**每份 ADR 的 Links 章节应使用语义链接类型引用相关 ADR，例如 `Refined by`、`Supersedes`、`Defined by`、`Contradicts`。
- **退役编号：**绝不重用 ADR 编号。若被拒绝，应在索引中保留该编号并标记为 `rejected`。

## 完整示例

位于 `groktopus/groktocrawl#89` 的 GroktoCrawl 适配器架构 PR 演示了完整工作流：
- 9 份使用 MADR 模板、覆盖适配器注册表模式的 ADR。
- 包含状态表的 README 索引。
- 包含 ADR 约定章节的 CONTRIBUTING.md 更新。
- 添加 ADR 引用的 AGENTS.md 更新。
