# 测试覆盖报告

生成时间：2026-06-10 17:44:47

## 概览

| 组件 | 源文件数 | 已覆盖文件 | 测试文件数 | 测试用例数 | 状态 |
|------|---------|-----------|-----------|-----------|------|
| core | 10 | 8/10 | 9 | 101 | ✅ |
| asset_mgmt | 3 | 3/3 | 2 | 5 | ✅ |
| auth | 5 | 5/5 | 2 | 44 | ✅ |
| blog | 5 | 5/5 | 2 | 46 | ✅ |
| cloud_integration | 15 | 7/15 | 8 | 40 | ✅ |
| config_mgmt | 1 | 1/1 | 1 | 2 | ✅ |
| crawler | 14 | 14/14 | 5 | 51 | ✅ |
| deploy_webhook | 1 | 0/1 | 0 | 0 | ❌ |
| github_proxy | 3 | 3/3 | 2 | 49 | ✅ |
| monitor | 2 | 2/2 | 6 | 14 | ✅ |
| oss | 7 | 7/7 | 2 | 28 | ✅ |
| search | 2 | 0/2 | 0 | 0 | ❌ |
| system_monitor | 4 | 4/4 | 2 | 6 | ✅ |

- **组件覆盖率**：11/13 (84.6%)
- **文件覆盖率**：59/72 (81.9%)
- **测试用例总数**：386

## 详细文件清单

### core ✅

源文件 10 个，测试文件 9 个，测试用例 101 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `core/base_plugin.py` | test_base_plugin.py | - | 6 | ✅ |
| `core/config.py` | test_config.py | - | 15 | ✅ |
| `core/container.py` | test_container.py | - | 13 | ✅ |
| `core/db.py` | test_db.py | - | 8 | ✅ |
| `core/middleware.py` | test_middleware.py | - | 21 | ✅ |
| `core/models.py` | - | - | 0 | ❌ |
| `core/plugin_registry.py` | test_plugin_registry.py | - | 17 | ✅ |
| `core/settings/app.py` | test_settings_app.py | - | 4 | ✅ |
| `core/settings/base.py` | test_base_plugin.py, test_settings_base.py | - | 11 | ✅ |
| `core/uid.py` | - | - | 0 | ❌ |

### asset_mgmt ✅

源文件 3 个，测试文件 2 个，测试用例 5 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/asset_mgmt/models.py` | test_asset_mgmt_service.py | test_asset_mgmt_api.py | 5 | ✅ |
| `plugins/asset_mgmt/routes.py` | test_asset_mgmt_service.py | test_asset_mgmt_api.py | 5 | ✅ |
| `plugins/asset_mgmt/services.py` | test_asset_mgmt_service.py | test_asset_mgmt_api.py | 5 | ✅ |

### auth ✅

源文件 5 个，测试文件 2 个，测试用例 44 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/auth/middleware.py` | test_auth.py | test_auth_api.py | 44 | ✅ |
| `plugins/auth/models.py` | test_auth.py | test_auth_api.py | 44 | ✅ |
| `plugins/auth/routes.py` | test_auth.py | test_auth_api.py | 44 | ✅ |
| `plugins/auth/services.py` | test_auth.py | test_auth_api.py | 44 | ✅ |
| `plugins/auth/session.py` | test_auth.py | test_auth_api.py | 44 | ✅ |

### blog ✅

源文件 5 个，测试文件 2 个，测试用例 46 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/blog/models.py` | test_blog.py | test_blog_api.py | 46 | ✅ |
| `plugins/blog/routes.py` | test_blog.py | test_blog_api.py | 46 | ✅ |
| `plugins/blog/sensitive_words.py` | test_blog.py | test_blog_api.py | 46 | ✅ |
| `plugins/blog/services.py` | test_blog.py | test_blog_api.py | 46 | ✅ |
| `plugins/blog/settings.py` | test_blog.py | test_blog_api.py | 46 | ✅ |

### cloud_integration ✅

源文件 15 个，测试文件 8 个，测试用例 40 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/cloud_integration/cost/calculator.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/deploy/artifact_manager.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/deploy/ssh_executor.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/log_parser.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/models.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/orchestrator.py` | test_cloud_orchestrator.py | - | 6 | ✅ |
| `plugins/cloud_integration/providers/aliyun.py` | test_cloud_providers_aliyun.py | - | 3 | ✅ |
| `plugins/cloud_integration/providers/base.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/providers/mock.py` | test_cloud_providers_mock_registry.py | - | 4 | ✅ |
| `plugins/cloud_integration/providers/registry.py` | test_cloud_providers_mock_registry.py | - | 4 | ✅ |
| `plugins/cloud_integration/providers/zhixingyun.py` | test_cloud_providers_zhixingyun.py | - | 3 | ✅ |
| `plugins/cloud_integration/routes.py` | - | test_cloud_routes_api.py | 5 | ✅ |
| `plugins/cloud_integration/services.py` | test_cloud_services_resources.py, test_cloud_services_workflow.py | - | 11 | ✅ |
| `plugins/cloud_integration/settings.py` | - | - | 0 | ❌ |
| `plugins/cloud_integration/steps.py` | - | - | 0 | ❌ |

### config_mgmt ✅

源文件 1 个，测试文件 1 个，测试用例 2 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/config_mgmt/routes.py` | - | test_config_mgmt_api.py | 2 | ✅ |

### crawler ✅

源文件 14 个，测试文件 5 个，测试用例 51 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/crawler/link_extractor.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/models.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/base.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/classify.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/fetch.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/parse.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/quality.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/pipeline/storage.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/probe.py` | test_crawler_scheduler_probe.py | - | 10 | ✅ |
| `plugins/crawler/routes.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/seed_manager.py` | test_crawler_seed_manager.py | - | 8 | ✅ |
| `plugins/crawler/services.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/settings.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |
| `plugins/crawler/url_scheduler.py` | test_crawler_orchestrator.py, test_crawler_pipeline.py, test_crawler_scheduler_probe.py, test_crawler_seed_manager.py | test_crawler_api.py | 51 | ✅ |

### deploy_webhook ❌

源文件 1 个，测试文件 0 个，测试用例 0 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/deploy_webhook/settings.py` | - | - | 0 | ❌ |

### github_proxy ✅

源文件 3 个，测试文件 2 个，测试用例 49 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/github_proxy/routes.py` | test_github_proxy.py | test_github_proxy_api.py | 49 | ✅ |
| `plugins/github_proxy/services.py` | test_github_proxy.py | test_github_proxy_api.py | 49 | ✅ |
| `plugins/github_proxy/settings.py` | test_github_proxy.py | test_github_proxy_api.py | 49 | ✅ |

### monitor ✅

源文件 2 个，测试文件 6 个，测试用例 14 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/monitor/models.py` | test_monitor_models.py | - | 1 | ✅ |
| `plugins/monitor/routes.py` | test_monitor_routes.py | - | 3 | ✅ |

### oss ✅

源文件 7 个，测试文件 2 个，测试用例 28 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/oss/aliyun.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/backends.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/models.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/rate_limiter.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/routes.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/services.py` | test_oss.py | test_oss_api.py | 28 | ✅ |
| `plugins/oss/settings.py` | test_oss.py | test_oss_api.py | 28 | ✅ |

### search ❌

源文件 2 个，测试文件 0 个，测试用例 0 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/search/routes.py` | - | - | 0 | ❌ |
| `plugins/search/services.py` | - | - | 0 | ❌ |

### system_monitor ✅

源文件 4 个，测试文件 2 个，测试用例 6 个

| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |
|--------|---------|---------|-------|------|
| `plugins/system_monitor/routes.py` | test_system_monitor_service.py | test_system_monitor_api.py | 6 | ✅ |
| `plugins/system_monitor/services.py` | test_system_monitor_service.py | test_system_monitor_api.py | 6 | ✅ |
| `plugins/system_monitor/settings.py` | test_system_monitor_service.py | test_system_monitor_api.py | 6 | ✅ |
| `plugins/system_monitor/stats.py` | test_system_monitor_service.py | test_system_monitor_api.py | 6 | ✅ |
