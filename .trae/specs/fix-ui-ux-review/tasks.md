# Tasks

## 高优先级

- [x] Task 1: 修复 `index.html` 基础配置 — `lang="zh-CN"`、`<title>` 改为 "锦年志"、添加 `<meta name="theme-color">`
- [x] Task 2: 修复 `GuestLayout.vue` 响应式布局 — 移除 `min-width: 1080px`，header-content 改用 flex 自适应，在 ≤768px 下合理折行
- [x] Task 3: 全局语义化交互元素 — 将 `AdminLayout.vue`、`UserLayout.vue`、`GuestLayout.vue` 中的 `<div @click>` 替换为 `<button>` 或 `<RouterLink>`，图标按钮补充 `aria-label`
- [x] Task 4: 修复表单 `autocomplete` 与 `type` — `Login.vue` 和 `Register.vue` 的输入字段设置正确的 `autocomplete`、`name` 和 `type` 属性
- [x] Task 5: 暗色模式补充 `color-scheme: dark` — 在 `theme.css` 的 `.dark` 类中添加

## 中优先级

- [x] Task 6: 全局替换 `transition: all` 为显式属性列表 — 涉及 `style.css`、`AdminLayout.vue`、`UserLayout.vue` 等文件
- [x] Task 7: 添加 `prefers-reduced-motion` 适配 — 在 `theme.css` 中添加全局媒体查询禁用动画，覆盖 `Login.vue`、`Register.vue`、`Home.vue` 的浮动/轮播动画
- [x] Task 8: `Explore.vue` 筛选状态同步到 URL — 标签/作者/视图模式筛选变化时更新 URL query params，页面加载时从 URL 恢复
- [x] Task 9: `PostEditor.vue` 添加未保存离开警告 — 使用 `beforeRouteLeave` 路由守卫检测草稿变更
- [x] Task 10: `AdminLayout.vue` / `UserLayout.vue` 下拉菜单外部点击关闭 — 参考 `GuestLayout.vue` 的 `handleClickOutside` 实现
- [x] Task 11: `PlatformShell.vue` / `BlogShell.vue` 硬编码颜色替换为设计系统 CSS 变量

## 低优先级

- [x] Task 12: `Home.vue` 封面图添加显式 `width`/`height` 属性防止 CLS
- [x] Task 13: `ConsoleShell.vue` 移动端添加汉堡菜单入口替代直接隐藏侧边栏
- [x] Task 14: `App.vue` themeOverrides 清理 — 移除与 `theme.css` 重复的硬编码颜色，统一引用 CSS 变量
- [x] Task 15: 全局交互优化 — 添加 `touch-action: manipulation`、侧边栏 `overscroll-behavior: contain`、表格数值列 `tabular-nums`

# Task Dependencies
- Task 3, Task 4, Task 5 无依赖，可与 Task 1, Task 2 并行
- Task 6 涉及全局，应在 Task 2 之后执行以避免冲突
- Task 13 依赖 Task 3 的语义化修改（涉及按钮标签）
- Task 14 依赖 Task 5（暗色模式变量已就位）
