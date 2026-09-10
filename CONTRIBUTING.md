# 为 Hermes 角色配置集贡献

感谢你考虑向本集合添加角色配置。高质量角色配置应符合以下要求。

## 角色配置要求

每个角色配置目录必须包含以下文件：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | **权威运行协议**：第一原则、职责边界、触发模式、加载顺序、输出契约 |
| `config.yaml` | 模型、provider 与工具集；**不得包含任何密钥** |
| `profile.yaml` | 元数据：描述、必需技能、推荐技能 |
| `README.md` | 使用指南：安装、配置、技能参考 |
| `AGENTS.md` | 指向 `SOUL.md` 的索引 + 该角色的上下游接口 |
| `.env.example` | 所需凭据清单（真实 `.env` 被 gitignore） |
| `skills/` | 指向共享池的相对符号链接（非文件内容） |

**为什么运行协议只在 `SOUL.md`：** Hermes 把 `$HERMES_HOME/SOUL.md` 注入每个会话，而 `AGENTS.md` 只有工作目录恰为该角色目录时才加载。触发模式与交接协议必须每会话生效，因此放 `SOUL.md`；`AGENTS.md` 只做索引，避免两份协议漂移。

## 技能共享

角色配置通过根级 `skills/` 目录共享技能。每个角色配置的 `skills/` 目录都包含指回共享池的**相对符号链接**：

```
skills/                          ← 实际技能文件（单份）
└── some-skill/
    ├── SKILL.md
    └── references/
profiles/some-profile/skills/    ← 符号链接
    └── some-skill -> ../../../skills/some-skill
```

- **不要**将技能文件复制到角色配置目录中，请使用符号链接。
- **不要**使用绝对符号链接路径。应从角色配置的 `skills/` 目录使用相对路径指回仓库根目录的 `skills/`。
- 如果角色需要共享池中不存在的技能，请先将该技能添加到 `skills/`，再从角色配置创建符号链接。

## 技能设计指南

共享池中的技能应满足：

- 职责单一且清晰
- 采用 Hermes 原生模式（产物金字塔输出、基于技能加载方法论）
- 使用渐进披露：`SKILL.md` 承载触发条件、核心流程、参考文件索引与硬约束；长步骤、示例、兼容性表和操作细节放入 `references/`。判断标准：加载 `SKILL.md` 后应足以决定接下来加载哪个参考文件。
- Hermes 只索引名为 `SKILL.md` 的文件，且 `skill_view` 不支持 `父/子` 技能名——阶段文档不能作为「子技能」按名字加载，必须放入 `references/` 并通过 `file_path` 加载。
- 不依赖 Agent 专用基础设施（如 council、cashew）
- 能在原生 Hermes 安装中工作

## 角色配置设计指南

- 每个角色都应职责清晰，并拥有独特的第一原则
- `SOUL.md` 应说明该角色区别于其他角色的思考方式
- 输出契约采用「结构化交接消息 + 产物金字塔」：状态、摘要、产物路径、证据、风险、待裁决事项
- 在 `SOUL.md` 中交叉引用相关角色，例如“与 `technical-architect` 协作”
- 不得把外部工具或私有基础设施设为前置依赖；原生 Hermes 工具是默认路径
- 不把任何人类责任（业务语义、交付取舍、风险接受）包装为 Profile

## 运行时状态

Profile 目录通过符号链接直接位于仓库内，Hermes 运行时会向其中写入运行时状态
（`state.db`、`logs/`、`skills/.hub/`、`skills/.bundled_manifest` 等，见 `.gitignore`）。

注意一处上游交互：Hermes 用 `rglob("SKILL.md")` 判断 Profile 是否已安装技能，而 `rglob`
不跟随目录符号链接，因此符号链接技能会被误判为「未安装」，从而触发自带技能重新播种。
提交前请运行：

```bash
./scripts/clean_profile_runtime.sh
python3 scripts/validate_profiles.py
```

`profiles/<name>/.no-bundled-skills` 标记必须保留在版本库中，否则全新克隆第一次运行会被播种整套自带技能。

同一根因还会让每次技能加载附带一条非阻断警告
`skill file is outside the trusted skills directory (~/.hermes/skills/)`——符号链接解析后的路径落在
`<repo>/skills/`，不在 Profile 自己的 `skills/` 下。

## 开始贡献

```bash
# Fork 仓库
gh repo fork lovelybowen/hermes-profiles --clone

# 创建角色配置
mkdir -p profiles/your-profile/skills
cp -r profiles/technical-architect/SOUL.md profiles/your-profile/
# ... 编辑 SOUL.md、profile.yaml、README.md、AGENTS.md ...

# 链接共享技能（相对路径，Git 以 120000 模式跟踪）
ln -s ../../../skills/artifact-pyramids profiles/your-profile/skills/

# 校验结构与符号链接（必须通过）
python3 scripts/validate_profiles.py

# 确认 Hermes 实际加载到的技能数与 profile.yaml 一致
hermes -p your-profile skills list

# 提交并创建 PR
git checkout -b feat/your-profile
git add profiles/your-profile
git commit -m "feat: add your-profile"
gh pr create
```

## 许可证

提交贡献即表示你同意按照本项目的 MIT 许可证授权你的贡献。
