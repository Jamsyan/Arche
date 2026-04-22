# 阿里云 PAI-DLC 知识库

> 本目录记录阿里云 PAI（Platform for AI）DLC（Deep Learning Containers）训练服务的调研结果。
> 目标：为 MindCore 项目的训练任务提供完整的 PAI-DLC 使用指南。

## 文档索引

| 文档 | 内容 | 适合场景 |
|------|------|---------|
| [01-服务概览](01-服务概览.md) | PAI-DLC 是什么、核心概念、架构图、与其他产品的关系 | 入门了解 |
| [02-快速入门](02-快速入门.md) | 从零到一提交第一个训练任务的完整步骤 | 第一次使用 |
| [03-镜像系统](03-镜像系统.md) | 官方预置镜像、自定义镜像构建、镜像地址格式 | 环境配置 |
| [04-计费与试用](04-计费与试用.md) | 公共资源组/专有资源组计费、免费试用、省钱策略 | 成本控制 |
| [05-存储与挂载](05-存储与挂载.md) | OSS/NAS/CPFS 挂载方式、代码源配置、数据集管理 | 数据接入 |
| [06-API参考](06-API参考.md) | CreateJob/ListJobs/GetJob 等核心 API 参数详解 | 自动化提交 |
| [07-SDK使用](07-SDK使用.md) | PAI Python SDK (Estimator) 和 alibabacloud-pai-dlc SDK | 代码化提交 |
| [08-MindCore接入方案](08-MindCore接入方案.md) | MindCore 训练任务接入 PAI-DLC 的具体方案设计 | **重点** |

## 关键链接

| 资源 | 链接 |
|------|------|
| PAI-DLC 产品页 | https://www.aliyun.com/product/pai |
| DLC 官方文档 | https://help.aliyun.com/zh/pai/user-guide/what-is-dlc |
| 快速入门 | https://www.alibabacloud.com/help/zh/pai/getting-started/distributed-training-dlc-quickstart |
| 计费说明 | https://help.aliyun.com/zh/pai/billing-of-dlc |
| 官方定价页 | https://www.aliyun.com/page-source/price/detail/machinelearning_price |
| 免费试用指南 | https://help.aliyun.com/zh/pai/getting-started/free-trial-guide |
| 官方镜像列表 | https://help.aliyun.com/zh/pai/user-guide/image-management/ |
| CreateJob API | https://api.aliyun.com/api/pai-dlc/2020-12-03/CreateJob |
| PAI Python SDK | https://help.aliyun.com/zh/pai/developer-reference/install-and-configure-pai-python-sdk |
| GitHub 示例 | https://github.com/aliyun/pai-examples |
| SDK 文档 | https://pai-sdk.oss-cn-shanghai.aliyuncs.com/pai/doc/latest/user-guide/training/submit-job.html |

## 核心结论速查

### 什么是 DLC？
PAI-DLC 是阿里云提供的 Serverless 深度学习训练平台。底层用 Kubernetes 拉起计算节点，支持单机和分布式训练。你只需要提供代码 + 数据 + 镜像，DLC 负责调度 GPU 资源。

### 两种资源组
- **公共资源组**：Serverless，按任务时长付费，无需管理机器。适合临时训练。
- **专有资源组**：独占 GPU 机器，DLC 平台费免费，你付 ECS 费用。适合长期大量训练。

### 免费试用
- 新用户 **100 CU·H**（计算单元·小时），有效期 3 个月
- 配合竞价实例（Spot）可以花很少的钱跑训练

### 推荐镜像
PyTorch 训练镜像：`registry.cn-hangzhou.aliyuncs.com/pai-dlc/pai-pytorch-training:<tag>`
建议使用较新的 PyTorch 2.x + CUDA 11.8+ 版本。

### 推荐提交方式
- **手动/调试**：PAI 控制台网页
- **脚本化**：PAI Python SDK（`pip install pai`）的 Estimator API
- **底层控制**：alibabacloud-pai-dlc20201203 SDK 直接调用 CreateJob API
