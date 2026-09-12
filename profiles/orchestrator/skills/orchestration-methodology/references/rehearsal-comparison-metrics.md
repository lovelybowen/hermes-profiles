# 重复演练对比指标：取数配方与陷阱

对比两轮同规格演练（同一需求、两次独立执行）时，指标必须**可复算**。本文件给出最小字段集、取数配方，以及本机实测踩到的四个坑。

一句话纪律：**没有冻结到持久目录的上一轮产物，就不能做定量对比。** `scratch` 工作区与 `attachments` 会随任务清理而丢失（N2）；此时与「上一轮」有关的字段只能退化为引用卡面记录值，属弱证据，必须标注 `source: recorded-card-values`。

## 1. 最小字段集

| 字段 | 取值来源 | 口径要求 |
|---|---|---|
| 端到端壁钟 | 根卡 `created_at` → 末子卡 `completed_at` | 必须区分**「至评审」**与**「含综合」**两个口径；混用会得出相反结论 |
| 执行壁钟 | 首个被派 worker `started_at` → 末子卡 `completed_at` | 剔除 intake 空转 |
| 准入耗时 | 根卡 `created_at` → 首个**被派** worker `started_at` | 必须排除根卡自身的 orchestrator run |
| 各角色时长与占比 | `task_runs.started_at/ended_at` 按 profile 汇总 | 用占比而非绝对值，跨轮规模可比 |
| tool call 数 | worker 会话日志**尾部**统计 | 按卡与合计分别给；日志缺失时显式标注，不填 0 |
| worktree 新建数 / 下游复用率 | `git worktree list` + 各卡 workspace | 复用率 = 复用同一棵的卡数 / 卡数 |
| 重复门禁计数 | 构建次数、浏览器门次数、diff+SHA 复算次数 | 按命令维度计数，不按「门」计数 |
| 交付 diff 规模 | `git diff --numstat <baseline> <commit>` | 与验收条件对照，并注明是否达标 |

## 2. 取数配方

### 2.1 Kanban DB（任务与 run 时间戳）

**必须写成脚本文件再执行。** 本机没有 `sqlite3` CLI；单查询模式（`-q`）下 `python3 -c "..."` 会被安全策略以「script execution via -e/-c flag」拒绝，heredoc 会被以「shell execution via heredoc」拒绝。可行路径只有：用文件写入工具落盘 `*.py`，再 `python3 <script>`。

```python
# extract_metrics.py（节选）
import sqlite3
c = sqlite3.connect('/root/.hermes/kanban.db')
c.row_factory = sqlite3.Row
t = c.execute("select id,assignee,created_at,started_at,completed_at"
              " from tasks where id=?", (tid,)).fetchone()
runs = c.execute("select id,profile,started_at,ended_at"
                 " from task_runs where task_id=? order by id", (tid,)).fetchall()
```

口径实现要点：

- 「首个被派 worker」= **子卡**（排除根卡自身）中最早的 `started_at`；若不排除，会把根卡 orchestrator run 算进准入耗时。
- 一个卡可能有多次 run（重试、心跳、重排）；`task_runs` 要逐条列出，别只取第一条。
- 壁钟用 `created_at`（建卡时刻）而非 `started_at`（派发时刻）作为起点，否则量不到准入 / 排队开销。

### 2.2 会话日志（tool call 数）

统计数据**只出现在日志文件尾部**：`/root/.hermes/kanban/logs/<task-id>.log` 里的

```
Messages:       89 (1 user, 87 tool calls)
Duration:       4m 40s
```

**只取文件尾部若干字符再匹配**（例如 `open(path).read()[-4000:]`）。对整个文件跑正则会命中日志正文里**自己被引用过的同款字符串**——本轮首次抽取即误命中，把自述文本当成了统计值。日志不存在（例如根卡未产生 worker run）时**显式标注「日志缺失」**，不要填 0；0 与「没跑」语义不同。

### 2.3 git（交付 diff 与 worktree）

```bash
git -C <repo> diff --numstat <baseline> <commit>
git -C <repo> worktree list
git -C <repo> rev-parse HEAD HEAD^
```

## 3. 陷阱清单（本机实测）

1. **`rm -rf`、heredoc、`python3 -c` 都会被安全策略拦截。** 终端以单查询模式运行时无人可批准危险命令：`rm -rf` 报「recursive delete」，heredoc 报「shell execution via heredoc」，`-c` 报「script execution via -e/-c flag」。清空构建目录不要用 `rm -rf`（打包器默认写入前清空 `outDir`，直接重跑即可）；写脚本一律用文件写入工具。
2. **日志统计只信尾部。** 见 §2.2；全文件正则会自我污染。
3. **对比基线随清理丢失。** `scratch` 工作区与 `attachments` 会被清理；上一轮产物未冻结则指标不可复算（N2）。
4. **别把「读取失败」当成「空输出」。** 采集函数若不校验文件存在与读取退出码，失败后会静默产出空哈希 `e3b0c442…`，与「命令确实无输出」不可区分（详见 `artifact-pyramids/references/evidence-levels-and-seb.md` §2.1）。

## 4. N2 一行 runbook

对比 / 重复演练**开工前**，先把上一轮的产物与门禁证据冻结到持久目录：

```bash
mkdir -p /root/kanban-evidence/<prev-task-id> && \
  cp -a <prev-attachments-or-workspace>/. /root/kanban-evidence/<prev-task-id>/
```

## 5. 参考实现

- `/root/.hermes/kanban/attachments/t_2963780e/extract_metrics.py` —— §2 的完整实现（DB 时间戳 + 日志尾部统计 + git diff + worktree 清册 + 两轮对比）
- `/root/.hermes/kanban/attachments/t_2963780e/verify_final.sh` —— 固定 SHA / blob / 改动覆盖 / 工作树状态 / 门禁产物 sha256 的独立锚点复算脚本

## 6. Intake 分类器校准指标（L0 快速通道健康度）

L0 快速通道（`gate-topology.md` §4.1）把分类质量从「流程约定」变成「可度量的运行时行为」，需要持续校准。以下指标从 Kanban 卡面与 git 记录**可复算**：

| 指标 | 取数来源 | 健康信号 |
|---|---|---|
| **L0 占比** | 卡面 `evidence_level: L0` 令牌 / 总实现卡数 | 持续偏低说明分类过保守（快速通道没人走）|
| **L0 事后升级率** | `needs_reclass: true` 令牌 + 抽样审计命中的升级触发器数 / L0 卡数 | 偏高说明 L0 阈值过松或快判不可靠 |
| **L0 返工率** | L0 卡后续触发 `kanban_request_changes` 的比例 | 偏高说明自验命令质量不足 |
| **L0 缺陷逃逸** | 抽样审计中发现的、验收命令未覆盖的缺陷数 | 任何逃逸都应回写验收模板 |
| **各档位 P50 壁钟** | 按 `evidence_level` 分组的根卡 `created_at` → 末子卡 `completed_at` | L0 与 L1 应有稳定差值，否则快速通道无意义 |
| **各角色实际调用率** | `task_runs` 按 profile 汇总 / 实现卡数 | 验证「L0 只建 engineer 卡」是否属实 |

判定口径：

- 令牌直接 grep 卡面（`evidence_level`、`needs_reclass` 当初设计为稳定可检索令牌，正是为此）；
- **L0 事后升级率或逃逸率连续超阈值 → 按主题收紧 L0 阈值或回滚快速通道**（对齐 AGENTS.md「迁移」节的按主题回滚）；
- 阈值在阶段 0–1 校准前是设计目标值（与 §4 预算纪律同口径），不得当成已生效的自动回滚机制——**回滚决策由 orchestrator / Delivery Owner 人工执行**。

SOURCES

```
/root/hermes-profiles/skills/orchestration-methodology/references/delivery-governance.md
 -> §2.1 工作区保留规则与「对比前冻结上一轮产物」runbook（本文件 §4 的落地位置）
/root/hermes-profiles/skills/artifact-pyramids/references/evidence-levels-and-seb.md
 -> §2.1 stdout 规范化约定与「读取失败 ≠ 空输出」陷阱
/root/.hermes/kanban/attachments/t_2963780e/extract_metrics.py
 -> §2 取数配方的可运行参考实现
/root/.hermes/kanban/attachments/t_2963780e/verify_final.sh
 -> 交付锚点复算参考
/root/.hermes/kanban/logs/<task-id>.log
 -> worker 会话尾部统计（tool call 数、duration）的唯一来源
```
