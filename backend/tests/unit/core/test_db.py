"""数据库模块测试。"""

import pytest

# 不要直接导入变量，导入模块
import backend.core.db as db_module
from backend.core.db import (
    init_db,
)


class TestDatabase:
    """测试数据库核心功能。"""

    def setup_method(self):
        """每个测试前重置 db 模块的全局变量，避免跨测试残留。"""
        db_module.engine = None
        db_module.session_factory = None
        db_module._initialized = False

    def teardown_method(self):
        """测试后再次清理 db 模块的全局变量。

        注意：不要 `Base.metadata.clear()` —— 这会清空所有插件 model 的
        表元数据，使其它使用 in_memory_db / Base.metadata.create_all 的
        测试在执行顺序之后丢失全部表，导致 `no such table` 失败。
        """
        db_module.engine = None
        db_module.session_factory = None
        db_module._initialized = False

    def test_init_db(self):
        """init_db 函数正确创建引擎和会话工厂。"""
        assert db_module.engine is None
        assert db_module.session_factory is None

        database_url = "sqlite+aiosqlite:///:memory:"
        engine, session_factory = init_db(database_url)

        assert engine is not None
        assert session_factory is not None
        assert engine is db_module.engine
        assert session_factory is db_module.session_factory
        # 验证引擎配置正确
        assert str(engine.url) == database_url

    def test_init_db_expire_on_commit_false(self):
        """init_db 创建的 session_factory 必须设置 expire_on_commit=False。

        这是关键配置，否则在 session 关闭后访问对象属性会抛出
        DetachedInstanceError，导致编排器等后台任务崩溃。
        """
        database_url = "sqlite+aiosqlite:///:memory:"
        _, session_factory = init_db(database_url)

        # 验证 expire_on_commit=False
        assert session_factory.kw.get("expire_on_commit") is False
