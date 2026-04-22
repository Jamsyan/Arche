# 命令规则

> 本目录定义了在 Arche 项目中允许和禁止使用的 shell 命令。
> Claude 在执行任何 Bash 操作前必须先查阅本规则。
>
> 本规则受 `constitution.md`（宪法）约束。

## 标准工作流命令（始终允许）

以下命令已在 `settings.json` 中配置为 allow，可直接执行，无需额外审批：

### 构建与依赖
- `uv sync` — 安装依赖
- `uv run <package>` — 运行 Python 包
- `uv run python` — 运行 Python 脚本

### 代码质量
- `uv run ruff check .` — Lint 检查
- `uv run ruff check <path>` — 检查指定文件
- `uv run ruff format .` — 格式化
- `uv run ruff format <path>` — 格式化指定文件

### 测试
- `uv run pytest` — 运行测试
- `uv run pytest <path>` — 运行指定测试

### Git 操作
- `git status` / `git diff` / `git log` / `git add` / `git commit` — 标准 git 操作
- `git push` / `git pull` — 推送拉取

### 前端构建
- `npm install` — 安装前端依赖
- `npm run dev` — 启动前端开发服务器
- `npm run build` — 构建前端

### 文件查看
- `ls` / `dir` / `tree` / `find` — 文件浏览
- `cat` / `head` / `tail` / `wc` — 文件内容查看
- `jq` — JSON 处理
- `which` / `type` — 命令查找

## 严格禁止的命令（需用户明确同意）

以下命令**不得自行执行**，必须先向用户说明用途并获得明确许可：

| 命令 | 原因 |
|------|------|
| `rm -rf` / `rm -f` | 删除文件不可逆 |
| `sudo` | 提升权限，可能影响系统安全 |
| `curl ... \| bash` | 管道执行远程代码，极高风险 |
| `wget ... \| sh` | 同上 |
| `pip install` | 项目使用 uv 管理依赖，不用 pip |
| `python -m pip` | 同上 |
| `apt-get` / `brew` / `choco` | 系统级包管理，需用户操作 |
| `docker build/run` | 容器操作，需用户确认 |
| 任何修改 `.claude/settings.json` 的操作 | 权限配置变更 |

## 需要确认的命令

以下命令可以执行，但执行前需简要说明用途：

| 命令 | 说明要求 |
|------|----------|
| `find` 带 `-delete` | 说明删除哪些文件 |
| 超过 30 秒的长运行命令 | 预估耗时，确认是否值得运行 |
| `git reset --hard` | 丢弃本地变更，高风险 |
| `git checkout --` | 丢弃未提交文件 |
| 任何写入 `data/` 目录的命令 | 数据文件可能很大/重要 |

## Python 执行规范

- **始终使用 `uv run python`**，不用裸 `python`
- **不要使用裸 `pip install`**，依赖变更写入 `pyproject.toml` 后 `uv sync`
- **不要直接编辑 `pyproject.toml`**，优先使用 `uv add`/`uv remove` 等命令间接修改，只有 uv CLI 不支持的场景才直接编辑
- **不要使用 `python -m pytest`**，用 `uv run pytest`
- **不要使用 `python -m ruff`**，用 `uv run ruff`

## 长运行命令规范

对于可能运行很久的命令（如数据迁移、批量处理）：

1. 先说明预计耗时
2. 使用 `run_in_background: true` 后台运行
3. 不要在 foreground 同步等待超时命令
4. 不要让用户反复审批同一个长命令的权限

## Git 提交规范

- **开发完成后不要自动提交** — 用户会手动审核并决定何时提交
- **提交时不要添加 Co-Authored-By** — 不使用 `Co-Authored-By: Claude ...` 行
- 用户明确要求提交时，才执行 `git commit`

## 更新记录

- 2026-04-21: 初始创建