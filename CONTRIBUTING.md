# 为 Hermes 角色配置集贡献

感谢你考虑向本集合添加角色配置。高质量角色配置应符合以下要求。

## 角色配置要求

每个角色配置目录必须包含以下四个文件：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | 身份文档：第一原则、输出契约、方法论要求 |
| `profile.yaml` | 元数据：描述、必需技能、推荐技能 |
| `README.md` | 使用指南：安装、快速开始、技能参考 |
| `AGENTS.md` | Agent 指南：触发模式、加载顺序、交接协议 |

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
- 使用渐进披露：`SKILL.md` 作为精简索引，方法论位于 `references/`
- 不依赖 Agent 专用基础设施（如 council、cashew）
- 能在原生 Hermes 安装中工作

## 角色配置设计指南

- 每个角色都应职责清晰，并拥有独特的第一原则
- `SOUL.md` 应说明该角色区别于其他角色的思考方式
- 输出契约应采用产物金字塔格式（以路径作为交接内容）
- 在 `SOUL.md` 中交叉引用相关角色，例如“与 `technical-architect` 协作”

## 开始贡献

```bash
# Fork 仓库
gh repo fork lovelybowen/hermes-profiles --clone

# 创建角色配置
mkdir -p profiles/your-profile/skills
cp -r profiles/technical-architect/SOUL.md profiles/your-profile/
# ... 编辑 SOUL.md、profile.yaml、README.md、AGENTS.md ...

# 链接共享技能
ln -s ../../../skills/artifact-pyramids profiles/your-profile/skills/

# 提交并创建 PR
git checkout -b feat/your-profile
git add profiles/your-profile
git commit -m "feat: add your-profile"
gh pr create
```

## 许可证

提交贡献即表示你同意按照本项目的 MIT 许可证授权你的贡献。
