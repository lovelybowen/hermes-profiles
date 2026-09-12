# Intake 快速路径：一页决策树

小任务 intake 的**快速分类入口**。目标：对无歧义的小任务，在只加载本文件的情况下完成 T 类 / 风险 / 门禁 / 证据档位判定，产出与完整流程**同格式**的六字段 intake 块——下游不需要知道这条判定来自快速路径还是完整流程。

本文件是 `requirements-intake.md` + `gate-topology.md` 的**摘要执行层**，不是权威出处。任何与权威文件冲突之处，以权威文件为准。

## 1. 何时可以用快速路径

同时满足：

1. 请求**单一且无歧义**（一句话到一段话，只有一个可判定目标）；
2. 你能在**不加载其余参考文件**的情况下确信改动面很小；
3. 不需要向 Intent Owner 澄清业务语义。

任一不满足 → 回退完整流程：`skill_view('orchestration-methodology', file_path='references/requirements-intake.md')` 与 `references/gate-topology.md`。

## 2. 决策树

```
请求是否要改代码 / 配置 / 文档？
├─ 否（答问、讨论、研究）            → T0/T1，G0，L0，仅 orchestrator 直接回答，不建实现卡
└─ 是
   ├─ 是否命中高风险清单？（鉴权/权限、支付/资金、数据迁移、公开 API、
   │    数据库 schema、密钥/PII、依赖供应链、跨服务契约）
   │  └─ 是 → T5/T6 或按 §8 升级，G2，Full —— 退出快速路径，加载完整参考
   └─ 否
      ├─ 单文件 且 ≤30 行 且 无新增/升级依赖 且 验收可一条命令判定？
      │  └─ 是 → **L0 快速通道**（gate-topology.md §4.1）：
      │          T2（文档）/ T4（代码），G1，evidence_level: L0
      │          基线用三项简化基线（requirements-intake.md §1 例外）
      │          不建 QA 卡、不建综合卡；工程师自验命令 + exit code 进交接
      └─ 否 → 按 evidence-levels-and-seb.md §1.3 升级触发器落档：
               多文件 / >30 行 → L1；跨模块 / 接口 / 依赖 → L1+L2
               （T4 仍建 QA 卡；此时若需完整规则，回退加载 gate-topology.md）
```

## 3. 机械信号（可选，先算再判）

判定「单文件 / ≤30 行 / 无依赖」不必靠目测。可用共享技能脚本从 diff 机械计算：

```bash
python skills/orchestration-methodology/scripts/intake_signals.py \
  --repo <项目路径> --baseline <基线 rev>          # 已提交对比
python .../intake_signals.py --repo <项目路径>      # 未提交改动（工作区 vs HEAD）
```

输出 JSON：文件数、增删行数、是否触碰依赖文件、高风险路径命中、建议档位。**脚本是辅助信号：机械部分（行数、文件数、路径模式）应当采纳，业务风险判断（这个 counter 是否计费）永远留给 orchestrator。** 脚本建议升档而理由不充分时，按保守方向处理。

## 4. 产出：六字段 intake 块（与完整流程同格式）

```yaml
task_class: T0 | T1 | T2 | T3 | T4 | T5 | T6
risk: R-none | R-low | R-moderate | R-high | R-critical
gate: G0 | G1 | G2
evidence_level: L0 | L1 | L1+L2 | Full
reason: <改动面 / 不可逆性 / 爆炸半径 的一句话依据>
evidence: <原始请求 / intake 卡 id + intake_signals.json 路径（如使用）>
```

写入任务卡 body 与交接消息，两处同值同义——快速路径**不豁免**这个纪律（`requirements-intake.md` §6.1）。

## 5. 快速通道的退出条件

实现中任一信号出现，工程师立即停止并 `needs_reclass: true` 交回：

- 改动将超出单文件 / 30 行；
- 需要动依赖、接口签名、配置 schema；
- 发现业务风险命中高风险清单。

orchestrator 收到后按完整流程重新分类，**不得沿用旧档位**。

## 6. 示例：counter 按钮

「在现有 Vue 组件里增加可点击 counter，点击后数字加一」

- 单文件（`src/components/Counter.vue`）、约 10 行、无依赖、无接口变化、不在高风险清单
- → `task_class: T4`，`risk: R-low`，`gate: G1`，`evidence_level: L0`
- → 一张 frontend-engineer 实现卡；交接含 `npm test -- Counter -> exit 0`
- → 不建金字塔、不建 QA 卡；reviewer 可选，跳过则记录原因

若后续变为「点击调用后端接口、写库、另一页面实时显示」→ 命中接口 + 跨模块 → 退出快速通道，L1+L2，T4 建 QA 卡。

SOURCES

```
references/gate-topology.md
 -> §4.1 L0 快速通道、§2 T0–T6 分类、§4 决策矩阵、§8 人工升级条件（权威出处）
references/requirements-intake.md
 -> §1 七字段基线与 L0 三项简化基线、§6.1 intake 记录块（权威出处）
../artifact-pyramids/references/evidence-levels-and-seb.md
 -> §1.1 L0 阈值、§1.3 升级触发器（档位权威出处）
scripts/intake_signals.py
 -> 机械信号计算（本文件 §3 的实现）
```
