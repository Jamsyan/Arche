"""SSH 执行器，用于远程命令执行和文件传输。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import asyncssh

from backend.core.middleware import AppError

if TYPE_CHECKING:
    from asyncssh.connection import SSHClientConnection


class SSHError(AppError):
    def __init__(
        self,
        message: str = "SSH 操作失败",
        code: str = "ssh_error",
        status_code: int = 500,
    ):
        super().__init__(message, code, status_code)


class SSHExecutor:
    """SSH 远程命令执行 + SFTP 文件传输封装。"""

    def __init__(self):
        self._connections: dict[str, SSHClientConnection] = {}

    async def connect(
        self,
        host: str,
        port: int = 22,
        user: str = "root",
        key_path: str | None = None,
        password: str | None = None,
    ) -> SSHClientConnection:
        """建立 SSH 连接。"""
        conn_key = f"{host}:{port}"
        if conn_key in self._connections:
            return self._connections[conn_key]

        connect_kwargs: dict = {
            "host": host,
            "port": port,
            "username": user,
            "known_hosts": None,  # TODO: 生产环境应验证 host key
        }

        if key_path:
            connect_kwargs["client_keys"] = [key_path]
        elif password:
            connect_kwargs["password"] = password
        else:
            raise SSHError("SSH 认证失败：需要提供密钥路径或密码")

        try:
            conn = await asyncssh.connect(**connect_kwargs)
            self._connections[conn_key] = conn
            return conn
        except Exception as e:
            raise SSHError(f"SSH 连接失败 ({host}:{port}): {e}")

    async def execute(self, conn_key: str, cmd: str, timeout: int = 300) -> str:
        """执行远程命令。"""
        conn = self._connections.get(conn_key)
        if not conn:
            raise SSHError(f"SSH 连接不存在: {conn_key}")

        try:
            result = await conn.run(cmd, timeout=timeout, check=True)
            stdout = result.stdout
            return stdout.decode() if isinstance(stdout, bytes) else (stdout or "")
        except asyncssh.Error as e:
            raise SSHError(f"远程命令执行失败: {cmd}\n{str(e)}")
        except Exception as e:
            raise SSHError(f"SSH 执行失败: {e}")

    async def download(self, conn_key: str, remote_path: str, local_path: Path) -> None:
        """SFTP 下载远程文件。"""
        conn = self._connections.get(conn_key)
        if not conn:
            raise SSHError(f"SSH 连接不存在: {conn_key}")

        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(remote_path, str(local_path))
        except Exception as e:
            raise SSHError(f"SFTP 下载失败: {remote_path} -> {local_path}: {e}")

    async def upload(self, conn_key: str, local_path: Path, remote_path: str) -> None:
        """SFTP 上传本地文件。"""
        conn = self._connections.get(conn_key)
        if not conn:
            raise SSHError(f"SSH 连接不存在: {conn_key}")

        try:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(str(local_path), remote_path)
        except Exception as e:
            raise SSHError(f"SFTP 上传失败: {local_path} -> {remote_path}: {e}")

    async def compute_sha256(self, conn_key: str, remote_path: str) -> str:
        """计算远程文件的 SHA256。"""
        output = await self.execute(conn_key, f"sha256sum {remote_path}")
        return output.split()[0] if output else ""

    async def compute_local_sha256(self, local_path: Path) -> str:
        """计算本地文件的 SHA256。"""
        h = hashlib.sha256()
        with open(local_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    async def close(self, conn_key: str) -> None:
        """关闭指定连接。"""
        conn = self._connections.pop(conn_key, None)
        if conn:
            conn.close()
            await conn.wait_closed()

    async def close_all(self) -> None:
        """关闭所有连接。"""
        for key in list(self._connections):
            await self.close(key)
