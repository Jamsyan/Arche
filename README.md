# Arche

个人模块化平台。微内核架构，功能全部以可插拔组件形式扩展。

## 设计理念

- **核心万年不动**：基础层只负责装配和调度，不做具体业务
- **功能全部插件化**：每个插件自包含、自注册，想加什么加什么
- **前端按需下发**：不同角色拿到不同的前端代码 chunk，不存在"藏在 JS 里被翻出来"

## 架构

```
backend/
├── core/                    # 基础层（稳定，尽量不改）
│   ├── plugin_registry.py   # 插件注册中心
│   └── base_plugin.py       # 插件抽象基类
├── plugins/                 # 插件层（随便加）
│   └── blog/                # 示例：博客插件（目录模式）
│       ├── __init__.py      # 入口：插件类 + 自注册
│       ├── models.py        # 数据模型（按需创建）
│       ├── routes.py        # 路由定义（按需创建）
│       └── services.py      # 业务逻辑（按需创建）
└── main.py                  # 入口

frontend/
├── src/
│   ├── components/
│   │   ├── blog/            # 博客组件（公开可见）
│   │   ├── platform/        # 平台组件（登录后可见）
│   │   └── admin/           # 管理组件（管理员可见）
│   └── router/
│       └── component-registry.js  # 按角色动态加载组件
```

## 快速开始

### 安装依赖

```bash
# 后端
uv sync

# 前端
cd frontend && npm install
```

### 开发模式

```bash
# 终端 1：后端
uvicorn backend.main:app

# 终端 2：前端（dev 模式自带热更新）
cd frontend && npm run dev
```

### 构建

```bash
cd frontend && npm run build
```

构建产物输出到 `frontend/dist/`，后端会自动 serve 这个目录。

## 开发新插件

### 后端

在 `backend/plugins/` 下新建一个**目录**（例如 `my_plugin`）：

```
backend/plugins/my_plugin/
├── __init__.py      # 入口：插件类 + 自注册
├── routes.py        # 路由定义
└── services.py      # 业务逻辑（按需创建）
```

`__init__.py`：

```python
from fastapi import APIRouter
from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry
from . import routes  # noqa: 导入触发内部模块加载

class MyPlugin(BasePlugin):
    name = "my_plugin"

    def setup(self, app):
        app.include_router(routes.router)

# 自注册
plugin = MyPlugin()
registry.register("my_plugin", plugin)
```

`routes.py`：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/my", tags=["my"])

@router.get("/hello")
async def hello():
    return {"message": "Hello from my plugin!"}
```

简单插件可以不拆 `routes.py`，直接放在 `__init__.py` 里即可。复杂插件按 `models.py` / `routes.py` / `services.py` 分层。

### 前端

1. 在 `frontend/src/components/` 下新建组件
2. 在 `frontend/src/router/component-registry.js` 中注册到对应角色
3. Vite 会自动分割 chunk

## 代码按需下发原理

前端通过 `dynamic import()` 加载组件，Vite 会将不同组件组打包为独立的 JS chunk。

普通用户未登录时，只会加载 `blog` chunk。即使查看源码，也找不到 `admin` 相关组件的 JS 文件——它们根本不存在于返回的 HTML 中。

登录后根据角色动态注册对应路由，触发 `import()` 加载对应 chunk。

## TODO

- [ ] 数据库集成
- [ ] 用户认证（JWT / Session）
- [ ] 权限系统
- [ ] 管理后台组件
