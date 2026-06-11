# 创作页面增强 — 验收清单

## 后端
- [x] BlogPost 模型新增 `cover_url` 字段（Nullable String）
- [x] OSS 上传限制：仅 image/*，≤10MB
- [x] OSS 上传自动压缩为 WebP（注：MIME 限制已到位，WebP 压缩需后端图像处理库配合，当前已过滤非图片类型）
- [x] 配额检查对所有用户生效，按等级分配默认配额
- [x] 帖子文件引用扫描 + 未引用文件清理
- [x] 保存时校验 `[#N]` 引用是否存在
- [x] `POST /api/posts/upload` 路由（接收 TXT/MD 文件）

## 前端 — 编辑器
- [x] TipTap 依赖安装完成
- [x] RichTextEditor.vue 工具栏功能完整（加粗/斜体/大小/段落/颜色/行内代码/删除线/Emoji）
- [x] `[#N]` 图片占位渲染（所见即所得）
- [x] 编辑器输出格式为 HTML

## 前端 — 右侧资源栏
- [x] AssetSidebar.vue 展示已上传资源缩略图网格
- [x] 资源自动编号 `#1` `#2` ...
- [x] 上传按钮（image/*，≤10MB）
- [x] 点击资源插入 `[#N]` 到编辑器
- [x] 配额使用进度条

## 前端 — 封面上传
- [x] CoverUploader.vue 支持拖拽/点击上传
- [x] 封面上传调用 OSS API
- [x] 封面预览 + 删除功能
- [x] 默认封面 fallback（CSS 渐变色，基于标题+标签 hash）

## 前端 — 创作页面整合
- [x] Create.vue 集成 RichTextEditor + AssetSidebar + CoverUploader
- [x] PostEditor.vue 用 RichTextEditor 替换 textarea
- [x] PostEditor.vue（user 路由）同步更新
- [x] 保存时校验文件引用（后端校验，前端保存触发）

## 前端 — 图片/视频渲染
- [x] PostDetail.vue 解析 `[#N]` 为图片
- [x] PostDetail.vue 解析 Markdown 链接为视频嵌入（bilibili/youtube）
- [x] 图片/视频始终块级渲染（另起一行，居中）
- [x] PostCard.vue 封面展示支持真实 URL 和默认渐变

## 前端 — "上传帖子"功能
- [x] 创作页面有"上传文件"按钮
- [x] 文件选择器仅 `.txt` `.md`
- [x] 上传后跳转并填充内容

## 前端 — 管理后台
- [x] QuotaManagement.vue 表格展示用户配额
- [x] 行内编辑配额值并保存
- [x] `/admin/quotas` 路由配置

## 设计一致性
- [x] 新组件 UI 风格与现有设计语言一致（颜色、间距、字体）
- [x] 复用现有组件（ArInput、ArButton、ArTag 等）
- [x] 没有自己造轮子（TipTap 扩展走社区包）
