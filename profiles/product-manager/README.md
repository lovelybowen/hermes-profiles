# 产品经理 - Hermes 角色

面向 Hermes Agent 的产品管理专精角色。撰写 spec、管理路线图、对齐团队，把客户需求翻译为可排序的交付物。

## 本角色提供什么

- **Spec 撰写** —— 工程师、设计师和干系人都能据以工作的结构化需求文档
- **优先级排序** —— RICE 评分、MoSCoW、机会解决方案树，用于权衡决策
- **干系人沟通** —— 面向工程师、设计师、高管和客户的适配化消息
- **客户发现** —— 访谈指南、问题验证、基于成果的需求
- **决策日志** —— 追踪权衡、理由与预期结果的轻量格式

## 安装

```bash
# 方式一：安装独立 distribution 仓库（推荐）
hermes profile install github.com/lovelybowen/product-manager-agent --alias

# 方式二：克隆本仓库后一键安装全部 9 角色
git clone https://github.com/lovelybowen/hermes-profiles.git && cd hermes-profiles
./scripts/install-all.sh

# 启动（必须用 manifest 原名安装，不要 --name 改名，否则 Kanban 按名路由断链）
hermes --profile product-manager
```

### 配置

`config.yaml` 提供模型与工具集配置（`hermes-cli`）。API key 放在 `.env`，该文件已被 `.gitignore` 排除，不会进入版本库：

```bash
cp profiles/product-manager/.env.example profiles/product-manager/.env
# 编辑该文件，填入 DEEPSEEK_API_KEY
```

运行协议（第一原则、沟通风格、输出契约）见 `profiles/product-manager/SOUL.md` —— 这是权威来源。

## 快速开始

角色加载后，给它一个产品提示：

> 「为通知偏好界面写一份 spec。用户想控制收到哪些通知、以及通过什么渠道接收（邮件、推送、应用内）。」

角色将：

1. 界定问题与用户细分
2. 产出用户故事与验收标准
3. 用合适的框架圈定优先级范围
4. 记录开放问题与权衡
5. 在 `/tmp/pm-workflow/<project>/00-index.md` 输出一个产物金字塔

## 技能依赖

| 技能 | 能力 | 加载命令 |
|---|---|---|
| `artifact-pyramids` | 三层渐进披露输出格式 | `skill_view('artifact-pyramids')` |
| `product-methodology` | RICE、MoSCoW、机会解决方案树、spec 模板、客户访谈、干系人沟通、决策日志 | `skill_view('product-methodology')` |
| `skill-feedback-loop` | 技能回流协议（条件加载：任务中发现方法论缺陷时） | `skill_view('skill-feedback-loop')` |
| `kanban-exception-watchdog` | 异常终态兜底巡检（部署用：no-agent cron 注册与脚本说明） | `skill_view('kanban-exception-watchdog')` |

### 支撑参考

| 参考 | 加载命令 |
|---|---|
| RICE 优先级 | `skill_view('product-methodology', 'references/rice-framework.md')` |
| MoSCoW 优先级 | `skill_view('product-methodology', 'references/moscow-prioritization.md')` |
| 机会解决方案树 | `skill_view('product-methodology', 'references/opportunity-solution-trees.md')` |
| 客户访谈指南 | `skill_view('product-methodology', 'references/customer-interview-guide.md')` |
| Spec 模板 | `skill_view('product-methodology', 'references/spec-template.md')` |
| 干系人沟通 | `skill_view('product-methodology', 'references/stakeholder-communication.md')` |
| 决策日志 | `skill_view('product-methodology', 'references/decision-log.md')` |
| 产物金字塔映射 | `skill_view('product-methodology', 'references/artifact-pyramid-mapping.md')` |

## 输出格式

所有输出遵循产物金字塔约定。对任何调用方的响应是 `00-index.md` 的绝对路径。

## 验证

- [ ] 接受产品提示并产出产物金字塔
- [ ] 金字塔包含问题定义、用户故事、优先级和成功标准
- [ ] 响应是 `00-index.md` 的绝对路径，不是摘要
- [ ] 每个方法论参考可通过 skill_view() 独立加载
