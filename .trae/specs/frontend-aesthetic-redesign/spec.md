# 前端美学重构 Spec

## Why

当前前端 UI 存在以下核心问题：
1. **视觉风格缺乏辨识度** — Naive UI 默认风格占主导，全站 Glassmorphism 导致视觉层级扁平
2. **布局系统重复且不一致** — GuestLayout/UserLayout/AdminLayout 代码高度重复，padding/spacing 值不统一
3. **组件体系混乱** — ProTable/ProForm 和 Naive UI 原生组件职责重叠，组件与 API 未形成一一对应关系
4. **交互体验薄弱** — 动效几乎为零（仅基础 fade），页面切换/微交互缺失
5. **页面膨胀** — 管理员页面过多，部分功能可合并或裁剪
6. **Footer 大而不当** — 三栏 footer 仅为三个法律条目存在，视觉权重过高

## Design Direction

**东方现代主义 × Apple 式设计韵律 × 国风元素点缀**

- **色彩**: 墨色体系（焦/浓/重/淡/清五色墨）+ 宣纸白为底 + 朱砂/石青/藤黄矿物色点缀
- **字体**: 黑体系现代 sans-serif（Noto Sans CJK / HarmonyOS Sans），配以有骨力的字重层级
- **布局**: 非对称构图 + 大留白 + 三大块差异化
- **动效**: 以 Apple 式物理感动效为基础，点缀国风元素（如水墨晕染加载）
- **Footer**: 极简单行底栏，仅保留版权 + 必要备案链接

## What Changes

### 1. 设计系统重构（theme.css 完全重写）

**BREAKING**: 现有 `--primary-color: #9a5a2f` 色系替换为墨色体系

#### 色彩系统

| Token 层级 | 色值 | 映射 |
|-----------|------|------|
| 底色 | 宣纸白 / 浅墨灰 | body 背景 |
| 墨色五层 | 焦(纯黑) → 清(浅灰) | 文字层级(text-primary~disabled) |
| 主色 | 墨绿/黛青 `#2d4a3e` 或 `#3a5a4a` | 品牌主色、按钮、链接 |
| 点缀色集 | 朱砂 `#c23a2b` / 石青 `#4a7c94` / 藤黄 `#d4a017` | 标签、状态、强调交互 |

#### 字体系统
- 新增 `--font-sans` / `--font-serif` / `--font-mono` 三层字体栈
- 中文优先：HarmonyOS Sans / Noto Sans CJK SC / PingFang SC
- 西文/数字：Inter / SF Pro Text
- 字重体系：400(regular) / 500(medium) / 600(semibold) / 700(bold)
- 行高体系：tight(1.2) / normal(1.6) / relaxed(1.8)

#### 间距系统升级
- 现有 spacing 保留但扩充：xs(4) / sm(8) / md(16) / lg(24) / xl(32) / 2xl(48) / 3xl(64) / 4xl(80)
- 新增布局专用间距：--layout-gap / --section-gap / --content-padding

#### 阴影系统
- 从"柔和阴影"改为"纸墨阴影"——更硬朗、更有层次感
- 基于墨色而非暖棕色：使用 `rgba(0, 0, 0, alpha)` 而非 `rgba(67, 45, 28, alpha)`

#### 玻璃效果
- 从通用样式降级为特定场景点缀（浮层、弹窗、hover 状态）
- 主体内容使用实底背景 + 细腻投影

### 2. 统一布局系统

将 GuestLayout / UserLayout / AdminLayout 合并为一个可配置的 **BaseLayout**，通过 props/slots 差异化：

```
BaseLayout
├── Header (统一组件)
│   ├── 左: SiteLogo + 导航 (可配置)
│   ├── 中: 搜索 (公开端) | 面包屑 (用户/管理端)
│   └── 右: 用户菜单 | 登录注册入口
├── Sidebar (统一组件，可折叠)
│   ├── 公开端: 薄侧边栏 (桌面仅推荐/标签云, 移动端收起)
│   ├── 用户端: 正常宽度, 菜单项含 icon+text
│   └── 管理端: 正常宽度, 分组导航
├── Content Area (main slot)
└── FooterBar (统一极简组件)
```

#### 布局差异策略

| 维度 | 公开端 (Guest) | 用户端 (User) | 管理端 (Admin) |
|-----|---------------|--------------|---------------|
| 侧边栏 | 桌面薄栏, 移动无 | 完整侧边栏 | 完整侧边栏 |
| Header | Logo + 导航 + 搜索 | Logo + 面包屑 | Logo + badge + 面包屑 |
| Footer | 极简底栏 | 极简底栏 | 极简底栏 |
| 视觉基调 | 开阔温润 | 专注高效 | 清晰利落 |

### 3. 组件体系重构（分层策略）

#### 第一层：完全自建视觉组件
```
components/
  ui/
    ArButton.vue      ← NButton 替换
    ArTag.vue         ← NTag 替换  
    ArCard.vue        ← 卡片容器
    ArBadge.vue       ← 徽标
    ArDivider.vue     ← 分割线
    ArIcon.vue        ← 图标包装
    ArInput.vue       ← NInput 替换（外壳定制，内部保留 Naive UI 逻辑）
```

#### 第二层：业务组件（直接映射 API）
每个核心 API 对应一个业务组件，组件内部直接调用 API：

```
components/
  blog/
    PostCard.vue      ← getBlogPostsApi → 列表展示
    PostDetail.vue    ← getPostBySlugApi → 详细阅读
    PostEditor.vue    ← createPostApi / updatePostApi
    CommentList.vue   ← getPostCommentsApi
    CommentForm.vue   ← createPostCommentApi
    LikeButton.vue    ← likePostApi
    FavoriteButton.vue ← addFavoriteApi / removeFavoriteApi
    TagList.vue       ← getBlogTagsApi
  
  user/
    UserCard.vue      ← 用户信息展示
    UserMenu.vue      ← 用户导航菜单
  
  admin/
    ModerationPanel.vue ← 审核操作面板
    UserTable.vue       ← 用户管理
    SystemMetrics.vue   ← 系统监控
    PostTable.vue        ← 帖子管理
```

#### 第三层：复杂组件保留 Naive UI 封装
- `NDataTable` — 保留，仅通过 CSS 变量覆写外观
- `NForm` + 复杂校验 — 保留，包装为 ArForm
- `NUpload` — 保留
- `NSelect` / `NCheckbox` / `NRadio` — 暂保留，逐步替换

### 4. 页面整合与裁剪

#### 保留并优化的页面

| 分组 | 页面 | 说明 |
|-----|------|------|
| 公开端 | Home, Explore, PostDetail, About, Login, Register, 404, 403 | 全部保留，视觉重构 |
| 用户端 | Console, CreatorDashboard, PostEditor, Posts, Profile | 全部保留，视觉重构 |
| 管理端 | ModerationPosts (帖子审核) | **核心保留** |
| 管理端 | Users | **核心保留** |
| 管理端 | SystemMonitor | **核心保留** |
| 管理端 | AssetAdmin / OssAdmin | 合并为 ResourceAdmin |

#### 可裁剪/合并的页面

| 页面 | 处理方式 | 原因 |
|-----|---------|------|
| ConfigAdmin | 裁剪 | 非核心功能，配置可通过 API 管理 |
| CrawlerAdmin | 裁剪 | 非核心功能 |
| Plugins | 裁剪 | 非核心功能 |
| ModerationPending | 合并入 ModerationPosts | 功能重叠 |
| OssAdmin | 合并入 AssetAdmin | 同为资源管理 |

### 5. 动效系统

#### 基础动效规范
- **页面过渡**: View Transitions API + CSS opacity/transform 组合，Apple 式平滑
- **卡片交互**: hover scale(1.02) + shadow 演进，带 easing curve
- **列表进入**: stagger animation（子项依次出现，间隔 50-80ms）
- **侧边栏展开**: 弹性缓动 cubic-bezier(0.34, 1.56, 0.64, 1)

#### 国风点缀动效
- **加载状态**: 墨滴入水晕开效果（CSS radial-gradient animation）
- **点赞/收藏**: 微粒子扩散效果（同 Apple 式但更克制）
- **页面切换**: 轻微 ink wash 过渡（非必须，性能降级友好）

### 6. Footer → 极简底栏

```html
<footer class="footer-bar">
  <span>© 2024 锦年志</span>
  <span class="sep">·</span>
  <a>苏ICP备2026004054号-1</a>
  <span class="sep">·</span>
  <a>苏公网安备...</a>
</footer>
```

- 单行，不设背景色/玻璃效果，仅用 border-top 与内容区区分
- 在所有 Layout 中统一使用，用户端/管理端可隐藏（通过 BaseLayout prop）

## Impact

- Affected specs: 全部前端 UI 层
- Affected code: `frontend/src/` 下几乎所有文件（styles/components/layouts/views）
- **未经影响的**: 后端 API 层、数据模型、路由定义、store 状态、服务层代码
- **BREAKING**: `theme.css` 色系 token 变更，现有组件引用旧变量需更新

## Technical Constraints

- Vue 3 + TypeScript + Vite 构建体系不变
- Naive UI 保留为底层依赖但减少直接使用
- 所有动效必须响应 `prefers-reduced-motion`
- 深色模式需全程同步
- 组件库分层重构可并行进行
