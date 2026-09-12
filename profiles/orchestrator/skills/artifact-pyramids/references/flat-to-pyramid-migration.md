# 扁平输出迁移至产物金字塔

将现有扁平文件输出转换为产物金字塔格式时，应遵循此模式。它已应用于基线缓存（SkillOpt PR #23）和验证结果（PR #29），两处复用相同结构。

## 模式

假设已有如下扁平输出目录：

```
outputs/
├── item-1.json            ← 条目级结果
├── item-2.json
└── item-3.json
```

转换为：

```
output-pyramid/epoch-<N>/
├── 00-index.md                    ← 仅导航 + 来源追溯（不含发现）
├── 01-summary/findings.md         ← L1：YAML frontmatter（汇总指标）+ 人类可读摘要
├── 02-analysis/
│   ├── category-a.md              ← L2：每个有意义的条目类别一份文件
│   └── category-b.md              ← L2：每份均包含链接到 L3 的 SOURCES
└── 03-dossiers/
    ├── item-1.json                ← L3：原始 JSON 文件，schema 不变
    ├── item-2.json
    └── item-3.json
```

## 规则

### L1 YAML frontmatter
可通过 `json.loads()` 由机器解析。包含下游使用方需要快速获得的汇总指标（计数、比率、平均值）。不得使用需要递归解析的嵌套对象，只使用扁平键值对和 ID 列表。

### L2 分析文件
每个有意义的条目类别（已接受与已拒绝、成功与失败、按类型）对应一份文件。每份文件：
- 列出该类别中的每个条目，并为每项提供一行摘要
- 以映射到各个 L3 档案的 `## SOURCES (LAYER 3 NAVIGATION)` 部分结尾
- SOURCES 中的路径必须是**相对路径**（例如 `03-dossiers/item-1.json`），以支持可移植性

### L3 档案
保留原始扁平 JSON 文件，schema 不变。应复制而非创建符号链接，使金字塔自包含；通过 `shutil.copy2` 复制以保留元数据。

### 00-index.md
仅包含导航和来源追溯。不包含发现、结论或评分。根据 output-classification-framework 参考资料：“`00-index.md` 仅用于将使用方引导至正确层级的文件。”

## 下游使用方变更

如果下游过程以前读取扁平文件，则增加可识别金字塔的读取路径：

```python
# 先尝试金字塔，再回退到扁平 glob
pyramid_index = os.path.join(state_dir, "output-pyramid", f"epoch-{epoch}", "00-index.md")
if os.path.exists(pyramid_index):
    summary_path = os.path.join(os.path.dirname(pyramid_index), "01-summary", "findings.md")
    meta = json.loads(open(summary_path).read().split("---", 2)[1])
    item_ids = [e["id"] for e in meta.get("items", [])]
    dossier_dir = os.path.join(os.path.dirname(pyramid_index), "03-dossiers")
    result_files = sorted(os.path.join(dossier_dir, f"{eid}.json") for eid in item_ids)
else:
    result_files = sorted(glob.glob(os.path.join(flat_dir, "*.json")))
```

## 使用时机

- 已有由下游过程消费的扁平 JSON 输出
- 条目可自然分类（已接受/已拒绝、通过/失败、按类型）
- 人类或 Agent 需要在不加载每个条目的情况下浏览汇总结果
- 希望在迁移期间保持向后兼容（仍写入扁平文件，金字塔作为增量输出）
