# Tasks

- [ ] Task 1: 重构路由系统 — 将 admin 路由从 role.ts 合并到 static.ts，添加 tasks 路由
  - 删除 `role.ts`
  - 在 `static.ts` 中添加所有 `/admin/*` 路由（三大类卡页面 + 子页面），设 `meta.layout: 'guest'`, `meta.console: true`, `meta.level: 0`
  - 在 `static.ts` 中添加 `/tasks`、`/tasks/crawler`、`/tasks/cloud` 路由，设 `meta.layout: 'guest'`, `meta.requiresAuth: true`
  - 移除 `/posts`、`/creator`、`/profile` 的 `meta.console: true`
  - 为 `/console` 添加 `meta.level: 0`

- [ ] Task 2: 简化 permission store — 移除动态路由注入逻辑
  - 移除 `generateRoutes()` 中的 `router.addRoute()` 和 `router.removeRoute()` 调用
  - 移除对 `adminRoutes` 的 import 引用
  - 保留权限校验方法不变

- [ ] Task 3: 重构 ConsoleShell — 移除创作组，添加管理组+快捷访问组
  - 移除创作组（我的文章、写文章、创作者看板）
  - 移除顶部"导航"文字标签
  - 添加三大类管理组（用户管理、内容管理、运维管理），点击跳转到对应的卡片概览页
  - 添加快捷访问组，从 localStorage 读取/存储快捷方式
  - 添加"加添加快捷方式"按钮逻辑

- [ ] Task 4: 创建三大类卡片概览页
  - 新建 `views/admin/UsersOverview.vue` — 4 张卡片（用户列表、帖子资产、评论资产、静态资产）
  - 新建 `views/admin/ContentOverview.vue` — 3 张卡片（帖子审核、评论管理、举报处理）
  - 新建 `views/admin/OpsOverview.vue` — 6 张卡片（系统监控、运行时配置、OSS 存储、权限管理、插件管理、日志管理）
  - 每个卡片展示数据预览和跳转按钮

- [ ] Task 5: 新建托管任务页 + 更新顶部导航
  - 新建 `views/Tasks.vue` — 包含爬虫管理和云训练管理两张卡片
  - 在 `BaseHeader.vue` 的 `nav-menu` 中添加"托管任务"入口（仅登录用户可见）

- [ ] Task 6: 删除 AdminLayout + 清理 GuestLayout
  - 删除 `layouts/AdminLayout.vue`
  - 简化 `GuestLayout.vue`——移除 `isConsoleRoute` 中 ConsoleShell 对非管理员的包裹（已在路由层面由 level: 0 过滤）
  - 清理 `BaseHeader.vue` 中 `layoutMode === 'admin'` 的相关代码

# Task Dependencies

- Task 1 是 Task 3、Task 4、Task 5 的前置依赖（路由定义好了才能创建页面和导航）
- Task 2 是 Task 6 的前置依赖（先简化 permission store）
- Task 3、Task 4、Task 5 可并行
- Task 6 可在最后做，或与其它任务并行
