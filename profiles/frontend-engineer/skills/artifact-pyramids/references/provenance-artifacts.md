# 来源追溯产物 - 辅助故障转移元数据

产物金字塔不仅适用于研究输出。任何生成具有不同细节深度的尝试链的系统都天然适合使用它。Hermes Agent 中的辅助故障转移系统（PR #32411、Issue #36797）就是完整示例。

## 问题

主提供者失败时，`_FailoverChatCompletions` 包装器会遍历回退链。它记录每次尝试，却只返回一个简略结果；下游使用方若不将时间戳与日志文件关联，就无法知道实际由*哪个*提供者服务该请求。

## 金字塔形态

同一调用链，即在 N 个提供者中进行一次遍历并选出一个成功者，天然具有渐进披露结构：

### 第 1 层 - `served_by`（始终存在）

```
{
  "served_by": "openrouter/gpt-4o-mini",
  "fallback_chain_used": true,
  "fallback_count": 1
}
```

每个辅助响应都携带此字段。只有一个字段，对常规场景没有额外开销。只需了解“谁处理了此请求”的 UI 和下游 Agent 在此停止读取。

### 第 2 层 - 来源追溯链（机器可读、按需选择）

```
{
  "provenance": [
    {
      "provider": "opencode-go",
      "model": "deepseek-v4-flash",
      "status": "failed",
      "failure": "502 Bad Gateway",
      "latency_ms": 3200
    },
    {
      "provider": "openrouter",
      "model": "gpt-4o-mini",
      "status": "success",
      "latency_ms": 890
    }
  ]
}
```

按顺序记录每次尝试的数组。它作为可选响应字段添加，使用方通过请求它来选择加入；不需要它的使用方无需承担 token 成本。需要推理提取质量的下游 RAG Agent 会读取该层。

### 第 3 层 - 完整诊断跟踪（仅调试端点）

```
{
  "trace_id": "aux_comp_172832",
  "attempts": [
    {
      "provider": "opencode-go",
      "model": "deepseek-v4-flash",
      "request": {"messages_len": 4, "estimated_tokens": 24000},
      "error": "APIStatusError: 502 Bad Gateway\nbody: upstream unavailable",
      "started_at": "2026-06-01T12:00:01.234Z",
      "duration_ms": 3200
    },
    {
      "provider": "openrouter",
      "model": "gpt-4o-mini",
      "response": {"choices": [], "usage": {"total_tokens": 485}},
      "started_at": "2026-06-01T12:00:04.500Z",
      "duration_ms": 890
    }
  ]
}
```

包含完整错误载荷、请求上下文和时间水位。通过调试端点或显式请求进行保护，默认不附加到响应中。排查生产事件的操作人员读取该层，其他人无需承担 token 成本。

## 为什么适用

`_FailoverChatCompletions` 包装器在运行时已经拥有三个层级的全部信息：

- **L1：**它知道成功提供者，该信息可直接获取。
- **L2：**它在 `last_error` 变量中跟踪每次尝试的状态和失败原因。
- **L3：**在决定继续或抛出错误前，它捕获完整异常对象。

金字塔是对同一遍历过程的结构化捕获，按使用方所需深度组织。包装器当前仅记录后丢弃，这一结构说明应当捕获什么。

## 相关内容

- Issue #36797 - 将来源追溯作为产物金字塔的功能请求。
- PR #32411 - 添加 `_FailoverAuxiliaryClient` 以及生成这些数据的包装器。
- 参考：通用框架见 `references/artifact-pyramid-framework.md`。
