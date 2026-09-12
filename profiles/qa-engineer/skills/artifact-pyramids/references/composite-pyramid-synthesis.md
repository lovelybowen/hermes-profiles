# 复合金字塔综合

当多个并行子 Agent 分别生成自己的产物金字塔（每个研究维度一个）时，orchestrator 会将它们综合成单一的**复合金字塔**，并按**机会/实体**而非**来源 Agent** 组织。

## 何时使用此模式

任何由两个或更多子 Agent 调查独立维度、且需要将其发现合并为统一视图的并行研究流水线。示例：
- 职位搜索：4 名 researcher（ATS、高管猎寻、聚合站点、公司页面）→ 1 个整合后的机会金字塔
- 竞争分析：市场规模 + 技术可行性 + 竞争格局 → 1 个合并金字塔
- 尽职调查：财务 + 技术 + 法务 + 运营 → 1 个交易金字塔

## 保留子金字塔的问题

每个子 Agent 金字塔都按该 Agent 的发现组织。当下游 orchestrator 或评分 Agent 需要评估例如“Komodo Health”时，它必须：
1. 阅读 R1 的金字塔，查看 Greenhouse 上的职位列表
2. 阅读 R3 的金字塔，确认 Built In 是否也发现了它
3. 在头脑中交叉核对两个来源是否指向同一个机会

这违背了渐进披露的目的。复合金字塔会重新组织数据，使一个 `02-analysis/komodo-health.md` 文件包含所有来源中的全部相关信息。

## 综合协议

### 第 1 步：交叉引用所有候选项

阅读每个子金字塔的 L1 摘要。建立一份主清单，列出以 `company|role` 标识的每个唯一候选项。记录每个候选项由哪些子金字塔发现。

### 第 2 步：构建复合金字塔

```
<project-root>/
├── 00-index.md              ← Entry point with cross-dedup summary
├── 01-summary/
│   └── findings.md          ← L1: merged findings with triage
├── 02-analysis/             ← L2: one file per OPPORTUNITY
│   ├── komodo-health.md
│   ├── picnichealth.md
│   ├── billing-platform.md
│   └── ...
└── 03-dossiers/
    ├── dedup-log.md          ← Cross-result dedup audit trail
    └── sub-pyramids-archive.md  ← What was absorbed and from where
```

与单 Agent 金字塔的关键区别在于：L2 文件以**机会**（公司 + 职位）命名，而不是以**研究维度**命名。下游 Agent 阅读 `02-analysis/komodo-health.md` 即可获取全部信息——无论它是由 R1 还是 R3 发现的。

### 第 3 步：跨结果去重

对每个候选项，检查它是否出现在多个子金字塔中。如果同一 `company|role` 同时由 R1（Greenhouse）和 R4（招聘页面）发现，则合并为一个条目。在 `03-dossiers/dedup-log.md` 中记录此次碰撞：

```markdown
| 公司 | 职位 | 发现者 | 其他发现者 | 结论 |
|---------|------|----------|---------------|---------|
| Veeva Systems | VP Engineering | R3 (Built In) | R4（招聘页面） | 已在去重集合中——无碰撞 |
| Komodo Health | VP AI Engineering | R1 (Greenhouse) | — | R1 独有 |
```

### 第 4 步：移除子金字塔

复合金字塔经验证完整后：
1. 确认所有子金字塔中的全部候选项都已在复合金字塔中体现
2. 删除各个子金字塔目录
3. 更新 `03-dossiers/sub-pyramids-archive.md`，记录移除的内容
4. 修复复合金字塔中所有引用旧子金字塔路径的 `SOURCES` 部分

### 第 5 步：修复 SOURCES 导航

移除后，更新所有指向已删除子金字塔的 `SOURCES` 部分。将 researcher 专用的 `../researcher-1/00-index.md` 引用替换为指向 `03-dossiers/sub-pyramids-archive.md` 的引用。

## 实践示例

参见 2026 年 6 月 1 日的 jobs-finder 会话（`companion-session-summary.md`）。该模式在此会话中形成，并应用于 4 个 researcher 金字塔，最终产出 11 个整合后的机会。
