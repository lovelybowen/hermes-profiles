# 评审员 - Hermes 角色

代码与架构评审员负责评审 PR、执行质量门、审计回归风险并依据标准开展验证。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/reviewer ~/.hermes/profiles/
hermes --profile reviewer
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/reviewer/.env.example profiles/reviewer/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/reviewer/SOUL.md` —— 这是权威来源。

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 渐进披露输出格式 |
| `review-methodology` | 代码、安全、架构与工作流门禁评审标准 |

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
