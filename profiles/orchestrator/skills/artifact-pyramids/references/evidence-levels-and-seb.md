# 证据等级与 SEB：层深阈值与证据复用纪律

本文件定义产物金字塔的**证据深度档位**（L0 / L1 / L1+L2 / Full）与 **SEB（Structured Evidence Bundle，结构化证据包）** 的复用、完整性核验与不足处置规则。

它回答两个问题：

1. 这个任务该生成多深的金字塔？（第 1 节）
2. 别人的证据我能不能直接采信，凭什么？（第 2–4 节）

**层级命名说明：** `L1` / `L2` / `L3` 是金字塔的层级（摘要 / 分析 / 档案）。证据档位 `L0` / `L1` / `L1+L2` / `Full` 描述**生成到哪一层为止**：`L0` 不生成金字塔，`L1` 只到摘要，`L1+L2` 到分析，`Full` 三层齐备。数量前缀不可混用：`L1` 档位只产生 `01-summary/`，不产生 `03-dossiers/`。

---

## 1. 四档层深阈值

### 1.1 档位定义

| 档位 | 适用场景（intake 触发条件） | 最低产物要求 | 最低证据强度 | 默认预算 |
|---|---|---|---|---|
| **L0** | T0 / T1；单文件且 ≤30 行且无依赖的 T2 / T4；纯状态、阻断、澄清、审批请求 | **不生成金字塔**：不创建 `00-index.md`，不创建任何层级目录。只用结构化交接消息（`status` / `summary` / `evidence` / `risks`） | 变更文件清单；至少一条可复核命令及其 exit code；无改动时给出显式「无改动」声明 | 不需要门禁产物 |
| **L1** | 多文件改动；diff ≤200 行；T3；单模块 T4 | `00-index.md` + `01-summary/` 至少 1 个文件。**不创建空层级目录** | 固定完整 commit SHA；`changed_files` 含 blob hash；每条命令的 exit code 与 stdout hash；`SOURCES` 至少 1 条可达引用 | G1 目标 ≤12 轮 / 300s |
| **L1+L2** | 跨模块改动；新增依赖；接口 / 契约变化 | 在 L1 基础上增加 ≥1 份 `02-analysis/` 维度文件；`SOURCES` 上下都完整 | L1 全部，外加接口 / 依赖变化的对照证据（变更前后签名、依赖锁文件、schema 差异） | G1 目标 ≤12 轮 / 300s |
| **Full** | T5 / T6；数据或环境迁移；公开 API；安全相关；高风险清单命中 | 三层齐备：`00-index.md` + `01-summary/` + `02-analysis/`（按维度）+ `03-dossiers/`（原始证据、命令输出、SEB） | L1+L2 全部，外加完整 SEB（第 2 节）、门禁产物路径、质量门 A/B/C 全过 | G2 目标 ≤30 轮 / 900s |

### 1.2 决策顺序

```
intake 一次性分类（T 档 + 高风险清单）
  → 命中 ≥2 条升级触发器？ → 保守升级一档
  → 落档（L0 / L1 / L1+L2 / Full）
  → 写进任务卡与交接消息的 evidence_level，下游继承
```

**只由 intake 决策一次，下游继承。** 工程师、QA、reviewer 不重新选择档位；发现档位不足时按 1.3 上报升级，不自行降档。

### 1.3 进入下一档所需的证据强度（升级触发器）

命中任一条即升档，多条叠加时取最高档：

| 观察到的信号 | 升到 |
|---|---|
| 改动涉及 ≥2 个文件，或 diff >30 行 | ≥ L1 |
| 出现提交、分支、可交付产物 | ≥ L1 |
| diff >200 行，或超出单模块边界 | ≥ L1（超出模块边界时直接 L1+L2） |
| 跨模块调用、接口签名变化、新增 / 升级依赖、配置 schema 变化 | ≥ L1+L2 |
| 迁移、公开 API、安全相关、T5 / T6、高风险清单命中 | Full |
| 档位无法判定 | 保守升一档（与 intake 的保守升级纪律一致） |
| SEB 完整性核验失败（第 3 节） | 升到 Full 并全量复算 |

**降档只允许发生在 intake 决策点。** 下游不得因为「时间紧」「改动看起来小」自行降档。确需降档必须记录理由、通知 orchestrator，并保留原档位的证据要求。

---

## 2. SEB（结构化证据包）：最小字段

SEB 是任务在交接时打包的**可复用证据单元**。目标：下游（reviewer、后续 Flow、复核者）在不动手重跑的前提下，能判定「这份证据是否仍然有效」。

字段清单（最小集；`*` 为必需，缺失即阻断复用）：

| 字段 | 含义 | 说明 |
|---|---|---|
| `schema_version` * | 证据包版本 | 结构变更时必须递增 |
| `task_id` * | 产生该证据的 Kanban 任务 | 复用时的追溯锚点 |
| `commit` * | 被固定评审的完整 commit SHA | 复用必须同 SHA；不得用「当前工作区」替代 |
| `baseline` * | 实现依据的基点 revision / SHA | 与需求基线 revision 对应 |
| `changed_files[]` * | `path` + `blob_sha`（`git hash-object`）+ 增删行数 | 内容寻址，是防篡改的核心 |
| `commands[]` * | `cmd` + `exit_code` + `stdout_sha256` + `stdout_normalizer` + `cwd` | 门禁结论必须能追到原始命令与原始输出；`stdout_sha256` 一律对**规范化输出**取值（§2.1） |
| `anchor` | `commands[].anchor`：输出无法规范化时的**可复算替代锚点** | 与 `stdout_normalizer: unstable` 配对使用（§2.1） |
| `seb_integrity_note` | `seb_integrity` 取值的理由 | 令牌必须逐字合法，理由**不得**并入令牌（§4.1） |
| `gate_artifacts[]` * | `gate` + `path` + `sha256` | 质量门产物必须可达且哈希匹配 |
| `producer` * | 产生者 profile 与 run id | 谁产出的证据 |
| `produced_at` * | 产生时间（UTC、ISO 8601） | 仅用于记录与排序，**不作为失效依据** |
| `env` | OS / 内核 / 运行时版本 | 命令结论依赖环境时补充 |

**内容寻址原则：** SEB 的有效性由 `commit` + `blob_sha` + `sha256` 决定，与产生时间无关。时间只用于审计排序；「证据太旧」不构成拒绝理由，「内容不一致」才是。

### 2.1 `commands[].stdout_sha256` 的采集与规范化约定

**问题（两个被误判成「证据不一致」的假阳性）：**

- **非确定性字段入哈希。** `npm run build` 输出含 `built in 86ms` 之类耗时行；同样源码重跑必然得到不同哈希，严格复核者会判「证据不一致」。
- **采集约定不一致。** 同一语义的「空输出」，一方留档为 1 字节换行（`01ba4719…`），另一方为 0 字节（`e3b0c442…`）；语义相同但令牌不可比。

**规则：`stdout_sha256` 一律对「规范化输出」取值。** 固定基线规则（所有命令隐含，不写进令牌）：

1. **字节保真采集。** `cmd > out.raw 2>&1`，stdout+stderr 原样落盘；`exit_code` 单独记录。**不得**用命令替换（`x=$(cmd)`）或管道截断代替采集——它们会改写字节并吞掉末尾换行。
2. **CRLF → LF。**
3. **剥离末尾换行。** 规范化结果末尾的换行全部删除；因此「空输出」恒为 **0 字节**，`stdout_sha256` 恒为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。
4. **删除非确定性行。** 按 `stdout_normalizer` 令牌额外删除；**未标注即视为 `none`**。
5. **取哈希。** 对第 4 步结果字节取 sha256，写入 `stdout_sha256`。

`stdout_normalizer` 令牌：

| 令牌 | 额外删除 | 典型命令 |
|---|---|---|
| `none` | 无（仅基线规则） | `git status --porcelain`、`git rev-parse`、`git hash-object` |
| `drop-build-timing` | 构建 / 打包耗时行，如 `built in 86ms`、`✓ built in 1.20s` | `npm run build`、`vite build`、`cargo build` |
| `drop-timestamps` | 时间戳 / 日期前缀行 | 带时间戳的 runner 输出 |
| `drop-progress` | 进度 / 百分比 / spinner 行 | 下载、迁移、批量任务 |
| `unstable` | 不删除；改用 `commands[].anchor` 作为可复算替代锚点 | 输出含随机端口 / 并发顺序 / 哈希种子 |

组合令牌用 `+` 连接（如 `drop-build-timing+drop-timestamps`）。

**可复制的采集示例（POSIX sh）：**

```sh
# 1) 字节保真采集；exit code 单独记录
git status --porcelain > gate.status.raw 2>&1; echo $? > gate.status.exit

# 2) 规范化取哈希：基线规则 + 可选 ERE 删除
norm_hash() {                    # $1=raw 文件  $2=额外删除的 ERE（可空）
  [ -f "$1" ] || { echo "ERROR: raw missing: $1" >&2; return 2; }
  d=$(mktemp -d)
  tr -d '\r' < "$1" > "$d/s1"
  if [ -n "$2" ]; then grep -vE "$2" "$d/s1" > "$d/s2"; mv "$d/s2" "$d/s1"; fi
  printf '%s' "$(cat "$d/s1")" > "$d/canon"      # 剥离末尾换行；空输出 => 0 字节
  sha256sum "$d/canon" | cut -d' ' -f1
}
norm_hash gate.status.raw ''                       # stdout_normalizer: none
```

**本机实测锚点（可直接复算）：**

| 原始输出 | 规范化后 | `stdout_sha256` |
|---|---|---|
| 0 字节 | 0 字节 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| 单个 `\n` | 0 字节 | `e3b0c442…`（与上一行**同值**——这正是 F2 的消除点） |
| 两个 `\n` | 0 字节 | `e3b0c442…`（与上一行**同值**） |
| `a\n` | `a`（1 字节） | `ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb` |
| 构建输出含 `built in 86ms` 与 `built in 91ms`，`drop-build-timing` | 104 字节 | 两者同为 `903e12713b07fa4d7603a2ffd8e2ad1570d6ecc188f645fb8e4ebe74dd7baf50` |

**陷阱：读取失败不得静默退化为「空输出」。** 上表配方若省略 `[ -f "$1" ]` 校验，raw 文件缺失时 `tr` 失败但管道仍产出空字节流，哈希同样是 `e3b0c442…`——与「命令确实无输出」不可区分。采集函数必须对文件存在与读取退出码显式报错。

**替代锚点。** 输出无法规范化到确定性时，不要强行删行（会删掉真实内容差异）；改用可复算的替代锚点并显式标注：产物内容哈希（如 `dist/index.html` 的 `<script src>` 与 bundle 文件名）、产物文件 sha256、或 `git diff --numstat` 行数。锚点写入 `commands[].anchor`。

**复核纪律。** 复算时按交接声明的 `stdout_normalizer` 同名规则复算，未标注视为 `none`。哈希不一致时先判定是**约定差异**还是**输出内容差异**：双方按同一 normalizer 复算后仍不一致才判 `failed`；仅属约定差异（如空输出的 0 字节 vs 1 字节换行）必须如实记录差异来源，**不得**要求任一方把数字改成与对方一致。

---

## 3. SEB 复用条件与完整性核验

### 3.1 何时可以复用（全部满足才可复用）

| # | 前置条件 |
|---|---|
| 1 | 待采信的固定 SHA 与 SEB 的 `commit` **完全一致**（同 SHA） |
| 2 | `baseline` 与 intake / 需求基线记录的 revision 一致 |
| 3 | `changed_files` 覆盖 `git diff --name-status <baseline>..<commit>` 的全部条目，**无遗漏、无多余** |
| 4 | 逐文件复算的 blob hash 与 `changed_files[].blob_sha` 全部一致（含「文件应存在/应删除」状态） |
| 5 | 每条命令的 `exit_code` 与结论一致（门禁必须二元，非 0 不得记为通过） |
| 6 | `gate_artifacts[]` 路径可达且实际 `sha256` 与记录一致 |
| 7 | 命令的前提条件仍成立（cwd、分支、环境未变） |

任一条不满足 → **停止复用**，按 3.3 处置。不存在「部分满足就部分采信」的中间态。

### 3.2 完整性核验流程（reviewer 先核验，再抽样）

```
Step 1 结构核验：必需字段齐全、类型合法
Step 2 锚点核验：commit == 被评审 SHA；baseline == 基线 revision
Step 3 内容核验：对 changed_files 逐一复算 blob hash 并比对
Step 4 产物核验：gate_artifacts 路径存在 + sha256 匹配；命令 stdout hash 按交接声明的 stdout_normalizer 复算（§2.1）
Step 5 覆盖核验：changed_files 与 tree diff 完全对应（无遗漏、无多余）
Step 6 抽样：默认只抽最高风险项（风险序：公开 API / 迁移 / 安全 > 跨模块接口 > 单模块逻辑 > 文档）
Step 7 升级：Step 1–5 任一步失败 → 自动升级为全量复算，标记 seb_integrity: failed
```

抽样规模建议 ≥1 项，且必须覆盖最高风险类别。核验（Step 1–5）通过后，未抽样部分可直接采信——**采信的强度来自内容寻址核验，而不是来自抽样比例。**

### 3.3 缺失或不完整的处置（降级 / 阻断）

| 情形 | 处置 |
|---|---|
| 应 Full 却完全没有 SEB | **阻断**：返回 `status: blocked` 风格交接（证据不足），不得进入批准阶段；补齐后重跑核验 |
| `commit` / `baseline` / `changed_files` 等必需字段缺失 | **阻断复用**：要求补齐，不得以「部分核验通过」放行 |
| 非必需字段缺失（`env`、`schema_version`） | 允许复用，但标记 `seb_incomplete: true` 并写进结论 |
| `commit` 不同或 `baseline` 漂移 | **停止复用 + 全量复算**（同 SHA 前提被破坏） |
| blob hash / 产物 hash 不一致 | 判定证据被篡改或工作树已变 → **全量复算 + 风险上报**，不得静默 |
| 命令 exit code 非 0 却记为通过 | 判门禁失败（二元结论），回到实现者 |
| stdout hash 不一致但语义相同（如空输出的 0 字节 `e3b0c442…` vs 1 字节换行 `01ba4719…`） | 先按 §2.1 以同一 `stdout_normalizer` 复算求判定：复算后一致则判**采集约定差异**并如实记录来源，**不得**判 `failed`；复算后仍不一致才按下一行「blob / 产物 hash 不一致」处置 |
| 预算耗尽（超出档位轮次 / 秒数） | 只允许**部分裁决**：标 `confidence: reduced` 并列出 `uncovered`；不得伪装通过 |

**降级的是置信度，不是门禁要求。** Full 档任务缺 SEB 时，不得降级为 L1 放行；只能阻塞或标记不完整。允许的降级只有：`confidence: reduced` + 显式 `uncovered` 清单。

---

## 4. 交接字段与可检索令牌

交接消息的 `evidence` 至少包含：

```yaml
evidence:
  evidence_level: L0 | L1 | L1+L2 | Full
  commit: <完整 SHA>
  baseline: <revision / SHA>
  changed_files: [<path>, ...]
  commands: ["<cmd> -> exit <code>, stdout_sha256:<hash> (stdout_normalizer: none|drop-build-timing|drop-timestamps|drop-progress|unstable)"]
  seb: <SEB 文件路径或内联块>
  seb_integrity: passed | failed | not_required
  seb_integrity_note: <取该令牌的理由；生产者自产证据填 self-produced (producer == task)>
  sampling: <抽样了哪些最高风险项>
  confidence: full | reduced
  uncovered: [<未覆盖项>]     # confidence: reduced 时必填
```

稳定可检索令牌（供 grep / 门禁脚本使用）：

```
L0  L1  L1+L2  Full  SEB  seb_integrity  seb_integrity_note  blob_sha
stdout_sha256  stdout_normalizer  confidence: reduced  uncovered  evidence_level
```

### 4.1 `seb_integrity` 的合法令牌与语义

`seb_integrity` 是**闭集合令牌**，只允许三个值，必须**逐字**使用：

| 令牌 | 语义 | 谁填写 |
|---|---|---|
| `passed` | 复用方对本 SEB 执行了 §3.2 Step 1–5，全部通过 | 复用方（`reviewer` / `qa-engineer` / 下游 Flow） |
| `failed` | 核验被实际执行，Step 1–5 任一步失败 | 复用方 |
| `not_required` | 不发生跨任务 SEB 复用：证据由本任务自产（`producer` 指向当前任务），或档位为 `L0`（不要求 SEB） | 生产者（自产证据的交接方） |

规则：

1. **必须逐字。** 不得追加括号、来源或理由。`"not_required (self-produced)"` **不是**合法令牌——它是「令牌 + 理由」的拼接，会让 grep 与闭集合校验失配，也让下游无法机器判定。理由写进独立字段 `seb_integrity_note`。
2. **自产证据的正确取值是 `not_required`**，理由写进 `seb_integrity_note`，例如 `seb_integrity_note: self-produced (producer == task)`。不要用 `passed` 冒充（此时没有任何复用方核验过），也不要用 `failed`。
3. **`not_required` 不豁免 SEB 字段完整性。** `commit` / `baseline` / `changed_files` / `commands` / `gate_artifacts` 仍须齐全；`not_required` 只表示「复用前核验」这一步不适用。
4. **填权随复用转移。** 生产者交接时为 `not_required`；`reviewer` / `qa-engineer` 一旦跨任务复用该 SEB，必须在自己的结论中给出 `passed` 或 `failed`。门禁文案要求「必须 `passed`」时，指的是**复用方**的结论，不是生产者的初值。
5. **`L0` 例外。** 档位为 `L0` 时不生成金字塔、不要求 SEB；此时取 `not_required`，理由 `seb_integrity_note: l0-no-seb-required`。

---

## 5. 平台边界（不得声称已实现）

本节规则是**文档层的纪律**，不改变任何运行时行为：

- **运行时「自动门禁超时降级」不存在。** 超时后自动降级、自动全量复算、自动升级档案，都需要平台能力，属平台缺口（C4-4）。
- **抽样与核验目前由 reviewer 手工执行**，没有平台钩子强制。
- 本文档不得被引用为「SEB 复用已自动化」的证据；任何「自动降级已生效」的表述都是不实声称。
- 本文件不修改 reviewer Profile 的技能实现（属需人工批准的范围）。

**预算纪律（软目标）：** 普通 G1 ≤12 轮 / 300s；高风险 G2 ≤30 轮 / 900s。超预算只能部分裁决（第 3.3 节），不能无限运行，也不能伪装通过。

---

## 6. 与其他参考资料的关系

| 参考资料 | 本文件如何扩展它 |
|---|---|
| `pipeline-stages.md` | 定义层级**是什么**；本文件定义**生成到哪一层为止**（L0 档位即第 0 层：不生成金字塔） |
| `quality-gates.md` | 定义完成金字塔后的验证；本文件定义**复用他人证据前**的完整性核验 |
| `output-classification-framework.md` | 决定内容放在**哪一层**；本文件决定**要不要建这些层** |
| `methodology-to-pyramid-mapping.md` | 定义角色的领域产物如何映射到层级；本文件定义 `evidence_level` 由 intake 一次性下发并由下游继承 |

## SOURCES

```
references/evidence-levels-and-seb.md
 -> 本文件：L0/L1/L1+L2/Full 层深阈值 + SEB 复用与完整性核验规则
references/pipeline-stages.md
 -> 三层级定义与生成流程（L0 档位在此为「不生成金字塔」）
references/quality-gates.md
 -> 质量门 A/B/C（金字塔内部验证；与 SEB 复用核验互补）
references/output-classification-framework.md
 -> 层级内容契约（决定内容放哪一层）
references/methodology-to-pyramid-mapping.md
 -> 角色方法论到金字塔层级的映射
<skills-root>/orchestration-methodology/references/delivery-governance.md
 -> 交接消息中的治理字段（commit / changed_files / tests / worktree / branch）
<repo-root>/AGENTS.md「证据等级与 SEB」章节
 -> 上级全局约定；本文件是它在 artifact-pyramids 技能内的落地展开
上游 Kanban 任务 t_567d53e4 的 implementation-plan.md「A3」节
 -> 层深阈值、SEB 最小字段、预算纪律的原始意图（附件随任务，不在本仓库内）
```
