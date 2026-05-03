# CloudIntegration 测试地图（组件级）

## 覆盖范围

- 组件代码：
  - `backend/plugins/cloud_integration/services.py`
  - `backend/plugins/cloud_integration/orchestrator.py`
  - `backend/plugins/cloud_integration/routes.py`
  - `backend/plugins/cloud_integration/tools.py`
  - `backend/plugins/cloud_integration/steps.py`
  - `backend/plugins/cloud_integration/log_parser.py`
  - `backend/plugins/cloud_integration/cost/calculator.py`
  - `backend/plugins/cloud_integration/providers/registry.py`
  - `backend/plugins/cloud_integration/providers/mock.py`
  - `backend/plugins/cloud_integration/providers/aliyun.py`
  - `backend/plugins/cloud_integration/providers/zhixingyun.py`
- 测试代码：
  - 单元（7 文件）
    - `backend/tests/unit/test_cloud_orchestrator.py`
    - `backend/tests/unit/test_cloud_services_workflow.py`
    - `backend/tests/unit/test_cloud_services_resources.py`
    - `backend/tests/unit/test_cloud_providers_mock_registry.py`
    - `backend/tests/unit/test_cloud_providers_aliyun.py`
    - `backend/tests/unit/test_cloud_providers_zhixingyun.py`
    - `backend/tests/unit/test_cloud_tools.py`
  - 集成（最小烟囱，1 文件）
    - `backend/tests/integration/test_cloud_routes_api.py`

## 风险点与测试归属

### 1) 任务/实例状态机（单元）
- `services.py::_transition`：合法/非法状态转换
- `start_job`、`stop_job`、`complete_job`、`fail_job`：状态推进与终止条件
- `create_job`、`launch_job`、`delete_job`：任务全生命周期
- `create_instance`、`start_instance`、`stop_instance`：实例生命周期、cost 计算入口

### 2) 资源管理（单元）
- `dataset/repo/artifact` 的 `create/list/get/delete`
- 创建重复 path/url 时抛 `AppError`
- `delete_dataset`/`delete_artifact` 调用 unified storage 的 `delete`
  - 通过 `storage_mock` fixture 注入，避免重复样板

### 3) Orchestrator 步骤推进（单元）
- `orchestrator.py::_process_job` 关键步骤：`_step_create_instance`、`_step_connect_ssh`、`_step_start_training`
- 失败收敛 `_fail_job`、重试 `_retry_step`
- SSH 信息未就绪 → 重试，超过上限 → 失败态
- 缺少仓库 URL → `missing_repo`

### 4) Provider 注册与具体实现（单元）
- `registry.py`：注册、未知 provider 抛错；测试用 `restore_provider_registry` fixture 防全局污染
- `mock.py`：实例生命周期、指标与费用
- `aliyun.py`：配置校验、状态映射、费用 fallback
- `zhixingyun.py`：签名计算、状态映射、费用 fallback

### 5) 纯函数（单元）
- `steps.py`：命令构造
- `log_parser.py`：日志解析
- `cost/calculator.py`：费用计算

### 6) API 链路（集成 - 烟囱）
- `/api/cloud/jobs`（GET 列表 / POST 创建）
- `/api/cloud/jobs/{id}/launch`
- `/api/cloud/costs`
- 鉴权失败（401）路径

## 关键失败路径清单（已覆盖）

- 状态非法转换（任务/实例）
- Provider 抛错被包装为 `AppError(provider_error)`
- 缺少仓库 URL 启动编排 → `missing_repo`
- SSH 信息未就绪触发重试
- 重试超过上限进入失败态
- 创建数据集/仓库时 path/url 重复 → 抛错
- 删除资源时调用 unified storage 的 `delete`

## 已知缺口

- 集成测试目前仅覆盖 `jobs` 与 `costs` 入口，`datasets/repos/artifacts` 的 HTTP 路径暂未覆盖。
- `tools.py` 的端到端编排尚未补完整 happy path 集成测试。

## 覆盖率验收命令

```bash
# 所有 cloud 单元测试（按需查覆盖）
uv run pytest backend/tests/unit -k cloud --override-ini addopts='' --cov=backend/plugins/cloud_integration --cov-branch --cov-report=term-missing

# cloud 最小 routes 烟囱
uv run pytest backend/tests/integration/test_cloud_routes_api.py --no-cov -v
```
