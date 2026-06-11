# Checklist

## 高优先级

- [x] `index.html` 中 `lang` 属性为 `zh-CN`，`<title>` 为 "锦年志"
- [x] `index.html` 包含 `<meta name="theme-color">`
- [x] `GuestLayout.vue` 在 1024px 视口下无水平滚动条
- [x] `GuestLayout.vue` header 在 ≤768px 下导航区域合理折行
- [x] `AdminLayout.vue` 中 `.user-info` 使用 `<button>` 标签且有 `aria-label`
- [x] `AdminLayout.vue` 中 `.menu-item` 使用 `<RouterLink>` 或 `<button>`
- [x] `UserLayout.vue` 中 `.user-info` 使用 `<button>` 标签且有 `aria-label`
- [x] `GuestLayout.vue` 中下拉菜单项使用 `<button>` 或 `<RouterLink>`
- [x] `GuestLayout.vue` 搜索输入框有 `aria-label`
- [x] `Login.vue` 账号输入有 `autocomplete="username"`、`name="identity"`
- [x] `Login.vue` 密码输入有 `autocomplete="current-password"`
- [x] `Register.vue` 邮箱输入有 `type="email"`、`autocomplete="email"`
- [x] `Register.vue` 用户名输入有 `autocomplete="username"`
- [x] `Register.vue` 密码输入有 `autocomplete="new-password"`
- [x] `theme.css` `.dark` 类包含 `color-scheme: dark`

## 中优先级

- [x] `style.css` 中 `.fade-transform-*` 过渡使用显式属性列表
- [x] `AdminLayout.vue` 中所有 `transition` 使用显式属性列表
- [x] `UserLayout.vue` 中所有 `transition` 使用显式属性列表
- [x] `theme.css` 包含 `@media (prefers-reduced-motion: reduce)` 全局动画禁用
- [x] `Login.vue` 打字机效果在 prefers-reduced-motion 时禁用
- [x] `Login.vue` 浮动装饰球在 prefers-reduced-motion 时禁用
- [x] `Register.vue` 浮动装饰球在 prefers-reduced-motion 时禁用
- [x] `Home.vue` 热门轮播在 prefers-reduced-motion 时禁用自动切换
- [x] `Explore.vue` 筛选标签变化时 URL query 同步更新
- [x] `Explore.vue` 页面加载时从 URL query 恢复筛选状态
- [x] `PostEditor.vue` 离开页面前检测未保存更改并弹出确认
- [x] `AdminLayout.vue` 用户菜单在外部点击时关闭
- [x] `UserLayout.vue` 用户菜单在外部点击时关闭
- [x] `PlatformShell.vue` 中无硬编码颜色（`#d9d9d9`、`#1890ff` 等）
- [x] `BlogShell.vue` 中无硬编码颜色（`#d9d9d9`、`#1890ff` 等）

## 低优先级

- [x] `Home.vue` 封面图 `<img>` 有显式 `width`/`height` 属性
- [x] `Home.vue` 作者头像 `<img>` 有显式 `width`/`height` 属性
- [x] `ConsoleShell.vue` 在 ≤860px 视口下显示汉堡菜单入口
- [x] `App.vue` themeOverrides 已精简，移除与 theme.css 重复的硬编码颜色
- [x] 全局 `html, body, #app` 设置 `touch-action: manipulation`
- [x] 侧边栏容器设置 `overscroll-behavior: contain`
- [x] `ProTable.vue` 数值列设置 `font-variant-numeric: tabular-nums`
