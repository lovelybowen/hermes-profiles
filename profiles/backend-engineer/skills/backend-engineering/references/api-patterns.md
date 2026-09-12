# API 模式

## 端点设计

| 方面 | REST | gRPC | GraphQL |
|--------|------|------|---------|
| 资源建模 | 名词表示资源，动词表示方法 | 带 RPC 方法的服务 | 模式定义的类型与查询 |
| 请求结构 | 路径参数、查询参数、请求头、请求体 | Protobuf 消息 | 带变量的 query/mutation |
| 响应结构 | 带信封的 JSON | Protobuf 消息 | 形状与查询结构匹配 |
| 错误报告 | HTTP 状态码加错误体 | gRPC 状态码加详情 | `errors` 数组中的错误 |
| 版本控制 | URL 路径或请求头 | proto 中的包版本 | 带弃用机制的模式演进 |
| 分页 | 优先游标分页 | proto 参数中的令牌分页 | 连接/边模式（Relay） |

## 版本控制策略

| 策略 | 机制 | 破坏性变更处理 |
|----------|-----------|------------------------|
| URL 路径 | `/v1/resources`、`/v2/resources` | 新建路径，保留旧路径 |
| 请求头 | `Accept: application/vnd.api+json; version=2` | 使用新 Accept 请求头值 |
| 查询参数 | `?version=2` | 使用新参数值，保留旧默认值 |
| 不设版本 | 通过增量变更原地演进 | 仅允许增量变更 |

公开 API 优先使用 URL 路径版本控制，它最直观且歧义最少。

## 分页

| 策略 | 优点 | 缺点 | 最适合场景 |
|----------|------|------|----------|
| 游标分页 | 写入期间稳定，不会发生偏移漂移 | 游标不透明，不能跳到第 N 页 | 实时数据、信息流 |
| 偏移分页 | 简单，可跳转任意页面 | 写入期间可能跳过或重复 | 静态数据集、管理 UI |
| 键集分页 | 快速、稳定 | 需要排序键，多列实现复杂 | 大型数据集、有序数据 |

始终包含分页元数据：`{data: [...], next_cursor: "...", has_more: true}`。

## 错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body is malformed.",
    "details": [
      {"field": "email", "reason": "must be a valid email address"},
      {"field": "age", "reason": "must be a positive integer"}
    ],
    "request_id": "req_abc123"
  }
}
```

每个错误响应都应包含：机器可读代码、人类可读消息、用于追踪的请求 ID，以及用于程序处理的结构化详情。
