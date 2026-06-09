# Arche

> **核心万年不动，功能全部插件化。**

Arche 是一个个人模块化平台，采用微内核架构。所有功能以可插拔插件形式扩展，前端按角色按需下发代码 chunk。

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)

🌐 **线上地址**：[www.jamsyan.top](https://arche.lumoa.cn)

---

## 目录

- [特性](#特性)
- [内置插件](#内置插件)
- [快速开始](#快速开始)
- [部署](#部署)
- [相关文档](#相关文档)
- [关于](#关于)

## 特性

- **核心万年不动** — 基础层只负责装配和调度，不做具体业务
- **功能全部插件化** — 每个插件自包含、自注册，想加什么加什么
- **前端按需下发** — 不同角色拿到不同的 JS chunk，未登录用户看不到管理端代码
- **开发零摩擦** — 新增插件不改核心代码，重启即生效

## 内置插件

| 插件 | 描述 | 状态 |
|------|------|------|
| **blog** | 博客系统，支持敏感词过滤、富文本编辑、段落评论、点赞收藏 | 可用 |
| **auth** | 用户认证（JWT）+ 在线会话追踪 | 可用 |
| **oss** | 对象存储（MinIO + 阿里云 OSS 冷热迁移） | 可用 |
| **crawler** | 网页爬虫，种子管理 + 智能调度 + 流水线处理 | 可用 |
| **cloud_integration** | 云训练管理（智星云 / 阿里云 ECS / Mock） | 可用 |
| **github_proxy** | GitHub API 代理，带缓存和限流 | 可用 |
| **system_monitor** | 系统资源监控（CPU / 内存 / 磁盘 / 网络 / 进程） | 可用 |
| **asset_mgmt** | 资产管理 | 开发中 |
| **config_mgmt** | 运行时动态配置管理 | 可用 |
| **monitor** | 监控告警与通知模板 | 可用 |
| **deploy_webhook** | 部署 Webhook 回调 | 可用 |

## 快速开始

```bash
# 克隆
git clone https://github.com/Jamsyan/Arche.git
cd Arche

# 后端
uv sync
cp .env.example .env   # 编辑 .env，至少设置 SECRET_KEY
uv run uvicorn backend.main:app --reload

# 前端（新终端）
cd frontend && npm install && npm run dev
```

前端访问 `http://localhost:5173`，后端 API 在 `http://localhost:8000`。

完整的开发环境搭建与贡献指南见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 部署

### Docker Compose

```bash
docker compose up -d
```

包含 Nginx（反向代理 + SSL）、后端、PostgreSQL、MinIO 四个服务。

### 生产环境注意事项

1. 更换 `SECRET_KEY` 为随机字符串
2. 使用 PostgreSQL 替代 SQLite（修改 `DATABASE_URL`）
3. 配置 SSL 证书（挂载到 `/ssl` 目录）
4. 所有环境变量详见 `.env.example`

## 相关文档

- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南、开发环境搭建、Commit 规范
- [docs/](docs/) — 各模块架构与设计文档

## 关于

- **作者**: [jamsyan](https://github.com/Jamsyan)
- **联系**: jihanyang123@163.com
- **许可证**: [Apache License 2.0](LICENSE)
