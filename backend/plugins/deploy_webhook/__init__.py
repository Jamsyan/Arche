"""Deploy webhook plugin — 接收 CI/CD 触发器 POST 请求，执行部署脚本。"""

from __future__ import annotations

import asyncio
import os
import subprocess
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI


class DeployRequest(BaseModel):
    token: str


router = APIRouter()

# 部署脚本路径，默认生产服务器位置
DEPLOY_SCRIPT = os.environ.get("DEPLOY_SCRIPT", "/home/admin/arche/deploy.sh")


def _run_script() -> tuple[int, str, str]:
    """执行部署脚本。返回 (returncode, stdout, stderr)。"""
    proc = subprocess.run(
        ["bash", DEPLOY_SCRIPT],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return proc.returncode, proc.stdout, proc.stderr


@router.post("/api/deploy")
async def trigger_deploy(request: DeployRequest):
    deploy_token = os.environ.get("DEPLOY_TOKEN", "")
    if not deploy_token or request.token != deploy_token:
        raise HTTPException(status_code=401, detail="Invalid deploy token")

    if not os.path.isfile(DEPLOY_SCRIPT):
        raise HTTPException(
            status_code=500,
            detail=f"Deploy script not found at {DEPLOY_SCRIPT}",
        )

    returncode, stdout, stderr = await asyncio.to_thread(_run_script)

    if returncode != 0:
        return {
            "status": "failed",
            "returncode": returncode,
            "stdout": stdout[-2000:],
            "stderr": stderr[-1000:],
        }

    return {
        "status": "success",
        "stdout": stdout[-2000:],
    }


class DeployWebhookPlugin(BasePlugin):
    name = "deploy_webhook"
    version = "0.1.0"

    def setup(self, app: "FastAPI") -> None:
        app.include_router(router)


plugin = DeployWebhookPlugin()
registry.register("deploy_webhook", plugin)
