---
name: skill-feedback
description: "技能回流：把任务执行中发现的方法论缺陷/改进建议回传到共享技能池"
labels: ["skill-feedback"]
body:
  - type: markdown
    attributes:
      value: |
        感谢回流方法论改进！先搜索既有 issue 避免重复。
        触发条件与完整协议见 `skills/skill-feedback-loop/SKILL.md`。
  - type: input
    id: skill
    attributes:
      label: 涉及技能
      description: 如 orchestration-methodology、artifact-pyramids
    validations:
      required: true
  - type: dropdown
    id: type
    attributes:
      label: 反馈类型
      options:
        - missing（规则缺失，无法判定）
        - wrong（规则与实际不符）
        - improvement（存在更优路径）
        - systemic（同类失败重复 ≥2 次）
    validations:
      required: true
  - type: textarea
    id: scenario
    attributes:
      label: 触发场景
      description: 什么任务、什么场景下发现（任务 id / 项目 / Flow）
    validations:
      required: true
  - type: textarea
    id: problem
    attributes:
      label: 问题描述
      description: 规则缺失/错误/次优的具体描述
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: 建议改动
      description: 可直接落地为 PR 的规则文本（不接受纯吐槽）
    validations:
      required: true
  - type: textarea
    id: evidence
    attributes:
      label: 证据
      description: 任务 id、交接消息字段、失败记录
    validations:
      required: true
