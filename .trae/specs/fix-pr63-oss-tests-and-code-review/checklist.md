# Checklist

## Task 1: OSS 测试修复

- [x] `test_filename_with_path_traversal_raises_error` 使用允许的 MIME 类型且能正确触发 `invalid_filename`
- [x] `test_filename_with_backslash_raises_error` 使用允许的 MIME 类型且能正确触发 `invalid_filename`
- [x] `test_normal_filename_passes` 使用 `image/png` 且通过验证
- [x] `test_allowed_mime_types_pass` 只测试当前 `ALLOWED_MIME_TYPES` 中的类型
- [x] `test_upload_creates_database_record` 使用 `image/png` 并正确创建记录
- [x] `test_upload_creates_correct_object_key` 使用 `image/png` 并验证路径前缀
- [x] 所有配额测试（`test_p1_user_has_quota_check` 等）使用允许的 MIME 类型
- [x] 所有下载测试使用允许的 MIME 类型
- [x] 所有删除测试使用允许的 MIME 类型
- [x] 所有列表测试使用允许的 MIME 类型
- [x] 运行 `uv run pytest backend/tests/unit/test_oss.py -v` 全部通过

## Task 2: import time 位置修复

- [x] `import time` 在 `backend/core/__init__.py` 模块顶部而非函数体内

## Task 3: soft_delete_user 重复删除防护

- [x] 对已软删除的用户调用 `soft_delete_user` 抛出 `AppError`
- [x] `soft_delete_user` 对未删除用户正常执行删除操作

## Task 4: _path_stats 归档机制

- [x] `get_path_stats()` 返回跨窗口的累积数据
- [x] 5 分钟重置时数据不丢失
- [x] 运行 `uv run pytest --no-cov -ra --tb=short` 后端测试全部通过
