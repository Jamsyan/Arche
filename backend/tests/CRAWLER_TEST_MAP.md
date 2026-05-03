# Crawler 测试地图（组件级）

## 覆盖范围

- 组件代码：
  - `backend/plugins/crawler/services.py`
  - `backend/plugins/crawler/routes.py`
  - `backend/plugins/crawler/probe.py`
  - `backend/plugins/crawler/seed_manager.py`
  - `backend/plugins/crawler/url_scheduler.py`
  - `backend/plugins/crawler/link_extractor.py`
  - `backend/plugins/crawler/pipeline/*`
- 测试代码：
  - `backend/tests/unit/test_crawler_pipeline.py`
  - `backend/tests/unit/test_crawler_seed_manager.py`
  - `backend/tests/unit/test_crawler_scheduler_probe.py`
  - `backend/tests/unit/test_crawler_orchestrator.py`
  - `backend/tests/integration/test_crawler_api.py`

## 风险点与测试归属

### 1) 抓取与解析链路（单元）
- `FetchStage`：HTTP 成功/异常、title 提取、链接抽取与去重。
- `ParseStage`：空 HTML、已有错误短路、正文和链接提取。
- `ClassifyStage`：title 模式优先、路径模式命中、默认 other。
- `QualityStage`：HTTP 错误、功能页路径/标题、内容过短拒绝。
- `StorageStage`：本地回退写入、超大内容 gzip、OSS 写入路径。

### 2) 种子与调度（单元）
- `SeedManager`：URL 规范化、去重、黑白名单、探嗅处理、链接发现。
- `UrlScheduler`：入队/出队、域名并发上限、active 计数与释放。

### 3) 探嗅与总调度（单元）
- `ProbeService`：功能页判定（path/title）、异常回退、资源关闭。
- `CrawlerOrchestrator`：探嗅拒绝、流水线成功、存储失败、统计查询。

### 4) API 链路（集成）
- `/api/crawler/status|start|stop`
- `/api/crawler/seeds|blacklist`
- `/api/crawler/records|records/{id}|records/{id}/file`
- `/api/crawler/stats`
- 鉴权失败（401）路径

## 关键失败路径清单（已覆盖）

- 探嗅异常 -> 任务拒绝
- 功能页/无内容页 -> 黑名单或拒绝
- 抓取异常 -> `item.error`
- 质检失败（HTTP>=400/功能页/过短）-> 丢弃
- 存储失败分支（返回 `None`）-> rejected 计数增加
- 文件下载接口：记录不存在、文件不存在

## 已知缺口

- `pipeline/storage_stage.py` 的 OSS 写入路径目前依赖 mock，缺真实 OSS 集成回归。
- `link_extractor.py` 对超大 HTML 的退化策略尚未单独覆盖。
- 集成层只覆盖 happy path 与 401，没有覆盖外部 HTTP 抖动场景。

## 覆盖率验收命令

```bash
uv run pytest backend/tests/unit/test_crawler_pipeline.py backend/tests/unit/test_crawler_seed_manager.py backend/tests/unit/test_crawler_scheduler_probe.py backend/tests/unit/test_crawler_orchestrator.py backend/tests/integration/test_crawler_api.py --override-ini addopts='' --cov=backend/plugins/crawler --cov-branch --cov-report=term-missing --cov-fail-under=80
```
