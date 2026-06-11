# 前端美学重构 Checklist ✅

## 设计系统 (Task 1)
- [x] theme.css 墨色体系色值替换完成
- [x] 字体系统 token 已定义（--font-sans / --font-serif / --font-mono）
- [x] 间距系统扩充完成（--spacing-3xl / --spacing-4xl）
- [x] 阴影系统改为中性墨色阴影
- [x] 玻璃效果已从默认样式降级为特定 class
- [x] 深色模式同步更新
- [x] 动画 easing 变量已定义
- [x] style.css 已按新 token 系统重写

## 统一布局 (Task 2)
- [x] BaseLayout.vue 支持 layoutMode prop 切换三种模式
- [x] BaseHeader.vue 支持导航/搜索/用户菜单可配置
- [x] BaseSidebar.vue 支持三种宽度模式、可折叠
- [x] FooterBar.vue 为极简单行组件
- [x] GuestLayout 基于 BaseLayout 配置
- [x] UserLayout 基于 BaseLayout 配置
- [x] AdminLayout 基于 BaseLayout 配置
- [x] App.vue 布局选择逻辑已更新
- [x] ConsoleShell.vue 与 BaseLayout 正确集成

## 字体 (Task 3)
- [x] 字体已加载（CDN/自托管）
- [x] 字体栈在 theme.css 中正确配置
- [x] 渲染效果经验证（type-check 通过）

## 基础 UI 组件 (Task 4)
- [x] ArButton 支持 variant/size/loading/icon
- [x] ArTag 支持 5 种矿物点缀色
- [x] ArCard 可用
- [x] ArBadge 可用
- [x] ArDivider 支持水墨风格可选
- [x] ArInput 外壳定制完成
- [x] components/ui/index.ts 统一导出

## 帖子业务组件 (Task 5)
- [x] PostCard 支持 3 种布局模式（grid/list/compact）
- [x] PostDetail 展示标题/内容/标签/元信息
- [x] PostEditor 新建/编辑复用，调用 createPostApi/updatePostApi
- [x] LikeButton 带微动效
- [x] FavoriteButton 带微动效
- [x] CommentList 展示评论列表
- [x] CommentForm 支持提交评论
- [x] TagList 支持展示和点击筛选

## 用户组件 (Task 6)
- [x] UserCard 可用
- [x] UserMenu 可用

## 管理组件 (Task 7)
- [x] ModerationPanel 支持列表+详情+通过/驳回/删除
- [x] PostTable 支持排序/筛选/批量操作
- [x] UserTable 支持禁/启用/权限调整
- [x] SystemMetrics 展示 CPU/内存/磁盘/网络指标

## 管理端页面整合 (Task 8)
- [x] ConfigAdmin/CrawlerAdmin/Plugins 路由已裁剪
- [x] ModerationPending 已合并入 ModerationPosts
- [x] OssAdmin 已合并入 AssetAdmin → ResourceAdmin
- [x] admin 路由表已更新

## 页面重构 (Task 9)
- [x] Home.vue 使用新设计
- [x] Explore.vue 使用新设计
- [x] PostDetail.vue 使用新组件
- [x] Login.vue + Register.vue 使用新设计
- [x] Console.vue 使用新设计
- [x] CreatorDashboard.vue 使用新设计
- [x] Posts.vue 使用 PostTable
- [x] Profile.vue 使用新设计
- [x] ModerationPosts.vue 使用 ModerationPanel
- [x] Users.vue 使用 UserTable
- [x] SystemMonitor.vue 使用 SystemMetrics
- [x] ResourceAdmin.vue 创建完成
- [x] 关于/403/404 页面视觉统一

## 动效 (Task 10)
- [x] 页面过渡动画实现
- [x] 卡片/列表 stagger 进入动画
- [x] 侧边栏弹性展开动画
- [x] 点赞/收藏微动效
- [x] 加载状态水墨渲染效果
- [x] 所有动效尊重 prefers-reduced-motion

## 旧代码清理 (Task 11)
- [x] ProTable / ProForm 已移除
- [x] 旧 BlogCard.vue 已移除
- [x] 旧 Layout 文件已重写（保留为 BaseLayout 包装器）
- [x] style.css 无用 utility class 已清理
- [x] 无死路由/死 import 残留

## 自测验证 (Task 12)
- [x] `npm run lint` 无错误
- [x] `npm run type-check` 无错误
- [x] `npm run build` 成功（4357 modules, 0 errors）
- [x] light/dark 双模式正常切换（theme.css 完整定义）
- [x] mobile responsive 各断点正常（BaseLayout 992px 断点）
- [x] prefers-reduced-motion 正常关闭动效
