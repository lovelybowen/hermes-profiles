---
name: skill-feedback-loop
description: "技能回流协议：角色在任务执行中发现方法论缺陷时，如何把改进建议回传到 hermes-profiles 共享技能池。"
version: 0.2.0
author: lovelybowen
license: MIT
metadata:
  hermes:
    tags: [skill-feedback, methodology-improvement, knowledge-loop]
---

# 技能回流协议

技能池的流向不只是「池 → 副本 → distribution」。角色在**真实任务执行**中发现的方法论缺陷与改进，通过本协议回流到共享池，让本仓库成为团队方法论的活的中枢。

## 当前状态（重要）

回流闭环目前是**人工流程**：没有回流扫描器、汇总器或自动 Issue/PR 创建器；「orchestrator 自动汇总到 Flow」和「cron 定期巡检 board」属于规划项（见 `docs/hermes-profiles-guide.md` 第 7 节路线图）。当前实际可用的机器校验只有 payload 格式校验（见下文「校验」）。执行本协议时不要声称任何环节已自动化。

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

字段约束：`skill` 必须是共享池中存在的技能名；`type` 只允许 `missing` / `wrong` / `improvement` / `systemic`；`scenario` / `problem` / `proposal` / `evidence` 均为非空字符串。

## 校验（提交前必做）

payload 写入 comment 或开 Issue 前，先落盘为 YAML 并过格式校验：

```bash
python scripts/validate_skill_feedback.py my-feedback.yaml   # 或 `python3`，见下
```

校验器检查：必需字段与非空、`type` 枚举、`skill` 在共享池中存在、跨文件重复检测（相同 skill + file + problem 视为重复反馈）。校验失败时先修 payload，不要提交。

## 流转路径（当前为人工执行）

```
角色在任务中发现问题
  → 在当前任务卡 comment 写 skill_feedback（先过校验器）
  → 人工归集：任务收尾时由人（或 orchestrator 会话）把 comment 抄录为
    GitHub Issue（模板 .github/ISSUE_TEMPLATE/skill-feedback.yml）或直接 PR
  → 人审查（本仓库 maintainer）
  → PR 进共享池 → sync_skills.py 物化 → bump distribution 版本（受
    scripts/version_lock.json 约束，见 README「版本锁定」）
  → 各端 hermes profile update
```

自动化规划（扫描 board / 汇总 / 自动建 Issue）见 `docs/hermes-profiles-guide.md` 第 7 节；落地前不要在交接或文档中描述为已有能力。

## 硬约束

- 回流建议**不阻塞当前任务**：先把工作按现行规则完成，再提 feedback。
- `proposal` 必须可直接落地（能变成 PR 的规则文本），不接受纯吐槽。
- 同一反馈不重复提交：先在 board 搜索既有 skill_feedback comment；已归集为 Issue 的先搜 `skill-feedback` label。
- 改动进池前不生效：任务永远按**当前已安装版本**的技能执行。

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `.github/ISSUE_TEMPLATE/skill-feedback.yml`（本仓库） | 以 GitHub Issue 形式提交技能回流时（Issue Form，`.yml` 是 GitHub 表单模板的合法扩展名） |
| `scripts/validate_skill_feedback.py`（本仓库） | 提交 feedback payload 前做格式 / 枚举 / 重复校验时 |
