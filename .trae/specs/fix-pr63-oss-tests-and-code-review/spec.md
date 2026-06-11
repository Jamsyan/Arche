# Fix PR #63 - OSS 测试修复与代码审查问题修复

## Why

PR #63 引入了多项重大变更，其中 OSS 存储服务的 `ALLOWED_MIME_TYPES` 从支持多种文件类型（txt/pdf/csv/json/zip 等）缩小为仅限图片类型（png/jpg/jpeg/gif/webp）。这导致 18 个现有的 OSS 单元测试全部失败，因为测试代码仍在使用 `text/plain`、`application/pdf` 等非图片 MIME 类型。此外，代码审查发现的 3 个问题也需要修复。

## What Changes

### 1. 修复 18 个失败的 OSS 单元测试（`test_oss.py`）

- **MIME 类型更新**：将所有测试中的 `text/plain`、`application/pdf` 等非图片 MIME 替换为允许的图片 MIME（`image/png`、`image/jpeg` 等）
- **同名断言调整**：`test_normal_filename_passes` 测试使用 `application/pdf` 现在为不允许类型，需改用 `image/png`
- **文件名验证测试修复**：`test_filename_with_path_traversal_raises_error` 等先用非法文件名触发错误，需改用允许的 MIME 类型
- **`test_allowed_mime_types_pass` 更新**：白名单测试列表需同步更新为实际允许的 MIME 类型

### 2. 修复代码审查问题

- **`import time` 移到模块顶部**：将 `backend/core/__init__.py` 中 `record_request_stats` 函数体内的 `import time` 移到文件顶部模块导入区
- **`soft_delete_user` 添加重复删除防护**：在 `backend/plugins/auth/services.py` 的 `soft_delete_user` 方法中添加 `deleted_at` 检查，已删除用户再次调用时抛出错误
- **`_path_stats` 添加归档机制**：在 `backend/plugins/system_monitor/stats.py` 中，将 `_path_stats` 重置前的数据归档到历史记录中，避免数据丢失

### NOT Changing

- **BlogFavorite ID 字段类型**：用户表示暂不处理，后续系统化调整

## Impact

- Affected specs: 无（新增 spec）
- Affected code:
  - `backend/tests/unit/test_oss.py` — 18 个测试用例需更新 MIME 类型
  - `backend/core/__init__.py` — import time 位置调整
  - `backend/plugins/auth/services.py` — 添加重复删除防护
  - `backend/plugins/system_monitor/stats.py` — path_stats 归档机制

## ADDED Requirements

### Requirement: OSS 测试使用允许的 MIME 类型

The system SHALL update all OSS unit tests to use only MIME types that are in the current `ALLOWED_MIME_TYPES` list.

#### Scenario: 文件名验证测试
- **WHEN** 测试使用带路径穿越字符的文件名且 MIME 类型为 `image/png`
- **THEN** 应触发 `invalid_filename` 错误

#### Scenario: MIME 白名单测试
- **WHEN** 测试 `test_allowed_mime_types_pass`
- **THEN** 只应测试当前 `ALLOWED_MIME_TYPES` 中的类型

### Requirement: soft_delete_user 幂等性

The system SHALL prevent re-soft-deleting an already soft-deleted user.

#### Scenario: 重复删除
- **WHEN** 对已软删除的用户再次调用 `soft_delete_user`
- **THEN** 应抛出 `AppError`，提示用户已被删除

### Requirement: _path_stats 数据持久化

The system SHALL preserve per-path request statistics across 5-minute reset windows by archiving into history.

#### Scenario: 路径统计查询
- **WHEN** 在多个 5 分钟窗口后查询 `get_path_stats()`
- **THEN** 返回的数据应包含所有窗口的累积统计（不丢失）
