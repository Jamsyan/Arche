# Tasks

## Task 1: 修复 OSS 单元测试（18 个失败）

更新 `backend/tests/unit/test_oss.py` 中的所有测试用例，将不允许的 MIME 类型替换为 `ALLOWED_MIME_TYPES` 中的图片类型。

- [ ] SubTask 1.1: 修复文件名验证测试
  - 将 `test_filename_with_path_traversal_raises_error` 中 `text/plain` → `image/png`
  - 将 `test_filename_with_backslash_raises_error` 中 `text/plain` → `image/png`
  - 将 `test_normal_filename_passes` 中 `application/pdf` → `image/png`，文件名 `my-document.pdf` → `image.png`
- [ ] SubTask 1.2: 修复 `test_allowed_mime_types_pass`
  - 将白名单测试列表更新为实际允许的 MIME 类型（仅图片类型）
- [ ] SubTask 1.3: 修复上传测试
  - 将 `test_upload_creates_database_record` 中 `text/plain` → `image/png`
  - 将 `test_upload_creates_correct_object_key` 中 `text/plain` → `image/png`
- [ ] SubTask 1.4: 修复配额测试
  - 将 `test_p1_user_has_quota_check` 等配额测试中 `text/plain` → `image/png`
- [ ] SubTask 1.5: 修复下载/删除/列表测试
  - 将所有剩余的 `text/plain` 使用替换为 `image/png`

## Task 2: 修复 import time 位置

- [ ] 将 `backend/core/__init__.py` 中 `record_request_stats` 函数体内的 `import time` 移到文件顶部的模块导入区

## Task 3: 为 soft_delete_user 添加重复删除防护

- [ ] 在 `backend/plugins/auth/services.py` 的 `soft_delete_user` 方法中，在设置删除字段之前检查 `deleted_at` 是否已设置，若是则抛出 `AppError`

## Task 4: 为 _path_stats 添加归档机制

- [ ] 在 `backend/plugins/system_monitor/stats.py` 中，将 `_path_stats` 重置前的数据保存到历史 `deque` 中
- [ ] 修改 `get_path_stats()` 返回合并后的累积数据

# Task Dependencies

- Task 1、2、3、4 互不依赖，可以并行执行
