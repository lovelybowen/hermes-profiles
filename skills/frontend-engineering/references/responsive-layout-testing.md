# 前端工程方法论参考

> 全面介绍响应式布局系统、断点策略、
> 跨设备测试，以及前端测试模式（组件、集成、
> 视觉回归、无障碍和测试数据管理）的参考资料。
>
> 编制时间：2026 年 6 月

---

## 目录

1. [响应式布局系统](#1-响应式布局系统)
2. [断点策略](#2-断点策略)
3. [跨设备测试方法论](#3-跨设备测试方法论)
4. [前端测试概览](#4-前端测试概览)
5. [组件测试](#5-组件测试)
6. [集成测试](#6-集成测试)
7. [视觉回归测试](#7-视觉回归测试)
8. [无障碍测试](#8-无障碍测试)
9. [测试数据管理](#9-测试数据管理)

---

## 1. 响应式布局系统

### 核心理念

> **“CSS Grid 用于布局；Flexbox 用于对齐。”**
>
> 根据问题的维度选择合适的工具。

现代 CSS 提供三种布局原语，每种都适合处理不同的关注点。
现代方法会将三者结合使用，而不是三选一。

### 1.1 CSS Grid——二维布局

**最适合：** 页面级结构、复杂的多轴布局、精确的空间控制，
以及行和列同时重要的布局。

| 使用场景 | 示例 |
|---|---|
| 整页模板 | 页眉、侧边栏、主体和页脚区域 |
| 卡片网格 | 图库、仪表盘、电商列表 |
| 元素重叠 | 首屏区、杂志式布局 |
| 原生间距布局 | 使用 `gap` 属性避免通过外边距变通 |
| 基于比例的尺寸 | `fr` 单位、`minmax()`、`auto-fill`/`auto-fit` |

**关键模式：**

```css
/* 无需媒体查询的响应式网格 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1rem;
}

/* 用于页面布局的命名网格区域 */
.page {
  display: grid;
  grid-template-areas:
    "header  header"
    "sidebar main"
    "footer  footer";
  grid-template-columns: 1fr 3fr;
}
```

**何时应选择 Grid 而不是 Flexbox：**
- 需要同时控制行和列
- 希望显式放置元素（grid-column / grid-row）
- 已有预定义的布局结构（布局优先设计）
- 需要无需变通方案即可重叠元素
- 正在构建页面级模板

### 1.2 Flexbox——一维对齐

**最适合：** 组件级布局、线性序列、动态内容流、
居中，以及沿单一轴分布项目。

| 使用场景 | 示例 |
|---|---|
| 导航栏 | 水平链接列表、工具栏 |
| 卡片内部布局 | 标签与值组成的行、按钮组 |
| 居中 | 内容垂直或水平居中 |
| 动态换行 | 标签、筹码、徽章列表 |
| 灵活间距 | 在页脚上使用 `justify-content: space-between` |
| 重新排序 | 使用 `order` 属性实现响应式重排 |

**关键模式：**

```css
/* 居中 */
.container {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式换行 */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* 经典的两端间距布局 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

**何时应选择 Flexbox 而不是 Grid：**
- 内容沿一个方向流动（行或列，而非两者同时）
- 项目尺寸未知，且应由项目决定布局（内容优先设计）
- 只需要简单的居中或对齐
- 正在构建可复用 UI 组件（按钮、导航、工具栏）
- 项目需要自然换到下一行

### 1.3 容器查询——组件级响应式

**最适合：** 必须根据父容器而非视口尺寸进行适配的可复用组件。
这代表了从以视口为中心转向
以容器为中心的设计范式。

```css
/* 建立容器上下文 */
.card-grid {
  container-type: inline-size;
  container-name: cards;
}

/* 针对容器进行查询 */
@container cards (width >= 30rem) {
  .card {
    display: grid;
    grid-template: "media body" auto / 2fr 3fr;
  }
  .card__media {
    block-size: 100%;
    object-fit: cover;
  }
}

@container cards (width >= 60rem) {
  .card {
    grid-template: "media body aside" auto / 1fr 2fr 1fr;
  }
}
```

**容器单位：**
| 单位 | 含义 |
|---|---|
| `cqw` | 容器宽度的 1% |
| `cqh` | 容器高度的 1% |
| `cqi` | 容器行内尺寸的 1% |
| `cqb` | 容器块尺寸的 1% |
| `cqmin` | `cqi` 与 `cqb` 中较小者 |
| `cqmax` | `cqi` 与 `cqb` 中较大者 |

**样式查询**（CSS 2025）：根据容器的自定义
属性或状态有条件地应用样式。

```css
@container style(--density: compact) {
  .card { padding: 0.75rem; gap: 0.5rem; }
}

@container style(--theme: surface) {
  .card { background: #fff; color: #111; }
}
```

**何时使用容器查询：**
- 同一组件会出现在多种上下文中（侧边栏与主要内容区）
- 希望获得真正可复用的设计系统组件
- 组件断点不同于页面级断点
- 需要相对于组件而非视口缩放排版

**渐进增强模式：**

```css
/* 基础样式——在所有环境中均可工作 */
.card { display: block; }

/* 增强样式——仅在受支持时启用 */
@supports (container-type: inline-size) {
  .card-wrapper { container-type: inline-size; }
  @container (width >= 25rem) {
    .card { display: grid; grid-template-columns: 1fr 2fr; }
  }
}
```

### 1.4 决策矩阵：Grid、Flexbox 与容器查询

| 标准 | CSS Grid | Flexbox | 容器查询 |
|---|---|---|---|
| **维度** | 二维（行 + 列） | 一维（行或列） | 不适用（只提供上下文） |
| **主要用途** | 页面布局 | 组件对齐 | 组件适配 |
| **内容驱动还是布局驱动** | 布局优先 | 内容优先 | 容器驱动 |
| **间距支持** | 原生 `gap` | 原生 `gap` | 通过宿主布局 |
| **重叠支持** | 原生支持（网格放置） | 并非为此设计 | 不适用 |
| **重新排序** | 通过放置位置 | 通过 `order` | 不适用 |
| **响应式技术** | `auto-fill`/`minmax()` + MQ | `flex-wrap` + MQ | `@container` 查询 |
| **浏览器支持** | 普遍支持 | 普遍支持 | 约 90% 以上（2026 年） |
| **可复用组件** | 可行，但较僵化 | 良好 | 最匹配 |

### 1.5 现代流式布局工具箱（2025+）

除了这三种原语，现代 CSS 还提供流式尺寸工具，可以减少
或消除媒体查询：

```css
/* 流式排版 */
h1 { font-size: clamp(1.5rem, 2.5vw + 1rem, 3rem); }

/* 流式网格列 */
.grid { grid-template-columns: repeat(auto-fill, minmax(clamp(12rem, 30%, 24rem), 1fr)); }

/* 使用 aspect-ratio 实现内在尺寸 */
.card { aspect-ratio: 16 / 9; }

/* 使用逻辑属性支持 RTL */
.card { margin-inline: 1rem; padding-block: 2rem; }
```

---

## 2. 断点策略

### 2.1 设备无关与内容驱动

**2025 至 2026 年的行业共识是：采用内容驱动的断点，而不是
基于设备的预设。**

| 方法 | 说明 | 结论 |
|---|---|---|
| **设备无关** | 在内容布局失效的关键宽度处设置断点（例如 480px、768px、1024px） | 传统最佳实践——优于固定设备定位，但仍以视口为中心 |
| **内容驱动** | 由内容本身决定断点——调整尺寸直到显示不正常，再添加断点 | 现代最佳实践 |
| **容器驱动** | 断点通过 `@container` 位于组件上，而非视口上 | 前沿方法（2025+） |

### 2.2 固定断点的问题

传统断点策略使用设备类别：

```css
/* 避免：设备特定 */
@media (max-width: 575px)   { /* 手机 */ }
@media (min-width: 576px)   { /* 平板 */ }
@media (min-width: 992px)   { /* 笔记本电脑 */ }
@media (min-width: 1200px)  { /* 桌面设备 */ }
```

这种方法会失败，因为：
- 新设备不断出现（折叠屏、超宽屏、二合一设备）
- 同一组件在不同上下文中可能需要不同断点
- 它将布局逻辑与任意屏幕宽度耦合，而这些宽度可能不符合内容的实际需求

### 2.3 内容驱动的断点策略

**方法：**

1. **在浏览器中设计**——逐步调整尺寸；每当布局失效时停下来
2. **在每个失效点添加断点**，根据发生问题的内容命名，而不是根据像素值命名
3. **断点使用 `rem` 而非 `px`**——尊重用户的字号偏好
4. 添加媒体查询前，**优先采用流式技术**（clamp、minmax、auto-fill）

```css
/* 推荐：以 rem 表示的内容驱动断点 */
/* 断点位于 30rem、48rem、64rem */

/* 优先：先使用流式技术，再使用媒体查询 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
}

/* 仅当流式布局不足时才添加媒体查询 */
@media (width >= 64rem) {
  .card-grid { grid-template-columns: repeat(3, 1fr); }
}
```

### 2.4 推荐的断点范围

这些不是固定值，而是内容通常会失效的范围：

| 范围（约） | 常用名称 | 行为 |
|---|---|---|
| < 30rem（约 480px） | 单列 | 堆叠所有内容 |
| 30-48rem（约 480-768px） | 窄屏 | 可以使用两列网格 |
| 48-64rem（约 768-1024px） | 中等 | 三列布局、侧边栏 |
| 64-90rem（约 1024-1440px） | 宽屏 | 完整布局、多列 |
| > 90rem（约 1440px） | 超宽屏 | 最大宽度约束、留白 |

> **关键洞见：** 这些是指导原则，而不是教条。让你的内容决定
> 确切数值。数据表可能需要 50rem，而长篇文章可能
> 只需要 35rem。

### 2.5 现代媒体查询语法

CSS 媒体查询 Level 4+ 引入了范围语法（2025 年已得到广泛支持）：

```css
/* 旧语法 */
@media (min-width: 768px) and (max-width: 1024px) { }

/* 新范围语法——更简洁 */
@media (768px <= width <= 1024px) { }
@media (width >= 48rem) { }
@media (width < 30rem) { }
```

### 2.6 偏好查询（兼顾无障碍）

除了尺寸之外，现代响应式设计还会查询用户偏好：

```css
/* 尊重减少动态效果的偏好 */
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}

/* 尊重减少透明效果的偏好 */
@media (prefers-reduced-transparency: reduce) {
  .glass { background: solid; }
}

/* 尊重深色模式偏好 */
@media (prefers-color-scheme: dark) {
  :root { --bg: #111; --text: #eee; }
}

/* 尊重提高对比度的偏好 */
@media (prefers-contrast: more) {
  .card { border: 2px solid; }
}
```

---

## 3. 跨设备测试方法论

### 3.1 响应式设计测试金字塔

```
        /\
       /  \         手动设备测试
      / M  \        （关键路径使用真实硬件）
     / a  u \
    / n  a  \      设备模拟 E2E
   / u  l    \     （Playwright 模拟矩阵）
  / a  t  e   \
 / l  e  s  t  \
/_______________\   自动化布局安全检查
                   （容器查询、流式布局验证）
```

### 3.2 设备模拟矩阵（Playwright/Cypress）

根据真实用户分析数据定义测试矩阵。常见策略如下：

```javascript
// Playwright 配置——设备模拟
const devices = [
  { name: 'iPhone 15', width: 390, height: 844, deviceScaleFactor: 3 },
  { name: 'Pixel 8', width: 412, height: 915, deviceScaleFactor: 2.625 },
  { name: 'iPad Air', width: 820, height: 1180, deviceScaleFactor: 2 },
  { name: 'Desktop 1440', width: 1440, height: 900, deviceScaleFactor: 1 },
  { name: 'Desktop 1920', width: 1920, height: 1080, deviceScaleFactor: 1 },
];
```

### 3.3 响应式测试检查清单

| 检查项 | 方法 | 工具 |
|---|---|---|
| 内容不溢出 | 自动化 CSS 断言 | Playwright `toHaveCSS` |
| 触摸目标 >= 44px | 自动化尺寸检查 | Playwright 边界框 |
| 无水平滚动条 | 视觉回归 | Percy / Chromatic |
| 字号 >= 16px（避免 iOS 缩放） | 模拟检查 | Safari/iOS 设备 |
| 点击目标不重叠 | 布局检查 | axe-core / 手动 |
| 所有交互元素均可通过触摸操作 | E2E 测试 | Playwright 触摸模拟 |
| 存在 viewport 元标签 | 代码检查 | Lighthouse |

### 3.4 真实设备测试策略

**自动化模拟可覆盖约 80% 的响应式缺陷。** 以下情况需要真实设备：

1. **触摸交互**——悬停状态、拖动、滑动、压力触控
2. **硬件特性**——刘海、灵动岛、相机开孔、安全区域
3. **性能**——真实 CPU/内存限制、网络限速
4. **渲染差异**——Safari 与 Chrome 的字体渲染、亚像素差异

**实践方法：**
- **CI/CD：** 模拟矩阵（Playwright + 设备）
- **拉取请求评审：** 视觉回归（Percy/Chromatic）
- **发布前：** 真实设备云（BrowserStack / Sauce Labs / AWS Device Farm）
- **关键路径：** 团队自有的实体设备

### 3.5 环境模拟

```javascript
// Playwright——响应式与环境模拟
test('慢速 3G 环境下的首页', async ({ page }) => {
  await page.emulate({ viewport: { width: 390, height: 844 } });
  await page.context().addInitScript(() => {
  // 模拟减少动态效果
    window.matchMedia = (query) => ({
      matches: query.includes('reduce-motion'),
      media: query,
      addListener: () => {},
      removeListener: () => {},
    });
  });
  await page.goto('/', { waitUntil: 'networkidle' });
  // 断言……
});
```

---

## 4. 前端测试概览

### 4.1 测试奖杯（现代前端）

使用 Kent C. Dodds 的**测试奖杯**取代传统“测试金字塔”，
它能更好地体现前端测试的优先级：

```
    /\
   /  \        静态分析（TypeScript、ESLint）
  /    \       单元/组件测试（Vitest + Testing Library）
 /      \      集成测试（Playwright / Cypress）
/________\     E2E 测试（仅限关键用户旅程）
```

**静态分析**在编译时捕获类型错误和代码检查问题。
**组件测试**验证隔离的 UI 行为。
**集成测试**（测试套件的主体）验证各项功能能否协同工作。
**E2E 测试**端到端覆盖最关键的用户旅程。

### 4.2 测试矩阵摘要

| 层级 | 工具 | 范围 | 速度 | 不稳定性 | CI 成本 |
|---|---|---|---|---|---|
| 静态 | TypeScript、ESLint | 类型、代码检查 | 即时 | 无 | 免费 |
| 组件 | Vitest + Testing Library | 单个组件 | 快（毫秒） | 低 | 低廉 |
| 集成 | Playwright / Cypress | 功能、页面交互 | 中等（秒） | 低至中 | 中等 |
| 视觉回归 | Percy / Chromatic | 像素级 UI | 中等（秒） | 中 | 较高 |
| 无障碍 | axe-core + Lighthouse | WCAG 违规 | 快（毫秒至秒） | 低 | 低廉 |
| 关键 E2E | Playwright | 完整用户旅程 | 慢（分钟） | 中 | 最高 |

---

## 5. 组件测试

### 5.1 Vitest + React Testing Library

**标准设置（2025 至 2026 年）：**

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true, // 处理 CSS 导入
  },
});
```

```javascript
// src/test/setup.js
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => { cleanup(); });
```

### 5.2 核心查询优先级

**按照用户体验 UI 的方式进行测试：**

```
1. getByRole          — 几乎所有场景的首选
2. getByLabelText     — 表单字段
3. getByPlaceholderText — 输入提示
4. getByText          — 非交互文本
5. getByDisplayValue  — 表单值
6. getByAltText       — 图像
7. getByTitle         — 工具提示
8. getByTestId        — 最后的选择（data-testid）
```

### 5.3 组件测试模式

**渲染 + 交互 + 断言：**

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';

it('点击按钮时递增计数', async () => {
  const user = userEvent.setup();
  render(<Counter />);

  await user.click(screen.getByRole('button', { name: /递增/i }));

  expect(screen.getByText('计数：1')).toBeInTheDocument();
});
```

**测试行为，而不是实现：**

```javascript
// 反例：测试内部状态
expect(counter.state.count).toBe(1);

// 正例：测试用户看到的内容
expect(screen.getByText('计数：1')).toBeInTheDocument();
```

**模拟外部依赖：**

```javascript
import axios from 'axios';
vi.mock('axios');

it('获取后显示帖子', async () => {
  const posts = [{ id: 1, title: '你好' }];
  axios.get.mockResolvedValue({ data: posts });

  render(<PostsList />);

  await waitFor(() => {
    expect(screen.getByText('你好')).toBeInTheDocument();
  });
});
```

**自定义 Hook 测试：**

```javascript
import { renderHook, waitFor } from '@testing-library/react';

it('返回获取的数据', async () => {
  const { result } = renderHook(() => useFetch('/api/data'));

  await waitFor(() => expect(result.current.loading).toBe(false));

  expect(result.current.data).toEqual({ id: 1 });
});
```

### 5.4 最佳实践（组件测试）

| 实践 | 理由 |
|---|---|
| 测试用户可见结果，而非内部实现 | 重构不会破坏测试 |
| 每个测试使用一个断言（可行时） | 失败消息清晰 |
| 使用 `userEvent`，而非 `fireEvent` | 模拟真实交互 |
| 模拟 API 调用，而非模块 | 保持测试快速且聚焦 |
| 优先使用 `screen.` 方法，而非解构 render 的结果 | 保持测试可维护性 |
| 测试之间始终清理 DOM | 防止测试污染 |
| 使用描述性的测试名称 | `it('提交时禁用按钮')` |
| 针对组件契约而非内部实现编写测试 | 测试用于验证行为 |

---

## 6. 集成测试

### 6.1 Playwright 与 Cypress 对比（2025 至 2026 年）

| 维度 | Playwright | Cypress |
|---|---|---|
| **浏览器支持** | Chromium、Firefox、WebKit | Chromium、Firefox（有限）、WebKit（测试版） |
| **语言** | JS/TS、Python、Java、.NET | 仅 JS/TS |
| **架构** | 浏览器协议（CDP）——在浏览器外运行 | 浏览器内——在浏览器内部运行 |
| **多标签页/窗口** | 原生支持 | 有限 |
| **网络模拟** | 路由拦截 | cy.intercept |
| **并行执行** | 原生支持、分片 | 需要 Dashboard |
| **跨域 iframe** | 完整支持 | 有限 |
| **移动设备模拟** | 内置设备描述符 | 仅 cy.viewport |
| **API 测试** | 与浏览器相同的上下文 | cy.request |
| **社区** | 势头更强（State of JS 2025 满意度为 91%） | 成熟，但满意度下降（72%） |
| **CI 集成** | 零配置 | 需要 Dashboard 或插件 |

**结论（2026 年）：** 由于浏览器支持更广、多标签页处理能力更强且
发展势头更好，Playwright 已成为新项目的默认选择。对于已经投入
Cypress 生态的团队，Cypress 仍然可行。

### 6.2 Playwright 集成测试模式

**页面对象模型（POM）——推荐：**

```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() { await this.page.goto('/login'); }
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="submit"]');
  }
  async getErrorMessage() {
    return this.page.textContent('[data-testid="error"]');
  }
}
```

```typescript
// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test('凭据无效时显示错误', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('bad@email.com', 'wrong');

  await expect(loginPage.getErrorMessage()).toContain('凭据无效');
});
```

**使用设备模拟的响应式集成测试：**

```typescript
test('移动端导航可用', async ({ page }) => {
  // 模拟移动端视口
  await page.setViewportSize({ width: 390, height: 844 });

  await page.goto('/');
  await page.click('[data-testid="hamburger"]');
  await expect(page.locator('[data-testid="nav-menu"]')).toBeVisible();

  // 触摸目标达到最小尺寸（44x44 CSS 像素）
  const links = page.locator('nav a');
  const count = await links.count();
  for (let i = 0; i < count; i++) {
    const box = await links.nth(i).boundingBox();
    expect(box?.width).toBeGreaterThanOrEqual(44);
    expect(box?.height).toBeGreaterThanOrEqual(44);
  }
});
```

**在集成测试中模拟 API：**

```typescript
test('无结果时显示空状态', async ({ page }) => {
  // 拦截 API 调用并返回空结果
  await page.route('**/api/search**', async route => {
    await route.fulfill({ json: { results: [] } });
  });

  await page.goto('/search');
  await page.fill('[name="q"]', 'nonexistent');
  await page.press('[name="q"]', 'Enter');

  await expect(page.getByText('未找到结果')).toBeVisible();
});
```

### 6.3 测试组织方式

```
tests/
  e2e/
    login.spec.ts
    checkout.spec.ts
  integration/
    api/
      search.spec.ts
      user.spec.ts
    features/
      filters.spec.ts
      pagination.spec.ts
  visual/
    homepage.spec.ts
    product-card.spec.ts
  accessibility/
    homepage.a11y.spec.ts
    form.a11y.spec.ts
```

---

## 7. 视觉回归测试

### 7.1 方法

| 方法 | 工具 | 优点 | 缺点 |
|---|---|---|---|
| **逐像素截图差异** | Percy、Applitools、Chromatic | 捕获每一处视觉变化 | 需要管理基线，动态内容可能导致不稳定 |
| **DOM 快照** | Jest/Vitest 快照 | 快速，无需浏览器 | 脆弱，无法捕获仅涉及 CSS 的变化 |
| **CSS-in-JS 快照** | Storybook + Chromatic | 组件级，与设计系统集成 | 需要设置 Storybook |
| **布局差异** | Playwright 截图 | 整页、支持设备模拟 | 较慢，不同环境会产生差异 |
| **AI 辅助** | Percy AI、Applitools Eyes | 智能检测变化，减少误报 | 成本、供应商锁定 |

### 7.2 Percy（BrowserStack）

```javascript
// Cypress + Percy
cy.visit('/');
cy.percySnapshot('Homepage');

// Playwright + Percy
import percySnapshot from '@percy/playwright';
test('首页视觉效果', async ({ page }) => {
  await page.goto('/');
  await percySnapshot(page, 'Homepage');
});
```

### 7.3 Chromatic（Storybook）

```javascript
// .github/workflows/chromatic.yml
name: Chromatic
on: push
jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: npm ci
      - uses: chromaui/action@v11
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

### 7.4 Playwright 原生视觉测试

```typescript
import { test, expect } from '@playwright/test';

test('首页与快照匹配', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,
    fullPage: true,
  });
});
```

### 7.5 视觉测试最佳实践

| 实践 | 详细说明 |
|---|---|
| 模拟动态内容 | 用夹具替代真实数据，以获得稳定截图 |
| 冻结动画 | 使用 `page.addStyleTag()` 禁用 CSS 动画 |
| 隔离组件状态 | 测试加载、空、错误和边界情况状态 |
| 设置一致的视口 | 始终使用已知视口尺寸生成快照 |
| 使用 CI 差异阈值 | 允许配置像素容差，以减少不稳定情况 |
| 在 PR 中评审差异 | 对未经批准的视觉变化阻止合并 |
| 有意识地重建基线 | 不要在每次提交时执行——仅在预期发生变化时执行 |

---

## 8. 无障碍测试

### 8.1 自动化覆盖率

自动化无障碍测试大约能捕获 **30-40%** 的 WCAG 违规问题。
这覆盖了容易处理的常见且可检测问题。对于其余 60-70%，
仍然需要手动测试。

**自动化擅长捕获的问题：**
- 图像缺少替代文本
- 表单缺少标签
- 颜色对比度不足
- ID 重复
- 缺少 ARIA 属性
- ARIA 用法无效
- 缺少 lang 属性
- 空链接或按钮

**需要手动测试的内容：**
- 合理的阅读顺序
- 键盘导航流程
- 屏幕阅读器播报
- 焦点管理
- 有意义的替代文本
- 仅依靠颜色传递信息

### 8.2 axe-core 集成

**在 Vitest/单元测试中（jest-axe）：**

```javascript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('没有无障碍违规', async () => {
  const { container } = render(<Button>点击我</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

**在 Playwright E2E 测试中：**

```typescript
import AxeBuilder from '@axe-core/playwright';

test('首页没有无障碍违规', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

// 指定 WCAG 级别
test('满足 WCAG AA 要求', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});

// 定向扫描——指定元素
test('导航菜单可无障碍访问', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: '菜单' }).click();
  const results = await new AxeBuilder({ page })
    .include('#nav-flyout')
    .analyze();
  expect(results.violations).toEqual([]);
});
```

### 8.3 Lighthouse CI

```javascript
// lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "staticDistDir": "./build",
      "settings": { "onlyCategories": ["accessibility"] }
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", { "minScore": 0.9 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### 8.4 CI/CD 集成

```yaml
# .github/workflows/accessibility.yml
name: Accessibility
on: [pull_request]
jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - run: npx playwright install
      - name: 运行无障碍测试
        run: npx playwright test --project=a11y
```

### 8.5 无障碍测试成熟度模型

| 级别 | 所做工作 | 覆盖率 |
|---|---|---|
| 1. 无 | 不进行无障碍测试 | 0% |
| 2. 仅手动 | 偶尔进行 Lighthouse 审计 | 30-40%（零散） |
| 3. CI 自动化 | 在 Playwright 测试中对每个 PR 运行 axe-core | 30-40%（持续） |
| 4. 自动化 + 强制执行 | Lighthouse CI 分数质量门 | 30-40% + 回归检测 |
| 5. 集成到组件测试 | 对每个组件运行 jest-axe | 组件级 30-40% |
| 6. 完整流水线 | Axe + Lighthouse + 手动审计 + 屏幕阅读器 | 自动化 30-40% + 手动 60-70% |

---

## 9. 测试数据管理

### 9.1 数据生成策略

| 策略 | 说明 | 使用时机 |
|---|---|---|
| **夹具** | JSON/YAML 文件中预定义的静态数据 | 不经常变化的测试数据 |
| **工厂** | 通过可覆盖项以编程方式生成数据 | 大量测试需要略有差异的数据时 |
| **Faker** | 随机的真实感数据（姓名、电子邮件、地址） | 压力测试、大型数据集 |
| **种子数据** | 已知且可复现的数据库状态 | 需要一致基线的 E2E 测试 |
| **API 模拟** | 拦截的网络响应 | 没有后端的集成/组件测试 |

### 9.2 夹具模式

```json
// src/test/fixtures/user.json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "admin"
}
```

```javascript
// 在测试中使用夹具
import userFixture from './fixtures/user.json';

it('渲染用户资料', () => {
  render(<UserProfile user={userFixture} />);
  expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
});
```

### 9.3 工厂模式

```javascript
// src/test/factories/user.js
import { faker } from '@faker-js/faker';

export function buildUser(overrides = {}) {
  return {
    id: faker.number.int({ min: 1, max: 10000 }),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    role: faker.helpers.arrayElement(['user', 'admin', 'moderator']),
    avatar: faker.image.avatar(),
    createdAt: faker.date.past().toISOString(),
    ...overrides,
  };
}

// 用法
const admin = buildUser({ role: 'admin', name: '管理员用户' });
const users = Array.from({ length: 20 }, () => buildUser());
```

### 9.4 请求模拟模式

```javascript
// MSW（Mock Service Worker）——推荐方法
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: '模拟用户',
    });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it('获取并显示用户', async () => {
  render(<UserDetail userId="42" />);
  await waitFor(() => {
    expect(screen.getByText('模拟用户')).toBeInTheDocument();
  });
});
```

### 9.5 测试数据隔离

| 关注点 | 解决方案 |
|---|---|
| **测试之间的状态泄漏** | `afterEach` 清理、重置 MSW 处理程序 |
| **E2E 的数据库状态** | 测试套件运行前填充数据库，运行后拆除 |
| **工厂中的共享状态** | 返回新对象，而非单例 |
| **依赖加密方法的 ID** | 确定性的 faker 种子：`faker.seed(123)` |
| **日期/计时器** | 假计时器：`vi.useFakeTimers()` |

### 9.6 测试数据设置模式

```javascript
// 模式 1：在 describe 块中设置
describe('UserList', () => {
  const users = Array.from({ length: 5 }, (_, i) =>
    buildUser({ id: i + 1 })
  );

  it('渲染所有用户', () => {
    render(<UserList users={users} />);
    expect(screen.getAllByRole('listitem')).toHaveLength(5);
  });
});

// 模式 2：自定义 render
function renderWithProviders(ui, { users = [], ...options } = {}) {
  const wrapper = ({ children }) => (
    <UserProvider users={users}>
      {children}
    </UserProvider>
  );
  return render(ui, { wrapper, ...options });
}

// 模式 3：测试工厂函数
function setupUserList(overrides = {}) {
  const users = overrides.users ?? [buildUser()];
  const onSelect = vi.fn();
  const utils = render(<UserList users={users} onSelect={onSelect} />);
  return { ...utils, users, onSelect };
}
```

### 9.7 前端测试数据最佳实践

| 实践 | 详细说明 |
|---|---|
| 使用真实感数据 | 捕获真实渲染问题，而不只是验证模式 |
| 将数据与断言分离 | 工厂有助于编写可读且能体现意图的测试 |
| 优先使用 MSW，而非 vi.mock | MSW 在网络层工作，不需要模拟模块 |
| 使用确定性种子 | 使用 `faker.seed(123)` 复现失败 |
| 在适当层级进行模拟 | API 模拟 > 模块模拟 > 全局模拟 |
| 测试之间执行清理 | 防止状态泄漏导致测试不稳定 |
| 保持夹具精简 | 只包含测试实际使用的字段 |

---

## 参考资料与延伸阅读

- **CSS Grid 与 Flexbox 对比**：blog.logrocket.com/css-flexbox-vs-css-grid
- **容器查询指南**：caisy.io/blog/css-container-queries
- **超越媒体查询（2025）**：medium.com/@orami98/beyond-media-queries
- **现代断点策略**：penpot.app/blog/how-to-use-css-and-media-query-breakpoints
- **Playwright 无障碍测试**：playwright.dev/docs/accessibility-testing
- **Vitest + Testing Library 设置**：freecodecamp.org/news/how-to-test-react-applications-with-vitest
- **CI/CD 中的无障碍测试**：testparty.ai/blog/accessibility-testing-cicd
- **视觉回归指南**：desplega.ai/blog/deep-dive-7-visual-regression-testing-ui-bugs
- **响应式 Web 设计基础**：web.dev/articles/responsive-web-design-basics
- **用一行 CSS 实现十种现代布局**：web.dev/articles/one-line-layouts
