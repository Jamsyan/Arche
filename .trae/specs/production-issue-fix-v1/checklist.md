# Checklist

## P0 组

### Task 1: CPU 监控容器兼容性 ✅
- [x] 容器环境检测逻辑已实现
- [x] cgroup 指标读取已实现，容器内不再使用 `psutil` 宿主值
- [x] 预警阈值改为可配置参数 (`CPU_WARN_THRESHOLD`)
- [x] `uv run pytest backend/tests/unit/test_system_monitor_service.py` 通过 ✅

### Task 2: 帖子详情页偶发 500 ✅
- [x] 浏览量更新使用原子 SQL + try/except 降级
- [x] 并发访问同一帖子不再产生 500
- [x] `uv run pytest backend/tests/unit/` 通过 ✅ (310 passed)

## P1 组

### Task 3: CI/CD 版本号跳跃 ✅
- [x] `fix:` 提交 → patch 提升
- [x] `feat:` 提交 → minor 提升
- [x] `breaking:`/`refactor:` → major 提升
- [x] CHANGE_PERCENT 阈值已调整 (major > 50%, minor > 15%)

### Task 4: MD 文件上传流程 ✅
- [x] 上传 .md 后自动跳转编辑模式
- [x] 标题 + 正文自动填充到编辑器
- [x] 无封面时自动生成渐变封面 (getCoverGradient)

### Task 5: 用户等级修改即时反馈 ✅
- [x] `loadUsers(page.value)` 有 `await`
- [x] 本地乐观更新已实现
- [x] 编辑弹窗防重复提交 (`:loading` 状态)

### Task 6: 管理员重置密码 ✅
- [x] 后端 `reset_password` 方法已实现
- [x] `POST /auth/users/{id}/reset-password` 端点已添加
- [x] 前端操作栏"重置密码"按钮已添加
- [x] 仅 P0 可调用
- [x] `uv run pytest backend/tests/unit/test_auth.py -v` 通过 ✅ (29 passed)

## P2 组

### Task 7: Markdown 渲染 ✅
- [x] MD 渲染库已安装 (`marked`)
- [x] `renderContent` 重构为完整 MD 渲染管线
- [x] 副标题/粗体/列表/代码块/引用等语法正确渲染
- [x] `cd frontend && npm run type-check && npm run build` 通过 ✅

### Task 8: 帖子卡片尺寸 ✅
- [x] 探索页 `minmax` 已调整为 `220px`
- [x] 首页 `latest-grid` 已约束最大宽度
- [x] `PostCard.vue` 有 `max-width: 420px` 上限
- [x] `cd frontend && npm run type-check && npm run build` 通过 ✅

### Task 9: 个人中心优化 ✅
- [x] 后端 `_user_to_dict` 暴露 email 字段 (bio/birthday 模型无此字段)
- [x] 前端 `UserInfo` 类型补充字段
- [x] Profile.vue 重新设计：头像区域、信息卡片、统计卡片
