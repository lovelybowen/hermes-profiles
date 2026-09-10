# 前端工程师 - Hermes 角色

前端工程师负责实现 UI 组件、状态管理、API 集成、响应式布局和客户端性能优化。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/frontend-engineer ~/.hermes/profiles/
hermes --profile frontend-engineer
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/frontend-engineer/.env.example profiles/frontend-engineer/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/frontend-engineer/SOUL.md` —— 这是权威来源。

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 渐进披露输出格式 |
| `frontend-engineering` | 组件架构、状态管理、API 集成与性能方法论 |

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
