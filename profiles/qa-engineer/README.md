# QA 工程师 - Hermes 角色

QA 工程师负责测试策略、测试自动化、回归测试和质量门，设计让团队能够持续放心交付的测试方法。

## 安装

```bash
# 方式一：安装独立 distribution 仓库（推荐）
hermes profile install github.com/lovelybowen/qa-engineer-agent --alias

# 方式二：克隆本仓库后一键安装全部 8 角色
git clone https://github.com/lovelybowen/hermes-profiles.git && cd hermes-profiles
./scripts/install-all.sh

# 启动（必须用 manifest 原名安装，不要 --name 改名，否则 Kanban 按名路由断链）
hermes --profile qa-engineer
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/qa-engineer/.env.example profiles/qa-engineer/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/qa-engineer/SOUL.md` —— 这是权威来源。

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 渐进披露输出格式 |
| `qa-methodology` | 测试策略、自动化、回归测试与质量门方法论 |

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
