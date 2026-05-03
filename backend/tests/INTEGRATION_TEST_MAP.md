# Arche 集成测试矩阵

## 目标

用于追踪各插件在 HTTP 集成层的覆盖情况，重点关注权限边界与关键成功路径，而不仅是覆盖率数字。

## 矩阵（2026-04-27）

| 插件 | 现有集成测试 | 未认证路径 | 越权路径 | 管理员成功路径 | 主要缺口 |
|---|---|---|---|---|---|
| `auth` | `test_auth_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | 管理端用户编辑/启停可补 |
| `github_proxy` | `test_github_proxy_api.py` | 已覆盖 | 已覆盖（P5 -> 403） | 已覆盖 | 下游 GitHub 错误映射细节可补 |
| `oss` | `test_oss_api.py` | 已覆盖 | 基础覆盖 | 已覆盖（stats） | admin 端 quota/rate-limit/files 缺口较大 |
| `crawler` | `test_crawler_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | 错误码分支与分页参数可补 |
| `cloud_integration` | `test_cloud_routes_api.py` | 已覆盖 | 已覆盖 | 已覆盖（mock service） | GPU 指标路径与异常分支可补 |
| `monitor` | `test_monitor_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | 列表筛选/分页边界可补 |
| `system_monitor` | `test_system_monitor_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | service 异常透传与排序字段兜底可补 |
| `config_mgmt` | `test_config_mgmt_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | groups/reload 的边界与空库场景可补 |
| `asset_mgmt` | `test_asset_mgmt_api.py` | 已覆盖 | 已覆盖 | 已覆盖 | 关键词/时间筛选在 HTTP 层可补 |
| `blog` | （待补） | 缺失 | 缺失 | 缺失 | 路由体量最大，优先补集成测试 |

## 优先级

1. `blog`：先补公开列表、登录发帖、P0 审核、收藏/举报路径。
2. `oss`：扩展管理员端（quota、rate-limit、files）与 P1 配额边界。
3. 其余插件按错误分支与参数边界补强。

## 运行建议

```bash
# 快速回归集成层（不跑覆盖率）
uv run pytest backend/tests/integration --no-cov -ra --tb=short
```
