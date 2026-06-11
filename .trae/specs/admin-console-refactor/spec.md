# 管理控制台重构 Spec

## Why

当前管理后台存在两个问题：
1. **两套管理体系并存**：AI 自动生成了一个独立的 `AdminLayout`，与 ConsoleShell 中的"管理"组功能重叠、定位模糊
2. **管理功能平铺无层次**：所有管理页面同层级排列，随着功能增多难以扩展和维护

需要统一为**一套控制台**，按管理任务性质划分大类层级，并预留快捷访问扩展能力。

## What Changes

### 架构变更

- **删除** `AdminLayout.vue`（AI 生成的独立管理壳，从未被使用）
- **删除** `role.ts`（动态注入的 admin 路由，合并到 `static.ts`）
- **ConsoleShell 重构**：移除已迁移的"创作"组；新增"管理"组（三大类）+ "快捷访问"组
- **控制台变为管理员独占**：普通用户不再可访 `/console`，也不显示控制台入口

### 侧边栏新结构

```
控制台首页                          ← 保留，去掉顶部"导航"标签
──────── ─ ─ ─ ─ ─                ← 视觉分割线
用户管理                            ← 管理组（无组文字标签，点击跳转卡片页）
内容管理
运维管理
──────── 快捷访问 ────────────────  ← 有组标签
[动态快捷方式 1]                    ← 用户自定义，存 localStorage
[+] 添加快捷方式
```

### 路由变动

| 路由 | 变更 |
|---|---|
| `/admin/*` | 改为 `layout: 'guest'` + `console: true`，不再用 `layout: 'admin'` |
| `/console` | 增加 `level: 0`，仅管理员可访 |
| `/posts`, `/creator`, `/profile` | 移除 `console: true`，不再套 ConsoleShell |
| `/tasks` (新建) | 托管任务概览页，顶部导航入口，非控制台内部 |
| `/tasks/crawler` | 爬虫管理详情页 |
| `/tasks/cloud` | 云训练管理详情页 |

### 三大类及卡片划分

| 大类 | 卡片（中小类） |
|---|---|
| **用户管理** (`/admin/users`) | 用户列表、帖子资产、评论资产、静态资产 |
| **内容管理** (`/admin/content`) | 帖子审核、评论管理、举报处理 |
| **运维管理** (`/admin/ops`) | 系统监控、运行时配置、OSS 存储管理、权限管理、插件管理、日志管理 |

### 快捷方式

- 用户可从卡片页手动添加快捷方式到侧边栏
- 可拖拽排序、移除
- 持久化存储在 `localStorage`
- 第一版实现手动添加/移除，拖拽排序延后

### 页面交互模型

```
左侧侧边栏 (大类)                 右侧内容区
  ├ 控制台首页                    卡片页（点击大类时展示）
  ├ ─ ─ ─ ─ ─                    每个卡片 = 数据预览 + 跳转按钮
  ├ 用户管理   ──点击──→         ┌─────────────────┐
  ├ 内容管理                     │ 用户列表         │
  ├ 运维管理                     │ 总用户 128 人    │
  ├ ─ 快捷访问 ─                 │ → 进入管理       │
  ├ [快捷方式]                   └─────────────────┘
                                  ┌─────────────────┐
                                  │ 帖子资产         │
                                  │ 总帖子 456 篇    │
                                  │ → 进入管理       │
                                  └─────────────────┘
```

### 顶部导航(BaseHeader)变化

- 导航栏新增 `RouterLink`：**"托管任务"**，指向 `/tasks`
- 仅登录用户可见

### 后端待补充端点（列入规划，本次实现留占位）

| 端点 | 功能 | 优先级 |
|---|---|---|
| `GET/POST/PUT/DELETE /api/admin/plugins` | 插件 CRUD | 中 |
| `GET /api/admin/logs` | 日志检索 | 低 |

## Impact

- **Affected specs**: 路由系统、权限系统、布局系统
- **Affected code**:
  - `frontend/src/layouts/AdminLayout.vue` — **BREAKING**: 删除
  - `frontend/src/router/modules/role.ts` — **BREAKING**: 删除
  - `frontend/src/router/modules/static.ts` — 大幅修改，加入 admin 路由和 tasks 路由
  - `frontend/src/store/modules/permission.ts` — 简化，移除动态路由注入
  - `frontend/src/components/ConsoleShell.vue` — 重构侧边栏结构
  - `frontend/src/layouts/GuestLayout.vue` — 移除 ConsoleShell 对非管理员的包裹
  - `frontend/src/layouts/BaseHeader.vue` — 新增"托管任务"导航项
  - `frontend/src/views/user/Console.vue` — 保留，管理员首页
  - `frontend/src/views/admin/` — 3 个新建卡片页 + 子页面结构调整
  - `frontend/src/views/Tasks.vue` — 新建

## ADDED Requirements

### Requirement: 左侧导航重构
控制台侧边栏 SHALL 展示 控制台首页 + 管理组(三大类) + 快捷访问组 三层结构。
- **WHEN** 管理员登录并访问任意 `/admin/*` 或 `/console` 页面
- **THEN** 侧边栏显示三大类（用户管理、内容管理、运维管理）和快捷访问区

### Requirement: 三大类卡片页
每个大类 SHALL 有独立的卡片概览页，展示该分类下所有子功能的预览数据卡片。
- **WHEN** 用户点击用户管理
- **THEN** 右侧展示 4 张卡片（用户列表、帖子资产、评论资产、静态资产），每张卡片含数据预览和跳转按钮

### Requirement: 控制台管理员独占
控制台页面 `/console` 和所有 `/admin/*` 路由 SHALL 仅允许 level=0 的管理员访问。
- **WHEN** 普通用户访问 `/console` 或 `/admin/*`
- **THEN** 导航守卫跳转到 `/403`
- 普通用户的顶部导航按钮"控制台" SHALL 隐藏

### Requirement: 快捷访问功能
侧边栏底部 SHALL 提供"快捷访问"区域，用户可自定义常用功能的快捷入口。
- **WHEN** 用户在卡片页点击"添加到快捷访问"
- **THEN** 该功能被添加到侧边栏快捷访问区，并持久化到 localStorage

## MODIFIED Requirements

### Requirement: 路由系统
管理后台路由 SHALL 从动态注入改为静态定义在 `static.ts` 中。

### Requirement: 顶部导航
顶部导航栏 SHALL 新增"托管任务"入口，爬虫管理和云训练管理从控制台迁出。

## REMOVED Requirements

### Requirement: AdminLayout 独立管理壳
**Reason**: 功能与 ConsoleShell 重复，从未被使用
**Migration**: 删除文件，所有管理页面统一走 ConsoleShell

### Requirement: role.ts 动态路由注入
**Reason**: 不再需要动态路由，统一静态定义后由导航守卫控制权限
**Migration**: 内容合并到 static.ts，删除 role.ts

### Requirement: ConsoleShell 创作组
**Reason**: 创作功能已迁移到顶部导航栏
**Migration**: 从 ConsoleShell 中移除创作组

### Requirement: 普通用户的控制台访问
**Reason**: 控制台内容仅管理员可用
**Migration**: `/console` 路由增加 `level: 0`，普通用户顶部导航隐藏"控制台"入口
