# 08 — MindCore 接入 PAI-DLC 方案

> 本文档是**重点文档**，定义了 MindCore 训练任务如何接入阿里云 PAI-DLC。

## 整体架构

```
本地开发                 阿里云 PAI-DLC
┌──────────────┐        ┌─────────────────────────────┐
│  clean.py    │──推──▶ │  OSS: oss://mindcore-data/  │
│  数据清洗     │        │  ├─ dataset/v1/             │
├──────────────┤        │  ├─ code/mindcore.tar.gz    │
│  SDK 提交     │──推──▶ │  └─ results/                │
│  训练任务     │        ├─────────────────────────────┤
│              │◀──拉──▶ │  DLC: PyTorchJob            │
│  查看结果     │        │    → python -m mindcore     │
│  TensorBoard │◀──拉──▶ │  TensorBoard                │
└──────────────┘        └─────────────────────────────┘
```

## 阶段一：试训验证（当前阶段）

### 目标
用少量数据（3000 条以内）+ hidden_dim=512 + 公共资源组 Spot 实例，验证全链路通畅。

### 数据准备
1. 下载开源中文 SFT 数据集（如 Chinese-Dolly-15k）
2. 本地运行 `clean.py` 质量筛选
3. 上传到 OSS：`oss://mindcore-data/dataset/v1/`

### 训练任务配置

```python
from pai.estimator import Estimator

estimator = Estimator(
    image_uri="registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
    source_dir="./src/mindcore",
    command=(
        "pip install pytorch-lightning rich tensorboard pyyaml && "
        "python -m mindcore train --config config/demo_train.yaml"
    ),
    instance_type="ecs.gn7i-c8g1.2xlarge",  # A10 1卡
    instance_count=1,
    max_run_time=7200,                      # 2 小时上限
    use_spot=True,                          # 竞价实例
)

estimator.fit(
    inputs={
        "data": "oss://mindcore-data/dataset/v1/",
    },
    job_name="mindcore-trial",
    wait=False,
)
```

### 预期费用
- 1 卡 A10 Spot 实例：~1-2 元/小时
- 训练 2 小时：~2-4 元
- 加上试用额度（100 CU·H），基本免费

### demo_train.yaml 需要调整的点

```yaml
# 数据源改为 OSS（DLC 挂载后路径变为 /mnt/data/）
data:
  sources:
    - path: /mnt/data/cleaned_00000.jsonl
      weight: 1.0

# checkpoint 保存到挂载的输出目录
checkpoint:
  save_dir: /mnt/output/checkpoints/
  output: oss://mindcore-data/results/pretrain_demo/
```

## 阶段二：正式训练

### 目标
使用清洗后的自有数据 + hidden_dim=4096 + 专有资源组，训练可用模型。

### 资源规划
- 至少 1 卡 V100（32GB）或 A100
- 建议专有资源组（包月更划算）
- 训练时间预计数小时到数十小时

### 训练任务配置

```python
estimator = Estimator(
    image_uri="registry.cn-hangzhou.aliyuncs.com/your-namespace/mindcore-training:latest",
    # 使用自定义镜像（预装所有依赖）
    command="python -m mindcore train --config config/production.yaml",
    instance_type="ecs.gn6v-c8g1.2xlarge",  # V100 1卡
    instance_count=1,
    max_run_time=86400,                      # 24 小时
    use_spot=False,
)
```

## 自动化训练管线设计

### 目标
实现"改配置 → 一键提交 → 自动看结果"的闭环。

### 脚本设计：`scripts/submit_pai_job.py`

```python
#!/usr/bin/env python3
"""提交 MindCore 训练任务到 PAI-DLC"""

import argparse
from pai.estimator import Estimator

def submit_job(config_path: str, job_name: str, use_spot: bool = True):
    estimator = Estimator(
        image_uri="registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:2.0-gpu-py310-cuda11.8",
        source_dir="./src/mindcore",
        command=f"pip install pytorch-lightning rich tensorboard pyyaml && "
                f"python -m mindcore train --config {config_path}",
        instance_type="ecs.gn7i-c8g1.2xlarge",
        instance_count=1,
        max_run_time=7200,
        use_spot=use_spot,
    )

    estimator.fit(
        inputs={"data": "oss://mindcore-data/dataset/v1/"},
        job_name=job_name,
        wait=False,
    )
    print(f"已提交: {job_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/demo_train.yaml")
    parser.add_argument("--name", default="mindcore-auto")
    parser.add_argument("--no-spot", action="store_true")
    args = parser.parse_args()
    submit_job(args.config, args.name, use_spot=not args.no_spot)
```

### 完整工作流

```bash
# 1. 数据清洗
uv run mindcore clean data/raw.jsonl -o data/cleaned --pretrain

# 2. 推送到 OSS（通过 ossutil 或脚本）
ossutil cp -r data/cleaned/pretrain/ oss://mindcore-data/dataset/v1/

# 3. 提交训练
uv run python scripts/submit_pai_job.py --config config/demo_train.yaml --name trial-001

# 4. 查看任务状态
uv run python scripts/submit_pai_job.py --list

# 5. 训练完成后拉结果
ossutil cp -r oss://mindcore-data/results/trial-001/ checkpoints/trial-001/

# 6. 查看训练曲线
tensorboard --logdir checkpoints/trial-001/tensorboard/
```

## 数据流水线与 DLC 的衔接

```
原始数据 → clean.py → 清洗后 JSONL → push_data.sh → 服务器
                                              ↓
                                        ossutil 上传
                                              ↓
                                    oss://mindcore-data/dataset/
                                              ↓
                                    DLC 挂载为 /mnt/data/
                                              ↓
                                    训练任务读取数据
                                              ↓
                                    产物写入 /mnt/output/
                                              ↓
                                    自动上传回 oss://mindcore-data/results/
```

## 关键注意事项

1. **路径适配**：本地路径（`data/cache/`）在 DLC 中变为挂载路径（`/mnt/data/`），配置文件需区分本地和 DLC 两套
2. **依赖安装**：DLC 官方镜像不含 pytorch-lightning，需要在启动命令中 `pip install` 或自定义镜像
3. **Python 版本**：DLC 镜像通常用 Python 3.8-3.10，MindCore 本地用 3.13，注意兼容性
4. **Token 化**：Tokenizer 训练需要在 DLC 容器中执行，产物保存到挂载路径
5. **日志输出**：DLC 的 stdout 自动捕获为训练日志，确保 Rich 在非终端环境下降级输出
6. **超时保护**：务必设 `max_run_time`，防止任务意外长时间运行产生高额费用

## 下一步行动

- [ ] 下载并清洗 Chinese-Dolly-15k 数据集
- [ ] 编写 `scripts/submit_pai_job.py` 提交脚本
- [ ] 配置 OSS bucket 并上传测试数据
- [ ] 用公共资源组 Spot 实例提交第一个试训任务
- [ ] 验证 TensorBoard 和训练报告正常输出
