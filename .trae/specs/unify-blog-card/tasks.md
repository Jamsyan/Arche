# Tasks

- [x] Task 1: 创建 `BlogCard.vue` 组件 — 一个接收 `post` + props 开关的统一卡片，支持 `grid` / `list` / `compact` 三种布局
  - [x] 定义 props：`post: BlogPost`, `layout`, `showCover`, `showExcerpt`, `showMeta`, `showActions`, `coverHeight`
  - [x] 实现 grid 布局（封面+渐变遮罩+标签/日期徽章+标题+摘要+交互芯片）
  - [x] 实现 list 布局（标题+摘要+标签+作者/统计/日期行）
  - [x] 实现 compact 布局（标题+标签（左），日期（右），单行）
  - [x] 所有布局共享 `card-glass` 类，hover 继承 `card-glass` 提升效果
  - [x] emit `open` 事件
  - [x] 使用 `font-variant-numeric: tabular-nums` 处理统计数字
  - [x] 添加 `touch-action: manipulation` 到可点击区域

- [x] Task 2: 重构 `Home.vue` — 替换三种内联卡片为 `BlogCard`
  - [x] Hero 区域：`layout="grid"` `showCover="false"` `showActions="false"`
  - [x] Latest 网格：`layout="grid"` `showCover="true"` `showActions="true"`
  - [x] Quick 列表：`layout="compact"` `showExcerpt="false"`
  - [x] 移除所有旧的内联卡片 CSS（hero-card、post-card、quick-item、action-chip 等）
  - [x] 保留 Hero Carousel 逻辑（hot rotation、dots 指示器）

- [x] Task 3: 重构 `Explore.vue` — 替换卡片/宽行模式为 `BlogCard`
  - [x] Card 模式：`layout="grid"` `showCover="true"`
  - [x] Wide-row 模式：`layout="list"` `showCover="false"`
  - [x] 移除旧 `display-item` 卡片 CSS 和 `WideExcerptCell` 自定义组件
  - [x] 保留 ProTable 的 compact-table 模式不变

- [x] Task 4: 重构 `Console.vue` — post-row 替换为 `BlogCard` compact
  - [x] 列表项使用 `BlogCard` `layout="compact"` `showMeta="true"`
  - [x] 移除旧 `.post-row` CSS

- [x] Task 5: 重构 `Posts.vue` — 表格渲染改用 `BlogCard` compact
  - [x] ProTable 的 render 函数中使用 `BlogCard` `layout="compact"`
  - [x] 移除表格中重复的标题/状态/操作列（保留 ProTable 分页）

- [x] Task 6: 清理 — 删除未使用的旧组件
  - [x] 删除 `src/components/blog/BlogCardGrid.vue`
  - [x] 删除 `src/components/blog/BlogListDetail.vue`
  - [x] 删除 `src/components/blog/BlogListCompact.vue`

# Task Dependencies
- Task 2~5 全部依赖 Task 1（需先有 BlogCard 组件）
- Task 2、3、4、5 可并行执行
- Task 6 在 Task 2~5 完成后执行（确认无引用再删除）
