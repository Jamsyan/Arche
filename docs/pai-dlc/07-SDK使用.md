# 07 — SDK 使用

## SDK 类型选择

阿里云提供了两套 Python SDK 来操作 PAI-DLC：

| SDK | 安装命令 | 定位 | 适合 |
|-----|---------|------|------|
| **PAI Python SDK** (`pai`) | `pip install pai` | 高级 API，Estimator 抽象 | 快速上手、类似 SageMaker 体验 |
| **PAI-DLC OpenAPI SDK** | `pip install alibabacloud-pai-dlc20201203` | 底层 API，直接调用 OpenAPI | 精细控制、自动化编排 |

---

## 方案一：PAI Python SDK（推荐）

### 安装
```bash
pip install pai
```

### 初始化配置
```bash
python -m pai.toolkit.config
```

配置项：
- `access_key_id` / `access_key_secret`
- `region`（如 `cn-hangzhou`）
- `workspace_id`
- `oss_bucket`

也可代码中直接配置：
```python
import pai

pai.set_config(
    access_key_id="your-ak",
    access_key_secret="your-sk",
    region="cn-hangzhou",
    workspace_id="your-workspace-id",
)
```

### Estimator 方式提交

```python
from pai.estimator import Estimator

estimator = Estimator(
    image_uri="registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
    source_dir="./src/mindcore",      # 本地代码目录
    entry_point="train.py",            # 入口脚本
    command="python -m mindcore train --config config/demo_train.yaml",
    instance_type="ecs.gn7i-c8g1.2xlarge",
    instance_count=1,
    max_run_time=7200,
    use_spot=True,                     # 竞价实例
    outputs=["/mnt/output/checkpoints/"],
)

estimator.fit(
    inputs={
        "data": "oss://mindcore-data/dataset/v1/",
    },
    job_name="mindcore-job",
    wait=True,                         # 阻塞等待完成
)
```

### TorchEstimator（PyTorch 专用）

```python
from pai.estimator import TorchEstimator

estimator = TorchEstimator(
    image_uri="registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
    source_dir="./src",
    entry_point="train.py",
    instance_type="ecs.gn7i-c8g1.2xlarge",
    hyperparameters={
        "config": "config/demo_train.yaml",
        "epochs": 10,
        "batch_size": 32,
    },
)

estimator.fit(inputs={"data": "oss://mindcore-data/dataset/v1/"})
```

### 任务管理

```python
from pai.dlc import Job

# 获取任务
job = Job.get(job_name="mindcore-job")

# 查看状态
print(job.status)

# 查看日志
print(job.get_logs())

# 停止任务
job.stop()

# 删除任务
job.delete()
```

### TensorBoard 集成

```python
from pai.dlc import Tensorboard

tb = Tensorboard.create(
    log_dir="/mnt/output/tensorboard/",
    job_name="mindcore-tb",
)
print(tb.access_url)
```

---

## 方案二：alibabacloud-pai-dlc SDK

### 安装
```bash
pip install alibabacloud-pai-dlc20201203
```

### 初始化客户端

```python
from alibabacloud_pai_dlc20201203.client import Client
from alibabacloud_tea_openapi.models import Config

config = Config(
    access_key_id="your-ak",
    access_key_secret="your-sk",
    endpoint="pai-dlc.cn-hangzhou.aliyuncs.com",
)
client = Client(config)
```

### 创建训练任务

```python
from alibabacloud_pai_dlc20201203.models import (
    CreateJobRequest,
    CreateJobRequestResourceConfig,
    CreateJobRequestResourceConfigResourceConfigs,
    DataSourceItem,
    CodeSourceItem,
)

# 资源配置
resource_config = CreateJobRequestResourceConfig(
    resource_configs=[
        CreateJobRequestResourceConfigResourceConfigs(
            instance_type="ecs.gn7i-c8g1.2xlarge",
            count=1,
            role="worker",
        )
    ]
)

# 数据源
data_sources = [
    DataSourceItem(
        data_source_type="OSS",
        uri="oss://mindcore-data/dataset/v1/",
        mount_path="/mnt/data",
        access_permission="RO",
    ),
    DataSourceItem(
        data_source_type="OSS",
        uri="oss://mindcore-data/results/",
        mount_path="/mnt/output",
        access_permission="RW",
    ),
]

# 代码源
code_source = CodeSourceItem(
    code_repo_type="git",
    code_url="https://github.com/your-org/MindCore.git",
    revision="master",
    code_dir="/code",
)

# 创建请求
request = CreateJobRequest(
    display_name="mindcore-training",
    job_type="PyTorchJob",
    image="registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
    user_command="cd /code && python -m mindcore train --config config/demo_train.yaml",
    resource_config=resource_config,
    data_sources=data_sources,
    code_source=code_source,
    options='{"mountType": "ossfs"}',
    max_running_time_in_seconds=14400,
    use_spot=True,
)

# 提交
response = client.create_job(request)
print(f"Job ID: {response.body.job_id}")
```

### 查询任务

```python
from alibabacloud_pai_dlc20201203.models import ListJobsRequest

# 查询列表
list_req = ListJobsRequest(
    workspace_id="your-workspace-id",
    page_size=10,
    page_number=1,
)
resp = client.list_jobs(list_req)
for job in resp.body.jobs:
    print(f"{job.display_name}: {job.status}")

# 查询详情
from alibabacloud_pai_dlc20201203.models import GetJobRequest
get_req = GetJobRequest(job_id="job-xxx")
detail = client.get_job(get_req)
print(detail.body)
```

### 停止任务

```python
from alibabacloud_pai_dlc20201203.models import StopJobRequest

stop_req = StopJobRequest(job_id="job-xxx")
client.stop_job(stop_req)
```

---

## 方案三：DLC 命令行工具

安装后可在终端直接操作 DLC：

```bash
# 提交 PyTorch 任务
dlc submit pytorchjob --job_file ./job.params

# 查看任务列表
dlc list jobs

# 查看任务日志
dlc get logs --job-id job-xxx
```

`job.params` 示例：
```ini
name=mindcore-job
image=registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8
command=python -m mindcore train --config config/demo_train.yaml
worker_count=1
ecs_spec=ecs.gn7i-c8g1.2xlarge
use_spot=true
max_run_time=7200
```

---

## SDK 文档链接

| 文档 | 链接 |
|------|------|
| SDK 安装与配置 | https://help.aliyun.com/zh/pai/developer-reference/install-and-configure-pai-python-sdk |
| Estimator 提交训练 | https://help.aliyun.com/zh/pai/developer-reference/submit-a-training-job |
| PyTorch 训练部署 | https://help.aliyun.com/zh/pai/developer-reference/train-and-deploy-a-pytorch-model |
| PAI-DLC SDK 中心 | https://api.aliyun.com/api-tools/sdk/pai-dlc |
| GitHub 示例 | https://github.com/aliyun/pai-examples |
| Checkpoint 使用示例 | https://github.com/aliyun/pai-examples/blob/master/pai-python-sdk/training/checkpoint/checkpoint.ipynb |
| TensorBoard 示例 | https://github.com/aliyun/pai-examples/blob/master/pai-python-sdk/training/tensorboard/tensorboard.ipynb |
| SDK 在线文档 | https://pai-sdk.oss-cn-shanghai.aliyuncs.com/pai/doc/latest/user-guide/training/submit-job.html |
