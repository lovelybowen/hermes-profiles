# Profile × Hermes 版本兼容矩阵

本矩阵由 hermes-profiles maintainer 维护，声明每个角色 distribution 已验证的 Hermes 版本区间。
发布新 distribution 版本或升级 Hermes 后，按本矩阵判断哪些角色需要回归测试。

## 矩阵

| Profile | 当前版本 | hermes_requires | 已验证 Hermes 版本 | 备注 |
|---|---|---|---|---|
| orchestrator | 1.3.0 | `>=0.21.0` | 0.21.2 | 依赖 `kanban.orchestrator_profile`、boards、卡片 `--goal`、`--completion-contract`；1.3.0 起 DA 分解审批门（plan_approve 决策 + 审批卡拓扑） |
| researcher | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| technical-architect | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| backend-engineer | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| frontend-engineer | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| qa-engineer | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| debugger | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| reviewer | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖 |
| product-manager | 1.2.0 | `>=0.21.0` | 0.21.2 | 无平台特性依赖；需求侧用户入口 |

## 平台能力 → 最低 Hermes 版本

本文档/SOUL 引用的平台能力，其最低版本如下（声明即约束：引用了就必须保证 floor）：

| 平台能力 | 最低版本 | 使用位置 |
|---|---|---|
| Kanban 基础（任务/依赖边/按名 assignee） | 0.12.0 | 全角色 SOUL（协作语法） |
| `kanban.orchestrator_profile` 配置键 | 0.21.0 | README/AGENTS（入口约定） |
| Kanban boards（`boards create` / `set-default-workdir`） | 0.21.0 | project-context-binding 技能（一项目一 board） |
| Kanban 卡片 `--goal` / `--goal-max-turns` | 0.21.0 | 路线图（低风险卡 Ralph 循环，未强制） |
| `--completion-contract OWNER/REPO` | 0.21.0 | 路线图（PR 完成契约，未强制） |
| `hermes_requires` 语义化版本校验 | 0.12.0 | 全部 distribution.yaml |

## 维护规则

1. **矩阵条目与 distribution.yaml 同步变更**：改 `hermes_requires` 必须同步改矩阵；CI 校验两者一致。
2. **升级 Hermes 后**：先跑 `validate_profiles.py`，再对本矩阵中受影响角色做一次 T2 级冒烟任务，通过后更新「已验证」列。
3. **新平台能力入池**：SOUL/技能引用新平台能力时，在本文件登记最低版本，并把 `hermes_requires` 提到不低于该版本。
4. **floor 只升不降**（在 major 兼容线内）：避免下游已升级的用户被拉回。

## 与发布流程的关系

`scripts/publish.sh` 发布时应对照本矩阵确认 `hermes_requires` 已更新；`scripts/validate_profiles.py --offline` 快速检查矩阵与 manifest 一致性（不解析远端版本）。
