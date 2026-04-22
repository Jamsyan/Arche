# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## 项目概述

Arche 是个人模块化平台，采用微内核架构。所有功能以可插拔插件形式扩展，前端按角色按需下发代码 chunk。

## 常用命令

```bash
# 后端开发
uvicorn backend.main:app

# 前端开发
cd frontend && npm run dev

# 构建前端（产物输出到 frontend/dist/，后端自动 serve）
cd frontend && npm run build

# 同步依赖
uv sync          # 后端
cd frontend && npm install  # 前端
```

## 架构

### 后端：微内核 + 插件

```
backend/
├── core/
│   ├── __init__.py          # create_app() 工厂函数，挂载静态文件和激活插件
│   ├── base_plugin.py       # BasePlugin 抽象基类
│   └── plugin_registry.py   # PluginRegistry 单例 + discover_plugins()
├── plugins/
│   └── blog/                # 示例：博客插件（目录模式）
│       ├── __init__.py      # 入口：定义插件类 + 自注册
│       ├── models.py        # 数据模型
│       ├── routes.py        # FastAPI 路由
│       └── services.py      # 业务逻辑
└── main.py                  # 入口，先 discover_plugins() 再 create_app()
```

**启动流程**：`main.py` → `discover_plugins()` 扫描 `plugins/` 下所有子目录 → 每个目录的 `__init__.py` 在 import 时自注册到 `registry` → `create_app()` 调用 `registry.activate_all(app)` 激活所有插件。

**插件结构规范**：每个插件是一个目录，必须包含 `__init__.py`（入口+自注册）。内部文件按需拆分——简单插件可只放 `__init__.py`，复杂插件按 `models.py` / `routes.py` / `services.py` 分层。

**开发新插件**：在 `backend/plugins/` 下新建目录，`__init__.py` 中定义插件类继承 `BasePlugin`，实现 `setup(self, app)` 注册路由，调用 `registry.register(name, plugin)` 自注册。无需修改核心代码。

### 前端：Vue 3 + Vite 按角色动态加载

```
frontend/src/
├── App.vue                     # 根据 isAuthed 切换 BlogShell / PlatformShell
├── main.js                     # Vue 入口
├── router/
│   ├── index.js               # Vue Router，beforeEach 守卫校验角色
│   ├── component-registry.js   # 角色→组件映射，dynamic import 懒加载
│   └── auth.js                # useAuth() 组合函数（登录/登出/用户信息）
└── components/
    ├── blog/                   # 公开可见
    ├── platform/               # 登录后可见
    └── admin/                  # 管理员可见
```

**按需下发原理**：Vite 通过 `dynamic import()` 将不同角色的组件拆为独立 JS chunk。未登录用户只加载 blog chunk，admin 相关 JS 文件根本不会被返回。

### TODO（尚未实现）

- [ ] 数据库集成
- [ ] 用户认证（JWT / Session）
- [ ] 权限系统
- [ ] 管理后台组件

注意：`/api/auth/*` 端点目前在 auth.js 中已有前端调用代码，但后端尚未实现对应路由。

## 技术栈

- 后端：Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- 前端：Vue 3.5, Vue Router 4.5, Vite 6
- 包管理：uv（后端）, npm（前端）
- 测试：pytest（已配置，暂无测试文件）
