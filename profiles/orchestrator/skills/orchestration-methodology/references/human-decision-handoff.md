# 人类决策交接

当工作流遇到 Agent 无权裁决的业务语义、交付取舍或风险接受问题时，使用本协议生成可追溯的决策包。决策包准备事实和选项；最终决定始终由明确的人类责任人作出。

## 责任路由

| 决策类型 | 人类责任人 |
|---|---|
| 业务价值、优先级、角色、场景、流程或业务规则 | `Intent Owner` |
| 技术范围、实现边界、交付取舍或拓扑选择 | `Delivery Owner` |
| 高风险动作、例外或残余风险 | `Risk Approver` |

## 基线前置条件

决策包必须引用已确认需求基线，而不是复制或改写基线正文。基线引用至少包含稳定标识、URI、revision 或 content hash，并能定位角色、场景、流程、业务规则和验收标准。缺少引用、字段不完整或内容相互冲突时，将 Flow 标记为 `blocked` 并交回 `Intent Owner`。

## 决策包

```yaml
decision_id: <stable-id>
flow_id: <flow-id>
status: pending # pending | approved | rejected | superseded
owner_role: Intent Owner # Intent Owner | Delivery Owner | Risk Approver
baseline:
  artifact_id: <baseline-id>
  uri: <artifact-uri>
  revision: <revision-or-null>
  content_hash: <hash-or-null>
question: <需要裁决的单一问题>
options:
  - id: option-a
    summary: <选项>
    evidence_refs: [<artifact-uri-or-trace-ref>]
    constraints: [<约束>]
    impacts: [<影响>]
    risks: [<风险>]
recommendation:
  option_id: option-a
  rationale: <基于证据的理由>
affected_artifacts: [<artifact-uri-or-trace-ref>]
decision:
  selected_option: null
  decided_by: null
  decided_at: null
  rationale: null
```

`revision` 与 `content_hash` 至少填写一个。选项必须使用相同基线和评价约束，无法核验的判断明确标为未知。

## 推进规则

1. 编排者收集专家产物并生成 `pending` 决策包，完成标准是问题单一、选项可比较、证据可定位、责任人明确。
2. 责任人填写决定后，将状态改为 `approved` 或 `rejected`。没有人类决定时，受影响分支保持 `blocked`。
3. 决定改变业务语义时，由 `Intent Owner` 发布新的需求基线 revision；编排者只更新引用并将受影响的下游工件标记为需要重验。
4. 决定只影响技术实现时，由 `Delivery Owner` 更新对应架构或工作包，再重新执行受影响的 QA 与 Review 门禁。
5. 高风险例外只有在 `Risk Approver` 明确记录接受范围和残余风险后才能继续。

## 完成条件

决策交接只有在状态、责任人、基线引用、选择结果、理由和受影响工件均已记录，并且所有受影响下游门禁已重新排队后才算完成。

## Feishu / Kanban 实现约定

飞书只是决策界面，不能以聊天文本代替持久化决定。决策卡必须绑定以下不可变字段：

```yaml
decision_id: <single-use id>
task_id: <kanban task id>
baseline_revision: <revision>
commit_sha: <sha or null>
requested_action: baseline_approve | push | merge | deploy | risk_accept
allowed_approvers: [<user id>]
expires_at: <timestamp>
```

卡片回调先验证操作者、过期时间、单次使用状态、任务状态、需求 revision 和 commit SHA；任何一项不匹配都拒绝并保持任务 `blocked`。批准结果写入决策记录后，才可解除对应的人工阻断任务。

交付动作必须使用批准记录中的固定 action、repository、branch 和 commit，不接受批准后重新解析的当前工作区。动作完成后必须回读远端状态，将原始命令和结果写入 Kanban，并通知发起该决策的 Feishu 会话。

Hermes 内置的危险命令审批只回答“是否允许执行一条命令”，不能替代本协议的需求、交付和风险审批。
