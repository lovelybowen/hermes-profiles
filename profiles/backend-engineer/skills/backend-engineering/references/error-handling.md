# 错误处理

## 错误分类

| 类别 | HTTP 对应项 | 含义 | 示例 |
|----------|--------------|---------------|---------|
| 验证 | 400 | 客户端发送了错误内容 | 缺少必填字段 |
| 认证/授权 | 401/403 | 调用方无权执行操作 | 令牌过期、权限不足 |
| 未找到 | 404 | 资源不存在 | ID 无效、实体已删除 |
| 冲突 | 409 | 因状态原因无法完成操作 | 重复、版本已过期 |
| 限流 | 429 | 请求过多 | 超出配额 |
| 内部错误 | 500 | 服务端发生错误 | 数据库不可用、未处理异常 |
| 不可用 | 503 | 服务当前无法处理请求 | 熔断器打开、过载 |

## 异常处理策略

| 捕获位置 | 应做什么 | 示例 |
|---------------|------------|---------|
| Repository | 将数据库错误封装为领域异常 | `UserNotFoundException`、`DuplicateEmailError` |
| Service | 处理领域异常并编排恢复 | 冲突时重试，不可用时回退 |
| Controller 边界 | 将领域异常映射为错误响应 | `UserNotFoundException` → 带错误体的 404 |
| Middleware 边界 | 捕获未处理异常、记录日志并返回 500 | 全局错误处理器、结构化日志和追踪 |

## 结构化日志字段

服务层的每条日志都应包含：

- `request_id` - 来自请求头或由 middleware 生成的关联 ID。
- `service` - 服务名称。
- `operation` - 正在执行的操作。
- `duration_ms` - 耗时。
- `error_code` - 出错时的机器可读代码。
- `caller` - 生成日志的函数或模块。

## 错误响应体

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please retry after the specified time.",
    "retry_after_seconds": 30,
    "request_id": "req_abc123"
  }
}
```
