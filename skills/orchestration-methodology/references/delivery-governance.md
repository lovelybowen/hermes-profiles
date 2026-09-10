# 交付治理：工作区隔离、质量门与审批矩阵

编排者在分解和路由实现类工作时遵循的治理规则。目标：让并行实现互不干扰，让每道质量门有可验证的输入，让不可逆动作停在人类责任人手里。

## 1. 工作区隔离

| 任务类型 | 工作区 | 完成后 |
|---|---|---|
| 代码实现（后端 / 前端 / 缺陷修复） | 独立 Git worktree，一任务一 worktree | 保留 |
| 代码评审 | 只读被评审的 worktree | — |
| 设计、研究、文档 | 项目约定目录（如 `docs/ai-rnd/<slug>/`） | 保留 |
| 一次性分析 | Kanban `scratch` 工作区 | **删除**（必须显式声明产物） |

规则：

- **禁止两个实现任务共用同一个工作区。** 并行实现必须各自持有 worktree。
- 实现类任务不得直接改动主分支，也不得改动其他任务的工作区。
- Kanban `scratch` 工作区在任务完成时被删除。产物必须先通过 `kanban_complete(artifacts=[...])` 声明，否则视为未交付。
- `dir:<绝对路径>` 与 `worktree` 工作区在完成后保留。

## 2. 分支与提交约定

```
task/<task-id>-<short-slug>
```

- 分支从基线 revision 对应的提交切出。
- 交接证据必须包含 `commit`（完整 SHA）与 `changed_files`。
- `reviewer` 只评审这个 SHA，不评审「当前工作区」。
- 一个实现任务可以多次提交；交接时给出最终 SHA。

## 3. 质量门顺序

```
实现完成
  → qa-engineer 执行验证（自动化测试、lint、构建、契约检查）
      ├─ 已知实现缺陷     → 原实现者
      └─ 未知根因 / 反复失败 → debugger → 原实现者
  → reviewer 对固定 SHA 独立评审
      ├─ 需修改 → kanban_request_changes(reason=...) → 原实现者
      └─ 通过   → 人类批准阶段
```

- QA 与 Reviewer 是两道独立的门，不能合并成一次检查。
- 门禁结论必须是二元的（通过 / 失败），并附原始命令与原始输出。
- `reviewer` 不修复代码；`qa-engineer` 不做最终裁定。
- `debugger` 的修复完成后，受影响的验证必须由 `qa-engineer` 重新执行。

## 4. 审批矩阵

| 操作 | 默认权限 |
|---|---|
| 在任务 worktree 内读 / 写文件 | Agent 可执行 |
| 运行测试、lint、构建、本地脚本 | Agent 可执行 |
| 本地 `commit` 到任务分支 | Agent 可执行 |
| `push` 到远端 | **需要人类批准** |
| 创建 / 更新 PR | Agent 可执行，但必须回传可访问链接 |
| 合并 PR | **需要人类批准** |
| 部署到测试环境 | **按 `Delivery Owner` 策略** |
| 部署到生产 | **需要人类批准** |
| 修改数据库、基础设施、密钥 | **需要 `Risk Approver` 批准** |
| 接受残余风险 / 例外 | **需要 `Risk Approver` 批准** |
| 修改已确认需求基线 | **需要 `Intent Owner` 批准** |

人类责任人不是可调度的 Hermes Profile：`Intent Owner`（业务价值与语义）、`Delivery Owner`（技术范围与交付取舍）、`Risk Approver`（高风险例外与残余风险）。

## 5. 交接消息中的治理字段

```yaml
status: completed | blocked | review_required | needs_decision
evidence:
  commit: <sha>
  changed_files: [...]
  tests: "原始命令 + 结果"
  worktree: <path>
  branch: task/<id>-<slug>
risks: [...]
decisions_required: [...]
```

`decisions_required` 中每一项都要写清：需要谁裁决、裁决什么、不裁决的后果。
