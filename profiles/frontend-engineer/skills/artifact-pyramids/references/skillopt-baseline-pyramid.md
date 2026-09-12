# 实践示例：将 SkillOpt 基线缓存组织为产物金字塔

SkillOpt 的 validate 阶段将产物金字塔用作**机器可读的缓存格式**，而不只是一种研究输出结构。这是一种新的应用方式：金字塔既作为人类可读的摘要，也作为下游流水线阶段的数据源。

## 问题

validate 阶段需要将每项拟议编辑的表现与未编辑技能的基线进行比较。基线必须满足：

1. **可缓存**——在同一轮次重新运行 validate 时，应跳过基线运行
2. **机器可读**——merge 阶段读取逐任务结论以计算差值
3. **人类可读**——检查状态目录的操作人员应能立即理解结果
4. **可移植**——在目录移动后仍然有效，并可独立于生成它的机器运行

单一 JSON 文件满足第 1、2 项，但不满足第 3、4 项。产物金字塔可满足全部四项要求。

## 结构

```
<state_dir>/baseline/epoch-<N>/
├── 00-index.md                  ← 仅导航 + 来源追溯（不含发现）
├── 01-summary/
│   └── findings.md              ← L1：YAML frontmatter 指标 + 摘要
├── 02-analysis/
│   └── per-task-evaluation.md   ← L2：逐任务通过/失败 + 质量 + 原因
├── 03-dossiers/
│   └── task-<id>.json           ← L3：每项任务的原始 oneshot stdout/stderr
└── baseline.json                ← 配套 JSON 快照（向后兼容）
```

## 层级设计决策

### L1 (01-summary/findings.md)

L1 文件使用 **YAML frontmatter** 保存机器可解析的指标，并使用 Markdown 正文供人类阅读：

```yaml
---
epoch: 3
pass_rate: 0.6667
tasks_passed: 2
tasks_failed: 1
total_tasks: 3
avg_quality_score: 0.7667
weighted_score: 0.7234
validation_context: skill_workspace_v1
metric_weights: {"pass_rate": 0.35, "quality_score": 0.35, "speed_score": 0.15, "token_efficiency": 0.15}
target: /path/to/skill/SKILL.md
created_at: 2026-06-03T21:38:05Z
---
```

该 frontmatter 与 `json.loads()` 兼容（无需 yaml 依赖），并包含下游 merge 阶段所需的每项指标。正文提供人类可读的上下文。

### L2 (02-analysis/per-task-evaluation.md)

逐任务明细——每项任务对应一个小节，其中包含状态、质量评分和原因：

```markdown
## Task: validation-task-1
**状态：**PASS | **质量：**0.9
**原因：**正确处理边界情况

## Task: validation-task-2
**状态：**FAIL | **质量：**0.0
**原因：**遗漏所需输出格式
```

### L3 (03-dossiers/task-<id>.json)

原始 oneshot 输出，使用与下游阶段预期数据结构匹配的 `"result"` 键存储：

```json
{
  "task_id": "validation-task-1",
  "stdout": "...",
  "stderr": "",
  "result": {
    "pass": true,
    "quality_score": 0.9,
    "reason": "正确处理边界情况",
    "duration_seconds": 2.345,
    "token_estimate": 485
  }
}
```

## 缓存命中/未命中

| 路径 | 检查 | 操作 |
|------|-------|--------|
| 缓存命中 | `00-index.md` 存在 | 从 L1 frontmatter 读取指标，扫描 L3 档案获取逐任务细节。验证 `validation_context` 字段是否过期。 |
| 缓存未命中 | `00-index.md` 不存在 | 运行基线验证任务，写入完整金字塔结构 |
| 损坏 | L1 frontmatter 无法解析 | 记录错误，进入缓存未命中路径（重新计算） |

## 关键边界规则（来自 output-classification-framework.md）

- **00-index.md** 仅包含导航 + 来源追溯——不含发现、指标或结论语句
- **L1** 回答“我应该做什么？”——包含通过率和加权评分，而非逐任务明细
- **L2** 回答“我为什么应该这样做？”——按任务维度组织的逐任务证据
- **L3** 回答“这是真的吗？”——原样保存的原始 oneshot 输出

## 配套 JSON 快照

在金字塔旁写入 `baseline.json`，供需要访问原始 JSON、但不希望解析 Markdown 的工具使用。这可以确保迁移期间的向后兼容，并使外部脚本无需解析 Markdown 即可使用基线数据。

## 常见陷阱

- **键命名一致性：**L3 档案必须使用 `"result"` 键（而不是 `"verdict"`）保存规范化结论——下游 `baseline_by_task` 字典推导式使用 `detail.get("result", ...)`。不匹配会使缓存命中路径转入启发式回退。
- **SOURCES 中的相对路径：**使用 `02-analysis/per-task-evaluation.md`，而非 `/absolute/path/to/02-analysis/...`——金字塔必须可移植。
- **`state_dir` 顺序：**基线目录路径根据 `state_dir` 计算，必须在使用它之前完成赋值（Python 按顺序执行模块级赋值）。
