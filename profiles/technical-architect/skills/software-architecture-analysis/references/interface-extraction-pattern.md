# 接口提取——实践示例

本参考资料以 [cashew 思维图谱库](https://github.com/rajkripal/cashew)（MIT 许可证）为目标代码库，演示阶段 3b 的接口提取模式。目标是提取隐含的存储契约，设计与提供方无关的 DAO 接口，从而支持可替换的后端（sqlite-vec、KuzuDB、DuckDB+vss 等）。

这是一个教学示例——可推广的是方法论，而不是特定项目。

## 五个步骤

### 第 1 步——理念优先

接触代码前先阅读 `PHILOSOPHY.md`、`DESIGN.md` 和 `README.md`。cashew 仓库的理念揭示了一项关键约束：**“简单图，智能推理层”**——边不携带类型标签，节点类型仅作为给 LLM 的描述性提示，不承担图引擎操作的关键职责。必须将此约束写入契约。`Edge` 数据类没有 `type` 或 `label` 字段。

### 第 2 步——盘点所有存储操作

阅读所有核心模块，并提取每一种不同的数据库操作：

| 模块 | 操作 | 当前实现 |
|--------|-----------|-----------------------|
| db.py | 节点 CRUD、连接管理、schema 迁移 | 轻量 sqlite3 包装器，schema 位于常量中 |
| embeddings.py | KNN 搜索、双写、维度不匹配、新颖性检查 | vec0 快速路径 + numpy O(N) 回退 + 文本 Jaccard 回退 |
| sleep.py | 交叉链接候选项、去重簇、GC、核心提升 | sklearn 成对矩阵、Bron-Kerbosch、通过 SQL 随机采样 |
| retrieval.py | 嵌入搜索 → BFS 遍历 → 混合评分 | vec0 查询 + 递归 CTE + 手动评分 |
| traversal.py | 追踪派生路径、审计 | 递归 CTE、UNION BFS、Python 中的 DFS |
| session.py | 上下文组装、访问跟踪、节点创建 | db.py 原语 + 时间戳更新 |
| graph_utils.py | 为批量操作加载嵌入 | 完整 embeddings 表 → numpy 数组 |

### 第 3 步——识别边界泄漏（变通方案）

四种变通方案表明边界位置有误：

1. **双写向量存储**——每次嵌入都写入两个表（embeddings BLOB + vec_embeddings 虚拟表），并带有维度不匹配检测和三层回退链（vec0 → numpy → Jaccard）。这是 sqlite-vec 不支持原生 HNSW 所带来的代价。

2. **应用内存中的 O(N²) 成对矩阵**——休眠周期将所有嵌入加载到 sklearn 中计算余弦相似度；对于 20 万个 1024 维节点，内存占用约达 160GB。原生 HNSW 提供方会以增量方式完成此操作。

3. **Python 字符串中的递归 CTE**——图遍历通过原始 SQL 递归 CTE 手工实现，而原生图数据库只需一个 `MATCH` 子句即可完成。

4. **将全表加载到 numpy**——交叉链接候选项发现会把整个 embeddings 表加载到内存，而不是执行增量近似查询。

**关键经验：**这些不是缺陷，而是揭示当前架构边界泄漏位置的信号。每一项都适合被推入契约之后。

### 第 4 步——设计契约

生成一个 Python ABC（抽象基类），在 8 个领域中包含约 30 个方法：

- 带有 `initialize()`/`close()` 生命周期的 `StorageProvider` 基类
- 节点 CRUD：`create_node`、`get_node`、`update_node`、`delete_node`、`scan_nodes`、`count_nodes`
- 边 CRUD（简单图——无边类型）：`create_edge`、`get_neighbors`、`delete_incident_edges`、`redirect_edges`
- 向量 KNN：`set_embedding`、`get_embedding`、`find_similar`、`find_similar_by_id`、`scan_embeddings`
- 图遍历：`bfs`、`shortest_path`、`trace_derivation`
- 批处理/维护：`find_cross_link_candidates`、`find_near_duplicates`、`random_sample`、`get_graph_metrics`
- 事务和自省

**关键决策：**
- `find_cross_link_candidates` 返回候选对，但不规定*如何*实现——sqlite-vec 在内部执行 O(N²)，HNSW 提供方则执行增量查询
- `find_near_duplicates`（Bron-Kerbosch 算法）作为业务逻辑保留在应用代码中，而不属于存储层
- `random_sample` 是提供方操作——原生采样远比将全部内容加载到 Python 高效
- 任何位置都没有边的类型/标签字段——在数据模型层强制执行简单图约束

### 第 5 步——双提供方概念验证

设计两个提供方实现来验证契约：

- **提供方 A（sqlite-vec）：**将现有双写、sklearn 矩阵、递归 CTE 和维度不匹配检测封装进契约。所有变通方案都成为*该提供方的内部复杂性*，而不是应用核心的复杂性。

- **提供方 B（KuzuDB）：**第二个实现用于证明契约完整。原生 HNSW 意味着 `set_embedding` 是一次列写入、`find_similar` 是 `QUERY_VECTOR_INDEX`、`shortest_path` 是 `MATCH`。无需回退链——由于底层基础能够处理这些操作，提供方更简单。

两个提供方都通过同一套测试，从而证明该抽象是可靠的。

## 核心要点

1. **理念就是约束。**接触代码前先阅读理念——它会告诉你接口必须尊重什么。

2. **变通方案就是信号。**双写、回退链、全表加载、在 SQL 中手工实现图遍历——每一项都在说明边界从何处泄漏。

3. **针对代码库的*需求*进行设计，而不是针对当前底层的*做法*。**接口代表应用需求，而非当前提供方的能力。

4. **双提供方验证可以发现泄漏。**如果无法针对同一接口实现第二个提供方，说明契约存在缺口。

5. **高成本操作决定性能特征。**`find_similar`、`find_cross_link_candidates` 和 `bfs` 决定系统的快慢。契约必须允许在原生底层上高效实现这些操作。
