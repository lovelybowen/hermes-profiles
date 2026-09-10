# 金字塔交接约定：看板、委派与质量门

产物金字塔是**交付物**，交接需要一条能路由、能判断、能验证的**消息**。本文件定义两者如何配合，以及编排、委派、门禁三种场景下的具体做法。

## 1. 交接消息（对所有调用方）

```yaml
status: completed | blocked | review_required | needs_decision
summary: 一到三句话——做了什么、结论是什么、是否达成目标
artifact: <绝对路径>/00-index.md        # 生成金字塔时必填
evidence:
  adrs: [ADR-001, ...]
  views: [system-context, container, ...]
  constraints: [受影响的约束]
  commit: <sha>                          # 涉及代码变更时
risks: [未解决的架构风险]
decisions_required: [需要人类责任人裁决的事项]
```

规则：

1. 持久、可复用、需要跨角色交接的成果 → 必须生成金字塔，并在 `artifact` 给出 `00-index.md` 的绝对路径。
2. 状态、阻断、澄清、审批请求、单轮问答 → 只用上面的消息，不生成金字塔。
3. 路径必须对下游可达。Kanban scratch 工作区在任务完成时会被删除，因此产物必须先被声明。

## 2. Kanban 工作区与产物持久化

| 工作区类型 | 生命周期 | 用法 |
|---|---|---|
| `scratch`（默认） | **任务完成时删除** | 一次性分析；产物必须显式声明 |
| `dir:<绝对路径>` | 保留 | 项目约定目录、共享文档库；路径必须是绝对路径 |
| `worktree` / `worktree:<路径>` | 保留 | 涉及代码仓库的架构工作 |

scratch 工作区下的文件若未声明，等同于未交付。声明方式：

```
kanban_complete(
    summary="<交接消息的 summary>",
    metadata={"changed_files": [...], "adrs": [...], "views": [...]},
    artifacts=["<绝对路径>/00-index.md", "<绝对路径>/.../ADR-001.md"],
)
```

架构任务的 `metadata` 建议形状：

```json
{
  "changed_files": ["docs/ai-rnd/<slug>/00-index.md"],
  "adrs": ["ADR-001", "ADR-002"],
  "views": ["system-context", "container"],
  "superseded_adrs": ["ADR-000"],
  "open_risks": ["..."]
}
```

## 3. 何时用看板、何时用 `delegate_task`

| | `delegate_task` | Kanban |
|---|---|---|
| 形态 | RPC（fork → join），父 Agent 阻塞等待 | 持久任务队列，创建后即返回 |
| 身份 | 匿名子 Agent | 具名 Profile，有自己的记忆与技能 |
| 可恢复 | 不可 | block → unblock → 重跑；崩溃可回收 |
| 人在环 | 不支持 | 任意时刻评论/解除阻塞 |
| 审计 | 上下文压缩后丢失 | SQLite 行永久保留 |
| 跨角色/跨机器 | 否 | 是 |

**判据：** 需要在继续之前拿到一个推理结果，且不涉及其他角色或人类 → `delegate_task`。工作跨角色边界、需要存活重启、可能需要人工输入、或事后要可查 → Kanban。

两者可以共存：一个看板 worker 在自己的运行中调用 `delegate_task` 处理短期子问题。

## 4. 质量门检查清单

金字塔在离开工作者之前逐项自检：

**结构**

- [ ] `00-index.md` 存在，包含导航与 `SOURCES` 部分
- [ ] 每个层级文件都有带说明的 `SOURCES` 绝对路径引用
- [ ] `03-dossiers/` 保持扁平，无子目录
- [ ] 没有创建空的层级目录

**内容**

- [ ] 权衡与备选方案可见，被排除的选项有理由
- [ ] 每条约束都能追溯到引用它的 ADR
- [ ] 只有 `accepted` 的 ADR 被当作权威依据
- [ ] 失败模式被显式描述，不只描述顺利路径

**交接**

- [ ] 交接消息的 `summary` 独立可读，不需要打开文件才能判断
- [ ] `artifact` 指向真实存在的文件（交付前用 `ls` 验证）
- [ ] 产物已按工作区类型正确持久化（scratch → `artifacts=[...]`）
- [ ] `decisions_required` 写明需要谁裁决、裁决什么、不裁决的后果

**门禁决策**

| 情形 | 判定 |
|---|---|
| 结构完整、证据充分、无未决风险 | `completed` |
| 缺输入、依赖未就绪 | `blocked`（`kind=dependency`） |
| 需要他人评审才能推进 | `review_required` |
| 需要人类裁决业务语义或风险 | `needs_decision` |

## 5. 常见反模式

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 只返回 `00-index.md` 路径 | 调用方无法判断任务是否成功 | 交接消息 + `artifact` 路径 |
| 为每次状态更新都建金字塔 | 大量形式主义产物 | 状态用消息，成果用金字塔 |
| 把产物写进 scratch 却不声明 | 任务完成即丢失 | `kanban_complete(artifacts=[...])` |
| 把 `/tmp` 当交付目录 | 重启或清理后失效 | 任务工作区 / 项目约定目录 |
| 把 proposed ADR 当既定事实 | 下游按未定方案实现 | 标记为暂定，或先推动接受 |
