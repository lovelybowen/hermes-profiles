# 后端工程方法论参考

> 数据库访问模式与服务级测试——面向后端工程团队的综合参考资料。
> 编制日期：2026-06-05

---

## 目录

1. [连接池配置与规模估算](#1-连接池配置与规模估算)
2. [查询优化——索引使用、查询计划与 EXPLAIN](#2-查询优化索引使用查询计划与-explain)
3. [N+1 检测与缓解](#3-n1-检测与缓解)
4. [分页策略——游标、偏移量与键集](#4-分页策略游标偏移量与键集)
5. [事务边界设计](#5-事务边界设计)
6. [读写分离](#6-读写分离)
7. [复制延迟处理](#7-复制延迟处理)
8. [服务级测试概览](#8-服务级测试概览)
9. [业务逻辑单元测试](#9-业务逻辑单元测试)
10. [集成测试——API 契约、Testcontainers 与 WireMock](#10-集成测试api-契约testcontainers-与-wiremock)
11. [契约测试——Pact](#11-契约测试pact)
12. [测试夹具](#12-测试夹具)
13. [CI 集成](#13-ci-集成)

---

## 1. 连接池配置与规模估算

### 问题

为每个请求创建一个新的 TCP 连接无法扩展。在每秒请求数超过 10K 时，数据库会不堪重负。PostgreSQL 默认允许 100 个并发连接；超过这一数量会产生“sorry, too many clients already”错误。每次建立新连接还会增加 20-50 毫秒延迟。

### 解决方案

连接池会在应用启动时预先建立一组固定连接。线程从池中借用连接、执行查询，然后将连接归还池中。

```
┌──────────────┐      借用      ┌──────────────────┐
│   应用线程   │ ─────────────→ │      连接池      │
│   （请求）   │                │                  │
│              │ ←───────────── │  (HikariCP/      │
│              │      归还      │   pgBouncer)     │
└──────────────┘                └────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │     数据库服务器    │
                              │  (PostgreSQL/MySQL)│
                              └───────────────────┘
```

### 连接池规模估算公式

最常被引用的经验法则是：**连接池大小 = 2 ×（CPU 核心数）**。

不过，正确的做法应以实测为依据：

1. **从小规模开始**——对大多数服务先配置 20-30 个连接。
2. 使用真实流量模式**运行负载测试**。监控数据库 CPU、内存、连接等待时间和查询延迟。
3. 在测得的峰值用量之上**增加 15%-20% 的余量**。
4. 针对不同的工作负载模式**考虑使用多个连接池**（例如，管理查询使用小型池，面向用户的流量使用较大型池）。

### 关键配置参数

| 参数 | 说明 | 常用默认值 |
|-----------|-------------|---------------|
| `maximumPoolSize` | 池中的最大连接数 | 10-30 |
| `minimumIdle` | 要维持的最小空闲连接数 | 与 maxPoolSize 相同 |
| `connectionTimeout` | 等待连接的最长时间（毫秒） | 30000 |
| `idleTimeout` | 连接保持空闲的最长时间（毫秒） | 600000（10 分钟） |
| `maxLifetime` | 连接在池中的最长生命周期（毫秒） | 1800000（30 分钟） |

### 推荐库

| 语言 | 库 | 说明 |
|----------|---------|-------|
| Java/Kotlin | **HikariCP** | 行业标准——速度最快、最轻量 |
| Python | **psycopg2.pool / SQLAlchemy pool** | 内置；调优 pool_size 和 max_overflow |
| Node.js | **pg-pool** | node-postgres 的默认连接池 |
| Go | **pgxpool** (/jackc/pgx) | 高性能 Postgres 驱动 |
| Ruby | **connection_pool** | ActiveRecord 内部使用 |
| Rust | **deadpool-postgres** | 面向 tokio-postgres 的异步池 |
| .NET | **Npgsql pooling（内置）** | 默认启用连接池 |

### 基于代理的连接池（pgBouncer / PgCat）

对于微服务或无服务器场景，应使用数据库代理而不是应用级连接池：

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
pool_mode = transaction    # 事务级连接池
max_client_conn = 100
default_pool_size = 20
```

- **事务池化**——每个事务结束后将连接归还池中（最常见）。
- **会话池化**——整个会话期间一直持有连接（适用于预备语句）。
- **语句池化**——每条语句执行后归还连接（最少见）。

### 无服务器场景注意事项

无服务器函数生命周期较短，无法维持持久连接池。请采用基于代理的解决方案：

- **AWS RDS Proxy**（托管服务，IAM 认证）
- **Cloudflare Hyperdrive**
- **Supabase Supavisor**
- **PgCat**（开源代理）

---

## 2. 查询优化——索引使用、查询计划与 EXPLAIN

### 索引类型（以 PostgreSQL 为主）

| 索引类型 | 最适合 | 注意事项 |
|------------|----------|---------------|
| **B-Tree**（默认） | 等值与范围查询、ORDER BY、外键 | 通用型；适用于大多数场景 |
| **Hash** | 仅等值查找 | 单列；旧版本中不记录 WAL |
| **GIN**（广义倒排索引） | 全文搜索、数组、JSONB 包含查询 | 比 B-tree 更大；构建更慢 |
| **GiST**（广义搜索树） | 几何数据、全文搜索（排序） | 有损；支持最近邻查询 |
| **BRIN**（块范围索引） | 数据自然有序的超大表（时间序列、日志） | 极其紧凑；仅适合具有相关性的数据 |
| **SP-GiST** | 空间分区数据（地图、网络树） | 用途专门；适合聚集数据 |
| **覆盖索引**（`INCLUDE` 列） | 仅索引扫描 | 添加载荷列而不影响键的排序顺序 |

### 复合索引指南

- **顺序很重要**：等值条件列在前，然后是范围/ORDER BY 列。
- **最左前缀规则**：查询必须使用索引中最左侧的列，才能从该索引获益。
- 示例：`CREATE INDEX idx_users_org_status ON users (organization_id, status, created_at);`
  - 有助于 `WHERE org_id = ? AND status = ? ORDER BY created_at`
  - 对单独的 `WHERE status = ?` **没有**帮助。

### EXPLAIN 基础

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM orders WHERE user_id = 42;
```

**关键计划节点类型：**

| 节点 | 含义 |
|------|---------|
| **Seq Scan** | 全表扫描——在大表上代价高昂 |
| **Index Scan** | 索引查找 + 堆表获取 |
| **Index Only Scan** | 所需列全部位于索引本身（最快） |
| **Bitmap Heap Scan** | 将多个索引匹配结果合并为位图 |
| **Nested Loop** | 对外部的每一行扫描内部（适合小型连接） |
| **Hash Join** | 在一侧构建哈希表，用另一侧进行探测 |
| **Merge Join** | 对两侧排序后合并（适合大型有序集合） |

### 查询计划中的检查要点

1. **大表上的顺序扫描**——缺少索引。
2. **`rows` 与 `actual rows` 差异很大**——规划器中的统计信息已过时；运行 `ANALYZE`。
3. **占用大量内存的 `Sort` 节点**——考虑预排序索引或增大 `work_mem`。
4. **连接大型行集合的 `Nested Loop`**——可能需要其他连接策略。
5. **包含许多行版本的 `Bitmap Heap Scan`**——可能需要执行 vacuum。
6. **索引扫描后的 `Filter`**——索引缺少 WHERE 中使用的列。

### 索引维护

```sql
-- 检查索引使用情况
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- 未使用的索引（可考虑删除）

-- 重建膨胀的索引
REINDEX INDEX CONCURRENTLY idx_name;   -- 在 PG 12+ 中不会阻塞
```

### 常见反模式

- 单独为低基数列（例如布尔列）建立索引——选择性不足。
- 过度建立索引——每个索引都会增加写入开销（降低 INSERT/UPDATE/DELETE 速度）。
- 常见查询模式缺少复合索引。
- `SELECT *` 获取索引未覆盖的列，导致必须查找堆表。
- 在索引列上调用函数（`WHERE LOWER(email) = 'x'`），除非使用函数索引。

---

## 3. N+1 检测与缓解

### 什么是 N+1？

当应用先发出 1 次查询获取 N 行父级记录，随后又为每条父级记录各发出 1 次查询以获取关联数据时，就会出现 N+1 查询问题——总计执行 N+1 次查询，而不是一次高效查询。

### 示例（ORM 层伪代码）

```python
# N+1：1 次用户查询 + N 次订单查询
users = User.query.all()              # 1 次查询 → 100 个用户
for user in users:
    orders = user.orders               # 100 次查询！
    ...
```

```sql
-- 生成的查询：
SELECT * FROM users;                                       -- 1
SELECT * FROM orders WHERE user_id = 1;                    -- 2
SELECT * FROM orders WHERE user_id = 2;                    -- ...
SELECT * FROM orders WHERE user_id = 100;                  -- 101
```

### 检测技术

1. **ORM 查询日志**——启用 SQL 日志并观察重复出现的相似查询。
2. **APM 工具**——Scout、New Relic、Datadog 会自动突出显示 N+1 模式。
3. **手动 EXPLAIN**——检测短时间窗口内大量相同的查询。
4. **静态分析**——Rails 的 `bullet` gem、Django 的 `nplusone`、Java 的 `jpa-nplusone`。
5. **数据库端分析**——通过 `pg_stat_statements` 发现调用次数很高的语句。

### 缓解策略

| 策略 | ORM | 方式 |
|----------|-----|-----|
| **预加载（JOIN）** | Django `select_related` / Rails `includes` / Hibernate `JOIN FETCH` | 使用 JOIN 的单次查询 |
| **批量加载** | Django `prefetch_related` / Rails `preload` / Hibernate `@BatchSize` | 每张表单独查询，通过 `WHERE IN` 批量获取 |
| **GraphQL DataLoader** | 任意 GraphQL 技术栈 | 按请求批处理并去重 |
| **延迟 + 批量** | ORM 中常见 | 延迟到访问时才执行，然后批量加载 |

```python
# 使用预加载修复（Django）
users = User.objects.select_related('profile').prefetch_related('orders').all()

# 使用 DataLoader 修复（GraphQL）
from promise import Promise
from promise.dataloader import DataLoader

class OrderLoader(DataLoader):
    def batch_load_fn(self, user_ids):
        orders = Order.objects.filter(user_id__in=user_ids)
        return Promise.resolve([list(orders.filter(user_id=uid)) for uid in user_ids])
```

### 可以接受 N+1 的情形

- N 很小且固定（例如关联项少于 10 个）。
- 对延迟不敏感的管理面板或报表。
- 缓存未命中量很低的缓存结果。

---

## 4. 分页策略——游标、偏移量与键集

### Offset/Limit（最常见、可扩展性最低）

```sql
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 0;
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 20;
```

**优点：**
- 实现简单。
- 支持跳转到任意页（第 1 页、第 5 页、第 100 页）。
- 对开发人员而言直观易懂。

**缺点：**
- **性能随页码加深而下降**——OFFSET 100000 必须扫描并跳过 10 万行。
- **幻读/行缺失**——如果两次请求之间插入或删除了行，条目可能出现在多个页面中，也可能被完全跳过。
- **在写入负载下不一致**——数据移动时，`OFFSET` 的含义也随之变化。

### 基于游标的分页（可扩展性最高、API 优先）

```sql
-- 第一页：无游标
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;

-- 下一页：使用最后一个条目的游标值
SELECT * FROM orders
WHERE created_at < '2026-06-04T12:00:00Z'  -- 游标值
ORDER BY created_at DESC LIMIT 20;
```

```json
// API 响应结构
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNDUsImNyZWF0ZWRfYXQiOiIyMDI2LTA2LTA0VDEyOjAwOjAwWiJ9",
    "has_more": true
  }
}
```

**优点：**
- **任何深度下均为 O(1) 性能**——使用索引查找，而不是扫描并跳过。
- **一致**——不会出现幻读或漏行；游标标记固定位置。
- **能够承受写入负载**——插入或删除不会移动游标位置。

**缺点：**
- 无法任意跳页（只能前一页/后一页）。
- 需要唯一且可排序的列（通常是 ID 或时间戳）。
- 存在游标编码/解码开销（base64、不透明令牌）。

### 键集分页（查找法）

```sql
-- 在 (created_at, id) 上进行复合分页
SELECT * FROM orders
WHERE (created_at, id) < ('2026-06-04T12:00:00Z', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

- 使用 `(created_at, id)` 上的复合索引。
- 性能与基于游标的方式相近——在元组上进行索引查找。
- 需要复合比较和多列索引。

### 对比表

| 方面 | Offset/Limit | 游标 | 键集 |
|--------|-------------|--------|--------|
| **深分页性能** | O(n)——下降 | O(1)——恒定 | O(1)——恒定 |
| **随机访问页面** | 是 | 否 | 否 |
| **幻读** | 有 | 无 | 无 |
| **一致性** | 不稳定 | 稳定 | 稳定 |
| **实现复杂度** | 极低 | 中 | 低至中 |
| **需要可排序的唯一列** | 否 | 是 | 是 |
| **感知写入** | 否 | 是 | 是 |

### 建议

| 使用场景 | 策略 |
|----------|----------|
| **管理面板、小型数据集** | Offset/Limit（少于 1 万行时足够） |
| **公共 API、无限滚动** | 游标（REST/GraphQL 最佳实践） |
| **时间序列、日志、审计轨迹** | 在时间戳 + ID 上使用游标或键集 |
| **使用数据库分页的内部工具** | 键集（复杂度最低，无需游标编码） |

---

## 5. 事务边界设计

### ACID 属性

| 属性 | 含义 |
|----------|---------|
| **原子性（Atomicity）** | 全有或全无——事务要么完全完成，要么不产生任何影响 |
| **一致性（Consistency）** | 事务使数据库保持有效状态（约束得到保留） |
| **隔离性（Isolation）** | 并发事务不会相互干扰 |
| **持久性（Durability）** | 已提交的更改在故障后仍然保留 |

### 隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 | 序列化异常 |
|-------|-----------|--------------------|-------------|---------------------|
| **Read Uncommitted** | 可能 | 可能 | 可能 | 可能 |
| **Read Committed**（PostgreSQL、SQL Server、Oracle 的默认值） | 安全 | 可能 | 可能 | 可能 |
| **Repeatable Read** | 安全 | 安全 | 可能（PG：安全） | 可能 |
| **Serializable** | 安全 | 安全 | 安全 | 安全 |

**PostgreSQL 特性：**
- 默认为 **Read Committed**。
- Repeatable Read 也会防止幻读（使用快照隔离）。
- Serializable 使用可序列化快照隔离（SSI）——检测序列化冲突并中止事务。

### 选择隔离级别

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- 或者为会话设置：
SET default_transaction_isolation = 'repeatable read';
```

| 级别 | 使用时机 |
|-------|------------|
| **Read Committed** | 适用于大多数工作负载的默认选择。在一致性与性能之间取得良好平衡。 |
| **Repeatable Read** | 财务计算、报表——需要一致快照时使用。 |
| **Serializable** | 关键数据完整性场景（账本、库存分配）。中止率较高。 |

### 事务重试模式

**乐观重试（用于 Serializable / Repeatable Read 冲突）：**

```
RETRY_COUNT = 0
MAX_RETRIES = 3
BACKOFF = [50ms, 150ms, 500ms]

WHILE RETRY_COUNT <= MAX_RETRIES:
    BEGIN TRANSACTION
    TRY:
        -- 业务逻辑
        COMMIT
        BREAK
    CATCH serialization_failure:
        ROLLBACK
        SLEEP(BACKOFF[RETRY_COUNT])
        RETRY_COUNT += 1
    CATCH deadlock:
        ROLLBACK
        SLEEP(random 0-100ms)
        RETRY_COUNT += 1

IF RETRY_COUNT > MAX_RETRIES:
    RAISE "重试后事务仍然失败"
```

**最佳实践：**
- 使用带抖动的**指数退避**，避免惊群效应。
- 保持事务**简短**——尽量缩短锁持有时间。
- **先读后写**——在事务内部尽早发现冲突。
- 对实体级并发尽可能使用**乐观锁**（版本列），而不是悲观锁。

### 分布式事务

| 模式 | 说明 | 使用时机 |
|---------|-------------|------------|
| **两阶段提交（2PC）** | 协调器先让所有参与者做好准备，然后提交 | 仅限单一数据库系统内部 |
| **Saga（编舞）** | 每个服务发布事件；通过补偿操作回滚 | 微服务、异步边界 |
| **Saga（编排）** | 中央编排器发送命令并处理补偿 | 复杂的多服务工作流 |
| **发件箱模式（Outbox Pattern）** | 在同一数据库事务中将事件写入发件箱表，再异步发布 | 需要恰好一次保证的事件驱动架构 |
| **幂等键** | 每次操作使用唯一键来防止重复处理 | 支付处理、任何外部 API 调用 |

### 事务反模式

- 持有锁的**长时间运行事务**——拆分成更小的单元。
- 跨服务边界的**嵌套事务**——改用 Saga。
- **在循环内开启事务**——将工作批量合并到单个事务中。
- **在事务内混入大量 I/O**——外部 API 调用应在事务之前或之后进行。
- 对序列化失败**不处理重试**——每个 Serializable 工作负载都需要重试逻辑。

---

## 6. 读写分离

### 架构

```
                    ┌─────────────────┐
                    │       应用       │
                    │  （ORM / 客户端） │
                    └────┬────────┬───┘
                         │        │
                     写入       读取
                         │        │
                    ┌────▼──┐ ┌──▼────┐
                    │  主库 │ │ 副本  │ ──→（更多副本）
                    │（写） │ │（读） │
                    └───────┘ └───────┘
                        │          ↑
                        │  异步    │
                        │  复制    │
                        └──────────┘
```

### 实现方式

| 方式 | 机制 | 优点 | 缺点 |
|----------|-----------|------|------|
| **ORM 层**（`read_from=replica`） | 在 ORM 中配置（Django `DATABASES`、Rails `config`） | 简单；无需更改基础设施 | 每个服务都必须手动配置 |
| **数据库代理**（ProxySQL、PgBouncer、PgCat） | 根据查询类型路由 | 集中管理；无需更改应用 | 增加一次跳转；代理成为单点故障（SPOF） |
| **中间件**（例如 Spring `@Transactional(readOnly=true)`） | 注解驱动的路由 | 细粒度控制；声明式 | 特定于框架 |
| **客户端侧**（多数据库驱动配置） | 每种角色使用一个连接字符串 | 基础设施最少 | 需要在部署时配置 |

### 查询路由规则

```
写入 → 主库：
  - INSERT, UPDATE, DELETE, MERGE
  - DDL (CREATE TABLE, ALTER)
  - SELECT ... FOR UPDATE（需要主库）
  - 读写事务内部的 SELECT

读取 → 副本：
  - SELECT（不加锁）
  - 只读事务（@Transactional(readOnly=true)）
  - 报表查询、分析查询
```

### 不应从副本读取的情形

- **写后读**查询——数据可能尚未复制完成。
- **强一致性**要求（账本、库存）。
- 下一次读取依赖上一次写入的**紧密耦合**工作流。

### Spring Boot 示例（ReadWriteSplit 路由）

```java
@Transactional(readOnly = true)
public OrderDTO getOrder(Long id) { ... }  // 路由到副本

@Transactional
public OrderDTO createOrder(OrderDTO dto) { ... }  // 路由到主库
```

通过 `@ReadOnlyRepository` 注解或 AOP 通知配置 `AbstractRoutingDataSource`，从而在主库与副本 `DataSource` 之间切换。

---

## 7. 复制延迟处理

### 问题

异步复制数据库中，主库写入与副本可见之间始终存在一定延迟。这会导致：

- **写后读不一致**——用户创建资源后立即从过时的副本读取，却得到 404。
- **违反单调读**——用户先看到较新的数据版本，随后又看到较旧版本（来自另一个副本）。
- **违反因果关系**——实体 A 的状态依赖实体 B，但 B 的更新尚未到达。

### 处理策略

| 策略 | 说明 | 复杂度 |
|----------|-------------|------------|
| **读己之写（RYW）** | 将最近写入数据的读取路由到主库 | 低 |
| **单调读** | 将一个会话的读取路由到同一副本 | 低 |
| **有界陈旧性** | 拒绝从延迟超过阈值的副本读取 | 中 |
| **因果一致性（GTID）** | 跟踪客户端见过的事务 ID；确保副本应用这些事务后再提供读取 | 中 |
| **等待复制** | 写入后等待副本追赶上来，再提供读取 | 中 |
| **同步复制** | 主库在提交前等待 N 个副本 | 高（有延迟成本） |

### 读己之写（RYW）模式

```python
class DatabaseRouter:
    def __init__(self):
        self.recent_writes = {}  # user_id → 时间戳

    def execute_write(self, user_id, query, params):
        result = primary.execute(query, params)
        self.recent_writes[user_id] = time.now()
        return result

    def execute_read(self, user_id, query, params):
        last_write = self.recent_writes.get(user_id, 0)
        if time.now() - last_write < 5:  # 5 秒窗口
            return primary.execute(query, params)  # 使用主库
        else:
            return replica.execute(query, params)  # 使用副本
```

### 单调读一致性（Shopify 模式）

使用基于哈希的粘性选择，将所有相关读取路由到**同一副本**：

```sql
/* consistent_read_id:user_42 */ SELECT * FROM orders WHERE user_id = 42;
```

```
Hash("user_42") % NUM_REPLICAS = replica_index → 始终命中同一服务器
```

**权衡：**简单且开销低；如果该副本宕机，偶尔会出现不一致。

### 等待复制

```python
def write_and_wait(data):
    primary.execute("INSERT INTO ...", data)
    # 等待写入到达至少一个副本
    primary.execute("SELECT pg_current_wal_lsn()")  # Postgres
    # 或使用 pg_stat_replication

def read_with_consistency(key):
    # 检查副本是否已追赶到已知 LSN
    replica_lsn = replica.execute("SELECT pg_last_wal_replay_lsn()")
    if replica_lsn >= required_lsn:
        return replica.read(key)
    else:
        return primary.read(key)  # 回退到主库
```

### 按使用场景选择策略

| 使用场景 | 推荐策略 |
|----------|---------------------|
| **面向用户的 Web 应用提交表单之后** | 读己之写（在 5-30 秒内路由到主库） |
| **社交动态、时间线** | 单调读（会话粘滞到一个副本） |
| **分析、报表** | 可以接受有界陈旧性；几分钟的延迟也可以 |
| **库存、财务账本** | 始终从主库读取（强一致性） |
| **通知** | 接受最终一致性；基于时间戳去重 |

---

## 8. 服务级测试概览

```
                      覆盖率 ▲
                              │
                    ┌─────────┤
                    │  E2E    │   数量少、速度慢、成本高
                ┌───┤  测试   │
                │   └─────────┤
            ┌───┤            │
            │   │    服务    │   数量和速度均居中
        ┌───┤   │  （集成） │
        │   │   └───────────┤
    ┌───┤   │              │
    │   │   │    单元      │   数量多、速度快、成本低
    │   │   │    测试      │
    └───┴───┴──────────────┘
```

**测试金字塔**建议：
- **单元测试**：约 70%——快速、确定，在隔离环境中测试业务逻辑。
- **集成测试**：约 20%——测试边界（数据库、外部 API）。
- **契约测试**：约 5%——验证服务之间的 API 约定。
- **E2E 测试**：约 5%——覆盖正常路径上的关键流程。

---

## 9. 业务逻辑单元测试

### 原则

- **隔离测试**——模拟/存根所有协作者（数据库、文件系统、网络）。
- **聚焦逻辑**——测试业务规则、转换、校验和状态变化。
- **确定性**——不允许不稳定测试。不依赖外部系统。
- **快速**——单个测试在毫秒级完成。

### 单元测试的对象

```python
# 好：纯业务逻辑——应测试此处
class OrderService:
    def calculate_discount(self, order_total, customer_tier):
        if customer_tier == 'vip':
            return order_total * 0.20
        elif order_total > 1000:
            return order_total * 0.10
        else:
            return 0

# 差：非纯逻辑——涉及 I/O，应改为模拟边界
class OrderController:
    def create_order(self, request):
        order = Order(...)
        db.save(order)          # 这是集成层面的关注点
        notification.send(order) # 在单元测试中模拟此调用
        return order
```

### 仓储/数据层抽象

使用**仓储模式（Repository Pattern）**让业务逻辑可测试：

```java
// 业务逻辑——可以使用模拟仓储进行单元测试
public class OrderFulfillmentService {
    private final OrderRepository orderRepo;
    private final InventoryClient inventoryClient;

    public FulfillmentResult fulfillOrder(String orderId) {
        Order order = orderRepo.findById(orderId);
        if (order == null) return FulfillmentResult.notFound();

        boolean inStock = inventoryClient.checkStock(order.getSku(), order.getQuantity());
        if (!inStock) return FulfillmentResult.outOfStock();

        order.setStatus(OrderStatus.FULFILLED);
        orderRepo.save(order);
        return FulfillmentResult.success();
    }
}
// 单元测试：模拟 orderRepo 和 inventoryClient，测试所有分支
```

### 测试模式

| 模式 | 说明 |
|---------|-------------|
| **Given-When-Then** | 准备 → 执行 → 断言结构 |
| **参数化测试** | 使用一个测试方法测试多种输入组合 |
| **基于属性的测试** | 生成随机输入，并断言不变量成立 |
| **基于状态与基于交互** | 优先使用状态断言，而不是验证模拟对象的交互 |

---

## 10. 集成测试——API 契约、Testcontainers 与 WireMock

### Testcontainers

**是什么：**一个提供轻量、用后即弃测试容器（PostgreSQL、Redis、Kafka 等）的库，可用作 JUnit `@Rule` / `@Container`。

**为何使用真实容器而不是内存数据库：**

| 方式 | 问题 |
|----------|--------|
| **H2（内存数据库）** | SQL 方言不同、功能缺失、负载下行为不同 |
| **SQLite** | 没有 JSONB、PostGIS、全文搜索，类型强制转换方式不同 |
| **Testcontainers** | 真实的 PostgreSQL/MySQL——行为 100% 匹配 |

**示例（Java / Spring Boot + Testcontainers）：**

```java
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldPersistAndRetrieveUser() {
        User user = new User("alice@example.com", "Alice");
        User saved = userRepository.save(user);

        Optional<User> found = userRepository.findByEmail("alice@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Alice");
    }
}
```

**其他语言中的 Testcontainers：**

| 语言 | 库 |
|----------|---------|
| Python | `testcontainers` (pip) |
| Node.js | `testcontainers` (npm) |
| Go | `testcontainers-go` |
| .NET | `Testcontainers for .NET` |
| Rust | `testcontainers` (crate) |

### WireMock

**是什么：**基于 HTTP 的 API 模拟服务器。在集成测试期间存根化外部 HTTP 服务。

```java
@SpringBootTest
@WireMockTest(httpPort = 8089)
class PaymentServiceIntegrationTest {

    @Test
    void shouldProcessPaymentWhenGatewayRespondsSuccess() {
        // 准备：存根化外部支付网关
        stubFor(post(urlEqualTo("/gateway/charge"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    { "status": "success", "transaction_id": "txn_123" }
                """)));

        // 执行
        PaymentResult result = paymentService.charge(new Payment("user_1", 50.00));

        // 断言
        assertThat(result.isSuccess()).isTrue();
        assertThat(result.getTransactionId()).isEqualTo("txn_123");
    }

    @Test
    void shouldHandleGatewayTimeoutGracefully() {
        stubFor(post(urlEqualTo("/gateway/charge"))
            .willReturn(aResponse()
                .withStatus(504)));

        assertThrows(PaymentGatewayTimeoutException.class, () -> {
            paymentService.charge(new Payment("user_1", 50.00));
        });
    }
}
```

**WireMock 能力：**
- 根据 URL、HTTP 方法、请求头和请求体进行存根。
- 模拟延迟、超时和网络故障。
- 录制/回放（开发期间代理真实 API）。
- 验证请求确实发出（对预期交互进行断言）。
- 故障注入（格式错误的响应、连接重置）。

### 集成测试最佳实践

1. **测试边界**——使用 Testcontainers 测试仓储，使用 WireMock 测试外部 API。
2. **保持测试相互独立**——每个测试使用自己的事务或容器状态。
3. **在测试之间清理**——截断表或使用事务回滚。
4. **使用真实的数据**——涵盖触发唯一约束、空值、长字符串的边界情况。
5. **不要测试框架**——无需测试 Hibernate/JPA/ActiveRecord 能否正常工作。
6. **按行为命名测试**——使用 `shouldRejectOrderWhenInventoryExhausted()`，绝不使用 `testOrder1()`。

---

## 11. 契约测试——Pact

### 什么是契约测试？

契约测试通过让双方分别针对共享契约进行独立测试，验证两个服务（消费者和提供者）能否正确通信，而无需同时部署这两个服务。

### Pact 工作流

```
1. 消费者编写期望（Pact 文件）
   ┌──────────┐                 ┌──────────┐
   │  消费者  │ ──── 生成 ────→│ Pact     │
   │   测试   │                 │ 文件     │
   └──────────┘                 └────┬─────┘
                                     │
2. 提供者根据 Pact 进行验证          │
   ┌──────────┐                      │
   │  提供者  │ ←──── 验证 ──────────│
   │   测试   │                      │
   └──────────┘                      │
                                     │
3. Pact Broker 存储并比较差异         │
   ┌──────────────┐                  │
   │ Pact Broker  │ ←──── 存储 ──────│
   │ （版本化）   │                  │
   └──────┬───────┘                  │
          │                          │
4. Can-I-Deploy 检查版本              │
   ┌──────────┐                      │
   │ CI/CD    │ ←──── 兼容性 ────────│
   └──────────┘                      │
```

### 消费者侧测试（Pact）

```java
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "PaymentProvider", port = "8080")
class OrderServiceConsumerPactTest {

    @Pact(consumer = "OrderService")
    public V4Pact createPact(PactDslWithProvider builder) {
        return builder
            .given("a payment method exists with ID 'pm_1'")
            .uponReceiving("a request to charge a payment")
                .path("/gateway/charge")
                .method("POST")
                .headers("Content-Type", "application/json")
                .body(new PactDslJsonBody()
                    .stringType("payment_method_id", "pm_1")
                    .decimalType("amount", 49.99)
                )
            .willRespondWith()
                .status(200)
                .headers("Content-Type", "application/json")
                .body(new PactDslJsonBody()
                    .stringType("status", "success")
                    .stringType("transaction_id", "txn_abc123")
                )
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "createPact")
    void shouldChargePaymentSuccessfully(MockServer mockServer) {
        PaymentClient client = new PaymentClient(mockServer.getUrl());
        PaymentResponse response = client.charge("pm_1", 49.99);
        assertThat(response.getStatus()).isEqualTo("success");
    }
}
```

### 提供者侧验证

```java
@Provider("PaymentProvider")
@PactBroker(url = "${pactbroker.url}")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class PaymentProviderPactVerificationTest {

    @LocalServerPort
    int port;

    @BeforeEach
    void setup(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void pactVerificationTestTemplate(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("a payment method exists with ID 'pm_1'")
    void setupPaymentMethod() {
        // 设置测试数据——在调用提供者之前运行
        paymentMethodRepository.save(new PaymentMethod("pm_1", ...));
    }
}
```

### Pact 最佳实践

- **同时对消费者和提供者进行版本管理**——Pact Broker 跟踪兼容性矩阵。
- **使用 `can-i-deploy`**——`pact-broker can-i-deploy` 命令会在部署前检查两个版本是否兼容。
- **不要过度指定**——对大多数字段使用匹配器（`stringType`、`decimalType`），而不是精确值。只有字段值本身很重要时（例如状态枚举）才应使用精确值。
- **按环境标记 Pact**——使用 "prod"、"staging" 标记 Pact 版本，从而控制部署。
- **在 CI 中运行提供者验证**——不要只在本地运行。如果提供者更改破坏消费者契约，就让构建失败。

---

## 12. 测试夹具

### 什么是测试夹具？

测试夹具是在测试运行前提供已知基线状态的预定义数据设置。它们可以减少重复，并提高测试的可读性。

### 夹具策略

| 策略 | 说明 | 最适合 |
|----------|-------------|----------|
| **内联（测试局部）** | 直接在测试方法中创建数据 | 简单、聚焦的测试 |
| **工厂方法** | 使用合理默认值创建对象的辅助函数 | 大多数情况——灵活、可组合 |
| **Factory Boy / build()** | 使用库生成测试对象 | 复杂对象图 |
| **种子 SQL 文件** | 在测试套件之前加载预先填充的 SQL 插入语句 | 集成 + E2E 测试 |
| **JSON/YAML 快照** | 从夹具文件加载测试数据 | 数据复杂且嵌套时 |

### 示例：工厂模式（Python）

```python
# factories.py
class UserFactory:
    @staticmethod
    def create(
        email="test@example.com",
        name="Test User",
        tier="standard",
        balance=Decimal("100.00")
    ):
        return User(
            email=email,
            name=name,
            tier=tier,
            balance=balance
        )

# test_discount.py
def test_vip_discount():
    vip = UserFactory.create(tier="vip", balance=Decimal("500.00"))
    result = discount_service.calculate(vip, 200)
    assert result == Decimal("40.00")  # 20% VIP discount
```

### Factory Boy（Python）/ 构建器（Java）

```python
import factory

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    total = Decimal("100.00")
    status = OrderStatus.PENDING
    created_at = factory.Faker("date_time_this_year")

# 用法——只覆盖重要的部分
order = OrderFactory.create(status=OrderStatus.FULFILLED)
assert order.user.email == "test@example.com"  # 来自 UserFactory 的默认值
```

### 夹具反模式

- **共享可变夹具**——修改共享状态的测试会产生不稳定的顺序依赖。
- **数据过多**——每个测试都加载 1000 行会很慢；只使用所需的最少数据。
- **复制粘贴夹具**——会导致漂移；应使用带默认值的工厂。
- **魔法数字**——使用具名常量：用 `UNIT_PRICE = Decimal("10.00")` 代替裸露的 `10.00`。

---

## 13. CI 集成

### 在 CI 中执行测试

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  代码检查与 │     │    单元     │     │    集成     │     │    契约      │
│    静态     │ ──→ │    测试     │ ──→ │    测试     │ ──→ │    测试 /    │
│    分析     │     │（快速并行） │     │  （较慢）   │     │   E2E 测试   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────────────┘
     < 2 min           < 5 min            < 15 min            < 30 min
```

### 并行化

- **单元测试**——跨 CPU 核心并行运行（pytest-xdist、JUnit 并行执行）。
- **集成测试**——按服务/模块并行执行；每个测试类使用 Testcontainers 隔离。
- **契约测试**——消费者测试并行执行；提供者测试按 Pact 文件顺序执行。

### CI 流水线示例（GitHub Actions）

```yaml
name: CI
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', distribution: 'temurin' }
      - run: ./gradlew test --parallel     # 仅运行单元测试

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew integrationTest --tests *IntegrationTest
    # 也可以使用 Testcontainers，它会在测试中启动容器

  contract-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew pactVerify          # 提供者侧验证
      - run: ./gradlew pactPublish         # 发布到 Pact Broker

  pact-can-i-deploy:
    needs: contract-tests
    runs-on: ubuntu-latest
    steps:
      - run: pact-broker can-i-deploy
          --pacticipant OrderService
          --version $(cat version.txt)
          --to-environment production

  e2e-tests:
    needs: [integration-tests, pact-can-i-deploy]
    runs-on: ubuntu-latest
    steps:
      - run: docker compose -f docker-compose.e2e.yml up --abort-on-container-exit
```

### CI 最佳实践

| 实践 | 理由 |
|----------|-----------|
| **快速失败** | 首先运行最快的测试（单元 → 集成 → E2E）。 |
| **缓存依赖** | Maven/Gradle/npm/pip 缓存可加快重复构建。 |
| **缓存 Docker 层** | 针对 Testcontainers 拉取操作预热镜像缓存。 |
| **隔离不稳定测试** | 隔离不稳定测试；不要让它们阻塞流水线。 |
| **针对类生产数据库进行测试** | 使用与生产环境相同数据库版本的 Testcontainers。 |
| **将 Pact 验证作为必需检查运行** | 绝不部署破坏消费者契约的提供者。 |
| **将测试报告作为产物** | 发布 JUnit XML / HTML 报告以便调试。 |

### 测试运行优化

- **选择性执行测试**——只运行已更改模块的测试（gradle `--changed-latest`、`pytest --last-failed`）。
- **测试拆分**——将集成测试分散到多个 CI 运行器（`--shard` 标志）。
- **复用 Docker 层**——Dockerfile 更改会导致完整重建；将很少变化的层放在前面。
- **CI 中的数据库迁移**——运行一次迁移并为数据库创建快照，再为每个测试运行器恢复快照。

---

## 参考资料与延伸阅读

- **PostgreSQL 文档**——[EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)、[事务隔离](https://www.postgresql.org/docs/current/transaction-iso.html)
- **HikariCP**——[GitHub](https://github.com/brettwooldridge/HikariCP)（连接池规模估算）
- **PgBouncer**——[官方文档](https://www.pgbouncer.org/)（事务池化）
- **Pact**——[文档](https://docs.pact.io/)（契约测试）
- **Testcontainers**——[官方网站](https://testcontainers.com/)（集成测试）
- **WireMock**——[官方网站](https://wiremock.org/)（API 模拟）
- **Shopify Engineering**——[使用数据库副本实现读取一致性](https://shopify.engineering/read-consistency-database-replicas)
- **Crunchy Data**——[Postgres 新手索引指南](https://www.crunchydata.com/blog/postgres-indexes-for-newbies)
- **Scout APM**——[理解 N+1 数据库查询](https://www.scoutapm.com/blog/understanding-n1-database-queries)
- **AWS**——[RDS Proxy](https://aws.amazon.com/rds/proxy/)（无服务器连接池）
