# QA 方法论参考：测试自动化、质量门与质量指标

> 面向 QA 工程师的综合参考资料，涵盖测试自动化模式、质量门设计和质量指标。研究于 2026 年 6 月。

---

## 目录

1. [测试框架选择](#1-测试框架选择)
2. [CI 集成：并行执行、分片与测试拆分](#2-ci-集成并行执行分片与测试拆分)
3. [不稳定测试管理](#3-不稳定测试管理)
4. [质量门](#4-质量门)
5. [质量指标](#5-质量指标)

---

## 1. 测试框架选择

### 1.1 框架决策矩阵

| 准则 | pytest | Playwright | Vitest | Cypress |
|---|---|---|---|---|
| **语言** | Python | JS/TS、Python、.NET、Java | JS/TS（基于 Vite） | JS/TS（捆绑） |
| **主要领域** | 单元、集成、API | 浏览器 E2E、移动端（WebKit） | 单元、组件、E2E | 浏览器 E2E、组件 |
| **浏览器支持** | 不适用 | Chromium、Firefox、WebKit、Edge | 通过 Playwright/WDIO 浏览器模式 | Chromium、Firefox、Edge、WebKit |
| **并行能力** | pytest-xdist | 内置 worker + 分片 | 内置 worker 池 + 分片 | Dashboard 并行化（付费） |
| **自动等待** | 不适用 | 是（内置） | 不适用（VDOM 断言） | 是（内置、可重试） |
| **网络模拟** | responses / pytest-httpx | route() API | vi.mock / msw | cy.intercept() |
| **调试** | pdb / --pdb | Trace viewer、截图、视频 | 浏览器 DevTools | 时间旅行、快照 |
| **CI 优先？** | 是 | 是（blob 报告、分片） | 是（分片、池） | 基于 Dashboard |
| **社区** | 成熟，1 万多个插件 | 快速增长，微软支持 | 持续增长，Vite 生态 | 庞大、成熟 |
| **最适合** | Python 项目、数据/API 测试 | 多浏览器 E2E、跨平台 | Vite/React/Vue 组件与单元测试 | 与开发集成的 E2E、组件测试 |

### 1.2 各框架的使用时机

**pytest**
- 任意规模的 Python 项目
- 针对后端的 API/集成测试
- 数据流水线验证、数据库测试
- 大规模参数化测试（内置）
- 需要 500 多个插件时（django、mock、cov、xdist、splinter）
- 架构：使用限定作用域 fixture 的 `conftest.py` 层级

**Playwright**
- 跨浏览器 E2E（Chromium + Firefox + WebKit）
- 移动 Web 测试（模拟）
- 网络拦截和模拟
- CI 速度很重要时（原生分片 + worker）
- 使用 Trace viewer 调试不稳定测试
- 与浏览器测试一起进行 API 测试（请求上下文）

```typescript
// CI 中的 Playwright 分片
// npx playwright test --shard=1/4
// npx playwright test --shard=2/4
```

**Vitest**
- 基于 Vite 的项目（React、Vue、Svelte）
- 使用 HMR 的组件测试（开发期间即时反馈）
- 需要 ES module 支持的单元测试
- 希望使用兼容 Jest 但速度更快的 API 时
- 用于有限 E2E 的浏览器模式（实验性）

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    globals: true,
    pool: 'forks', // 或 'threads'
    poolOptions: { threads: { singleThread: true } },
  },
})
```

**Cypress**
- 面向开发人员、重视调试体验的 E2E
- 已处于 JS 生态中的团队
- React/Vue 组件测试（实验性）
- 时间旅行调试必不可少时
- 注意：没有付费计划时，跨浏览器能力有限（不支持 Safari）

### 1.3 框架选择决策流

```
项目是否使用 Python？
   |-- 是 --> 使用 pytest（通过 xdist 提速）
   |-- 否 --> 是否为基于 Vite 的 JS/TS 项目？
                 |-- 是 --> 单元/组件：Vitest
                 |          E2E：Playwright 或 Cypress
                 |-- 否 --> 非 Vite 的 JS/TS：Playwright（E2E）+ Jest/Vitest（单元）
```

---

## 2. CI 集成：并行执行、分片与测试拆分

### 2.1 三个并行层级

| 层级 | 作用 | 工具 |
|---|---|---|
| **作业内（多 worker）** | 多项测试在同一台机器上并行运行 | `pytest -n auto`（xdist）、Playwright worker、Vitest 池 |
| **跨作业（分片）** | 测试套件拆分成 N 组，每组在独立 CI runner 上运行 | `--shard=x/y`、matrix 策略 |
| **跨套件** | 不同测试类型（单元、集成、E2E）在独立 CI 作业中运行 | CI matrix、工作流编排 |

### 2.2 Pytest 并行

**pytest-xdist（节点内）**
```bash
# 自动检测 CPU 数量
pytest -n auto

# 固定 worker 数量
pytest -n 4

# 按作用域分配：每个 worker 获得一部分测试
pytest -n 4 --dist loadscope   # 同一模块中的测试保持在一起
pytest -n 4 --dist loadfile    # 同一文件中的测试保持在一起
pytest -n 4 --dist worksteal   # 动态重新平衡（pytest-xdist 3.x+）
```

**pytest-split（跨 CI 作业）**
```bash
# 作业 1
pytest --splits 4 --group 1

# 作业 2
pytest --splits 4 --group 2

# 使用 --store-durations 的计时数据平衡各组
```

```yaml
# GitHub Actions：pytest-split 与 matrix
jobs:
  test:
    strategy:
      matrix:
        group: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - run: pip install pytest pytest-split
      - run: pytest --splits 4 --group ${{ matrix.group }}
```

### 2.3 Playwright 分片

```yaml
# playwright.config.ts
export default defineConfig({
  fullyParallel: true, // 在测试层而非文件层拆分
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',
})

# 使用 matrix 的 GitHub Actions
# npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
jobs:
  test:
    strategy:
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report

  merge-reports:
    if: always()
    needs: [test]
    steps:
      - uses: actions/download-artifact@v4
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
```

**分片平衡技巧**
- `fullyParallel: true` 在单项测试层拆分，以实现均匀分配
- 不使用 `fullyParallel` 时，分片在文件层拆分（包含大量测试的文件会造成不平衡）
- 在 CI 中使用 `blob` reporter 捕获跨分片结果
- 将报告合并为单个 HTML，以便汇总查看

### 2.4 Vitest 分片

```bash
# CLI 分片
vitest --shard=1/4
vitest --shard=2/4

# 使用 matrix 的 GitHub Actions
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npx vitest --reporter=junit --shard=${{ matrix.shard }}/4
```

**Vitest 池选项**
| 池 | 说明 | 最适合 |
|---|---|---|
| `threads`（默认） | 使用 worker_threads，速度最快 | 纯单元测试 |
| `forks` | 使用 child_process，隔离性更好 | 有副作用的测试 |
| `vmThreads` | 在线程内使用 vm 模块 | 需要模块沙箱的测试 |

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: false,
        maxForks: 4,
        minForks: 1,
      },
    },
  },
})
```

### 2.5 Cypress 并行化

Cypress 需要使用 **Dashboard** 服务（付费）才能原生并行化：

```bash
# 在可用 CI 机器之间自动扩缩
cypress run --record --parallel
```

也可以使用 **cypress-split**（开源）手动拆分：
```bash
# 作业 1
cypress run --env split=1,of=4

# 作业 2
cypress run --env split=2,of=4
```

### 2.6 CI 测试分配最佳实践

1. **记录历史计时数据**——pytest-split 等工具使用之前的运行时长来平衡各组。先在基线上运行 `--store-durations`。
2. **设置作业级超时**——防止挂起的 worker 阻塞流水线。
3. **严重失败时快速失败**——将严重（阻断）测试与建议性测试分开，使严重失败尽早停止流程。
4. **使用依赖缓存**——在分片之间缓存 node_modules、.cache 和 pip 包。
5. **按耗时分片，而不是按字母顺序**——按字母顺序拆分测试会产生不均衡的分组。

---

## 3. 不稳定测试管理

### 3.1 定义与影响

> 不稳定测试（flaky 或 flakey test）是指在代码和测试环境均未变化的情况下，产生不一致结果的自动化测试——一次运行通过，下一次运行失败。

**影响摘要**
- **PR 延迟**——开发人员重新运行作业或请求覆盖
- **CI 成本提高**——重复运行消耗计算资源
- **失去信任**——团队绕过自动化，改用人工检查
- **客户风险**——真实缺陷被噪声掩盖
- **可量化**：每天运行 10,000 项测试时，5% 的不稳定率 = 每天 500 次误失败（每周损失约 40 多小时）

### 3.2 根因

| 类别 | 示例 | 修复模式 |
|---|---|---|
| **异步/竞态条件** | 元素就绪前点击、DOM 尚未更新 | 显式等待、自动等待框架 |
| **外部依赖** | API 延迟、数据库连接不稳定 | 模拟/存根外部服务 |
| **未受控测试数据** | 随机数据、数据碰撞 | 带种子的随机性、幂等设置 |
| **环境问题** | CI 资源争用、时钟偏差 | 增加资源、隔离测试环境 |
| **状态泄漏** | 共享可变状态、错误的 teardown | 每项测试隔离状态、fixture 清理 |
| **测试相互依赖** | 测试 B 依赖测试 A 的状态 | 完全独立的测试、随机执行顺序 |

### 3.3 检测策略

```bash
# 重复测试以复现不稳定性
pytest --repeat 20 test_flaky.py
npx playwright test --repeat-each=20
npx vitest --repeats 10
```

**自动检测**
1. **重试分析**——跟踪哪些测试首次尝试失败、重试后通过
2. **跨环境比较**——比较不同分支和 CI runner 的通过/失败情况
3. **统计趋势**——持续跟踪每项测试的不稳定率（失败次数/总运行次数）
4. **老化测试**——允许新测试进入主套件之前，先在 CI 中运行 100 次以上

### 3.4 管理框架

```
检测 --> 衡量 --> 排定优先级 --> 解决 --> 预防
```

| 阶段 | 行动 |
|---|---|
| **检测** | 重试（2-3 次）、repeat-each 运行、跨分支分析 |
| **衡量** | 不稳定率 = 失败次数/运行次数；设置阈值（<1-2%） |
| **排定优先级** | 优先修复核心工作流/关键路径测试；隔离非关键测试 |
| **解决** | 本地复现，检查 trace/日志/视频，稳定等待/选择器 |
| **预防** | 分配所有权、不稳定性预算、仪表盘 + 告警 |

### 3.5 自动重试与隔离

| 策略 | 工作方式 | 使用时机 |
|---|---|---|
| **自动重试** | 首次尝试失败的测试在报告失败前重试 1-3 次 | 冒烟测试、允许 1-2% 不稳定率的 CI |
| **隔离** | 将不稳定测试移入独立套件；继续运行但不阻塞流水线 | 不稳定率 >5% 或正在阻塞 PR 的测试 |
| **阻断** | 测试每次都必须在不重试的情况下通过 | 关键路径测试、安全、支付流程 |

```yaml
# Playwright：有限自动重试
# playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
})
```

### 3.6 稳定化模式

**稳定的选择器和等待（Playwright）**
```typescript
// 错误：盲目休眠
await page.waitForTimeout(3000)

// 正确：等待可观察状态
await expect(page.locator('[data-testid="submit"]')).toBeVisible({ timeout: 5000 })
await page.waitForLoadState('networkidle')
await page.waitForResponse(resp => resp.url().includes('/api/login') && resp.status() === 200)
```

**受控测试数据（pytest）**
```python
import uuid

def test_create_user(db_session):
    unique_email = f"test-{uuid.uuid4()}@example.com"
    # 使用 unique_email 防止碰撞
```

**隔离的 fixture（pytest）**
```python
@pytest.fixture(autouse=True)
def clean_state(db_session):
    yield
    db_session.rollback()  # 绝不在测试之间泄漏状态
```

**模拟外部服务**
```python
# 使用 responses 库的 pytest
import responses

@responses.activate
def test_api_call():
    responses.get("https://api.example.com/data", json={"key": "value"})
    # 此测试现在不会因网络产生不稳定性
```

### 3.7 老化测试协议

新测试进入主套件前应证明其可靠性：

1. **提交测试** → 在 PR 流水线中运行
2. **老化期** → 在 CI 中运行 100 次以上（后台作业或每夜执行）
3. **稳定性检查** → 如果不稳定率 > 阈值，隔离至修复完成
4. **提升** → 证明稳定后移入主测试套件

---

## 4. 质量门

### 4.1 定义与核心原则

> 质量门是内置于流水线中的强制措施；软件进入下一阶段或发布之前必须满足它。

**核心原则**

| 原则 | 说明 |
|---|---|
| **左移** | 尽早捕获问题——先静态分析，再单元测试，然后集成测试 |
| **默认自动化** | 优先使用自动化质量门；只有监管合规要求时才使用人工批准 |
| **快速反馈** | 先运行快速质量门（lint、单元测试）；后运行较慢质量门（E2E、性能） |
| **通过/失败无歧义** | 准则必须是二元的——不存在“基本通过” |
| **允许人工覆盖** | 必须存在可问责的紧急绕过机制（多方批准、审计跟踪） |
| **随时间演进** | 随项目成熟逐步收紧质量门阈值 |

### 4.2 质量门类型：阻断、建议与信息

| 类型 | 行为 | CI 信号 | 示例 |
|---|---|---|---|
| **阻断** | 流水线停止。产物不提升。发布被阻止。 | ❌ 红色 | 单元测试失败、安全漏洞 |
| **建议** | 流水线继续。记录警告并通知团队。 | ⚠️ 仅警告 | 代码覆盖率降至阈值以下、lint 警告 |
| **信息** | 不影响流水线。指标记录到仪表盘。 | ℹ️ 信息 | 测试执行时间趋势、不稳定率 |

**按阶段混合使用阻断门和建议门：**

```
提交 --> [Lint（建议）] --> [单元测试（阻断）]
  --> [构建（阻断）] --> [静态分析（建议）]
    --> [集成测试（阻断）] --> [E2E 测试（阻断）]
      --> [性能/负载（建议）] --> [安全扫描（阻断）]
        --> [人工批准（阻断）] --> 发布
```

### 4.3 各流水线阶段的常见质量门

| 阶段 | 质量门 | 类型 | 阈值 |
|---|---|---|---|
| **代码提交** | Lint/格式化 | 建议 | 0 个错误；记录格式化警告 |
| **构建** | 编译 | 阻断 | 0 个编译错误 |
| **单元测试** | 通过率 | 阻断 | 100% 通过（已知失败 = 0） |
| **代码覆盖率** | 覆盖率阈值 | 建议 → 阻断 | 单元 ≥ 80%，集成 ≥ 60% |
| **静态分析** | 缺陷/代码异味 | 阻断 | 0 个严重/阻塞缺陷 |
| **安全** | SAST/依赖检查 | 阻断 | 0 个高于阈值的已知 CVE |
| **集成测试** | 通过率 | 阻断 | 100% 通过 |
| **E2E 测试** | 通过率 | 阻断 | 100% 通过（含不稳定测试重试预算） |
| **性能** | 响应时间/吞吐量 | 建议 | p95 < 500ms，不允许 >10% 的回归 |
| **不稳定测试** | 隔离数量 | 建议 | 套件中不稳定测试 < N |

### 4.4 在 CI 中实施质量门

**GitHub Actions 示例——分阶段质量门**

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
        continue-on-error: true  # 建议：警告但继续

  unit-tests:
    needs: [lint]
    runs-on: ubuntu-latest
    steps:
      - run: npm test -- --coverage
      - run: |
          # 建议：覆盖率检查（警告但不失败）
          npx istanbul check-coverage --statement=80

  integration:
    needs: [unit-tests]
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:integration
        # 阻断：集成测试必须全部通过

  e2e:
    needs: [integration]
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test
        # 阻断：E2E 必须通过

  security-scan:
    needs: [unit-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: npm audit --audit-level=high
```

**Jenkins Pipeline——声明式质量门**

```groovy
stage('质量门') {
    steps {
        // 阻断：测试通过
        sh 'pytest tests/unit --junitxml=unit-results.xml'

        // 建议：覆盖率
        sh '''
            coverage=$(python -c "import json; d=json.load(open('coverage.json')); print(d['totals']['percent_covered'])")
            if (( $(echo "$coverage < 80" | bc -l) )); then
                echo "警告：覆盖率 ${coverage}% 低于 80% 阈值"
                # 不使构建失败
            fi
        '''

        // 阻断：SonarQube 质量门
        withSonarQubeEnv('SonarQube') {
            sh 'mvn sonar:sonar'
        }
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

### 4.5 安全门

| 检查 | 工具 | 质量门行为 |
|---|---|---|
| **SAST** | SonarQube、Semgrep、CodeQL | 出现严重/高危发现时阻断 |
| **SCA（依赖漏洞）** | Dependabot、Snyk、OWASP DC | CVSS ≥ 7.0 时阻断 |
| **密钥检测** | GitLeaks、TruffleHog | 出现任何硬编码密钥时阻断 |
| **容器扫描** | Trivy、Grype | 出现操作系统级严重 CVE 时阻断 |
| **许可证合规** | FOSSA、LicenseFinder | 商业项目中出现 GPL/AFL 时阻断 |

### 4.6 质量门演进

质量门应随项目和团队成熟而收紧：

```
阶段 1（起步）：
  - 阻断：测试必须编译并通过
  - 建议：覆盖率 > 50%

阶段 2（成长）：
  - 阻断：单元测试通过、覆盖率 > 70%、0 个严重 SonarQube 问题
  - 建议：覆盖率 > 80%、安全扫描无问题

阶段 3（成熟）：
  - 阻断：所有测试通过、覆盖率 > 80%、0 个阻塞/严重 SonarQube 问题、0 个高危 CVE
  - 建议：覆盖率 > 85%、不稳定率 < 2%

阶段 4（高绩效）：
  - 阻断：所有测试通过、覆盖率 > 85%、0 个 SonarQube 缺陷、0 个高于阈值的 CVE
  - 建议：覆盖率 > 90%、性能回归 < 5%、不稳定率 < 1%
```

**质量门复审节奏：**每季度重新评估质量门阈值。如果某个质量门从未触发（所有 PR 都轻易通过），考虑将其收紧。如果某个质量门触发过于频繁（50% 以上的 PR 被阻断），在团队提高代码质量期间暂时放宽。

### 4.7 常见反模式

| 反模式 | 问题 | 修正方式 |
|---|---|---|
| **阻断门过多** | 开发人员绕过或操纵流水线 | 只对关键检查使用阻断门；其余全部使用建议门 |
| **质量门从不变化** | 阈值随项目演进变得无关 | 每季度复审，逐步收紧 |
| **只衡量覆盖率，不衡量质量** | 未测试逻辑达到 90% 覆盖率会产生误导 | 将覆盖率与变异测试或代码审查结合 |
| **单个不稳定测试阻断整条流水线** | 团队失去对 CI 的信任 | 自动隔离不稳定测试；区分阻断与建议套件 |
| **所有事项都使用人工质量门** | 流水线成为瓶颈 | 自动化所有可脚本化事项；只为监管签字保留人工步骤 |

---

## 5. 质量指标

### 5.1 5-10 法则

只跟踪能够直接为决策提供信息的 **5-10 项核心指标**。少于 5 项会遗漏信号；超过 10 项会导致分析瘫痪，并降低可行动性。

### 5.2 指标分类

| 类型 | 定义 | 示例 |
|---|---|---|
| **绝对指标** | 原始计数 | 已运行测试、已发现缺陷、代码行数 |
| **派生指标** | 比率/百分比 | 覆盖率、通过率、缺陷密度 |
| **领先指标** | 预测未来质量 | 测试覆盖率、执行状态、代码复杂度 |
| **滞后指标** | 验证过去结果 | 生产逃逸缺陷、客户投诉、MTTR |
| **有效性指标** | 测试是否捕获缺陷？ | 缺陷检测百分比、测试有效性比率 |
| **效率指标** | 测试有多快？ | 测试执行时间、测试缺陷修复所需时间 |

### 5.3 核心指标——公式与指引

#### 5.3.1 测试覆盖率

```text
行覆盖率 =（已执行行数 / 总行数）× 100
分支覆盖率 =（已执行分支数 / 总分支数）× 100
函数覆盖率 =（已调用函数数 / 总函数数）× 100
```

**实践指引：**
- 100% 覆盖率是陷阱——达到约 80% 后回报递减
- 将覆盖聚焦于高风险领域：支付流程、认证、数据转换
- 结合**行覆盖率** + **分支覆盖率**（只有行覆盖率会遗漏 `if` 分支）
- 变异测试（pitest、mutmut）可验证覆盖质量——行覆盖率高但变异评分低，说明测试实际上没有断言行为

```bash
# pytest 覆盖率
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# vitest 覆盖率
npx vitest --coverage --coverage.thresholds.lines 80
```

#### 5.3.2 缺陷密度

```text
缺陷密度 = 已确认缺陷总数 / 软件规模（LOC 或功能点）
```

**解读：**
- 越低越好，但上下文很重要（复杂模块自然具有更高密度）
- **按严重程度分层**：严重：0.5/KLOC，轻微：2/KLOC → 密度相同，风险特征不同
- **按模块分层**：找出密度异常高的模块，进行针对性重构
- **与覆盖率结合**：缺陷密度高 + 覆盖率低 = 急需改进

**常见陷阱：**
- 在不同类型的项目之间比较缺陷密度（库与应用）
- 将重复/不会修复的缺陷计入数量
- 未按代码复杂度归一化（简单 CRUD 模块与复杂算法）

#### 5.3.3 测试有效性

```text
测试有效性 =（测试发现的缺陷数 / 发现的缺陷总数）× 100

或者采用更实用的公式：
DDP（缺陷检测百分比）=（发布前发现的缺陷数 /（发布前 + 发布后发现的缺陷数））× 100
```

**目标：**DDP > 95% 意味着进入生产环境的缺陷少于 5%。

**衡量测试捕获的内容：**
- 跟踪哪些测试实际发现了缺陷（在缺陷跟踪系统中关联）
- 识别从不失败的测试 → 考虑删除或重写
- **回归测试有效性**：已修复缺陷中有多少增加了回归测试？目标 > 80%。

#### 5.3.4 MTTD（平均检测时间）

```text
MTTD =（检测时间 - 引入时间）之和 / 发现的缺陷总数
```

其中，检测时间 = 首次观察到缺陷的时间（而不是报告时间）。

| 场景 | 典型 MTTD | 解读 |
|---|---|---|
| 自动化测试在 PR 中捕获缺陷 | 分钟 | 优秀——左移检测 |
| 在预发布 CI 中捕获 | 小时 | 良好 |
| 在 QA 期间捕获 | 天 | 需要更快反馈 |
| 由生产监控捕获 | 数小时至数天 | 对边界情况可接受 |
| 由生产环境中的客户报告捕获 | 数天至数周 | 糟糕——应投资监控 |

**降低 MTTD：**
- 扩大自动化测试覆盖范围
- 改进生产监控（APM、错误跟踪）
- 使用功能开关逐步发布
- 真实用户监控（RUM）和会话回放

#### 5.3.5 MTTR（平均解决/修复时间）

```text
MTTR =（解决时间 - 检测时间）之和 / 已修复缺陷总数
```

MTTR 包括：分诊 → 调试 → 修复 → 测试 → 部署

**按严重程度划分的目标：**
| 严重程度 | 目标 MTTR |
|---|---|
| 严重（P0） | < 1 小时 |
| 高（P1） | < 4 小时 |
| 中（P2） | < 24 小时 |
| 低（P3） | < 1 周 |

**降低 MTTR：**
- 自动回滚（快速恢复）
- 使用功能开关禁用有问题的代码，无需重新部署
- 结构化调试工具（Playwright trace、日志关联）
- 事件后复盘，以消除流程瓶颈

#### 5.3.6 缺陷逃逸率

```text
缺陷逃逸率 = 生产缺陷数 /（生产前缺陷数 + 生产缺陷数）× 100
```

**解读：**
- < 5%：强健的 QA 流程
- 5-15%：一般——仍有改进空间
- > 15%：存在显著逃逸模式——应投资左移测试

### 5.4 指标可视化

**推荐的仪表盘结构：**

```
╔══════════════════════════════════════╗
║  质量仪表盘——Sprint 24              ║
╠══════════════════════════════════════╣
║  通过率     │  覆盖率    │ 缺陷     ║
║  98.5% ✓    │  83% ⚠️    │  12 (3 P1)║
╠══════════════════════════════════════╣
║  DDP        │  MTTD      │ MTTR     ║
║  94% ✓      │  2.1h ✓    │  4.5h ⚠️ ║
╠══════════════════════════════════════╣
║  不稳定率   │  套件时长  │ 预算     ║
║  1.2% ✓     │  14m ✓     │  62% ▓██ ║
╚══════════════════════════════════════╝
```

### 5.5 按方法论选择指标

| 方法论 | 优先指标 |
|---|---|
| **Agile/Scrum** | Sprint 通过率、缺陷逃逸率、测试执行状态、按速度调整的覆盖率 |
| **Kanban** | 测试前置时间、单次修复周期时间、流动效率、WIP 限制 |
| **CI/CD** | 构建稳定性、部署频率、变更失败率、MTTD、MTTR |
| **Waterfall** | 需求覆盖率、各阶段缺陷密度、测试用例有效性 |

### 5.6 数据驱动的质量文化

**实施原则：**
1. **能否采取行动？**——如果指标发生变化，你是否知道下一步该做什么？如果不知道，就不要跟踪它。
2. **能否定期更新？**——使刷新频率与决策节奏匹配（CI 每日、覆盖率每个 Sprint、趋势每月）。
3. **与目标对齐**——更快发布 = 同时跟踪速度 + 质量（变更失败率）。
4. **避免虚荣指标**——“已执行测试”是活动；“捕获真实缺陷的测试”才是价值。
5. **广泛共享**——开发人员、PM 和高管都获得同一数据中与其相关的切片。

---

## 快速参考摘要

### 测试框架速查表

| 需求 | 选择 |
|---|---|
| Python API/单元测试 | pytest + xdist + pytest-cov |
| 多浏览器 E2E | Playwright（分片、trace viewer） |
| Vite/React 组件测试 | Vitest（HMR、浏览器模式） |
| 面向开发的 E2E 调试 | Cypress（时间旅行、可重试） |

### CI 并行速查表

| 工具 | 节点内 | 跨 CI 作业 | 耗时平衡 |
|---|---|---|---|
| pytest | `-n auto`（xdist） | pytest-split（`--splits N --group X`） | `--store-durations` |
| Playwright | `workers: N` | `--shard=x/y` | `fullyParallel: true` |
| Vitest | `poolOptions.forks.maxForks` | `--shard=x/y` | 池级平衡 |
| Cypress | 自动（Dashboard） | `--parallel`（Dashboard）或 cypress-split | Dashboard 管理 |

### 质量门速查表

| 质量门 | 阶段 | 类型 | 阈值 |
|---|---|---|---|
| 单元测试通过 | 构建 → 集成 | 阻断 | 100% |
| 覆盖率 ≥ 80% | 单元测试后 | 建议 → 阻断 | 行 + 分支 |
| 无严重 SonarQube 问题 | 静态分析 | 阻断 | 0 个阻塞 + 严重问题 |
| 无高危 CVE | 安全扫描 | 阻断 | CVSS ≥ 7.0 |
| E2E 测试通过 | 部署前 | 阻断 | 100%（重试预算） |
| 性能回归 < 10% | 负载测试 | 建议 | p95、吞吐量 |

### 质量指标速查表

| 指标 | 目标 | 公式 |
|---|---|---|
| 缺陷检测百分比 | > 95% | 发布前 /（发布前 + 发布后）× 100 |
| 缺陷密度 | < 1/KLOC（严重），< 5/KLOC（全部） | 缺陷数 / LOC × 1000 |
| 行覆盖率 | > 80% | 已执行行数 / 总行数 × 100 |
| MTTD | < 2 小时 | 检测时间之和 / 缺陷数 |
| MTTR（严重） | < 1 小时 | 解决时间之和 / 修复数 |
| 不稳定率 | < 2% | 不稳定失败次数 / 总运行次数 × 100 |
| 缺陷逃逸率 | < 5% | 生产缺陷数 / 缺陷总数 × 100 |

---

*文档生成于 2026 年 6 月。来源包括 Playwright 文档、Vitest 文档、SonarSource、TestRail、Currents、Information Week、MinimumCD Practice Guide，以及领先 QA 团队的行业模式。*
