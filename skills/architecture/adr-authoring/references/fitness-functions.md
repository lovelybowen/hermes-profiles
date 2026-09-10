# 将决策作为代码的适应度函数

适应度函数是以代码编写的自动检查，用于验证架构决策是否持续得到遵守。ADR 记录决策，适应度函数则*保证*决策被执行。

**概念来源：**https://github.com/architecture-decision-record/architecture-decision-record，基于 ADR 社区仓库中的“将决策作为代码的适应度函数”文档。

## 适应度函数如何连接 ADR

```
ADR：“我们为审计要求使用事件溯源”
    ↓
适应度函数：CI 测试断言每次状态变更都会生成事件
    ↓
如果提交引入了在未发出事件的情况下修改状态的代码路径 → 测试失败
```

ADR 捕获*意图*，适应度函数强制*执行*。

## 适应度函数为何重要

| 益处 | 说明 |
|---------|-------------|
| **客观衡量** | 通过/失败，而不是意见；结果可见且清晰。 |
| **持续强制** | 在每次提交、构建和部署时运行，形成活规则。 |
| **重构信心** | 变更期间自动捕获违反决策规则的情况。 |
| **可扩展治理** | 在不断增长的代码库中保证标准，而不创建人工瓶颈。 |

## 适应度函数方法

### 1. 架构单元测试（Java - ArchUnit）

[ArchUnit](https://www.archunit.org/) 使用普通 Java 单元测试框架，例如 JUnit、TestNG，检查架构规则。

```java
// 示例：强制服务不得直接访问 repository
@Test
public void services_should_not_access_repositories_directly() {
    JavaClasses classes = new ClassFileImporter().importPackages("com.myapp");
    ArchRule rule = classes()
        .that().resideInAPackage("..service..")
        .should().onlyAccessClassesThat()
        .resideInAnyPackage("..service..", "..api..");
    rule.check(classes);
}
```

**可强制的 ADR 模式：**
- 分层架构违规，例如 UI → Service → Repository 方向。
- 依赖注入规则，例如某些接口不得使用 `new`。
- 包循环检测。
- 与架构角色匹配的命名约定。

### 2. 架构单元测试（TypeScript - ArchUnitTS）

[ArchUnitTS](https://github.com/LukasNiessen/ArchUnitTS) 使用 Jest、Vitest、Jasmine 等为 TypeScript/JavaScript 提供相同模式。

```typescript
// 示例：Controller 应依赖 service，而非 repository
const rule = ArchRule.of('controllers')
    .should().onlyDependOn()
    .packages(['services', 'dto']);
```

### 3. AI 辅助适应度函数

对于无法表示为静态代码检查的决策，使用基于 LLM、具有结构化提示词模板的适应度函数：

```txt
IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.
IMPORTANT: Turn on extended thinking. Turn on expert advice. Turn on search.

这是一个适应度函数，用于评估我们的工作是否
使用了所有决策，并且正确、准确。

- 我们的决策在这里：{ADR 索引的 URL}
- 待评估工作在这里：{代码/PR/设计文档的 URL}

解释任何错误、问题、缺口和弱点。直截了当，明确决断。
```

**AI 辅助适应度函数的使用时机：**
- 同时根据多个 ADR 评估 PR。
- 检查一组相关决策之间的逻辑一致性。
- 验证设计文档或提案是否符合架构。
- 审计没有机械强制机制的决策。

## 映射到产物金字塔

| 层级 | 存放内容 | 与适应度函数的关系 |
|-------|-----------------|---------------------------|
| L1（01-summary/） | ADR 导航索引 | - |
| L2（02-analysis/） | 活跃 ADR（决策依据） | ADR 声明应强制*什么* |
| L3（03-dossiers/） | 已取代 ADR、运行产物 | 适应度函数位于此处 |

**适应度函数不是 ADR 本身的一部分。**它们是运行治理产物，存放在测试套件或 CI 管线中，而非决策日志中。ADR 应通过 Links 章节或 `Confirmed by` 注记*引用*任何强制它的适应度函数，但函数代码本身属于项目测试基础设施。

## 何时编写适应度函数

| 场景 | 示例 |
|------|---------|
| 决策影响可衡量的架构特性 | “所有服务必须记录结构化 JSON” → 测试断言日志输出格式 |
| 决策具有清晰通过/失败条件 | “包之间不允许循环依赖” → ArchUnit 测试 |
| 人工验证决策遵守成本高 | “每个 gRPC 端点必须限流” → CI 集成测试 |
| 监管或合规要求审计轨迹 | “所有状态修改必须记录日志” → Middleware 测试 |

当 ADR 明确规定可机械验证的规则时，应为其创建适应度函数。如果决策涉及成本或组织权衡，适应度函数不适用，应跳过自动强制并依赖 ADR 的依据进行治理。

## 与决策治理的关系

适应度函数将高级 ADR 模板，例如 NHS Wales、Gareth Morgan 中的**治理**和**确认**章节落实为可执行机制。如果 ADR 模板包含 Governance 章节，应在其中列出适应度函数：

```markdown
## Governance

此决策的遵守情况通过以下方式验证：
- ArchUnit 测试 `NoServiceDirectDatabaseAccessTest`，在每个 PR 上运行。
- 每个发布周期根据 {ADR 索引链接} 开展 AI 辅助审计。
```

## 将 Structurizr CI 检查作为适应度函数

使用 Structurizr DSL 编写 C4 模型文档时，Structurizr CLI 提供两个命令，可作为架构文档一致性的适应度函数：

### validate

检查 DSL 文件是否语法有效且结构一致：

```bash
structurizr-cli validate -w docs/arch/model/system.dsl
```

将其用作合并前 CI 门：DSL 无法解析时，架构模型即已损坏。它可避免提交产生无图表或损坏图表。

### inspect

检查模型是否发生架构漂移，验证 C4 模型是否与通过 `!adrs` 引用的 ADR 保持一致：

```bash
structurizr-cli inspect -w docs/arch/model/system.dsl
```

在每个修改 DSL 或 ADR 目录的 PR 中运行 CI。它可捕获：
- 被引用却不存在于 `!adrs` 路径中的 ADR 文件。
- 在视图中引用却未在模型中定义的元素。
- 模型与文档之间的关系不一致。

### CI 管线集成

```yaml
# .github/workflows/architecture-checks.yml (or similar)
steps:
  - name: 验证 Structurizr DSL
    run: structurizr-cli validate -w docs/arch/model/system.dsl

  - name: 检查漂移
    run: structurizr-cli inspect -w docs/arch/model/system.dsl
```

这些属于语法和结构检查。对于语义验证，即架构是否符合 ADR，应结合上文“AI 辅助适应度函数”章节中的提示词。二者共同构成完整验证管线：语法 → 结构 → 依据。

面向 GitHub Actions、GitLab CI 和 ForgeJo，包含验证、导出和部署的完整管线模板位于 `references/ci-pipeline-templates.md`，即 c4-diagramming 技能中。

## 延伸阅读

- ArchUnit：https://www.archunit.org/
- ArchUnitTS：https://github.com/LukasNiessen/ArchUnitTS
- ADR 社区仓库的适应度函数：https://github.com/architecture-decision-record/architecture-decision-record，参见 `locales/en/documents/fitness-functions-for-decisions-as-code/`。
