"""E2E 测试共享配置。"""

import os
from pathlib import Path
import pytest


def pytest_addoption(parser):
    """添加自定义命令行选项。"""
    parser.addoption(
        "--frontend-url",
        default="http://localhost:5173",
        help="前端开发服务器地址",
    )
    parser.addoption(
        "--chrome-path",
        default=None,
        help="Chrome/Chromium 可执行文件路径，不指定则用 Playwright 自带的",
    )


@pytest.fixture(scope="session")
def frontend_url(request):
    return request.config.getoption("--frontend-url")


@pytest.fixture(scope="session")
def chrome_path(request):
    return request.config.getoption("--chrome-path")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, chrome_path):
    """配置自定义浏览器路径。"""
    if chrome_path:
        return {**browser_type_launch_args, "executable_path": chrome_path}
    return browser_type_launch_args
