# 统一博客卡片组件 Spec

## Why

全局存在 8 种不同样式的博客卡片/列表项，分布在 Home、Explore、Console、Posts 四个页面。未来 API 字段变更（如新增字段、字段重命名）需要同步修改 8 处，维护成本极高。需统一为一个 `BlogCard` 组件，通过 props 开关控制展示形态。

## What Changes

- **新增** `src/components/blog/BlogCard.vue` — 统一博客卡片组件，支持 `grid` / `list` / `compact` 三种布局
- **BREAKING**: 移除现有未使用的 `BlogCardGrid.vue`、`BlogListDetail.vue`、`BlogListCompact.vue`
- **重构** `Home.vue` — 替换 hero-card、post-card、quick-item 为 `BlogCard`
- **重构** `Explore.vue` — 替换 display-item (card/wide 模式) 为 `BlogCard`；保留 ProTable 紧凑表模式（纯表格，无封面需求）
- **重构** `Console.vue` — 替换 post-row 为 `BlogCard`
- **重构** `Posts.vue` — 替换表格行渲染为 `BlogCard`（需结合 ProTable render）

## Impact

- Affected specs: `fix-ui-ux-review`
- Affected code: `src/components/blog/BlogCard.vue` (new), `src/views/Home.vue`, `src/views/Explore.vue`, `src/views/user/Console.vue`, `src/views/user/Posts.vue`

## ADDED Requirements

### Requirement: 统一卡片组件
系统 SHALL 提供一个 `BlogCard` 组件，接受单个 `BlogPost` 和以下 props：

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `post` | `BlogPost` | 必填 | 帖子数据 |
| `layout` | `'grid' \| 'list' \| 'compact'` | `'grid'` | 布局模式 |
| `showCover` | `boolean` | `false` | 是否显示封面图 |
| `showExcerpt` | `boolean` | `true` | 是否显示摘要 |
| `showMeta` | `boolean` | `true` | 是否显示元信息（作者/日期/统计） |
| `showActions` | `boolean` | `false` | 是否显示交互按钮（点赞/收藏/分享/热度） |
| `coverHeight` | `number` | `152` | 封面区域高度 (px) |

组件 SHALL emit `open` 事件，传递 `BlogPost`。

#### Scenario: Grid 布局带封面
- **WHEN** 传入 `layout="grid"` `showCover="true"`
- **THEN** 渲染封面图（含渐变遮罩 + 标签徽章 + 日期徽章）+ 标题 + 摘要 + 元信息

#### Scenario: List 布局无封面
- **WHEN** 传入 `layout="list"` `showCover="false"`
- **THEN** 渲染标题 + 摘要 + 标签 + 元信息（横向排列），类似现有 BlogListDetail

#### Scenario: Compact 布局
- **WHEN** 传入 `layout="compact"`
- **THEN** 渲染单行：标题（左）+ 日期（右），忽略封面/摘要/交互

#### Scenario: 未传入的可选内容不渲染
- **WHEN** 传入 `showActions="false"`
- **THEN** 不渲染交互芯片区域，DOM 中无对应空节点

### Requirement: 替换 Home.vue 卡片
Home 页面 SHALL 使用 `BlogCard` 组件替代当前的三种内联卡片样式。

#### Scenario: 首页精选大卡
- **WHEN** 渲染 Hero 区域
- **THEN** 使用 `BlogCard` `layout="grid"` `showCover="false"` `showActions="false"`

#### Scenario: 首页最新文章卡片
- **WHEN** 渲染 latest-grid 区域
- **THEN** 使用 `BlogCard` `layout="grid"` `showCover="true"` `showActions="true"`

#### Scenario: 首页快速列表
- **WHEN** 渲染 quick-list 区域
- **THEN** 使用 `BlogCard` `layout="compact"` `showTags="true"`

### Requirement: 替换 Explore.vue 卡片
Explore 页面 SHALL 在 card 和 wide-row 视图模式下使用 `BlogCard`。ProTable compact 模式保留不变。

#### Scenario: 卡片模式
- **WHEN** 视图模式为 card
- **THEN** 使用 `BlogCard` `layout="grid"` `showCover="true"`

#### Scenario: 宽行模式
- **WHEN** 视图模式为 wide-row
- **THEN** 使用 `BlogCard` `layout="list"`

### Requirement: 替换 Console 和 Posts 列表
控制台和我的文章页面 SHALL 使用 `BlogCard` 的 compact 模式。

## MODIFIED Requirements

无。原 `fix-ui-ux-review` spec 中的卡片布局修复已被本次重构覆盖。
