#!/usr/bin/env python3
"""Generate .env.example from all registered settings schemas."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# noqa: E402,F401 需要在 path 设置后导入以触发 settings 注册
from backend.core.config import config_manager  # noqa: E402

# 导入所有插件以触发 settings 注册
from backend.plugins import oss  # noqa: F401, E402
from backend.plugins import cloud_integration  # noqa: F401, E402
from backend.plugins import github_proxy  # noqa: F401, E402
from backend.plugins import crawler  # noqa: F401, E402
from backend.plugins import deploy_webhook  # noqa: F401, E402


def main():
    content = config_manager.generate_env_example()

    # 写入 .env.example
    output_path = project_root / ".env.example"
    output_path.write_text(content + "\n", encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Total lines: {len(content.splitlines())}")


if __name__ == "__main__":
    main()
