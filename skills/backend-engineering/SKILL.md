---
name: backend-engineering
description: "后端工程方法论 - API 实现模式（REST、gRPC、GraphQL）、服务架构（整洁/六边形/分层）、数据库访问模式、集成与中间件设计、错误处理和服务级测试。与语言和框架无关。"
version: 1.1.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [backend, api, services, server, database, integration, middleware, query-optimization, testing]
    related_skills: [software-architecture-analysis, qa-methodology, review-methodology]
---

# 后端工程方法论

后端工程负责构建支撑应用的服务端系统，包括 API、服务、数据访问、集成，以及让架构落地的运行时行为。本方法论覆盖架构设计（`technical-architect`）与质量验证（`reviewer`）之间的实现模式。

## 后端工程师的职责边界

| 负责 | 不负责 |
|---------|--------------|
| API 实现：REST/gRPC/GraphQL 端点、请求校验、响应格式化、错误处理、中间件链 | API 契约与服务边界设计，由 `technical-architect` 负责 |
| 服务逻辑：业务规则、工作流编排、状态管理、后台任务处理 | 部署管线与基础设施，需要明确的平台负责人 |
| 数据库访问模式：查询设计、连接管理、事务边界、N+1 检测、分页 | 企业数据建模与迁移治理，需要明确的数据负责人 |
| 集成代码：第三方 API 客户端、Webhook 处理器、消息队列生产者/消费者 | 代码评审与质量门，由 `reviewer` 负责 |
| 服务级可观测性埋点：结构化日志、指标、跟踪钩子 | 可观测性基础设施，需要明确的运维负责人 |
| 服务级测试：业务逻辑单元测试、API 契约集成测试 | 测试策略与自动化，由 `qa-engineer` 负责 |

## 参考文件

| 参考文件 | 加载时机 |
|-----------|-------------|
| `references/api-patterns.md` | 设计或实现 API 端点：资源建模、版本控制、分页、错误响应格式、请求校验 |
| `references/service-patterns.md` | 组织服务逻辑：整洁/六边形/分层架构、依赖注入、中间件组合、请求生命周期、后台任务 |
| `references/database-testing.md` | 数据库访问模式（连接池、查询优化、N+1 检测、分页策略、事务边界、读写分离、复制延迟）和服务级测试（业务逻辑单元测试、使用测试容器/WireMock 的 API 契约集成测试、Pact 契约测试、测试夹具、CI 集成） |
| `references/integration-patterns.md` | 集成外部系统：退避重试、断路器、幂等键、Webhook 验证、消息队列消费者 |
| `references/error-handling.md` | 系统化处理错误：客户端/服务端分类、结构化响应、异常处理模式、可观测性关联 |

## 核心原则

**接口就是契约** - API 边界是服务级契约。每个端点签名、请求模式、响应格式和错误码都是对使用方的承诺。破坏性变更是协调问题，不只是版本号变更。

**业务逻辑是重心** - 将业务规则与框架问题、传输协议和基础设施细节隔离。结构良好的服务能够承受 HTTP 库、数据库驱动和部署平台的变化。

**在合适的位置处理错误** - 在拥有足够上下文、能够作出有意义处理的边界捕获错误。捕获过早会丢失上下文，捕获过晚则无法恢复。

**既为成功设计，也为失败设计** - 每次外部调用都可能失败，每个数据库连接都可能中断，每条消息都可能重复。幂等、重试和优雅降级不是优化项，而是必要条件。

**在正确的层级测试** - 业务逻辑使用单元测试，API 契约使用集成测试，服务边界使用契约测试。每个层级捕获不同类型的故障。
