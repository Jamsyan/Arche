#!/usr/bin/env python3
"""
API 层冒烟测试：验证前端 API 层与后端接口契约是否匹配
"""
import json
import subprocess
import sys
from typing import Callable

# 跳过的接口列表，测一下
TEST_ENDPOINTS = [
    # ("/api/auth/me",
    ("/api/auth/users"),
    ("/api/auth/admin/users"),
    ("/api/blog/posts",
    ("/api/blog/tags",
    ("/api/blog/my-posts"),
    ("/api/blog/favorites",
    ("/api/blog/moderation/pending",
    ("/api/cloud/stats",
    ("/api/cloud/jobs",
    ("/api/cloud/datasets",
    ("/api/cloud/repos",
    ("/api/cloud/artifacts",
    ("/api/oss/storage/stats",
    ("/api/oss/my",
    ("/api/oss/quota",
    ("/api/oss/admin/stats",
    ("/api/oss/admin/rate-limit",
    ("/api/oss/admin/quotas",
    ("/api/crawler/status",
    ("/api/crawler/stats",
    ("/api/crawler/records",
    ("/api/monitor/system/qps",
    ("/api/monitor/system/memory",
    ("/api/monitor/default",
    ("/api/system/summary",
    ("/api/system/processes",
    ("/api/assets",
    ("/api/assets/stats",
    ("/api/admin/config",
    ("/api/github/search/repositories?q=test",
]

def main
