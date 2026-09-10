# 技术架构师 - Hermes 角色

这是 Hermes Agent 的系统架构专用角色。它设计服务边界、API 契约和部署拓扑，并使用**产物金字塔**格式生成架构文档。

## 角色能力

- **C4 模型** - 4 个缩放层级的结构视图（系统上下文、容器、组件、代码）
- **ADR** - 包含生命周期管理和 11 种模板格式的架构决策记录
- **arc42** - 系统约束、质量属性和部署上下文
- **产物金字塔** - 将三种方法论组合为一份可渐进披露的输出

## 前置条件

- 已安装并配置 [Hermes Agent](https://hermes-agent.nousresearch.com/)
- 已安装下方列出的技能（见“安装”）

## 安装

```bash
# 克隆角色配置仓库
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles

# 将角色配置链接到 ~/.hermes/profiles/
ln -s ~/hermes-profiles/profiles/technical-architect ~/.hermes/profiles/

# 切换角色配置（已包含技能，无需单独安装）
hermes --profile technical-architect
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/technical-architect/.env.example profiles/technical-architect/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/technical-architect/SOUL.md` —— 这是权威来源。

## 快速开始

加载角色后，向它提出架构任务：

> “为一个每分钟处理一万笔交易且需要符合 PCI-DSS 的支付处理系统设计服务边界。”

此角色会：
1. 发现约束（延迟、合规、团队结构）。
2. 生成 C4 结构视图（上下文 → 容器 → 组件）。
3. 将关键决策及其备选方案记录为 ADR。
4. 加入 arc42 上下文（质量属性、风险、部署）。
5. 在任务工作区（Kanban `worktree:` / `dir:`、项目约定目录或 `${ARCHITECT_ARTIFACTS_DIR:-./architecture}`）下输出产物金字塔，并返回 `00-index.md` 的绝对路径。

## 技能依赖

每个必需技能提供一项特定能力。开始协作时按顺序加载：

| 技能 | 能力 | 加载命令 |
|---|---|---|
| `artifact-pyramids` | 三层渐进披露规范 | `skill_view('artifact-pyramids')` |
| `software-architecture-analysis` | 代码库发现与架构分析 | `skill_view('software-architecture-analysis')` |
| `c4-diagramming` | C4 结构视图（Mermaid 或 Structurizr DSL） | `skill_view('c4-diagramming')` |
| `mermaid-diagrams` | 图表渲染（供 c4-diagramming 使用） | `skill_view('mermaid-diagrams')` |
| `adr-authoring` | ADR 生命周期、11 种模板、适应度函数 | `skill_view('adr-authoring')` |
| `arc42-context` | 约束、质量属性、风险/部署文档 | `skill_view('arc42-context')` |
| `architect-pyramid` | 输出编排、交叉引用规则 | `skill_view('architect-pyramid')` |

### 支持性参考资料（包含在技能中）

技能包包含可通过 `skill_view()` 访问的大量参考资料：

- **AaC 生态** - Structurizr DSL、C4-PlantUML、docToolChain、统一仓库约定、工具比较（`c4-diagramming` 技能，`references/architecture-as-code-ecosystem.md`）
- **CI 管线模板** - 用于自动生成架构文档的 GitHub Actions、GitLab CI、ForgeJo 模板（`c4-diagramming` 技能，`references/ci-pipeline-templates.md`）
- **ADR 格式目录** - 带有选择决策树的 11 种模板格式（`adr-authoring` 技能，`references/adr-format.md`）
- **适应度函数** - ArchUnit、AI 辅助检查、以 Structurizr CI 实现决策即代码（`adr-authoring` 技能，`references/fitness-functions.md`）
- **决策可持续性** - 用于评估 ADR 质量的 5 项标准和 8 条指南（`adr-authoring` 技能，`references/decision-sustainability.md`）

## 输出格式

所有输出都遵循产物金字塔约定：

```
<project>/
├── 00-index.md              ← 导航 + SOURCES
├── 01-summary/              ← C4 上下文图、arc42 质量树、ADR 索引
├── 02-analysis/             ← C4 容器/组件、活跃 ADR、arc42 第 1-4 节
└── 03-dossiers/             ← C4 代码、已取代 ADR、arc42 第 5-12 节
```

对任何调用方的响应都是 `00-index.md` 的绝对路径，而不是摘要或对话，只是一个路径。

## 验证

部署后的 `technical-architect` Agent 应通过以下检查：

- [ ] 接收架构任务并生成产物金字塔
- [ ] 金字塔包含三种方法论（C4、ADR、arc42）的产物
- [ ] 响应是 `00-index.md` 的绝对路径，而不是摘要
- [ ] 每种方法论都可独立使用
