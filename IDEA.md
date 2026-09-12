# IDEA：这个仓库想解决什么问题

## 一句话

一个面向 R&D 团队的 Hermes 角色配置（Profiles）维护源与分发中枢：研发团队被建模为 8 个专属 Profile（架构师、前后端、QA、调试、研究、评审、编排），每个角色精准内置其岗位所需的 `SOUL.md` 运行协议、专项技能和工具链；团队成员按需一条命令安装，秒级获得贴合岗位的 Hermes 开发环境。

## 核心玩法

- **全角色矩阵一键分发**：本仓库（monorepo）是唯一维护源——共享技能池 `skills/` 单一来源，`sync_skills.py` 按 `profile.yaml` 依赖物化副本；`publish.sh`（git subtree split）把每个角色发布为独立 distribution 仓库。新人或跨岗成员 `hermes profile install github.com/lovelybowen/<role>-agent --alias` 即可，`install-all.sh` 一键装齐 9 个角色。
- **多角色环境隔离**：每个角色独立的 SOUL、模型配置、技能集与记忆；product-manager 是需求侧用户入口（接收研发需求并建 intake 卡），orchestrator 是研发流程唯一入口，通过 Hermes Kanban 按名路由任务；default 回归通用助手，不参与研发流程。
- **方法论沉淀在技能，不在提示词**：产物金字塔（渐进披露的证据结构）、结构化交接契约（状态/摘要/产物/证据/风险/待裁决）、证据档位（L0→Full）都封装为可复用技能，随角色分发，也可移植到其他支持 Agent Skills 开放标准的运行环境。

## 设计原则

1. **单一来源，多处分发**：技能只在根 `skills/` 池维护一次，副本脚本生成，CI 校验一致性；禁止 symlink（安装器硬性拒绝）。
2. **一仓库一角色（发布侧）**：monorepo 便于维护，但安装器只认仓库根的 `distribution.yaml`，故每角色一个发布仓库，独立版本与更新。
3. **角色名即路由键**：manifest `name` 必须与目录名一致，安装时不改名——Kanban 编排依赖精确角色名。
4. **人类责任人不可编排**：业务价值、交付取舍、风险接受由 Intent Owner / Delivery Owner / Risk Approver 承担，Profile 只准备证据与选项。
5. **能在原生 Hermes 安装中工作**：不依赖 council、cashew 等 Agent 专用基础设施。

## 后续方向

见 [docs/hermes-profiles-guide.md 第 7 节](docs/hermes-profiles-guide.md) 的路线图：项目接入约定与安装摩擦（AGENTS.md 项目绑定、版本兼容矩阵、跨平台检查）→ 技能回流闭环与证据机器校验（技能回流协议**人工闭环已落地**——payload 校验器 + Issue Form + 版本锁定；board 自动扫描与自动汇总仍属规划；交接 Schema、SEB 完整性自动核验）→ 补齐编排平台能力（workspace 声明式路由、运行中取消、门禁降级）。
