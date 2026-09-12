# SkillOpt 流水线集成

SkillOpt 技能（magnus919/hermes-SkillOpt）使用产物金字塔作为所有阶段产物的原生输出格式。这是将金字塔用于**流水线输出**的实践示例——输出并非研究报告，而是供下游流水线阶段使用的结构化评估结果。

## 架构

SkillOpt 各阶段生成每轮档案，这些档案全部进入运行状态目录根部的**单一统一金字塔**。所有原始 JSON 数据都以带轮次前缀的文件名扁平放入 `03-dossiers/`。随着轮次完成，持续**修订**根级文件（`00-index.md`、`01-summary/findings.md`、`02-analysis/`）。

```
<state_dir>/
├── 00-index.md                     ← 每轮修订：轮次列表、导航
├── 01-summary/findings.md          ← 每轮修订：final_epoch、评分
├── 02-analysis/
│   ├── epoch-trajectory.md         ← 每轮修订：追加趋势行
│   └── epoch-1-overview.md         ← 每轮新增：阶段结果 + SOURCES
└── 03-dossiers/                    ← 扁平，无子目录
    ├── epoch-1-baseline.json
    ├── epoch-1-validation-edit-1.json
    └── epoch-2-baseline.json
```

每份轮次概览都由下一个流水线阶段使用——合并阶段从 `03-dossiers/` 读取档案以找到已接受的编辑 ID，然后加载各个结果 JSON 文件。这就是**复合金字塔综合**模式：合并阶段将多个 L3 档案的结果综合为一项决策。

**关键约束：**`03-dossiers/` 只包含扁平文件，不允许使用子目录。应改用带轮次前缀的文件名，例如 `epoch-1-baseline.json`、`epoch-2-validation-edit-3.json` 等。

## 与研究金字塔的关键区别

| 维度 | 研究金字塔 | 流水线金字塔 |
|-----------|-----------------|-----------------|
| 使用者 | 人类或下游 Agent | 自动化流水线阶段 |
| L1 格式 | 自由文本摘要 | YAML frontmatter（机器可解析） |
| L3 schema | 来源摘录、访谈记录 | 使用固定 schema 的结构化 JSON |
| 导航 | SOURCES 链接到分析文件 | SOURCES 按编辑/任务 ID 链接到 L3 |
| 更新模式 | 写入一次，供人类阅读 | 由程序读取，每轮修订并写入根金字塔 |

## 模式：面向机器使用方的 L1 Frontmatter

流水线金字塔在 YAML frontmatter 中存储结构化指标，下游阶段通过 `json.loads()` 解析这些指标：

```yaml
epoch: 2
total_edits: 4
accepted: 3
rejected: 1
accept_rate: 0.75
avg_pass_rate_delta: 0.08
accepted_edits:
  - edit_id: edit-1
    acceptance_reason: weighted_score_non_regression
  - edit_id: edit-2
    acceptance_reason: weighted_score_non_regression
rejected_edits:
  - edit_id: edit-3
    acceptance_reason: pass_rate_regression
```

## 模式：将 L2 分析作为决策支持

L2 文件按条目组织成字段一致的小节——合并阶段读取 L2，以确定应用哪些编辑、跳过哪些编辑：

```markdown
## edit-1 (replace)
- **原因：**weighted_score_non_regression
- **变化：**通过率 +0.33
- **评分变化：**加权评分 +0.2359

SOURCES (LAYER 3 NAVIGATION)
03-dossiers/edit-1.json
 -> edit-1 的原始验证结果
```

## 参考资料

- SkillOpt 仓库：https://github.com/magnus919/hermes-SkillOpt
- 产物金字塔阶段输出跟踪：`skillopt/references/artifact-pyramid-phase-outputs.md`
- 基线缓存：PR #23
- 验证结果：PR #29、issue #24
