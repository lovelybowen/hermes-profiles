# 嵌套金字塔模式——多产物系统的统一单层级结构

当单个系统生成多条不同的产物流（发布记录、验证结果、提案、基线指标、元反思）时，人们很自然会为每条流创建独立的金字塔目录：

```
❌ 分散——6 个独立金字塔
<state_dir>/
├── baseline/epoch-N/00-index.md
├── validation/epoch-N/00-index.md
├── rollout/epoch-N/00-index.md
├── reflection/epoch-N/00-index.md
├── proposal/epoch-N/00-index.md
├── slow-meta/epoch-N/00-index.md
└── run-summary.json
```

这会迫使使用者检查 6 个入口点才能了解可用内容。每个金字塔都与其他金字塔断开——没有交叉引用，也没有共享导航。

## 统一替代方案

将所有产物流嵌套在单个根金字塔下。每个轮次的数据以带轮次前缀的文件名扁平存放在 `03-dossiers/` 中。随着新轮次完成，**修订**根级文件——它们会不断增长，以反映当前状态。

```
✅ 统一——单个可导航树（扁平 `03-dossiers/`）
<state_dir>/
├── 00-index.md                          ← 每轮修订：导航链接、轮次列表
├── 01-summary/findings.md              ← 每轮修订：更新 final_epoch、评分
├── 02-analysis/
│   ├── epoch-trajectory.md             ← 每轮修订：追加趋势行
│   └── epoch-1-overview.md             ← 每轮新增：阶段摘要 + SOURCES → 档案
└── 03-dossiers/                        ← 扁平：无子目录
    ├── epoch-1-baseline.json
    ├── epoch-1-validation-edit-1.json
    ├── epoch-1-validation-edit-2.json
    ├── epoch-1-rollout-task-train-1.json
    ├── epoch-1-reflection.json
    ├── epoch-1-proposals.json
    ├── epoch-2-baseline.json
    ├── epoch-2-validation-edit-1.json
    └── epoch-2-slowmeta.json
```

### 关键约束：`03-dossiers/` 必须扁平

**`03-dossiers/` 绝不能包含子目录。**产物金字塔规范将档案层定义为范围最广、最扁平的参考资料库。`03-dossiers/` 内的子目录违反规范的扁平文件契约。

使用带轮次前缀的文件名，而不是嵌套目录：

| ❌ 错误（子目录） | ✅ 正确（扁平命名） |
|---|---|
| `03-dossiers/epoch-1/baseline.json` | `03-dossiers/epoch-1-baseline.json` |
| `03-dossiers/epoch-1/rollout/task-1.json` | `03-dossiers/epoch-1-rollout-task-1.json` |
| `03-dossiers/epoch-1/validation/edit-1.json` | `03-dossiers/epoch-1-validation-edit-1.json` |

命名约定：`epoch-<N>-<phase>[-<item>].json`

### 修订模式

根级文件绝不从头重写，而是随着轮次完成进行修订：

| 文件 | 每轮操作 |
|---|---|
| `00-index.md` | 更新轮次列表 + 指向新轮次概览的导航链接 |
| `01-summary/findings.md` | 更新 final_epoch、final_pass_rate、轮次数量 |
| `02-analysis/epoch-trajectory.md` | 向轨迹表追加新行 |
| `02-analysis/epoch-N-overview.md` | 始终新增——绝不修改之前的轮次 |
| `03-dossiers/epoch-N-*.json` | 始终新增——绝不修改之前的轮次文件 |

修订模式意味着，使用者通过阅读 `00-index.md` 即可看到整个运行的当前状态。逐步深入的文件（轮次概览、档案）一经写入便固定不变。

## 导航流

```
00-index.md
  └─ SOURCES → 01-summary/findings.md
                  └─ SOURCES → 02-analysis/epoch-trajectory.md
                  └─ SOURCES → 02-analysis/epoch-1-overview.md
                                  └─ SOURCES → 03-dossiers/epoch-1-baseline.json
                                  └─ SOURCES → 03-dossiers/epoch-1-validation-edit-1.json
```

阅读根 `00-index.md` 的使用者可以沿 `SOURCES` 链接直接进入 `03-dossiers/` 中的扁平档案，从而导航至任意轮次或阶段。无需遍历嵌套的 `00-index`——轮次概览本身就是该轮次的入口点。

## 何时使用

在以下情况下使用嵌套金字塔模式：
- 系统随时间生成 3 种或更多不同的产物类型
- 产物共享一个时间维度（轮次、回合、迭代）
- 使用者需要一眼了解系统的完整输出
- 希望避免并行目录结构导致文件系统膨胀

## 不应使用的情况

- 只生成一项产物的单轮研究任务（使用标准扁平金字塔）
- 产物流由完全独立的子系统所有的系统（改用复合金字塔综合）

## 与复合金字塔综合的关系

复合金字塔模式合并**多个独立 Agent** 的输出（例如，每个子 Agent 都生成自己的金字塔的研究流水线）。嵌套金字塔模式则将**单个系统**的输出组织到一个层级结构中。两者解决不同问题：
- 复合：将独立 Agent 金字塔合并为根级综合
- 嵌套：从头设计单个系统的输出树

## 实现模式

构建嵌套金字塔时，使用共享写入函数；所有阶段在写入各自 L3 档案后都调用该函数：

```python
def rebuild_epoch_pyramid(state_dir, epoch):
    """任何阶段写入 L3 档案后，重新构建轮次级索引、摘要和分析。"""
    epoch_dir = os.path.join(state_dir, "03-dossiers", f"epoch-{epoch}")
    if not os.path.exists(epoch_dir):
        return
    # 扫描现有 L3 档案
    # 从 board-metadata.json 读取 pass_rate_history
    # 写入 00-index.md、01-summary/findings.md 和所有 02-analysis/ 文件
    # 每个 02-analysis 文件都包含链接到其 L3 档案的 SOURCES
```

这会集中管理金字塔写入逻辑，使每个阶段只生成自己的原始数据（L3），再由单一函数处理渐进披露包装。

## 本次会话中的应用

此模式形成于 SkillOpt 产物金字塔转换会话（2026-06-03）。此前使用分散模式（为基线、验证、发布、反思、提案和 slow-meta 设置 6 个并行目录）。统一模式将所有内容整合到 `<state_dir>/` 下，并在 `03-dossiers/epoch-N/` 内按轮次嵌套。
