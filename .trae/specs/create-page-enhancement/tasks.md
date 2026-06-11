# Tasks

## Task 1: 后端 — BlogPost 模型加 cover_url 字段
- [x] 在 `backend/plugins/blog/models.py` 的 BlogPost 模型中新增 `cover_url: Mapped[Optional[str]]` 字段，默认 None
- [x] 在 `backend/plugins/blog/services.py` 中同步更新 `_post_to_dict` 返回值
- [x] 在 `frontend/src/services/api/blog.ts` 中同步更新 `BlogPost` 接口

## Task 2: 后端 — 上传限制强化 + 配额检查改进
- [x] 修改配额检查逻辑，移除 `user_level == 1` 限制
- [x] 实现按用户等级的默认配额分配逻辑
- [x] 增加 MIME 类型过滤（仅 `image/*`）和大小限制（≤10MB）
- [x] 上传路由权限从 `@require_level(1)` 改为 `@require_level(5)`

## Task 3: 后端 — 帖子文件生命周期管理
- [x] 新增 `PostFile` 模型（`blog_post_files` 表）
- [x] 实现保存/发布时的文件引用扫描逻辑（`scan_and_clean_post_files`）
- [x] 实现未被引用文件的自动清理逻辑
- [x] 在帖子保存 API 中集成文件校验（`validate_content`）

## Task 4: 后端 — "上传帖子"API
- [x] 在 `backend/plugins/blog/routes.py` 中新增 `POST /api/blog/upload-file` 路由
- [x] 前端 API 封装 `uploadPostFileApi`

## Task 5: 前端 — 安装 TipTap + 基础编辑器组件
- [x] 安装 TipTap 及相关扩展依赖
- [x] 创建 `RichTextEditor.vue`，实现完整工具栏
- [x] 添加 `[#N]` 图片占位渲染节点
- [x] 编辑器输出格式为 HTML

## Task 6: 前端 — 右侧 OSS 资源栏组件
- [x] 创建 `AssetSidebar.vue`，实现资源列表展示
- [x] 实现上传按钮和文件选择器
- [x] 实现点击插入 `[#N]`
- [x] 显示配额使用进度条

## Task 7: 前端 — 封面上传组件
- [x] 创建 `CoverUploader.vue`，支持拖拽/点击上传
- [x] 调用 OSS API 上传
- [x] 封面预览 + 删除功能

## Task 8: 前端 — 创作页面整合
- [x] PostEditor.vue 集成 RichTextEditor + CoverUploader
- [x] Create.vue 集成 AssetSidebar（右侧栏）
- [x] 保存时 cover_url 随 payload 提交
- [x] 组件索引文件更新导出

## Task 9: 前端 — 图片/视频渲染改造
- [x] PostDetail.vue 解析 `[#N]` 为图片
- [x] PostDetail.vue 解析 Markdown 链接为视频嵌入（bilibili/youtube）
- [x] 图片/视频始终块级渲染（另起一行，居中）
- [x] PostCard.vue 封面展示支持真实 URL 和默认渐变

## Task 10: 前端 — 默认封面 fallback 逻辑
- [x] 创建 `frontend/src/utils/cover.ts`，实现 `getCoverGradient` 函数
- [x] 在 PostCard、PostDetail 中统一应用

## Task 11: 前端 — "上传帖子"UI
- [x] 在创作页面新增"上传文件"按钮
- [x] 文件选择器仅 `.txt` `.md`
- [x] 上传后跳转并填充内容

## Task 12: 前端 — 配额管理后台页面
- [x] 创建 `QuotaManagement.vue`，表格展示用户配额
- [x] 行内编辑配额值并保存
- [x] 添加路由配置

## Task 13: 前端 — 路由更新
- [x] 在 `role.ts` 中添加 `/admin/quotas` 路由（P0 权限验证）

# Task Dependencies
- [Task 5, Task 6, Task 7] 可并行开发（前端独立组件）
- [Task 8] 依赖 [Task 5, Task 6, Task 7]
- [Task 9, Task 10] 依赖 [Task 8]
- [Task 1, Task 2, Task 3, Task 4] 可并行开发（后端独立）
- [Task 11] 依赖 [Task 4]
- [Task 12, Task 13] 独立
