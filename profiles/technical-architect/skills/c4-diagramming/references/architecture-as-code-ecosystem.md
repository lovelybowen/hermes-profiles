# Architecture as Code（AaC）生态

在同一个 Git 仓库中统一管理 C4 模型图、arc42 文档和架构决策记录（ADR）的工具、约定和模式。

## 1. Structurizr——C4 参考实现

Structurizr 是 C4 模型的官方“模型即代码”工具，由 C4 模型作者 Simon Brown 创建。你使用文本 DSL 定义完整的软件架构模型；所有图都根据该单一模型生成。

**主要网站：**https://structurizr.com/——**文档：**https://docs.structurizr.com/

### 核心概念

- **Workspace**——顶层容器。包含模型 + 视图 + 文档 + 决策。
- **Model**——定义元素（人员、软件系统、容器、组件）及其关系。
- **Views**——选择模型子集用于渲染图（系统上下文、容器、组件、动态、部署）。
- **DSL**——基于文本的领域特定语言。单一事实来源，适合 Git。

### 最小示例（全部四个 C4 层级）

```
workspace {

    model {
        user = person "客户"
        system = softwareSystem "互联网银行系统" {
            webapp = container "Web 应用" "TypeScript, React" {
                user -> this "使用"
            }
            api = container "API" "Go" {
                webapp -> this "发起 API 调用"
            }
            db = container "数据库" "PostgreSQL" {
                api -> this "读写"
            }
        }
    }

    views {
        systemContext system {
            include *
            autolayout lr
        }
        container system {
            include *
            autolayout lr
        }
        component api {
            include *
            autolayout lr
        }
        theme default
    }

}
```

### `!adrs` 关键词——原生 ADR 集成

Structurizr 可以将架构决策记录直接导入 workspace：

```
workspace {

    !adrs docs/adr

    model { ... }
    views { ... }

}
```

默认情况下，这会使用 adr-tools 格式导入 `docs/adr/` 中的所有 Markdown 文件。支持的格式：
- `adrtools`（默认）——要求文件符合 adr-tools 命名约定
- `madr`——用于 MADR 格式的 ADR
- `log4brains`——用于 log4brains 格式的 ADR

ADR 会与 C4 图一起渲染在 Structurizr UI 中。这是目前 C4 与 ADR 之间最紧密的集成。

### `!docs` 关键词——导入 arc42 文档

```
workspace {

    !docs docs/arc42

    model { ... }
    views { ... }

}
```

导入按 arc42 章节组织的 Markdown 或 AsciiDoc 文档，并在 UI 中与图和 ADR 一起渲染。支持基于章节的导航。

### Structurizr Lite——本地预览

用于在浏览器中渲染完整 workspace 的 Docker 容器：

```yaml
# docker-compose.yml
services:
  structurizr-lite:
    image: structurizr/lite
    ports:
      - "8081:8080"
    volumes:
      - ./docs/arch:/usr/local/structurizr
```

通过 `http://localhost:8081` 访问。在统一且带导航的 Web UI 中展示 C4 图、arc42 文档和 ADR。

### CI/CD 命令

```bash
# 验证 DSL 语法和模型一致性
structurizr-cli validate -w docs/arch/model/system.dsl

# 检查架构漂移
structurizr-cli inspect -w docs/arch/model/system.dsl

# 将图导出为 PlantUML
structurizr-cli export -w docs/arch/model/system.dsl -format plantuml

# 将图导出为 Mermaid
structurizr-cli export -w docs/arch/model/system.dsl -format mermaid

# 导出为静态 HTML 站点
structurizr-cli export -w docs/arch/model/system.dsl -format site
```

### DSL 实践手册

完整教程指南：https://docs.structurizr.com/dsl/cookbook/

涵盖主题：workspace 结构、模型元素、关系、视图、样式、主题、动画、部署节点、动态图、过滤、属性、视角。

---

## 2. C4-PlantUML——更轻量的替代方案

**仓库：**https://github.com/plantuml-stdlib/C4-PlantUML

通过 PlantUML include 文件为标准 PlantUML 增加 C4 语义。它不具备单模型一致性（每张图都是独立文件），但学习曲线远低于 Structurizr。

### 函数参考

| 函数 | C4 层级 | 目的 |
|---|---|---|
| `Person(alias, label, description)` | 任意 | 外部用户或参与者 |
| `Person_Ext(alias, label, description)` | 上下文 | 外部用户（系统边界之外） |
| `System(alias, label, description)` | 上下文 | 软件系统 |
| `System_Ext(alias, label, description)` | 上下文 | 外部软件系统 |
| `Container(alias, label, tech, description)` | 容器 | 应用容器（Web 应用、API、数据库） |
| `Container_Boundary(alias, label)` | 容器 | 对相关容器进行分组 |
| `Component(alias, label, tech, description)` | 组件 | 容器内的模块 |
| `System_Boundary(alias, label)` | 上下文 | 对相关系统进行分组 |
| `Rel(from, to, label, tech)` | 任意 | 元素之间的关系 |
| `Rel_D(from, to, label, tech)` | 任意 | 关系（虚线） |
| `Rel_Neighbor(from, to, label, tech)` | 任意 | 关系渲染优化 |
| `UpdateLayoutConfig(c4ShapeInRow, c4BoundaryInRow)` | 任意 | 布局调优 |
| `LAYOUT_WITH_LEGEND()` | 任意 | 使用自动图例渲染 |

### 示例

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(customer, "客户")
System(system, "你的系统", "核心平台")
System_Ext(external, "外部服务", "支付处理方")

Rel(customer, system, "使用")
Rel(system, external, "通过其扣款")
@enduml
```

### 何时优先于 Structurizr 选择它

| 情况 | 选择 |
|---|---|
| 团队已使用 PlantUML 绘制其他图 | C4-PlantUML（工具链一致） |
| 需要为临时文档快速绘制 C4 图 | C4-PlantUML（无需学习 DSL） |
| 需要跨 4 个 C4 层级保持多图模型一致 | Structurizr（单一事实来源） |
| 希望在图查看器中集成 ADR | Structurizr（原生支持 `!adrs`） |
| CI 流水线已包含 PlantUML | 两者皆可——Structurizr 可导出为 PlantUML |

---

## 3. docToolChain——arc42 构建流水线

**仓库：**https://github.com/docToolchain/docToolchain

专为 arc42 文档构建的、基于 Gradle 的文档即代码工具链。处理完整流水线：AsciiDoc 编译、PlantUML 图生成、PDF/HTML 导出、Confluence 发布。

### 关键能力

- **arc42 模板管理**——生成包含全部 12 个章节的 arc42 文档骨架
- **AsciiDoc 编译**——将 `.adoc` 源文件转换为 HTML、PDF、DocBook
- **PlantUML 集成**——在构建过程中渲染 C4 图（通过 C4-PlantUML include）
- **Confluence 导出**——通过 asciidoc2confluence 将渲染后的文档发布到 Confluence 空间
- **Gradle 任务层级**——将 `generateHTML`、`generatePDF`、`exportConfluence` 作为标准任务

### 目录结构约定

```
docs/
├── src/
│   ├── arc42/
│   │   ├── 01_introduction_and_goals.adoc
│   │   ├── ...
│   │   └── 12_glossary.adoc
│   └── images/
├── build/              ← 生成的输出
├── build.gradle        ← docToolChain 配置
└── gradle.properties
```

### 使用时机

docToolChain 适合希望以**标准化、构建流水线驱动**方式维护 arc42 文档的组织。它以增加仪式（Gradle 构建、严格目录结构）为代价，换取一致的输出格式和 Confluence 集成。对于只需要 C4 图和 ADR 的团队，Structurizr 更轻量。

---

## 4. 汇聚的仓库约定

AaC 社区已经汇聚出一种标准目录结构，用于在单个 Git 仓库中组合 C4、arc42 和 ADR。多个参考实现都采用相同模式：

### 目录结构

```
docs/arch/
├── model/
│   ├── system.dsl                ← Structurizr DSL（架构模型）
│   └── deployment/               ← 特定于部署的视图（开发、预发布、生产）
│       ├── dev.dsl
│       └── live.dsl
├── src/                          ← arc42 12 章节模板
│   ├── 01_introduction_and_goals.adoc
│   ├── 02_constraints.adoc
│   ├── 03_system_scope_and_context.adoc
│   ├── 04_solution_strategy.adoc
│   ├── 05_building_block_view.adoc
│   ├── 06_runtime_view.adoc
│   ├── 07_deployment_view.adoc
│   ├── 08_crosscutting_concepts.adoc
│   ├── 09_architecture_decisions.adoc
│   ├── 10_quality_requirements.adoc
│   ├── 11_technical_risks.adoc
│   └── 12_glossary.adoc
├── adr/                          ← 架构决策记录
│   ├── 0001-record-architecture-decisions.md
│   ├── 0002-use-postgresql.md
│   ├── 0003-adopt-event-sourcing.md
│   └── README.md                 ← 带状态表的 ADR 索引
├── images/                       ← 嵌入的截图、图
├── README.md                     ← 项目概览
└── docker-compose.yml            ← Structurizr Lite
```

### 三种方法论如何关联

| 组成部分 | 目的 | 创建者 | 使用者 |
|---|---|---|---|
| `model/system.dsl` | C4 模型（所有层级） | Technical architect | Structurizr 渲染 4 张图 |
| `src/09_architecture_decisions.adoc` | arc42 决策章节 | Technical architect | 阅读 arc42 文档的人类 |
| `adr/0002-use-postgresql.md` | 完整 ADR 内容 | Technical architect | Structurizr 通过 `!adrs` 导入 |
| `docker-compose.yml` | 本地预览 | 团队 | `docker compose up` → 浏览器 |

### 参考实现

- **dzimchuk/architecture-as-code**——Structurizr DSL + arc42 AsciiDoc + ADR + Docker Compose。最简洁的最小示例。https://github.com/dzimchuk/architecture-as-code
- **milanm/architecture-docs**——采用相同方法，但增加 PlantUML 图导出和 GitHub Pages CI。https://github.com/milanm/architecture-docs
- **bitsmuggler/arc42-c4-example**——为互联网银行系统填写的 arc42 模板。https://bitsmuggler.github.io/arc42-c4-software-architecture-documentation-example/

---

## 5. 工具比较

| 准则 | Structurizr | C4-PlantUML | Mermaid |
|---|---|---|---|
| **模型一致性** | 单一模型 → 全部 4 张图 | 每个文件单独 include | 每个文件手动维护 |
| **学习曲线** | 中等（DSL 语法） | 低（PlantUML） | 低 |
| **ADR 集成** | 原生（`!adrs` 关键词） | 无 | 无 |
| **arc42 集成** | 原生（`!docs` 关键词） | 无 | 无 |
| **CI 就绪度** | CLI + Docker 镜像 | PlantUML CLI | `mmdc` CLI |
| **GitHub 渲染** | 不支持（需要 Structurizr 查看器） | 通过 PlantUML GitHub Action | 原生支持（如果使用 flowchart 语法） |
| **本地预览** | Structurizr Lite（Docker） | PlantUML 服务器 | VS Code 插件 |
| **布局** | 自动 + 手动（拖动排列） | 仅自动 | 通过 `---` 方向自动布局 |

## 6. 延伸阅读

- Structurizr DSL 实践手册：https://docs.structurizr.com/dsl/cookbook/
- Structurizr DSL 语言参考：https://docs.structurizr.com/dsl/language
- Structurizr ADR 集成：https://docs.structurizr.com/dsl/adrs
- Structurizr“即代码”理念：https://docs.structurizr.com/as-code
- C4-PlantUML: https://github.com/plantuml-stdlib/C4-PlantUML
- docToolChain: https://github.com/docToolchain/docToolchain
- dzimchuk AaC 示例：https://github.com/dzimchuk/architecture-as-code
- milanm AaC 示例：https://github.com/milanm/architecture-docs
- CI 流水线模板（GitHub Actions、GitLab CI、ForgeJo）：`references/ci-pipeline-templates.md`
