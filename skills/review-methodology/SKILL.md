---
name: review-methodology
description: "专业评审方法论 - 代码评审、安全审计、架构评审和看板群体验证。参考资料定义 Google 代码评审标准、OWASP 审计模式和架构评估框架。"
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [review, code-review, security-audit, architecture-review, verification, quality]
    related_skills: [qa-methodology, systematic-debugging, software-architecture-analysis]
---

# 评审方法论

用于代码、安全、架构和 Agent 群输出验证的专业评审标准。

## 评审类型

| 类型 | 参考文件 | 加载时机 |
|------|-----------|-------------|
| **代码评审** | `references/code-review-standards.md` | 评审 PR 或差异：Google 工程实践的 9 个维度及项目专用约定 |
| **安全评审** | `references/security-review.md` | 审计漏洞：威胁建模、漏洞类别、依赖分析、供应链 |
| **架构评审** | `references/architectural-review.md` | 评估设计决策：耦合/内聚、可扩展性、数据流、抽象边界 |
| **群体质量门** | `references/swarm-verification.md` | 评估 Agent 群工作者输出：通过或阻断评审门 |

## 模板

| 模板 | 使用时机 |
|----------|-------------|
| `templates/code-review-response.md` | 编写按严重程度组织发现的 PR 评审 |
| `templates/security-finding.md` | 记录包含复现步骤的安全漏洞 |
| `templates/swarm-verdict.md` | 使用证据通过或阻断评审门 |

## 评审思维

无论类型如何，每次评审都遵循相同过程：

1. **理解意图** - 变更试图实现什么？先阅读描述、Issue 或简报。
2. **评估正确性** - 是否实现了声明的目标？在考虑风格或优雅程度前先回答这个问题。
3. **评估质量** - 构造是否适合其目的？检查复杂度、可维护性和测试覆盖率。
4. **评估风险** - 可能出现什么问题？检查边界情况、安全、回归和运行影响。
5. **沟通** - 清晰说明发现、严重程度和可执行的后续步骤，不针对个人，也不轻视问题。

在理解意图和正确性之前，不要直接讨论质量或风格。针对错误问题的漂亮方案仍然是错误方案。
