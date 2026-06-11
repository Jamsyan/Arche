# Tasks

执行顺序：P0 → P1 → P2，同优先级内可并行。

---

## Task 1: 修复 CPU 监控容器兼容性 [P0] ✅

- [x] 调研容器环境检测方案（检测 `/proc/1/cgroup`、`/sys/fs/cgroup/cpu.stat`）
- [x] 实现 cgroup v2 CPU 指标读取逻辑
- [x] 在 `SystemMonitorService` 中添加容器环境检测，容器内使用 cgroup 指标
- [x] 将预警阈值从硬编码 80% 改为可配置参数
- [x] 更新 `SystemMonitorSettings` 增加 `CPU_WARN_THRESHOLD` 配置项
- [x] 验证：运行测试 `uv run pytest backend/tests/unit/test_system_monitor_service.py` ✅ 3 passed

## Task 2: 修复帖子详情页偶发 500 [P0] ✅

- [x] 在 `get_post_by_slug` 中将浏览量更新改为原子 SQL 操作：`UPDATE blog_posts SET views = views + 1 WHERE id = :id`
- [x] 用 try/except 包裹浏览量更新逻辑，失败时降级、不影响主流程返回
- [x] 验证：运行测试 `uv run pytest backend/tests/unit/` ✅ 310 passed

## Task 3: 修复 CI/CD 版本号跳跃 [P1] ✅

- [x] 修改 `build.yml` 版本路由逻辑：提交信息优先级高于 LOC 百分比
  - `fix:` → patch
  - `feat:` → minor
  - `breaking:`/`refactor:` → major
- [x] 调整 CHANGE_PERCENT 阈值：major > 50%, minor > 15%

## Task 4: 修复 MD 文件上传流程 [P1] ✅

- [x] 调试 `Create.vue` 中 `handleFileSelected` 的数据流，上传后自动填充标题 + 正文到编辑器
- [x] 上传成功后直接跳转编辑模式并自动填充标题 + 正文
- [x] 无封面时自动调用 `getCoverGradient` 生成渐变色封面

## Task 5: 修复用户等级修改无即时反馈 [P1] ✅

- [x] 在 `handleLevelChange` 中补上 `await loadUsers(page.value)`
- [x] 实现乐观更新：API 返回后直接在本地 `users` 列表中更新对应行的 level
- [x] 编辑弹窗确认按钮添加 `:loading` 状态防止重复提交

## Task 6: 实现管理员重置密码 [P1] ✅

- [x] 后端 `auth/services.py` 新增 `reset_password(user_id, new_password)` 方法
- [x] 后端 `auth/routes.py` 新增 `POST /auth/users/{id}/reset-password` 端点（仅 P0）
- [x] 前端 `UsersOverview.vue` 操作栏增加"重置密码"按钮
- [x] 重置成功后前端弹出提示并自动刷新列表
- [x] 验证：运行测试 `uv run pytest backend/tests/unit/test_auth.py -v` ✅ 29 passed

## Task 7: 实现 Markdown 渲染 [P2] ✅

- [x] 安装 `marked` 库
- [x] 重构 `PostDetail.vue` 的 `renderContent` 函数，使用 MD 渲染库
- [x] 渲染管线：MD → HTML → 视频嵌入处理 → 图片引用处理 → 输出
- [x] 添加必要的 CSS 样式（标题、列表、代码块、引用等）
- [x] 验证：`cd frontend && npm run type-check && npm run build` ✅

## Task 8: 修复帖子卡片尺寸 [P2] ✅

- [x] 修改 `Explore.vue` 的 `explore-grid`：`minmax(280px, 1fr)` → `minmax(220px, 1fr)`
- [x] 修改 `Home.vue` 的 `latest-grid`：添加 `grid-template-columns` 约束，限制卡片最大宽度
- [x] `PostCard.vue` 添加 `max-width` 上限
- [x] 验证：`cd frontend && npm run type-check && npm run build` ✅

## Task 9: 优化个人中心页面 [P2] ✅

- [x] `UserInfo` 类型补充 `bio`、`email`、`avatar` 字段声明
- [x] 后端 `auth/services.py` 中 `_user_to_dict` 暴露 `bio`、`email`、`birthday` 等字段（email 已在，bio/birthday 模型无此字段）
- [x] 前端 `Profile.vue` 重新设计布局：
  - 头像 + 用户名/昵称头部区域
  - 信息卡片区（邮箱、角色、注册时间、生日等）
  - 统计数据卡片区（发帖数、阅读量、点赞数、收藏数）

---

# Task Dependencies

- 所有 Task 之间无依赖关系，可并行执行
- 推荐执行顺序：Task 1 + 2（后端稳定性）→ Task 3 + 5 + 6 + 7 + 8 + 9 → Task 4
