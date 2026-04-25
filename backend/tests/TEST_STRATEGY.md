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

### 已覆盖模块

| 模块 | 单元测试 | 集成测试 | 覆盖率 |
|------|---------|---------|--------|
| github_proxy | ✅ 12 个 | ✅ 2 个 | ~60% |
| oss | ✅ 23 个 | 🚧 待添加 | ~40% |
| auth | ✅ 29 个 | ✅ 12 个 | ~40% |
| blog | ❌ 0 个 | ❌ 0 个 | 0% |
| cloud_integration | ❌ 0 个 | ❌ 0 个 | 0% |
| crawler | ❌ 0 个 | ❌ 0 个 | 0% |
| monitor | ❌ 0 个 | ❌ 0 个 | 0% |
| system_monitor | ❌ 0 个 | ❌ 0 个 | 0% |

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

---

## 运行命令

```bash
# 运行所有测试
uv run pytest

# 只运行单元测试
uv run pytest backend/tests/unit/ -v

# 只运行集成测试
uv run pytest backend/tests/integration/ -v

# 只运行特定标记的测试（如慢速测试）
uv run pytest -m "slow" -v

# 查看终端覆盖率（默认，不落地文件）
uv run pytest --cov=backend --cov-report=term-missing

# 需要 HTML 报告时显式开启（输出到 .artifacts/tests/coverage/html）
uv run pytest --cov=backend --cov-report=html

# 查看组件测试覆盖盘点（源码数 / 测试文件数 / 用例数）
uv run python backend/scripts/coverage_inventory.py
```

---

## 产物管理约定

- 默认测试仅输出命令行结果，不生成 HTML 报告文件。
- 可选覆盖率产物统一放在 `.artifacts/tests/coverage/`：
  - HTML：`.artifacts/tests/coverage/html/`
  - XML：`.artifacts/tests/coverage/coverage.xml`
- `.artifacts/` 不入库，避免测试产物在仓库内散落。
