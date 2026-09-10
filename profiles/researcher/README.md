# R&D 研究员 - Hermes 角色

针对研发工作中的外部事实、技术选型和证据缺口开展调查与三角验证，并产出可追溯的结构化结论。研究结果支持需求基线和技术决策，但不修改已确认的业务语义。

## 安装

```bash
git clone https://github.com/lovelybowen/hermes-profiles.git ~/hermes-profiles
ln -s ~/hermes-profiles/profiles/researcher ~/.hermes/profiles/
hermes --profile researcher
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/researcher/.env.example profiles/researcher/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（触发模式、加载顺序、职责边界、交接契约）见 `profiles/researcher/SOUL.md` —— 这是权威来源。

## 技能依赖

| 技能 | 能力 |
|---|---|
| `artifact-pyramids` | 渐进披露输出格式 |
| `research-methodology` | 证据收集、来源评估、三角验证与核验 |
| `researcher-workflow` | 端到端研究任务工作流与产物生成 |

## 输出格式

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
