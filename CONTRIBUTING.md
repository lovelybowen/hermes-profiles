# 为 Hermes 角色配置集贡献

感谢你考虑向本集合添加角色配置。高质量角色配置应符合以下要求。

## 角色配置要求

每个角色配置目录必须包含以下文件：

| 文件 | 用途 |
|---|---|
| `SOUL.md` | **权威运行协议**：第一原则、职责边界、触发模式、加载顺序、输出契约 |
| `config.yaml` | 模型、provider 与工具集；**不得包含任何密钥** |
| `profile.yaml` | 元数据：描述、必需技能、推荐技能（sync_skills.py 据此物化副本） |
| `distribution.yaml` | distribution manifest：name（=目录名）、version、env_requires |
| `README.md` | 使用指南：安装、配置、技能参考 |
| `AGENTS.md` | 指向 `SOUL.md` 的索引 + 该角色的上下游接口 |
| `skills/` | 从共享池物化的真实文件副本（脚本生成，须提交） |

**为什么运行协议只在 `SOUL.md`：** Hermes 把 `$HERMES_HOME/SOUL.md` 注入每个会话，而 `AGENTS.md` 只有工作目录恰为该角色目录时才加载。触发模式与交接协议必须每会话生效，因此放 `SOUL.md`；`AGENTS.md` 只做索引，避免两份协议漂移。

## 技能共享（物化副本）

> 详见下方「技能回流」。技能不只是从池分发到角色——角色在任务中发现的方法论缺陷应通过回流协议回到池里。

角色配置通过根级 `skills/` 目录共享技能（单一来源）。各角色 `skills/` 下的副本由脚本物化为**真实文件**：

```
skills/                          ← 实际技能文件（单份，权威来源）
└── some-skill/
    ├── SKILL.md
    └── references/
profiles/some-profile/skills/    ← 真实副本（脚本生成）
    └── some-skill/SKILL.md ...
```

- **禁止符号链接**：`hermes profile install` 硬性拒绝 symlink payload；Windows 克隆会把 symlink 退化为文本文件。
- 修改共享池的技能后，运行 `python3 scripts/sync_skills.py` 重新物化并连同副本一起提交。
- 如果角色需要共享池中不存在的技能，请先将该技能添加到 `skills/`，再在 `profile.yaml` 的 `skills.required` 中声明，然后跑 sync_skills.py。

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

本仓库只作**分发源**，运行时 profile 由 `hermes profile install` 落盘到 `~/.hermes/profiles/`。
若曾在仓库内的 profile 目录中运行过 Hermes（旧布局），残留的运行时状态
（`state.db`、`logs/`、`skills/.hub/`、`skills/.bundled_manifest` 等）已被 `.gitignore` 排除，
提交前可运行 `./scripts/clean_profile_runtime.sh` 清理。

`profiles/<name>/.no-bundled-skills` 标记必须保留在版本库中并随 distribution 安装，
否则全新安装的 profile 第一次运行会被播种整套自带技能。

## 技能回流（从任务到池）

技能池的流向是双向的。角色在真实任务中发现方法论缺陷时，按 `skills/skill-feedback-loop/SKILL.md` 的协议回流：

1. 任务卡 comment 写 `skill_feedback`（skill / type / scenario / problem / proposal / evidence）。
2. orchestrator 在 Flow 收尾汇总，或由 maintainer 定期巡检 board。
3. 人审查后以 PR 进共享池（或先开 `.github/ISSUE_TEMPLATE/skill-feedback.md` Issue 讨论）。
4. `python3 scripts/sync_skills.py` 物化副本并 bump distribution 版本，各端 `hermes profile update`。

约束：回流不阻塞当前任务；`proposal` 必须可落地为 PR；改动进池前不生效。

## 开始贡献

```bash
# Fork 仓库
gh repo fork lovelybowen/hermes-profiles --clone

# 创建角色配置
mkdir -p profiles/your-profile
cp -r profiles/technical-architect/SOUL.md profiles/your-profile/
# ... 编辑 SOUL.md、profile.yaml、README.md、AGENTS.md ...

# 声明技能依赖后物化副本（真实文件，随 distribution 分发）
#   编辑 profiles/your-profile/profile.yaml → skills.required
python3 scripts/sync_skills.py

# 校验结构、manifest 与副本一致性（必须通过）
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
