---
name: skill-feedback-loop
description: "技能回流协议：角色在任务执行中发现方法论缺陷时，如何把改进建议回传到 hermes-profiles 共享技能池。"
version: 0.1.0
author: lovelybowen
license: MIT
metadata:
  hermes:
    tags: [skill-feedback, methodology-improvement, knowledge-loop]
---

# 技能回流协议

技能池的流向不只是「池 → 副本 → distribution」。角色在**真实任务执行**中发现的方法论缺陷与改进，通过本协议回流到共享池，让本仓库成为团队方法论的活的中枢。

## 触发条件（任一命中即触发）

1. 现有技能规则在当前场景**无法判定**（缺规则）。
2. 技能规则被执行后发现**与实际不符**（规则错）。
3. 发现比现有做法**更优的路径**（可改进）。
4. 同类失败**重复出现 ≥2 次**（系统性缺陷，优先级最高）。

## 回流消息格式（写入当前任务卡 comment）

```yaml
skill_feedback:
  skill: <技能名>            # 如 orchestration-methodology
  file: <文件>               # 如 references/delivery-governance.md §2（可选）
  type: missing | wrong | improvement | systemic
  scenario: <一句话：什么任务、什么场景>
  problem: <规则缺失/错误/次优的具体描述>
  proposal: <建议的规则改动，可直接落地为 PR diff>
  evidence: <任务 id + 交接消息中的相关字段>
```

## 流转路径

```
角色在任务中发现问题
  → 在当前任务卡 comment 写 skill_feedback
  → 任务收尾时 orchestrator 汇总到 Flow 级回流清单（或定期 cron 巡检 board）
  → 人审查（本仓库 maintainer）
  → PR 进共享池 → sync_skills.py 物化 → bump distribution 版本
  → 各端 hermes profile update
```

## 硬约束

- 回流建议**不阻塞当前任务**：先把工作按现行规则完成，再提 feedback。
- `proposal` 必须可直接落地（能变成 PR 的规则文本），不接受纯吐槽。
- 同一反馈不重复提交：先在 board 搜索既有 skill_feedback comment。
- 改动进池前不生效：任务永远按**当前已安装版本**的技能执行。

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `.github/ISSUE_TEMPLATE/skill-feedback.md`（本仓库） | 以 GitHub Issue 形式提交技能回流时 |
