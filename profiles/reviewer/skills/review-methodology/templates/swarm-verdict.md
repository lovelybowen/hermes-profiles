# 群体评审结论

> **适用范围：** 本模板仅用于**群体（swarm）模式**的质量门结论，令牌为 `{"gate": "pass" | "block"}`。
> Kanban G1 / G2 模式的 reviewer 结论**不使用** `gate` 令牌：发现阻断缺陷走 `kanban_request_changes` 退回原实现者，交接状态用 `review_status`（映射见 `references/swarm-verification.md`；档位与核验深度见 `references/evidence-level-verification.md`）。

## 结论
**PASS** / **BLOCKED**

## 证据档位

**`evidence_level`：**`L0` / `L1` / `L1+L2` / `Full`
**`seb_integrity`：**`passed` / `failed` / `not_required`
**`sampling`：**[抽样的最高风险项；`L1+L2` / `Full` 必填]
**`confidence`：**`full` / `reduced`
**`uncovered`：**[`confidence: reduced` 时必填且逐条可核对，否则填 `[]`]

> `evidence_level` / `seb_integrity` 的取值与判定以 `skills/artifact-pyramids/references/evidence-levels-and-seb.md` 为唯一权威出处；字段名以 `skills/orchestration-methodology/references/delivery-governance.md` §6 为准。

## 群体
**根任务 ID：**[root-id]
**目标：**[群体目标]

---

## 已评估的工作者输出

| 工作者 | 任务 | 状态 | 质量 |
|--------|------|--------|---------|
| [profile] | [标题] | 完成 | ✅ 通过 / ⚠️ 轻微问题 / ❌ 失败 |

---

## 发现摘要

[工作者总体产出的内容，用 2 至 4 句话概括。]

---

## 注意事项/缺口

[任何局限、开放问题，或综合者需要区别处理的领域。]

---

## 质量门

```
{"gate": "pass/block", "reason": "..."}
```

---

## （如通过）综合者简报

**发现了什么：**[汇总发现]
**缺少什么：**[需要补齐的缺口]
**什么不确定：**[低置信度发现]
**方向：**[基于证据的建议方法]
