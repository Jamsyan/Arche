# 创作页面增强 Spec

## Why

当前创作页面功能过于基础（纯文本 textarea），缺少封面设置、富文本编辑、多媒体插入等核心能力，无法满足内容创作者的日常使用需求。同时已有完善的 OSS 插件未与编辑器打通，资源利用率低。

## What Changes

### 1. 封面系统（新增）
- **BlogPost 模型新增 `cover_url` 字段**，允许为 Nullable 字符串
- **封面上传组件**：在创作页面顶部/侧边引入封面上传区域，调用 OSS 上传接口
- **默认封面 fallback**：用户未设置封面时，根据文章标签/标题 hash 自动分配预设 CSS 渐变色
- **前端 PostCard/PostDetail 展示**：优先展示封面上传的图片，无封面时展示渐变默认封面

### 2. 富文本编辑器（替换）
- **引入 TipTap**（基于 ProseMirror，Vue3 生态最佳），按需加载扩展
- **功能范围**（精简路线）：
  - 加粗 / 斜体
  - 字体大小（大号/小号）
  - 段落格式（标题 H2/H3、正文、引用块）
  - 文字颜色（有限色板，不开放自由取色）
  - 行内代码 / 删除线
  - Emoji 选择器
- **不包含**：表格、代码块高亮、拖拽调整图片大小、视频内嵌上传

### 3. 右侧 OSS 资源栏（新增）
- 创作页面右侧新增竖栏面板："帖子素材"
- 功能：
  - 展示当前帖子已上传的资源列表（图片、GIF）
  - 上传按钮（调用 OSS upload API，限制类型为 image/*，大小 ≤10MB）
  - 资源自动编号 `#1` `#2` `#3` ...
  - 点击资源 → 在编辑器光标处插入 `[#N]`
  - 显示当前用户的 OSS 配额使用量（已用 / 总量）
- 资源按帖子 ID 临时关联，仅在发布/保存时根据引用情况决定是否持久化

### 4. 图片/视频渲染规则（修改）
- **`[#N]` 语法**：引用已上传的图片资源，渲染时替换为实际 OSS URL
- **`[标题](url)` 语法**：标准 Markdown 链接，渲染时检测域名（bilibili.com / youtube.com），自动转 iframe 嵌入
- **块级渲染**：图片和视频不管在源码中位于什么位置，渲染时始终**另起一行**居中显示，前后不隔行，后续文字另起一行
- **保存时校验**：
  - `[#N]` 引用的图片不存在 → 报错提示
  - 视频链接格式无效 → 报错提示
  - 未使用的文件 → 自动标记清理（不持久化）

### 5. 帖子文件生命周期（新增）
- 上传的文件与帖子临时关联（session 级别）
- 保存/发布时扫描正文中所有 `[#N]` 引用
- 仅持久化被引用的文件
- 未被引用的文件自动标记删除
- 每次编辑重新走上述流程

### 6. "上传帖子"功能（新增）
- 创作页面新增"上传文件"按钮
- 支持文件类型：TXT、MD
- 上传后解析文件内容作为正文
- 不走 OSS 流程，直接解析为帖子正文

### 7. 配额管理后台页面（新增）
- 路由：`/admin/quotas`（P0 管理员权限）
- 表格展示所有用户的 OSS 配额使用情况
- 支持管理员调整单个用户的 `quota_bytes`
- 复用现有的 Admin API（`GET/PUT /api/oss/admin/quotas`）

### 8. 配额体系完善（修改）
- 移除对 `user_level == 1` 的限制，所有用户启用配额检查
- 不同用户等级默认配额：
  - P5（普通用户）：500MB
  - P4（认证用户）：1GB
  - P3（创作者）：2GB
  - P2/P1：5GB
  - P0（管理员）：不限

### 9. 上传限制强化（修改）
- 图片/GIF：≤10MB，自动压缩为 WebP
- 其他文件类型一律拒绝
- 视频上传暂不支持

## Impact

- Affected specs: 创作（Create/PostEditor）、博客展示（PostDetail/PostCard）、管理后台、OSS 插件
- Affected code:
  - `backend/plugins/blog/models.py` — BlogPost 加 cover_url
  - `backend/plugins/blog/services.py` — 保存逻辑加文件引用校验
  - `backend/plugins/blog/routes.py` — 上传帖子路由
  - `backend/plugins/oss/` — 配额检查逻辑调整、上传限制调整
  - `frontend/src/components/blog/PostEditor.vue` — 完全重写
  - `frontend/src/views/Create.vue` — 结构调整，增加右侧栏
  - `frontend/src/views/user/PostEditor.vue` — 同步更新
  - `frontend/src/components/blog/PostDetail.vue` — 渲染逻辑修改
  - `frontend/src/components/blog/PostCard.vue` — 封面展示修改
  - `frontend/src/views/admin/QuotaManagement.vue` — 新增
  - `frontend/src/router/modules/` — 新增路由

## ADDED Requirements

### Requirement: 封面系统
The system SHALL allow users to set a cover image for each post, with automatic default cover fallback.

#### Scenario: 用户设置封面（成功）
- **WHEN** 用户点击封面上传区域、选择图片文件（≤10MB，image/*）
- **THEN** 文件上传至 OSS，封面区域显示该图片，表单数据中 `cover_url` 更新

#### Scenario: 用户未设置封面
- **WHEN** 用户保存/发布帖子且 `cover_url` 为空
- **THEN** 系统根据帖子标签和标题的 hash 值自动分配预设渐变色，用于前端展示

### Requirement: 富文本编辑器
The system SHALL provide a WYSIWYG rich text editing experience with the specified limited feature set.

#### Scenario: 编辑帖子正文
- **WHEN** 用户在编辑器中输入文本、应用格式（加粗/斜体/大小/颜色/段落）
- **THEN** 编辑器实时显示格式化效果，底层存储为结构化内容（HTML）

#### Scenario: 插入图片引用
- **WHEN** 用户在右侧资源栏点击某个资源（如 `#1`）
- **THEN** 编辑器在光标位置插入 `[#1]` 并以图片占位实时渲染

### Requirement: 帖子资源管理
The system SHALL manage uploaded resources at per-post granularity with automatic cleanup of unreferenced files.

#### Scenario: 保存时清理未引用资源
- **WHEN** 用户保存帖子，正文中包含 `[#1]` `[#3]` 但不包含 `[#2]`
- **THEN** 系统持久化 #1 和 #3 关联的文件，#2 关联的文件标记为待删除

### Requirement: 图片/视频块级渲染
The system SHALL render all embedded images and videos as block elements (new line, centered), regardless of their position in the source text.

#### Scenario: 行内引用渲染为块级
- **WHEN** 用户写 `这是一张图片[#1]后面还有文字`
- **THEN** 渲染结果为：`这是一张图片`（段落结束）→ 图片（居中单独一行）→ `后面还有文字`（新段落开始）

### Requirement: 配额管理系统
The system SHALL enforce OSS storage quotas for all users based on their user level.

#### Scenario: 超出配额
- **WHEN** 用户上传文件且已用空间 + 文件大小 > 配额
- **THEN** 上传被拒绝，返回 403 状态码和配额超出提示

### Requirement: 帖子文件上传
The system SHALL support uploading TXT/MD files to create new posts.

#### Scenario: 上传 TXT 创建帖子
- **WHEN** 用户点击"上传帖子"按钮，选择 `.txt` 或 `.md` 文件
- **THEN** 系统解析文件内容作为正文，自动提取标题（从第一个 `#` 标题或文件名），打开创作页面并填充内容

### Requirement: 管理员配额管理
The system SHALL provide an administrative interface for viewing and modifying user OSS quotas.

#### Scenario: 调整用户配额
- **WHEN** 管理员在 `/admin/quotas` 页面修改某个用户的配额值并保存
- **THEN** 系统更新 `UserOSSQuota` 表中对应记录，前端显示更新后的值

## MODIFIED Requirements

### Requirement: 文件上传限制
- **BEFORE**: 上传时仅对 P1 用户做配额检查，允许所有 MIME 类型
- **AFTER**: 所有用户启用配额检查，仅允许 `image/*` 类型，单文件 ≤10MB

### Requirement: OSS 文件存储
- **BEFORE**: 上传即持久化，按用户空间隔离
- **AFTER**: 上传与帖子 session 关联，仅在保存/发布时根据正文引用关系决定文件是否持久化

### Requirement: 视频嵌入
- **BEFORE**: 不支持
- **AFTER**: 通过 `[标题](url)` 语法嵌入外部视频链接，前端渲染时自动识别 bilibili/youtube 并转 iframe

## REMOVED Requirements

### Requirement: 纯文本 textarea 编辑器
**Reason**: 被 TipTap 富文本编辑器替代
**Migration**: 所有现有文本内容在切换后仍可通过富文本编辑器编辑，向后兼容
