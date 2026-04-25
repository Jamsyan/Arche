"""插件配置基类测试。"""
from pydantic import Field
from backend.core.settings.base import PluginSettingsBase, create_plugin_settings


class TestPluginSettingsBase:
    """测试插件配置基类。"""

    def test_get_field_defaults(self):
        """get_field_defaults 方法正确返回所有字段的默认值。"""
        class TestSettings(PluginSettingsBase):
            api_key: str = "default-key"
            enabled: bool = True
            limit: int = 100
            hosts: list[str] = ["localhost", "127.0.0.1"]
            config: dict = {"key": "value"}
            optional: str | None = None
            no_default: str  # 没有默认值的字段

        defaults = TestSettings.get_field_defaults()

        assert defaults["api_key"] == "default-key"
        assert defaults["enabled"] == "True"
        assert defaults["limit"] == "100"
        assert defaults["hosts"] == "['localhost', '127.0.0.1']"
        assert defaults["config"] == "{'key': 'value'}"
        assert defaults["optional"] == ""  # None默认值为空字符串
        # 没有默认值的字段，Field.default是PydanticUndefined，str后是"<class 'pydantic_core._pydantic_core.PydanticUndefined'>"
        # 这种情况在实际使用中不会出现，因为插件配置应该都有默认值

    def test_get_field_defaults_with_field(self):
        """使用Field定义的字段也能正确获取默认值。"""
        class TestSettings(PluginSettingsBase):
            api_key: str = Field(default="default-key", description="API密钥")
            timeout: int = Field(default=30, ge=1, le=300, description="超时时间")

        defaults = TestSettings.get_field_defaults()

        assert defaults["api_key"] == "default-key"
        assert defaults["timeout"] == "30"


class TestCreatePluginSettings:
    """测试动态创建插件配置类函数。"""

    def test_create_plugin_settings_basic(self):
        """动态创建基础配置类。"""
        fields = {
            "api_key": str,
            "enabled": bool,
            "limit": int,
        }
        defaults = {
            "api_key": "default-key",
            "enabled": True,
            "limit": 100,
        }

        SettingsClass = create_plugin_settings("test_plugin", fields, defaults)

        # 类名正确
        assert SettingsClass.__name__ == "TestPluginSettings"
        # 是PluginSettingsBase的子类
        assert issubclass(SettingsClass, PluginSettingsBase)
        # 包含所有字段
        assert "api_key" in SettingsClass.model_fields
        assert "enabled" in SettingsClass.model_fields
        assert "limit" in SettingsClass.model_fields

        # 可以实例化，使用默认值
        settings = SettingsClass()
        assert settings.api_key == "default-key"
        assert settings.enabled is True
        assert settings.limit == 100

        # 可以传入自定义值
        settings = SettingsClass(api_key="custom-key", enabled=False, limit=50)
        assert settings.api_key == "custom-key"
        assert settings.enabled is False
        assert settings.limit == 50

    def test_create_plugin_settings_without_defaults(self):
        """没有提供默认值的情况。"""
        fields = {
            "api_key": str,
            "enabled": bool,
        }

        SettingsClass = create_plugin_settings("test_plugin", fields)

        # 可以实例化，但必须传入所有必填字段
        settings = SettingsClass(api_key="test-key", enabled=True)
        assert settings.api_key == "test-key"
        assert settings.enabled is True

    def test_create_plugin_settings_get_field_defaults(self):
        """动态创建的配置类也能正常使用get_field_defaults方法。"""
        fields = {
            "api_key": str,
            "enabled": bool,
            "limit": int,
            "optional": str | None,
        }
        defaults = {
            "api_key": "default-key",
            "enabled": True,
            "limit": 100,
            "optional": None,
        }

        SettingsClass = create_plugin_settings("test_plugin", fields, defaults)
        defaults_dict = SettingsClass.get_field_defaults()

        assert defaults_dict["api_key"] == "default-key"
        assert defaults_dict["enabled"] == "True"
        assert defaults_dict["limit"] == "100"
        assert defaults_dict["optional"] == ""
