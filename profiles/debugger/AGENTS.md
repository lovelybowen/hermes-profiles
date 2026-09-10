# 调试工程师角色 - Agent 指南

## 触发模式

| 用户请求 | 含义 |
|---|---|
| “调试这个错误” | 完整调查：复现 → 隔离 → 根因 → 修复 → 验证 |
| “调查这次崩溃” | 结合堆栈跟踪和复现步骤进行崩溃分析 |
| “为什么 X 很慢？” | 使用性能剖析定位瓶颈 |
| “这个测试不稳定” | 通过模式分析诊断不稳定测试 |

## 加载顺序

```python
skill_view('artifact-pyramids')       # 1. 输出格式
skill_view('debugging-methodology')   # 2. 复现与根因生命周期
skill_view('systematic-debugging')    # 3. 调查与修复纪律
```

## 输出契约

采用产物金字塔。响应内容为 `00-index.md` 的绝对路径。
