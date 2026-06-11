# Tasks

## Task Dependencies
- [Task 2] ~ [Task 1]
- [Task 3] ~ [Task 2]
- [Task 4] ~ [Task 2]
- [Task 5] ~ [Task 4]
- [Task 6] ~ [Task 4]
- [Task 7] ~ [Task 4]
- [Task 8] ~ [Task 4]
- [Task 9] ~ [Task 5, Task 6, Task 7, Task 8]

---

- [ ] Task 1: **设计系统重构 — theme.css 完全重写**
  将现有的茶棕米白体系替换为墨色体系（墨色五层 + 宣纸白底 + 矿物色点缀），扩充间距/阴影/字体系统，新增动画 easing 变量。
  - [ ] 1.1 重写 `theme.css`：色系替换（主色 → 黛青 `#3a5a4a`、文字 → 墨色五层、底色 → 宣纸白）
  - [ ] 1.2 新增字体系统 token：`--font-sans` / `--font-serif` / `--font-mono` + 字重行高体系
  - [ ] 1.3 间距系统扩充：新增 `--spacing-3xl`(64px) / `--spacing-4xl`(80px)
  - [ ] 1.4 阴影系统改版：从暖棕阴影改为中性墨色阴影
  - [ ] 1.5 玻璃效果保留为特定 class（`.glass-surface`）而非默认样式
  - [ ] 1.6 深色模式同步更新（墨色变体 → 更深层墨色）
  - [ ] 1.7 新增动画 easing 变量：`--ease-out-spring` / `--ease-out-smooth` / `--ease-stagger`
  - [ ] 1.8 更新 `style.css`：移除旧 utility class，按新 token 体系重写

- [ ] Task 2: **统一布局系统 — BaseLayout 构建**
  将 GuestLayout/UserLayout/AdminLayout 合并为单一可配置的 BaseLayout。
  - [ ] 2.1 创建 `layouts/BaseLayout.vue` — 核心骨架，通过 `layoutMode` prop 切换三种模式
  - [ ] 2.2 创建 `layouts/BaseHeader.vue` — 统一 header 组件（Logo/导航/搜索/用户菜单）
  - [ ] 2.3 创建 `layouts/BaseSidebar.vue` — 统一 sidebar 组件（支持三种宽度模式、可折叠）
  - [ ] 2.4 创建 `layouts/FooterBar.vue` — 极简底栏组件（单行，条件显示）
  - [ ] 2.5 重构 `GuestLayout.vue` → 基于 BaseLayout 的 guest 配置
  - [ ] 2.6 重构 `UserLayout.vue` → 基于 BaseLayout 的 user 配置
  - [ ] 2.7 重构 `AdminLayout.vue` → 基于 BaseLayout 的 admin 配置
  - [ ] 2.8 更新 `App.vue` 中的布局选择逻辑
  - [ ] 2.9 更新 `ConsoleShell.vue` 与 BaseLayout 的集成

- [ ] Task 3: **字体接入 — Google Fonts / 本地字体**
  引入 Noto Sans CJK SC / HarmonyOS Sans 等字体。
  - [ ] 3.1 确定字体加载策略（CDN/自托管）并接入
  - [ ] 3.2 在 `index.html` 或 `main.ts` 中添加字体加载
  - [ ] 3.3 在 `theme.css` 中配置完整字体栈
  - [ ] 3.4 验证字体在各端渲染效果

- [ ] Task 4: **基础 UI 组件库构建（ArUi）**
  自建视觉基础组件，替换 Naive UI 的对应组件。
  - [ ] 4.1 创建 `components/ui/ArButton.vue` — 按钮（支持 variant/size/loading/icon 模式）
  - [ ] 4.2 创建 `components/ui/ArTag.vue` — 标签（5 种矿物色点缀色）
  - [ ] 4.3 创建 `components/ui/ArCard.vue` — 卡片容器
  - [ ] 4.4 创建 `components/ui/ArBadge.vue` — 徽标
  - [ ] 4.5 创建 `components/ui/ArDivider.vue` — 分割线（含水墨风格可选）
  - [ ] 4.6 创建 `components/ui/ArInput.vue` — 输入框（外壳定制，内部包装 NInput）
  - [ ] 4.7 创建 `components/ui/index.ts` — 统一导出

- [ ] Task 5: **核心业务组件 — 帖子体系**
  以帖子为中心，构建与 API 一一对应的业务组件。
  - [ ] 5.1 创建 `components/blog/PostCard.vue` — 帖子卡片（3 种布局模式：grid/list/compact）
  - [ ] 5.2 创建 `components/blog/PostDetail.vue` — 帖子详细阅读（标题/内容/标签/元信息）
  - [ ] 5.3 创建 `components/blog/PostEditor.vue` — 帖子编辑器（新建/编辑复用，调用 createPostApi/updatePostApi）
  - [ ] 5.4 创建 `components/blog/LikeButton.vue` — 点赞按钮（带微动效）
  - [ ] 5.5 创建 `components/blog/FavoriteButton.vue` — 收藏按钮（带微动效）
  - [ ] 5.6 创建 `components/blog/CommentList.vue` — 评论列表
  - [ ] 5.7 创建 `components/blog/CommentForm.vue` — 评论输入框
  - [ ] 5.8 创建 `components/blog/TagList.vue` — 标签展示（可点击筛选）

- [ ] Task 6: **核心业务组件 — 用户体系**
  - [ ] 6.1 创建 `components/user/UserCard.vue` — 用户信息卡片
  - [ ] 6.2 创建 `components/user/UserMenu.vue` — 用户导航菜单

- [ ] Task 7: **核心业务组件 — 管理体系**
  - [ ] 7.1 创建 `components/admin/ModerationPanel.vue` — 帖子审核面板（列表+详情+通过/驳回/删除）
  - [ ] 7.2 创建 `components/admin/PostTable.vue` — 帖子管理表格（排序/筛选/批量操作）
  - [ ] 7.3 创建 `components/admin/UserTable.vue` — 用户管理表格（禁/启用/权限调整）
  - [ ] 7.4 创建 `components/admin/SystemMetrics.vue` — 系统监控指标卡（CPU/内存/磁盘/网络）

- [ ] Task 8: **管理端页面整合**
  - [ ] 8.1 裁剪 ConfigAdmin / CrawlerAdmin / Plugins 页面的路由注册
  - [ ] 8.2 将 ModerationPending 合并入 ModerationPosts（通过 status 筛选）
  - [ ] 8.3 将 OssAdmin 合并入 AssetAdmin → 创建 ResourceAdmin 页面
  - [ ] 8.4 更新 admin 路由表

- [ ] Task 9: **页面重构 — 应用新设计系统**
  逐个页面替换为新的组件体系和设计 token。
  - [ ] 9.1 首页 Home.vue 重构（新 PostCard + hero 区 + 动效）
  - [ ] 9.2 探索 Explore.vue 重构
  - [ ] 9.3 文章详情 PostDetail.vue 重构（使用 PostDetail + CommentList + CommentForm）
  - [ ] 9.4 登录/注册页 Login.vue + Register.vue 重构
  - [ ] 9.5 用户控制台 Console.vue 重构
  - [ ] 9.6 创作者看板 CreatorDashboard.vue 重构
  - [ ] 9.7 我的文章 Posts.vue 重构（使用 PostTable）
  - [ ] 9.8 个人中心 Profile.vue 重构
  - [ ] 9.9 帖子审核 ModerationPosts.vue 重构（使用 ModerationPanel）
  - [ ] 9.10 用户管理 Users.vue 重构（使用 UserTable）
  - [ ] 9.11 系统监控 SystemMonitor.vue 重构（使用 SystemMetrics）
  - [ ] 9.12 资源管理 ResourceAdmin.vue 创建（合并 AssetAdmin + OssAdmin）
  - [ ] 9.13 关于/403/404 页面视觉统一

- [ ] Task 10: **动效系统落地**
  - [ ] 10.1 在 `style.css` 中添加页面过渡动画（View Transitions + CSS）
  - [ ] 10.2 添加卡片/列表 stagger 进入动画
  - [ ] 10.3 添加侧边栏弹性展开动画
  - [ ] 10.4 添加点赞/收藏微动效
  - [ ] 10.5 添加加载状态水墨渲染效果
  - [ ] 10.6 确保所有动效尊重 `prefers-reduced-motion`

- [ ] Task 11: **清理旧代码**
  - [ ] 11.1 移除旧 ProTable / ProForm 组件（已被业务组件替代）
  - [ ] 11.2 移除旧 BlogCard.vue（已被 PostCard.vue 替代）
  - [ ] 11.3 移除旧 layouts（GuestLayout / UserLayout / AdminLayout 旧文件）
  - [ ] 11.4 清理 `style.css` 中不再使用的 utility class
  - [ ] 11.5 确认无死路由/死 import 残留

- [ ] Task 12: **自测验证**
  - [ ] 12.1 运行 `npm run lint` 无错误
  - [ ] 12.2 运行 `npm run type-check` 无错误
  - [ ] 12.3 运行 `npm run build` 成功
  - [ ] 12.4 确认 light/dark 双模式正常切换
  - [ ] 12.5 确认 mobile responsive 各断点正常
  - [ ] 12.6 确认 `prefers-reduced-motion` 正常关闭动效
