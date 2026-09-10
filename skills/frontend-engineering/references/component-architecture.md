# 组件架构

## 组合模式

| 模式 | 使用时机 | 示例 |
|---------|-------------|---------|
| 原子化设计 | 具有清晰层级的设计系统 | `Button → FormField → AddressForm → CheckoutPage` |
| 复合组件 | 共享隐式状态的相关组件 | `Select.Trigger`、`Select.Options`、`Select.Option` |
| Render props | 需要组件行为最大灵活性 | 将渲染委派给使用方的数据提供者 |
| 受控与非受控 | 表单输入、外部状态管理 | 受控：状态位于父组件。非受控：状态位于组件内部。 |
| 高阶组件 | 横切关注点，例如认证、日志 | `withAuth(Component)`、`withAnalytics(Component)` |

## Props 与状态接口设计

| 方面 | 指引 |
|--------|-----------|
| Props 应最小化 | 只传递组件所需内容，使用 context 避免 prop drilling。 |
| 可选 Props 的默认值 | 每个可选 prop 都应具有合理默认值。 |
| 布尔 Props 使用疑问式命名 | `isLoading`、`hasError`、`isDisabled`、`canSubmit` |
| 回调 Props 描述事件 | `onClick`、`onSubmit`、`onChange`、`onClose` |
| 避免复合职责 Props | 一个 prop 只做一件事。使用 `variant="primary|secondary|danger"`，不要使用 `mode="view|edit|admin"`。 |

## 无障碍基础

每个组件都必须支持：

- **键盘导航：**所有交互元素均可通过 Tab、Enter、Escape 和方向键访问及操作。
- **焦点管理：**可见焦点指示器、合理的 Tab 顺序、模态框中的焦点圈定。
- **屏幕阅读器支持：**ARIA 标签、角色、实时区域和地标。
- **颜色对比度：**文本符合 WCAG AA，普通文本 4.5:1，大文本 3:1。
- **减少动画：**动画和过渡应尊重 `prefers-reduced-motion`。
