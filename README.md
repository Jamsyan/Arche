# Arche

> **核心万年不动，功能全部插件化。**

Arche 是一个个人模块化平台，采用微内核架构。所有功能以可插拔插件形式扩展，前端按角色按需下发代码 chunk。

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)

## 目录

- [特性](#特性)
- [架构](#架构)
- [内置插件](#内置插件)
- [快速开始](#快速开始)
- [部署](#部署)
- [开发新插件](#开发新插件)
- [代码按需下发原理](#代码按需下发原理)
- [文档](#文档)
- [贡献](#贡献)
- [许可证](#许可证)

## 特性

- **核心万年不动**：基础层只负责装配和调度，不做具体业务
- **功能全部插件化**：每个插件自包含、自注册，想加什么加什么
- **前端按需下发**：不同角色拿到不同的 JS chunk，未登录用户根本看不到管理端代码
- **开发零摩擦**：新增插件不改核心代码，重启即生效

## 架构

```
backend/
├── core/                    # 微内核（稳定，尽量不改）
│   ├── plugin_registry.py   # 插件注册中心
│   ├── base_plugin.py       # 插件抽象基类
│   ├── config.py            # 分层配置（.env < 系统环境变量）
│   └── container.py         # 服务容器
├── plugins/                 # 插件层（随便加）
│   ├── blog/                # 博客
│   ├── auth/                # 认证
│   ├── oss/                 # 对象存储
│   ├── crawler/             # 爬虫
│   ├── cloud_integration/   # 云训练
│   ├── github_proxy/        # GitHub 代理
│   ├── system_monitor/      # 系统监控
│   └── asset_mgmt/          # 资产管理
└── main.py                  # 入口：先发现插件，再创建 App

frontend/
├── src/
│   ├── components/          # 按角色分组的组件
│   │   ├── blog/            # 公开可见
│   │   ├── platform/        # 登录后可见
│   │   ├── admin/           # 管理员可见
│   │   ├── dashboard/       # 仪表盘
│   │   ├── oss/             # OSS 管理
│   │   └── github/          # GitHub 代理
│   └── router/
│       └── component-registry.js  # 角色→组件映射，dynamic import
```

## 内置插件

| 插件 | 描述 | 状态 |
|------|------|------|
| **blog** | 博客系统，支持敏感词过滤 | 可用 |
| **auth** | 用户认证（JWT） | 可用 |
| **oss** | 对象存储（MinIO + 阿里云 OSS 冷热迁移） | 可用 |
| **crawler** | 网页爬虫，种子管理 + 存储 | 可用 |
| **cloud_integration** | 云训练（智星云 / 阿里云 ECS / Mock） | 可用 |
| **github_proxy** | GitHub API 代理，带缓存和限流 | 可用 |
| **system_monitor** | 系统资源监控（CPU / 内存 / 磁盘 / 网络） | 可用 |
| **asset_mgmt** | 资产管理 | 开发中 |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Jamsyan/Arche.git
cd Arche

# 安装后端依赖
uv sync

# 安装前端依赖
cd frontend && npm install && cd ..

# 配置环境变量
cp .env.example .env
# 编辑 .env，至少设置 SECRET_KEY
```

### 开发模式

打开两个终端：

```bash
# 终端 1：后端
uv run uvicorn backend.main:app --reload

# 终端 2：前端
cd frontend && npm run dev
```

前端访问 `http://localhost:5173`，后端 API 在 `http://localhost:8000`。

### 构建

```bash
cd frontend && npm run build
```

产物输出到 `frontend/dist/`，后端自动 serve。

## 部署

### Docker Compose

```bash
# 编辑 .env，填写所有必要的环境变量
docker compose up -d
```

包含 Nginx（反向代理 + SSL）、后端、PostgreSQL、MinIO 四个服务。

### 生产环境注意事项

1. 更换 `SECRET_KEY` 为随机字符串
2. 使用 PostgreSQL 替代 SQLite（修改 `DATABASE_URL`）
3. 配置 SSL 证书（挂载到 `/ssl` 目录）
4. 所有环境变量详见 `.env.example`

## 开发新插件

### 后端

在 `backend/plugins/` 下新建目录，例如 `my_plugin/`：

```
backend/plugins/my_plugin/
├── __init__.py      # 入口：插件类 + 自注册
├── routes.py        # 路由（可选）
└── services.py      # 业务逻辑（可选）
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

简单插件可以不拆 `routes.py`，直接放 `__init__.py`。复杂插件按 `models.py` / `routes.py` / `services.py` 分层。

### 前端

1. 在 `frontend/src/components/` 下新建组件
2. 在 `frontend/src/router/component-registry.js` 中注册到对应角色
3. Vite 自动分割 chunk，无需额外配置

## 代码按需下发原理

前端通过 `dynamic import()` 加载组件，Vite 会将不同组件打包为独立的 JS chunk。

未登录用户只会加载 `blog` chunk，即使查看源码，也找不到 `admin` 相关代码——它们根本不存在于返回的 HTML 中。登录后根据角色动态注册路由，触发 `import()` 加载对应 chunk。

## 文档

- [CLAUDE.md](CLAUDE.md) — 项目架构与开发指南
- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南
- [SECURITY.md](SECURITY.md) — 安全政策
- [docs/](docs/) — 各模块详细文档

## 贡献

欢迎提交 Issue 和 Pull Request！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[Apache License 2.0](LICENSE)
