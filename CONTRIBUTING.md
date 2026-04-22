# 贡献指南

感谢你关注 Arche 项目！无论你是提交 Bug 报告、改进文档，还是贡献代码，都请阅读以下指南。

## 目录

- [行为准则](#行为准则)
- [我能做什么](#我能做什么)
- [提交 Bug 报告](#提交-bug-报告)
- [提出功能建议](#提出功能建议)
- [代码贡献流程](#代码贡献流程)
- [开发环境搭建](#开发环境搭建)
- [代码风格](#代码风格)
- [提交 Commit 规范](#提交-commit-规范)
- [Pull Request 流程](#pull-request-流程)

## 行为准则

本项目遵循开源社区的基本行为准则：尊重他人、友好沟通、就事论事。

## 我能做什么

- **Bug 报告**：发现并报告问题就是最好的贡献
- **文档改进**：修正错别字、补充说明、优化 README
- **代码修复**：修 Bug、加测试、优化性能
- **功能开发**：实现新功能或插件

对于首次贡献者，建议从 `good first issue` 标签的 Issue 开始，熟悉项目后再提交更大的变更。

## 提交 Bug 报告

请在 GitHub 创建 Issue，包含以下信息：

1. **环境信息**：操作系统、Python 版本、浏览器版本
2. **复现步骤**：尽可能简洁，一步步写清楚
3. **预期行为**：你认为应该发生什么
4. **实际行为**：实际发生了什么
5. **日志/截图**：相关错误日志或截图

## 提出功能建议

请在 GitHub 创建 Issue，说明：

- 你想解决什么问题
- 你期望的效果是什么
- 是否有参考的实现或类似功能

## 代码贡献流程

1. Fork 本仓库
2. 基于 `master` 创建特性分支（`git checkout -b feat/your-feature`）
3. 修改代码，确保通过 lint 和测试
4. 提交变更（遵循 [Commit 规范](#提交-commit-规范)）
5. 推送到你的 Fork
6. 创建 Pull Request 到本仓库的 `master` 分支

## 开发环境搭建

### 后端

```bash
# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 运行 lint
uv run ruff check .

# 运行测试
uv run pytest

# 启动开发服务器
uv run uvicorn backend.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 代码质量检查

在提交 PR 前，请确保：

```bash
# 后端 lint + 格式化
uv run ruff check .
uv run ruff format .

# 前端 lint
cd frontend && npm run lint

# 测试
uv run pytest
```

## 代码风格

- **Python**：遵循 [Ruff](https://docs.astral.sh/ruff/) 规则，提交前运行 `uv run ruff format .`
- **JavaScript/Vue**：遵循前端项目的 ESLint 配置
- **注释**：仅在有隐藏约束、特殊 workaround 或读者可能困惑的 WHY 时添加注释，不要注释显而易见的代码
- **命名**：使用有意义的标识符名称，让代码自解释

## 提交 Commit 规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>
```

**Type**：
- `feat`：新功能
- `fix`：Bug 修复
- `docs`：文档变更
- `style`：代码格式（不影响功能）
- `refactor`：重构（不是新功能也不是修复）
- `perf`：性能优化
- `test`：测试相关
- `ci`：CI/CD 相关
- `chore`：构建/工具链变更

**示例**：
```
feat(oss): 添加 MinIO 分片上传支持
fix(blog): 修复敏感词过滤的边界条件
docs(readme): 补充部署文档中的环境变量说明
```

## Pull Request 流程

1. PR 标题简洁明了（70 字符以内）
2. PR 描述包含：
   - 变更摘要
   - 相关 Issue 链接
   - 截图或 GIF（前端变更）
3. 确保 CI 通过
4. 等待 Review，根据反馈调整

---

感谢你的时间和贡献！
