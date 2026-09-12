<!-- 角色保持项目无关；本文件是项目侧约定，由项目仓库自己维护。 -->
# <项目名> R&D 项目约定

> 本文件由项目仓库维护，orchestrator 建卡时 `workspace_path` 指向本项目 worktree，
> Hermes 按工作目录自动发现并注入给所有在该项目内工作的角色。
> 改本文件 = 改项目约定；改方法论 = 去共享池提 PR（见 hermes-profiles 仓库 CONTRIBUTING）。

## 1. 必填区（orchestrator 建卡前校验，缺失即阻塞 intake）

### 构建与验证命令

| 用途 | 命令 | 备注 |
|---|---|---|
| 安装依赖 | `<例如 npm ci / pip install -e .[dev]>` | |
| Lint | `<命令>` | |
| 单元测试 | `<命令（含超时/重试约定）>` | |
| 构建 | `<命令>` | |
| 其他质量门 | `<契约测试 / E2E / 安全扫描>` | |

### 责任人映射

| 角色 | 人 | 联系方式 / 审批通道 |
|---|---|---|
| Intent Owner | `<名>` | `<TG/Feishu>` |
| Delivery Owner | `<名>` | |
| Risk Approver | `<名>` | |

### 仓库拓扑

- 主仓库：`<url>`
- 关键目录：`<src/ 布局一句话>`
- worktree 约定：`<repo>/.worktrees/<task-id>`，分支 `wt/<task-id>`（默认；覆盖需记录理由）

## 2. 可选区（按项目情况增删）

### Kanban board

- board slug：`<project-slug>`（`hermes kanban boards create <slug>` 后 `set-default-workdir <repo 绝对路径>`）
- 默认证据目录：`<repo>/kanban-evidence/<flow-id>/`

### 部署边界

- 部署方式 / 环境：`<CI 推 main 触发 / 手动>`
- 高风险路径（T5/T6 常发区）：`<路径列表>`
- 密钥与凭据位置：`<vault / .env（永不入卡）>`

### 项目特有约定

- 分支模型、commit 格式、发布节奏
- 历史教训（供 debugger / reviewer 参考）：`<链接或内联>`

## 3. 校验

orchestrator intake 时校验：

1. §1 三张表非空（命令表至少含 lint + 测试；责任人映射三项俱全）。
2. `hermes kanban boards list` 中存在本项目的 board 且 default workdir 指向本仓库。
3. worktree 约定与 §1 声明一致。

校验失败 → 阻塞 intake，把缺失项作为候选 revision 交回 Intent Owner，不猜命令、不代填责任人。
