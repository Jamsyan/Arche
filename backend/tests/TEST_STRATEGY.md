# Arche 测试策略

## 测试分层

### 1. 单元测试（Unit Tests）
- **目标**：测试单个函数/方法的业务逻辑
- **范围**：Service 层、工具函数
- **方式**：直接 new 对象，Mock 外部依赖
- **文件**：`test_*.py`（如 `test_github_proxy.py`）

### 2. 集成测试（Integration Tests）
- **目标**：测试 HTTP API 完整请求链路
- **范围**：FastAPI 路由 → 中间件 → Service → 数据库
- **方式**：`TestClient` + 内存 SQLite
- **文件**：`test_*_api.py`（如 `test_github_proxy_api.py`）

### 3. 端到端测试（E2E Tests）- TODO
- **目标**：测试真实生产环境部署
- **范围**：前端 + 后端 + 真实数据库
- **方式**：Playwright + 测试环境

---

## 当前状态

> 数据由 `uv run python backend/scripts/coverage_inventory.py` 维护，
> 修改测试文件后请重新运行该脚本确认与本表一致。

### 已覆盖模块

| 模块 | 单元测试用例 | 集成测试用例 | 备注 |
|------|---------|---------|--------|
| core | 100 | — | 9 个 unit 文件，覆盖容器、配置、中间件、插件注册等基础设施 |
| auth | 32 | 12 | unit + 集成 API 全量覆盖 |
| blog | 42 | — | 服务层全 mock，无集成 |
| github_proxy | 40 | 9 | 集成 API 走 mock，预期失败已收敛到 strict xfail |
| oss | 22 | 4 | 集成层有 RecursionError 已知问题，记录在 strict xfail |
| crawler | 41 | 5 | 组件定向覆盖率 ≥ 80% |
| cloud_integration | 35 | 3 | unit 7 文件 + 1 集成烟囱 |
| monitor | 6 | 2 | unit + 1 集成烟囱 |

### 待补齐模块

`asset_mgmt`、`config_mgmt`、`deploy_webhook`、`system_monitor` 当前无测试文件，
需要按下文 P0/P1 思路逐步补齐。

### 目标覆盖率
- **核心模块**（auth, github_proxy, oss）: ≥ 80%
- **其他模块**: ≥ 60%
- **整体**: ≥ 70%

---

## 编写规范

### 单元测试
```python
@pytest.mark.asyncio
class TestSomeService:
    async def test_method_behavior(self, db_container):
        service = SomeService(db_container)
        result = await service.some_method()
        assert result == expected
```

### 集成测试
```python
@pytest.mark.asyncio
class TestSomeAPI:
    async def test_endpoint_behavior(self, client, auth_headers):
        response = await client.get(
            "/api/path/to/endpoint",
            headers=auth_headers,
            params={"key": "value"}
        )
        assert response.status_code == 200
        assert response.json()["field"] == expected
```

---

## Fixture 说明

| Fixture | 用途 |
|---------|------|
| `client` | HTTP 测试客户端（AsyncClient） |
| `auth_headers` | 普通用户认证头（已登录） |
| `admin_headers` | 管理员（P0）认证头 |
| `db_container` | 内存数据库 + 测试容器 |
| `in_memory_db` | 纯数据库 fixture（不含 app） |
| `fake_container` | Mock 容器（无真实数据库） |

### 内存 SQLite 共享连接

`in_memory_db` 使用 `sqlalchemy.pool.StaticPool` 让所有 session 共用同一连接，
避免 `sqlite+aiosqlite:///:memory:` 默认每连接一份独立 DB 的坑。
新增使用 `db_container` 的测试不需要再单独建表，但所有相关插件 model 必须在
fixture 内显式 `import`，否则 `Base.metadata.create_all` 会漏建表。

### `patch_container_service` 辅助

集成与单元测试经常需要把 `db_container.get(name)` 的某项替换成 mock，
避免散乱重复以下样板：

```python
old_get = db_container.get
db_container.get = lambda n: mock if n == "x" else old_get(n)
```

请改用 `backend/tests/conftest.py` 中的 `patch_container_service(container, name, service)`，
统一行为并保持其它服务透传。

### marker 自动分层

`backend/tests/conftest.py` 的 `pytest_collection_modifyitems` 会把
`backend/tests/integration/` 下的所有测试自动加上 `integration` marker，
所以新增集成测试不需要在文件内再写 `pytestmark`，但单元目录里如果模拟集成也要手动加 marker。

---

## 运行命令

```bash
# 与 CI 一致（默认带 --cov=backend --cov-fail-under=40）
uv run pytest

# 本地快速反馈：跳过覆盖率，加摘要和短回溯
uv run pytest --no-cov -ra --tb=short

# 只跑非集成测试（speed-up 本地反馈，集成 marker 由 conftest 自动应用）
uv run pytest -m "not integration" --no-cov

# 只运行单元/集成目录
uv run pytest backend/tests/unit/ -v
uv run pytest backend/tests/integration/ -v

# 只运行特定标记的测试（如慢速测试）
uv run pytest -m "slow" -v

# 需要 HTML 报告时显式开启（输出到 .artifacts/tests/coverage/html）
uv run pytest --cov=backend --cov-report=html

# 查看组件测试覆盖盘点（源码数 / 测试文件数 / 用例数）
uv run python backend/scripts/coverage_inventory.py

# 运行 crawler 组件完整覆盖回归（含分支覆盖）
uv run pytest backend/tests/unit/test_crawler_pipeline.py backend/tests/unit/test_crawler_seed_manager.py backend/tests/unit/test_crawler_scheduler_probe.py backend/tests/unit/test_crawler_orchestrator.py backend/tests/integration/test_crawler_api.py --override-ini addopts='' --cov=backend/plugins/crawler --cov-branch --cov-report=term-missing --cov-fail-under=80

# 运行 cloud_integration 单元优先回归
uv run pytest backend/tests/unit -k cloud -v --no-cov

# 运行 cloud 最小 routes 烟囱
uv run pytest backend/tests/integration/test_cloud_routes_api.py -v --no-cov

# 运行 monitor 单元优先回归
uv run pytest backend/tests/unit -k monitor -v --no-cov

# 运行 monitor 最小 API 烟囱
uv run pytest backend/tests/integration/test_monitor_api.py -v --no-cov
```

---

## 产物管理约定

- 默认测试仅输出命令行结果，不生成 HTML 报告文件。
- 可选覆盖率产物统一放在 `.artifacts/tests/coverage/`：
  - HTML：`.artifacts/tests/coverage/html/`
  - XML：`.artifacts/tests/coverage/coverage.xml`
- `.artifacts/` 不入库，避免测试产物在仓库内散落。

---

## Crawler 测试索引

- 测试地图：`backend/tests/CRAWLER_TEST_MAP.md`
- 单元测试：
  - `backend/tests/unit/test_crawler_pipeline.py`
  - `backend/tests/unit/test_crawler_seed_manager.py`
  - `backend/tests/unit/test_crawler_scheduler_probe.py`
  - `backend/tests/unit/test_crawler_orchestrator.py`
- 集成测试：
  - `backend/tests/integration/test_crawler_api.py`

## CloudIntegration 测试索引

- 测试地图：`backend/tests/CLOUD_TEST_MAP.md`
- 单元测试：
  - `backend/tests/unit/test_cloud_orchestrator.py`
  - `backend/tests/unit/test_cloud_services_workflow.py`
  - `backend/tests/unit/test_cloud_services_resources.py`
  - `backend/tests/unit/test_cloud_providers_mock_registry.py`
  - `backend/tests/unit/test_cloud_providers_aliyun.py`
  - `backend/tests/unit/test_cloud_providers_zhixingyun.py`
  - `backend/tests/unit/test_cloud_tools.py`
- 集成测试（可选烟囱）：
  - `backend/tests/integration/test_cloud_routes_api.py`

## Monitor 测试索引

- 测试地图：`backend/tests/MONITOR_TEST_MAP.md`
- 单元测试：
  - `backend/tests/unit/test_monitor_routes.py`
  - `backend/tests/unit/test_monitor_models.py`
  - `backend/tests/unit/test_monitor_plugin_init.py`
- 集成测试（可选烟囱）：
  - `backend/tests/integration/test_monitor_api.py`

## 常见失败排障

- `no such table: users` / `no such table: monitor_templates`
  - 原因：`create_all` 前模型未导入，metadata 不完整；或别处误调用了 `Base.metadata.clear()` 把全局 metadata 清空。
  - 处理：`in_memory_db` 已在 fixture 顶部显式 import 各插件 models；任何 teardown 都不要 clear `Base.metadata`。
- 覆盖率看起来"过低但测试都过了"
  - 原因：默认 `addopts` 会启用全仓 `--cov=backend`，并非只统计单个插件。
  - 处理：组件覆盖请使用 `--override-ini addopts=''` + `--cov=backend/plugins/<name>`。
- 集成测试 401
  - 原因：`/api/crawler/*`、`/api/cloud/*` 等受 `require_level(0)` 保护，缺少管理员 token。
  - 处理：使用 `admin_headers` fixture 调用接口。
- 集成测试出现意外 500 而不是 4xx
  - 原因：自定义 FastAPI 应用没有挂载 `register_error_handlers`，`AppError` 没有映射成业务错误码。
  - 处理：`test_app` fixture 已统一调用 `register_error_handlers`，新建测试 app 时也要照做。
- 集成测试间歇性互相影响
  - 原因：直接修改了 `global_container`、`registry._providers` 等模块级单例。
  - 处理：参考 `backend/tests/integration/test_monitor_api.py::monitor_global_db` 与
    `backend/tests/unit/test_cloud_providers_mock_registry.py::restore_provider_registry`，
    在 fixture 里 snapshot/restore 这些状态。
