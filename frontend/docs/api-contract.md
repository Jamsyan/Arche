# API Contract Sheet

本文档以后端源码为准，供前端 API 接入与联调使用。

## 约定

- Base URL: `/api`
- 认证: `Authorization: Bearer <token>`
- 通用响应: `{ code, message, data, success }`
- 稳定性标记:
  - `stable`: 可直接对接
  - `experimental`: 仍在演进，先灰度接入

## Auth (`/api/auth`) - stable

- `POST /register`
- `POST /login`
- `POST /logout` (auth)
- `GET /me` (auth)
- `POST /refresh`
- `GET /users` (admin)
- `GET /users/{user_id}` (admin)
- `PUT /users/{user_id}` (admin)
- `DELETE /users/{user_id}` (admin)
- `POST /users/{user_id}/disable` (admin)
- `POST /users/{user_id}/enable` (admin)
- `POST /admin/users` (admin)

## Blog (`/api/blog`) - stable

- `GET /posts`
- `GET /posts/by-id/{post_id}`
- `GET /posts/{slug}`
- `GET /posts/{post_id}/comments`
- `GET /tags`
- `GET /posts/by-tag/{tag_name}`
- `GET /posts/{post_id}/tags`
- `GET /posts/{post_id}/favorite-status`
- `POST /posts` (auth)
- `GET /my-posts` (auth)
- `PUT /posts/{post_id}` (auth)
- `DELETE /posts/{post_id}` (auth)
- `POST /posts/{post_id}/comments` (auth)
- `POST /posts/{post_id}/like` (auth)
- `POST /favorites/{post_id}` (auth)
- `DELETE /favorites/{post_id}` (auth)
- `GET /favorites` (auth)
- `POST /reports` (auth)
- `POST /import` (auth, multipart)
- `POST /tags` (auth)
- `POST /posts/{post_id}/tags` (auth)
- `DELETE /posts/{post_id}/tags/{tag_name}` (auth)
- `GET /moderation/pending` (admin)
- `POST /moderation/{post_id}/approve` (admin)
- `POST /moderation/{post_id}/reject` (admin)
- `POST /moderation/batch-approve` (admin)
- `POST /moderation/batch-reject` (admin)

## OSS (`/api/oss`) - stable

- `POST /upload` (auth)
- `GET /files/{file_id}` (auth)
- `DELETE /files/{file_id}` (auth)
- `GET /my` (auth)
- `POST /external/{tenant_id}/upload` (auth)
- `GET /external/{tenant_id}/files` (auth)
- `GET /storage/stats` (auth)
- `GET /quota` (auth)
- `POST /admin/evict` (admin)
- `GET /admin/quotas` (admin)
- `PUT /admin/quotas/{user_id}` (admin)
- `GET /admin/rate-limit` (admin)
- `PUT /admin/rate-limit` (admin)
- `PUT /admin/rate-limit/users/{user_id}` (admin)
- `GET /admin/files` (admin)
- `DELETE /admin/files/{file_id}` (admin)
- `GET /admin/stats` (admin)
- `GET /admin/stats/top-users` (admin)

## Cloud (`/api/cloud`) - mixed

- stable:
  - `GET /stats` (admin)
  - `GET /jobs` (admin)
  - `GET /jobs/{job_id}` (admin)
  - `POST /jobs` (admin)
  - `DELETE /jobs/{job_id}` (admin)
  - `POST /jobs/{job_id}/start|stop|complete|fail` (admin)
  - `GET /jobs/{job_id}/logs` (admin)
  - `GET /jobs/{job_id}/instances` (admin)
  - `POST /jobs/{job_id}/instances` (admin)
  - `POST /instances/{instance_id}/start|stop` (admin)
  - `GET /instances/{instance_id}/gpu-metrics` (admin)
  - `GET /costs` (admin)
  - `GET/POST /datasets` (admin)
  - `GET/DELETE /datasets/{dataset_id}` (admin)
  - `POST /datasets/{dataset_id}/sync` (admin)
  - `GET/POST /repos` (admin)
  - `DELETE /repos/{repo_id}` (admin)
  - `POST /repos/{repo_id}/sync` (admin)
  - `GET /artifacts` (admin)
  - `GET /artifacts/{artifact_id}` (admin)
  - `GET /artifacts/{artifact_id}/download` (admin)
  - `DELETE /artifacts/{artifact_id}` (admin)
- experimental:
  - `POST /jobs/{job_id}/launch`
  - `GET /jobs/{job_id}/progress`
  - `GET /jobs/{job_id}/steps`

## Crawler (`/api/crawler`) - stable(admin)

- `GET /status`
- `POST /start`
- `POST /stop`
- `GET /records`
- `GET /records/{record_id}`
- `GET /records/{record_id}/file`
- `POST /seeds`
- `GET /seeds`
- `POST /blacklist`
- `GET /blacklist`
- `GET /stats`

## Github Proxy (`/api/github`) - experimental

- `GET /health/status`
- `GET /raw/{path:path}`
- `POST /cache/clear`
- `ANY /{path:path}`

## System (`/api/system`) - stable(admin)

- `GET /summary`
- `GET /cpu`
- `GET /memory`
- `GET /disk`
- `GET /network`
- `GET /history`
- `GET /processes`

## Config (`/api/admin/config`) - stable(admin)

- `GET /`
- `GET /{key}`
- `PUT /{key}`
- `GET /groups`
- `POST /reload`

## Assets (`/api/assets`) - stable(admin)

- `GET /`
- `GET /search`
- `GET /stats`

## Monitor (`/api/monitor`) - experimental

- `GET /templates`
- `POST /templates`
- `GET /templates/{template_id}`
- `PUT /templates/{template_id}`
- `DELETE /templates/{template_id}`
- `GET /components/{component_id}/data` (mock)
