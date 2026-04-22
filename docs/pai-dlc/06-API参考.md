# 06 — API 参考

## API 概览

PAI-DLC 的 OpenAPI 版本为 `2020-12-03`。
API 端点（Endpoint）格式：`pai-dlc.<region>.aliyuncs.com`

常用地域端点：
- 杭州：`pai-dlc.cn-hangzhou.aliyuncs.com`
- 上海：`pai-dlc.cn-shanghai.aliyuncs.com`
- 北京：`pai-dlc.cn-beijing.aliyuncs.com`
- 乌兰察布：`pai-dlc.cn-wulanchabu.aliyuncs.com`

## 核心 API 列表

| API | 功能 | 文档 |
|-----|------|------|
| **CreateJob** | 创建训练任务 | [API调试](https://api.aliyun.com/api/pai-dlc/2020-12-03/CreateJob) |
| **GetJob** | 查询任务详情 | [GetJob](https://next.api.aliyun.com/document/pai-dlc/2020-12-03/GetJob) |
| **ListJobs** | 分页查询任务列表 | [ListJobs](https://help.aliyun.com/zh/pai/developer-reference/api-pai-dlc-2020-12-03-listjobs) |
| **StopJob** | 停止运行中的任务 | — |
| **DeleteJob** | 删除任务 | — |
| **CreateTensorboard** | 创建 TensorBoard 实例 | [CreateTensorboard](https://help.aliyun.com/zh/pai/developer-reference/api-pai-dlc-2020-12-03-createtensorboard) |
| **UpdateJob** | 更新任务配置 | [UpdateJob](https://www.alibabacloud.com/help/zh/pai/developer-reference/api-pai-dlc-2020-12-03-updatejob) |

## CreateJob — 创建训练任务

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| DisplayName | String | 是 | 任务显示名称 |
| JobType | String | 是 | 任务类型：`PyTorchJob`, `TensorFlowJob`, `RayJob`, `SlurmJob` |
| ResourceConfig | ResourceConfig | 是 | 资源配置（GPU 规格、节点数等） |
| WorkspaceId | String | 否 | 工作空间 ID |
| CodeSource | CodeSourceItem | 否 | 代码源配置 |
| DataSources | DataSourceItem[] | 否 | 数据源列表 |
| UserCommand | String | 否 | 容器内执行的命令（启动命令） |
| Image | String | 否 | 训练镜像地址 |
| Options | String | 否 | JSON 格式的高级选项 |
| MaxRunningTimeInSeconds | Integer | 否 | 最大运行时间（秒） |
| Priority | Integer | 否 | 任务优先级 |
| UseSpot | Boolean | 否 | 是否使用竞价实例 |

### ResourceConfig 参数

```json
{
  "ResourceConfigs": [
    {
      "InstanceType": "ecs.gn7i-c8g1.2xlarge",
      "Count": 1,
      "Role": "worker"
    }
  ]
}
```

| 参数 | 说明 |
|------|------|
| InstanceType | ECS 实例规格，如 `ecs.gn7i-c8g1.2xlarge`（A10 1卡） |
| Count | 节点数量 |
| Role | 角色：`worker` 或 `ps`（参数服务器） |

### CodeSourceItem 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| CodeSourceId | String | 否 | 已创建的代码源 ID |
| CodeRepoType | String | 否 | 仓库类型：`git` |
| CodeURL | String | 否 | Git 仓库地址 |
| Revision | String | 否 | 分支或 Commit |
| CodeDir | String | 否 | 容器内挂载路径 |
| ECSImageId | String | 否 | 代码拉取镜像 |

### DataSourceItem 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| DataSourceType | String | 是 | `OSS`, `NAS`, `CPFS`, `MaxCompute` |
| DataSourceId | String | 否 | 已创建的数据源 ID |
| FileSystemId | String | 否 | NAS 文件系统 ID |
| URI | String | 否 | OSS 路径，如 `oss://bucket/path/` |
| MountPath | String | 是 | 容器内挂载路径 |
| AccessPermission | String | 否 | `RO`（只读）或 `RW`（读写） |

### 请求示例

```json
{
  "DisplayName": "mindcore-training",
  "JobType": "PyTorchJob",
  "Image": "registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
  "UserCommand": "cd /code && pip install -r requirements.txt && python -m mindcore train --config config/demo_train.yaml",
  "ResourceConfig": {
    "ResourceConfigs": [
      {
        "InstanceType": "ecs.gn7i-c8g1.2xlarge",
        "Count": 1,
        "Role": "worker"
      }
    ]
  },
  "DataSources": [
    {
      "DataSourceType": "OSS",
      "URI": "oss://mindcore-data/dataset/v1/",
      "MountPath": "/mnt/data",
      "AccessPermission": "RO"
    },
    {
      "DataSourceType": "OSS",
      "URI": "oss://mindcore-data/results/",
      "MountPath": "/mnt/output",
      "AccessPermission": "RW"
    }
  ],
  "CodeSource": {
    "CodeRepoType": "git",
    "CodeURL": "https://github.com/your-org/MindCore.git",
    "Revision": "master",
    "CodeDir": "/code"
  },
  "Options": "{\"mountType\":\"ossfs\"}",
  "MaxRunningTimeInSeconds": 14400,
  "UseSpot": true
}
```

### 返回示例

```json
{
  "JobId": "job-xxxxxxxxxxxxxxx",
  "RequestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

## ListJobs — 查询任务列表

### 请求参数

| 参数 | 类型 | 说明 |
|------|------|------|
| WorkspaceId | String | 工作空间 ID |
| PageSize | Integer | 每页大小，默认 10 |
| PageNumber | Integer | 页码，默认 1 |
| Status | String | 按状态过滤：`Pending`, `Running`, `Succeeded`, `Failed` |
| JobType | String | 按类型过滤 |
| DisplayName | String | 按名称模糊搜索 |

### 返回示例

```json
{
  "Jobs": [
    {
      "JobId": "job-xxx",
      "DisplayName": "mindcore-training",
      "JobType": "PyTorchJob",
      "Status": "Running",
      "StartTime": "2026-04-14T10:00:00Z",
      "ResourceConfig": {...}
    }
  ],
  "TotalCount": 1,
  "PageSize": 10,
  "PageNumber": 1
}
```

## GetJob — 查询任务详情

```
GET /api/v1/jobs/{JobId}
```

返回任务的完整信息，包括状态、资源配置、日志地址等。

## 错误码

| 错误码 | 说明 |
|--------|------|
| InvalidParameter | 参数错误 |
| ResourceNotFound | 资源不存在 |
| QuotaExceeded | 配额不足 |
| InternalError | 内部错误 |

## 参考链接
- [CreateJob API 调试](https://api.aliyun.com/api/pai-dlc/2020-12-03/CreateJob)
- [CodeSourceItem 参数](https://help.aliyun.com/zh/pai/developer-reference/api-pai-dlc-2020-12-03-struct-codesourceitem)
- [DataSourceItem 参数](https://help.aliyun.com/zh/pai/developer-reference/api-pai-dlc-2020-12-03-struct-datasourceitem)
- [ListJobs API](https://help.aliyun.com/zh/pai/developer-reference/api-pai-dlc-2020-12-03-listjobs)
- [PAI-DLC OpenAPI 门户](https://api.aliyun.com/product/pai-dlc)
