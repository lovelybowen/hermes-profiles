# 思想谱系：软件架构文档中的渐进披露

产物金字塔将渐进披露应用于 AI Agent 的产出。但在过去 30 年中，软件架构文档方法论已分别以不同名称独立发现了这一原则。本参考资料追溯这条思想谱系，并阐明产物金字塔在架构领域已有发现的基础上进一步泛化了什么。

## 六项发现（按时间顺序）

| 年份 | 方法论 | 其对渐进披露的称呼 | 构建内容 |
|------|-------------|--------------------------------------|-----------------|
| 1995 | Kruchten 的 4+1 视图 | “并发视图”“部分表达” | 按利益相关方角色划分信息 |
| 2000 | IEEE 1471 / ISO 42010 | “视点”“利益相关方关注点” | 正式标准：视图是架构的“部分表达” |
| 2002 | Views and Beyond（SEI/Clements） | “视图选择”“范围界定” | 系统化选择应生成哪些视图的流程 |
| 2005 | Rozanski 与 Woods | “视点框架” | 针对受众选择视点 |
| 2008 | arc42 | “裁剪”“精简/基本/详尽” | 三种内置深度模式 + 画布“压缩版” |
| 2011 | ADR（Nygard） | “小型模块化文档” | 原子化决策——逐份阅读，按需串联 |
| 约 2011 | C4 模型（Brown） | “缩放层级”“分层抽象” | 上下文 → 容器 → 组件 → 代码逐层下钻 |

## 关键区别

### 架构领域的版本：基于角色、同步呈现
架构视图模型**按利益相关方角色**划分信息。不同视图同时面向不同的人存在。高管查看上下文视图，开发人员查看组件视图。这是作为*社会协作机制*的渐进披露——同时向不同受众讲述不同故事。

### 产物金字塔：基于角色且具有时间维度
产物金字塔增加了**时间展开**——同一个使用者（无论人类还是 Agent）会随下钻获得更多细节。这是作为*使用机制*的渐进披露——同一个人或 Agent 从摘要开始，按需深入。

架构领域发现了第一条轴，产物金字塔增加了第二条轴。

### 领域范围
架构文档覆盖结构可视化和决策。产物金字塔覆盖完整交付生命周期：战略 → 架构 → 实施 → 运营 → 学习。没有任何架构方法论具有更广的范围。

### 使用者类型
架构文档假定读者是能够翻页、打开文件并决定下一步读什么的*人类*。产物金字塔假定使用者是 *Agent*——这会彻底改变约束：
- 上下文窗口和 token 预算使渐进披露成为**硬性要求**，而不只是便利措施
- Agent 在调用之间没有状态——每个层级都必须可独立使用
- 导航必须显式呈现（带绝对路径的 `SOURCES` 区块），而不能隐式表达（“参见第 4 章”）

## 这意味着什么

架构社区已经验证了该机制有效——30 年的实践、数千个团队，并被记录在 IEEE 标准中。产物金字塔并未重新发现渐进披露，而是：

1. 为架构文档已逐步趋近但未命名的原则**命名**
2. 将其**泛化**到完整生命周期，而不只用于结构视图
3. 将其**扩展**到时间展开，而不只基于角色
4. 将其**应用**于新领域（AI Agent 输出）；在此领域，它是硬性要求，而非优化手段

## 来源

### Vault（永久知识库）

包含来源摘录、9 个支撑原子和逐方法论分析的完整研究位于 Magnus v2 Vault 中：

```
2 - Molecules/Intellectual Lineage of the Artifact Pyramid — Progressive Disclosure in Architecture Documentation.md
 -> 完整综合：9 个原子，覆盖 Kruchten（1995）、IEEE 1471、C4 模型、arc42、ADR、Views and Beyond、Rozanski 与 Woods。包含各规范来源的摘录。
```

### 规范 URL

### Vault（永久知识库）

包含来源摘录、9 个支撑原子和逐方法论分析的完整研究位于 Magnus v2 Vault 中：

```
2 - Molecules/Intellectual Lineage of the Artifact Pyramid — Progressive Disclosure in Architecture Documentation.md
 -> 完整综合，包含覆盖各方法论的 9 个原子、来源摘录和跨领域分析
```

### 规范 URL

- Kruchten (1995): https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- IEEE 1471: https://ieeexplore.ieee.org/document/875998
- ISO 42010: https://www.iso.org/obp/ui/en/#!iso:std:74393:en
- Views and Beyond (Clements et al.): https://www.pearson.com/en-us/subject-catalog/p/documenting-software-architectures-views-and-beyond/P200000000186/9780132488594
- arc42 template: https://docs.arc42.org/
- ADRs (Nygard, 2011): https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- C4 Model: https://c4model.com
- Rozanski & Woods: https://www.viewpoints-and-perspectives.info/
