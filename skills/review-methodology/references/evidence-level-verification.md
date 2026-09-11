# 证据档位与核验深度

本文件规定 reviewer 在**选择核验深度之前**必须做什么，以及 `L0` / `L1` / `L1+L2` / `Full` 四档各自对应的核验范围。

档位阈值、升级触发器、SEB 最小字段、复用前置条件与完整性核验流程的**唯一权威出处**是：

```
skills/artifact-pyramids/references/evidence-levels-and-seb.md
```

本文件**只引用、不复制**该文件的定义；两者冲突时一律以该文件为准。逐字段 SEB 核验与证据不足处置表见 `references/seb-integrity-and-insufficiency.md`（配套 reference，与本文分工见第 4 节）。

---

## 0. 入口：先读证据，再选深度（强制前置）

reviewer **不得**凭「改动看起来小」或「时间紧」自行挑选深度。固定顺序：

```
Step 0.1  读交接消息 evidence.evidence_level（L0 | L1 | L1+L2 | Full）
Step 0.2  读 SEB 与交接字段：commit / baseline / changed_files[]（含 blob_sha）
          / commands[]（含 exit_code、stdout_sha256）/ seb / seb_integrity
          / sampling / confidence / uncovered
Step 0.3  确认 evidence_level 与 intake 下发档位一致（下游继承，不重选）；
          缺失或低于风险要求 → 按 seb-integrity-and-insufficiency.md 的处置表上报，
          不自行降档，也不盲目全量复算
Step 0.4  按 evidence_level 落到第 1 节对应的一档执行
```

档位由 intake **一次性判定、下游继承**（完整阈值与升级触发器见权威文件 §1）；reviewer 只执行，不上调也不下调。确需变更档位只能退回 orchestrator 走 intake 决策点。

字段名的交付层权威是 `skills/orchestration-methodology/references/delivery-governance.md` §6。注意 `commands` 的机器可解析键名是 **`exit_code`**（`cmd` / `exit_code` / `stdout_sha256` / `cwd`），不是展示串 `exit <code>`；`seb_integrity`（`passed | failed | not_required`）与 `seb_incomplete` 是两个不同令牌，不得合并（见配套 reference）。

---

## 1. 档位 → 核验深度

| `evidence_level` | 核验深度 | 范围（做什么） | 明确不做 |
|---|---|---|---|
| `L0` | 快速扫描 | 变更文件清单；≥1 条可复核命令的 `exit_code`；无改动时给出显式「无改动」声明 | **不启动构建、不启动浏览器**；不生成金字塔；不要求 SEB |
| `L1` | 直接单模块验证（绑定 `changed_files`） | 仅围绕 `changed_files`：逐文件复算 blob hash、逐条命令重跑并复算 `stdout_sha256`、核对 `exit_code` 与二元结论一致 | 不扩散到未改动模块；不做跨模块接口影响核对；不跑全量构建 / 浏览器 |
| `L1+L2` | 跨模块 / 接口影响核对 + 关键路径抽样 | 在 L1 全部之上：核对接口 / 契约 / 依赖变化的对照证据（变更前后签名、锁文件、schema diff），并对关键路径按风险序抽样 ≥1 项且覆盖最高风险类别 | 不逐项全量复算全部改动；抽样规模按第 2 节；不为「求全」重复跑无关模块 |
| `Full` | 全量复算（逐项） | build / browser / diff / SHA **逐项重算**：完整构建、浏览器端到端、`baseline..commit` 全量 diff、逐文件与逐门禁产物 SHA、三层金字塔齐备、完整 SEB 复核 | 不以抽样代替；不得以任何理由把 `Full` 降为 `L1` / `L1+L2` 放行 |

「逐项」的含义是**每一项都要有可复核的原始命令与结果**，不是「跑一遍看起来通过就算」。四档的共同底线：门禁结论必须是二元的（通过 / 失败），非 0 `exit_code` 不得记为通过。

---

## 2. 抽样规则（`L1+L2` 与 `Full` 的边界）

风险序（高 → 低）：

```
公开 API / 迁移 / 安全  >  跨模块接口  >  单模块逻辑  >  文档
```

- `L1+L2`：抽样 ≥1 项，且**必须覆盖最高风险类别**；`sampling` 字段记录抽了哪些项。
- 完整性核验五步（结构 / 锚点 / 内容 / 产物 / 覆盖，见权威文件 §3.2）通过后，未抽样部分可直接采信——**采信强度来自内容寻址核验（`commit` + `blob_sha` + `sha256`），不是来自抽样比例**。
- `Full`：不抽样替代，逐项复算。

---

## 3. 各档核验命令清单（最小集）

命令中的 `<baseline>` / `<commit>` 取交接的 `baseline` 与 `commit`，`<path>` 取 `changed_files[].path`；重跑门禁时沿用交接 `commands[]` 记录的**原始命令与 `cwd`**，不得替换成「等效命令」。

**`L0`（快速扫描）**

```bash
git diff --name-status <baseline>..<commit>      # 变更清单；无输出即无改动
# 无改动时给出显式声明，而非空结论：
git diff --quiet <baseline>..<commit> && echo "no change"
```

**`L1`（直接单模块验证）**

```bash
git hash-object <path>                            # 逐个 changed_files 比对 blob_sha
git diff --name-status <baseline>..<commit>       # 覆盖核对：无遗漏、无多余
# 逐条重跑 commands[]，复算 stdout_sha256，核对 exit_code 与结论一致
```

**`L1+L2`（跨模块 / 接口影响核对 + 抽样）**

```bash
git diff <baseline>..<commit> -- <接口/契约文件>   # 变更前后签名对照
git diff <baseline>..<commit> -- <依赖锁文件>      # 如 package-lock.json / requirements.txt / go.sum
git diff <baseline>..<commit> -- <schema 文件>     # schema 差异
# 再按风险序抽样 ≥1 项（覆盖最高风险类别）并逐条复算
```

**`Full`（全量复算，逐项）**

```bash
# build   ：沿用交接 commands[] 中记录的构建命令，复算 exit_code 与 stdout_sha256
# browser ：端到端 / 关键路径浏览器验证，保留原始输出
git diff <baseline>..<commit>                     # 全量 diff，逐条核对
git hash-object <path>                            # 逐文件 SHA
sha256sum <gate-artifact-path>                    # 逐门禁产物 SHA，核对 gate_artifacts[].sha256
```

此外，`Full` 档必须先按权威文件 §3.1 逐条确认复用条件（同 SHA、baseline 一致、`changed_files` 与 tree diff 无遗漏无多余、blob / 产物 hash 匹配、命令前提仍成立）；任一条不满足 → **停止复用并全量复算**，不存在「部分采信」。

---

## 4. 与 SEB 核验、证据不足处置的分工

| 文件 | 负责 |
|---|---|
| 本文件 | **深度选择**：做到哪一档、覆盖多广、是否抽样 |
| `references/seb-integrity-and-insufficiency.md` | **逐字段 SEB 核验 + 证据不足处置表**（应 `Full` 无 SEB、档位不足、hash/commit 漂移、预算耗尽） |
| `skills/artifact-pyramids/references/evidence-levels-and-seb.md` | 档位阈值、SEB 最小字段、复用条件的**唯一权威定义** |
| `references/swarm-verification.md` | 群体模式门禁令牌 `{"gate": "pass"|"block"}`；与 Kanban G1/G2 模式术语不同，勿混用结论格式 |

---

## 5. 平台边界（不得声称已实现）

- 档位选择与按档核验是**文档层纪律**：运行时**没有**「按 `evidence_level` 自动选深度」「自动全量复算」或「自动门禁超时降级」的钩子；抽样与核验目前由 reviewer 手工执行，无平台强制。
- 不得把「本文件写了规则」表述为「运行时已自动核验」。

---

## SOURCES

```
skills/artifact-pyramids/references/evidence-levels-and-seb.md
 -> 唯一权威出处：四档阈值与升级触发器（§1）、SEB 最小字段（§2）、
    复用条件与完整性核验五步（§3）、交接字段（§4）
skills/orchestration-methodology/references/delivery-governance.md
 -> §6 交接治理字段名；§6.1 reviewer 交接证据要求；§6.2 证据不足处置
skills/review-methodology/references/seb-integrity-and-insufficiency.md
 -> 逐字段 SEB 核验与证据不足处置表（本文件只管深度选择）
skills/review-methodology/references/swarm-verification.md
 -> 群体模式门禁令牌（`{"gate": pass|block}`），与 Kanban 模式映射关系
skills/review-methodology/SKILL.md
 -> 评审入口；本文件应经 §评审类型表引用后才可达
```
