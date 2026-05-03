# Monitor 测试地图（组件级）

## 覆盖范围

- 组件代码：
  - `backend/plugins/monitor/__init__.py`
  - `backend/plugins/monitor/routes.py`
  - `backend/plugins/monitor/models.py`
- 测试代码：
  - 单元（3 文件）
    - `backend/tests/unit/test_monitor_routes.py`
    - `backend/tests/unit/test_monitor_models.py`
    - `backend/tests/unit/test_monitor_plugin_init.py`
  - 集成（最小烟囱，1 文件）
    - `backend/tests/integration/test_monitor_api.py`

## 风险点与测试归属

### 1) 路由层（单元）
- `routes.py::get_session_factory`：数据库未初始化时返回 500
- `list/create/get/update/delete template`：正常路径与 404 路径
- `get_component_data`：返回结构稳定（当前为 mock 数据，接入真实指标后需要补回归）

### 2) 模型层（单元）
- `MonitorTemplate.to_dict()`：默认值与时间字段序列化

### 3) 插件初始化（单元）
- `__init__.py` 的 `setup()`：路由挂载
- `register_services()`：无副作用（不应触发 DB 调用或外部连接）

### 4) API 链路（集成 - 烟囱）
- 模板 CRUD 最短链路
- 模板 not found 场景
- 通过 `monitor_global_db` fixture snapshot/restore `global_container`，避免污染其它测试

## 关键失败路径清单（已覆盖）

- DB 未初始化 → 路由返回 500
- 不存在的 template id → 404
- 集成层 `global_container` 注入的 `db` 在测试结束后被还原

## 已知缺口

- `get_component_data` 仅返回 mock，未来接真实数据源后需要补：
  - 鉴权与权限
  - 数据源不可用时的降级路径
- 暂无并发/竞态测试。

## 覆盖率验收命令

```bash
# 所有 monitor 单元测试
uv run pytest backend/tests/unit -k monitor --override-ini addopts='' --cov=backend/plugins/monitor --cov-branch --cov-report=term-missing

# monitor 最小 API 烟囱
uv run pytest backend/tests/integration/test_monitor_api.py --no-cov -v
```
