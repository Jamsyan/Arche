# 生产环境问题统一修复 Spec

## Why

项目 v1.0.1 上线后，在生产环境中发现了 11 个问题，涵盖 CI/CD 工作流、后端稳定性、前端功能和视觉体验。需要系统性地调研根因并逐一修复，确保生产环境稳定运行。

## Overview

共 11 个问题，按影响域分为 4 组：

| 分组 | 问题数 | 核心影响 |
|---|---|---|
| **CI/CD 工作流** | 1 | 版本号跳跃 |
| **后端稳定性** | 2 | CPU 误报、偶发 500 |
| **前端功能缺陷** | 4 | MD 不渲染、MD 上传、等级修改、重置密码 |
| **前端视觉优化** | 3 | 卡片尺寸、个人中心 |
| **其他补充** | 1 | 帖子加载失败 |

## What Changes

### P0 组：生产故障级

#### 1. CPU 监控误报
- **问题**：Docker 容器中使用 `psutil.cpu_percent(interval=0)` 读到宿主机 CPU 瞬时值，非容器真实使用量
- **解决方案**：
  - 检测容器环境，使用 cgroup 指标（`/sys/fs/cgroup/cpu.stat` 或 Docker API）
  - 回退方案：使用 `psutil.cpu_percent(interval=1)` 增加采样间隔，并对多次采样做移动平均
  - 预警阈值从固定 80% 改为可配置

#### 2. 帖子偶发性 500
- **问题**：`get_post_by_slug` 中 `views += 1 → commit → refresh` 在 SQLite 并发写入时产生写冲突
- **解决方案**：
  - 为 `BlogPost.views` 增加版本号乐观锁或使用 `UPDATE ... SET views = views + 1` 原子操作
  - 在 `get_post_by_slug` 中加 try/except 包裹浏览量更新逻辑，失败时不影响主流程
  - 将 `session.refresh()` 替换为直接读取最新值

### P1 组：严重功能缺陷

#### 3. 版本号跳跃
- **问题**：版本路由以 LOC 变更百分比为主决定因子，`fix:` 提交导致 major bump
- **解决方案**：
  - 改为"提交信息优先，LOC 为 fallback"策略
  - `fix:` → patch 提升
  - `feat:` → minor 提升
  - `breaking:`/`refactor:` → major 提升
  - 调整 CHANGE_PERCENT 阈值（major > 50%, minor > 15%）

#### 4. MD 文件上传流程
- **问题**：上传 MD 文件后进入编辑模式但不自动填充标题/正文，且无封面自动生成
- **解决方案**：
  - 上传 MD 后解析出标题 + 正文，自动填充到编辑器对应字段
  - 无封面时调用 `getCoverGradient` 自动生成封面
  - 上传后直接跳转到编辑模式（当前已有部分实现但数据流不通）

#### 5. 用户等级修改无即时反馈
- **问题**：`handleLevelChange` 中 `loadUsers(page.value)` 缺少 `await`
- **解决方案**：
  - 补上 `await loadUsers(page.value)`
  - 乐观更新：在 API 返回后先直接更新本地 `users` 列表中对应行的 level 值，再异步刷新
  - 禁用编辑弹窗中的重复提交

#### 6. 缺少重置密码
- **问题**：管理员无法重置用户密码
- **解决方案**：
  - 后端新增 `POST /auth/users/{id}/reset-password` 接口，重置为默认密码 `123456`
  - 前端用户管理操作栏增加"重置密码"按钮
  - 仅 P0 管理员可用

### P2 组：功能/体验缺陷

#### 7. MD 渲染不处理
- **问题**：`renderContent` 只处理视频嵌入、图片引用和换行，无 MD→HTML 转换
- **解决方案**：
  - 引入 `markdown-it` 或 `marked` 库
  - 替换 `renderContent` 中的简单文本处理为完整 MD 渲染管线
  - 支持标题、粗体、列表、代码块、引用、链接等标准 MD 语法

#### 8. 帖子卡片尺寸
- **问题**：首页/探索页卡片在宽屏下过大，无 `max-width` 上限
- **解决方案**：
  - 探索页 `minmax(280px, 1fr)` → `minmax(220px, 1fr)`
  - 首页 `latest-grid` 增加 `max-width` 约束
  - PostCard 组件增加 `max-width: 400px` 上限

#### 9. 个人中心太简陋
- **问题**：Profile.vue 只有 5 行基础信息
- **解决方案**：
  - 增加头像展示（使用现有 `ArAvatar`）
  - 增加邮箱字段
  - 增加统计卡片区（发帖数、阅读量、点赞数、收藏数）
  - 增加个人简介（bio 字段后端需补充暴露）
  - 优化视觉布局

## Impact

### Affected specs
- CI/CD pipeline (build.yml)
- backend plugin system_monitor
- backend plugin blog
- backend plugin auth
- frontend PostDetail component
- frontend PostCard component
- frontend users management (UsersOverview + UserTable)
- frontend Profile page
- frontend Create page

### Affected code
- `.github/workflows/build.yml`
- `backend/plugins/system_monitor/services.py`
- `backend/plugins/system_monitor/routes.py`
- `backend/plugins/blog/services.py`
- `backend/plugins/blog/routes.py`
- `backend/plugins/auth/routes.py`
- `backend/plugins/auth/services.py`
- `frontend/src/components/blog/PostDetail.vue`
- `frontend/src/components/blog/PostCard.vue`
- `frontend/src/views/user/Profile.vue`
- `frontend/src/views/admin/UsersOverview.vue`
- `frontend/src/components/admin/UserTable.vue`
- `frontend/src/views/Home.vue`
- `frontend/src/views/Explore.vue`
- `frontend/src/views/Create.vue`

## Requirements

### P0-1: CPU 监控容器兼容
- **WHEN** 系统运行在 Docker 容器中
- **THEN** CPU 采集应使用容器级指标而非宿主机指标
- **AND** 预警阈值应为可配置参数

### P0-2: 帖子详情并发安全
- **WHEN** 多个用户同时访问同一帖子
- **THEN** 浏览量更新不因并发写入冲突导致 500
- **AND** 浏览量更新失败不应阻止帖子正常返回

### P1-1: 语义化版本控制
- **WHEN** 合并 `fix:` 提交的 PR
- **THEN** 版本号应执行 patch 提升
- **WHEN** 合并 `feat:` 提交的 PR
- **THEN** 版本号应执行 minor 提升

### P1-2: MD 文件上传自动填充
- **WHEN** 用户上传 .md 文件
- **THEN** 前端应自动解析标题和正文并填充编辑器
- **AND** 如无封面应自动生成渐变封面

### P1-3: 等级修改即时反馈
- **WHEN** 管理员修改用户等级并确认
- **THEN** 表格应立即反映更新后的等级值

### P1-4: 管理员重置密码
- **WHEN** 管理员点击重置密码
- **THEN** 该用户密码应重置为 `123456`
- **AND** 仅 P0 管理员可执行此操作

### P2-1: Markdown 渲染
- **WHEN** 帖子内容包含 Markdown 语法
- **THEN** 前端应正确渲染为 HTML

### P2-2: 卡片尺寸约束
- **WHEN** 帖子卡片在宽屏下展示
- **THEN** 应有最大宽度限制，探索页应更高密度

### P2-3: 个人中心丰富化
- **WHEN** 用户访问个人中心
- **THEN** 应展示头像、统计卡片、完整个人信息
