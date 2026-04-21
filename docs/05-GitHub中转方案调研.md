# GitHub 中转方案调研

> 日期：2026-04-21
> 状态：调研阶段
> 目标：找到一种国内可用的 GitHub 访问中转方案，不需要额外部署代理服务器

---

## 1. 背景

国内直接访问 GitHub API 速度慢、不稳定。需要一个中转方案，让前端体验接近原生 GitHub。

**约束**：
- 仅个人使用（P1 及以上开放），不做公共服务
- 不需要做额外代理服务器，方案要简单
- 中转后的前端只保留 GitHub 核心功能，去掉 marketplace 等不必要部分

---

## 2. 方案调研

### 2.1 方案 A：GitHub REST API 后端代理

**原理**：后端 FastAPI 接收前端请求 → 转发到 GitHub REST API → 缓存响应 → 返回前端。

**优点**：
- 实现简单，FastAPI 一个 proxy 路由即可
- 可以在后端做缓存（Redis / 本地磁盘）
- 天然支持认证（后端持有 GitHub PAT）
- 前端不需要处理 GitHub API 细节

**缺点**：
- 服务器到 GitHub API 的速度取决于网络环境
- 国内服务器请求 GitHub API 本身就慢
- 需要处理 GitHub API 的 rate limit（未认证 60 次/小时，有 token 5000 次/小时）

**实现**：
```python
@app.api_route("/api/gh/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def github_proxy(path: str, request: Request):
    url = f"https://api.github.com/{path}"
    headers = {"Authorization": f"Bearer {GITHUB_PAT}"}
    resp = await httpx.request(request.method, url, headers=headers, ...)
    return resp
```

**可行性**：★★★★☆ — 最简单直接的方案，但速度取决于服务器网络

---

### 2.2 方案 B：SSH 隧道转发

**原理**：通过 SSH 连接到一台海外服务器（有良好 GitHub 访问的），建立隧道，流量走 SSH 隧道。

**实现方式**：
```bash
# 本地建立 SSH 动态转发（SOCKS5 代理）
ssh -D 1080 user@overseas-server

# 或者反向隧道
ssh -R 8080:api.github.com:443 user@overseas-server
```

**优点**：
- 隧道建立后，所有 GitHub 请求走隧道，速度快
- SSH 连接复用，不需要反复建立
- 加密传输，安全

**缺点**：
- **需要一台海外服务器**作为跳板
- SSH 连接断了需要重连
- 需要维护 SSH 密钥和服务器
- 隧道不稳定时会影响 GitHub 体验
- SOCKS5 代理需要 httpx/requests 配置 proxy，FastAPI 侧需要处理

**可行性**：★★★☆☆ — 需要海外服务器，多一层运维

---

### 2.3 方案 C：GitHub CLI (gh) 中转

**原理**：后端通过 `gh` CLI 命令操作 GitHub，而不是直接调 HTTP API。

**实现**：
```python
async def run_gh(args: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "gh", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode()

# 示例
repos = json.loads(await run_gh(["repo", "list", "--json", "name,description"]))
```

**优点**：
- `gh` 内置认证管理（`gh auth login`）
- 命令式 API，简单直观
- 自动处理 rate limit 提示
- 输出 JSON，易于解析

**缺点**：
- **`gh` 本身也调 GitHub API**，网络问题不解决
- CLI 调用有进程启动开销，不适合高频请求
- 不支持所有 GitHub API 端点
- 错误处理不如 HTTP API 精细
- 需要服务器上安装 `gh` 并配置认证

**可行性**：★★☆☆☆ — 本质和方案 A 一样调 API，只是封装成 CLI，没有解决网络问题

---

### 2.4 方案 D：GitHub Actions 中转

**原理**：利用 GitHub Actions 运行在 GitHub 基础设施上，天然高速。通过 Actions 触发器拉取数据，回传到我们服务器。

**实现**：
- 创建一个私有仓库
- 在仓库中部署 Action，定期或按需触发
- Action 调 GitHub API 拿到数据 → POST 回我们服务器
- 我们服务器缓存结果，前端读缓存

**优点**：
- 运行在 GitHub 内网，速度极快
- 免费（Actions 有 2000 分钟/月免费额度）
- 不需要额外服务器

**缺点**：
- 不是实时的，有延迟（Action 触发到完成需要时间）
- 只适合读操作（浏览仓库、看代码），写操作（PR、Issue）不好处理
- 调试困难
- 依赖 GitHub Actions 的可用性
- 数据回传需要额外的 webhook/回调机制

**可行性**：★★☆☆☆ — 延迟高，不适合交互式使用

---

### 2.5 方案 E：海外 VPS + Nginx 反向代理

**原理**：在一台海外 VPS 上部署 Nginx 反向代理到 `api.github.com`，我们服务器请求 VPS，VPS 转发到 GitHub。

**配置**：
```nginx
location /api/ {
    proxy_pass https://api.github.com/;
    proxy_set_header Authorization "Bearer $github_token";
    proxy_cache github_cache;
    proxy_cache_valid 200 10m;
}
```

**优点**：
- VPS 到 GitHub 速度快（同海外机房）
- Nginx 缓存减少重复请求
- 前端请求国内服务器，服务器请求海外 VPS，VPS 请求 GitHub
- 实现简单，Nginx 配置即可

**缺点**：
- **需要一台海外 VPS**（便宜的就行）
- 多一层网络跳数
- VPS 挂了 → GitHub 代理全挂

**可行性**：★★★★☆ — 最可靠的方案，但有额外成本（海外 VPS）

---

## 3. 方案对比

| 维度 | A: API 代理 | B: SSH 隧道 | C: gh CLI | D: Actions | E: Nginx 反代 |
|------|-------------|-------------|-----------|------------|---------------|
| 实现复杂度 | 低 | 中 | 低 | 高 | 低 |
| 速度 | 取决于服务器网络 | 好（隧道） | 同 A | 快（内网） | 好（VPS） |
| 实时性 | 实时 | 实时 | 实时 | 延迟 | 实时 |
| 是否需要额外服务器 | 否 | 是（海外） | 否 | 否 | 是（海外 VPS） |
| 是否解决网络问题 | 否 | 是 | 否 | 是 | 是 |
| 写操作支持 | 支持 | 支持 | 部分 | 不支持 | 支持 |
| 缓存能力 | 后端缓存 | 无 | 无 | 缓存到 Actions | Nginx 缓存 |
| 维护成本 | 低 | 中 | 低 | 高 | 低 |

---

## 4. 推荐方案

**如果你有一台海外服务器**：选 **方案 E（Nginx 反向代理）**

- VPS 到 GitHub 速度快
- Nginx 自带缓存，减少请求次数
- 实现简单，FastAPI 只需配置 `httpx` 代理指向 VPS
- 支持读写操作

**如果没有海外服务器**：选 **方案 A（API 代理）**，配合后端缓存

- 最简实现，不需要额外基础设施
- 如果服务器本身能访问 GitHub（虽然是慢一点），配合缓存能大幅减少实际 API 调用
- 后续有海外服务器了再升级到方案 E

**不推荐**：
- 方案 B（SSH 隧道）：维护成本高，连接不稳定
- 方案 C（gh CLI）：没有解决网络问题
- 方案 D（Actions）：延迟高，不适合交互式使用

---

## 5. 推荐实现（方案 A + 缓存）

```python
# backend/plugins/github_proxy/routes.py
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/gh", tags=["github"])

# 简单内存缓存，可换成 Redis
_cache = {}

@router.api_route("/{path:path}", methods=["GET"])
async def proxy_get(path: str, request: Request):
    url = f"https://api.github.com/{path}"
    # 检查缓存
    cache_key = url + str(request.query_params)
    if cache_key in _cache:
        return _cache[cache_key]

    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=dict(request.query_params))
        data = JSONResponse(content=resp.json(), status_code=resp.status_code)
        _cache[cache_key] = data
        return data
```

---

## 6. 待确认

- [ ] 你是否有海外服务器 / VPS？
- [ ] 如果有，域名/IP 是什么？
- [ ] 如果没有，先用方案 A + 缓存，后续再加海外反代？
