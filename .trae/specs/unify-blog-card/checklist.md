# Checklist

## BlogCard 组件

- [x] `BlogCard.vue` 文件存在且接收 `post: BlogPost` prop
- [x] 支持 `layout` prop，可选值 `'grid'` / `'list'` / `'compact'`
- [x] 支持 `showCover` prop，控制封面图显示
- [x] 支持 `showExcerpt` prop，控制摘要显示
- [x] 支持 `showMeta` prop，控制元信息显示
- [x] 支持 `showActions` prop，控制交互芯片显示
- [x] grid 布局下封面图有渐变遮罩和标签/日期徽章
- [x] grid 布局下交互芯片渲染（点赞/收藏/分享/热度）
- [x] list 布局横向排列标题+摘要+标签+作者+统计+日期
- [x] compact 布局单行：标题（左）+ 日期（右）
- [x] 所有布局使用 `card-glass` 类，hover 有视觉提升
- [x] emit `open` 事件，参数为 `BlogPost`
- [x] 统计数字使用 `font-variant-numeric: tabular-nums`

## Home.vue 重构

- [x] Hero 区域使用 `BlogCard` 替代旧 `.hero-card`
- [x] Latest 网格区域使用 `BlogCard` 替代旧 `.post-card`
- [x] Quick 列表使用 `BlogCard` 替代旧 `.quick-item`
- [x] 旧 card CSS 已移除（hero-card、post-card、quick-item 等）
- [x] Carousel 轮播逻辑保留且正常工作
- [x] 分页功能正常

## Explore.vue 重构

- [x] Card 模式使用 `BlogCard` 替代旧 `.display-item`
- [x] Wide-row 模式使用 `BlogCard` 替代旧 `WideExcerptCell`
- [x] 旧 `display-item` CSS 和 `WideExcerptCell` 组件已移除
- [x] Compact ProTable 模式保持不变
- [x] URL 筛选同步保持正常

## Console.vue 重构

- [x] 文章列表使用 `BlogCard` `layout="compact"`
- [x] 旧 `.post-row` CSS 已移除
- [x] 状态标签保留

## Posts.vue 重构

- [x] ProTable 行使用 `BlogCard` `layout="compact"` 渲染
- [x] 编辑/删除操作按钮保留

## 清理

- [x] `BlogCardGrid.vue` 已删除
- [x] `BlogListDetail.vue` 已删除
- [x] `BlogListCompact.vue` 已删除
- [x] `npm run type-check` 通过
- [x] `npm run lint` 通过
