"""插件配置基类。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic_settings import BaseSettings


class PluginSettingsBase(BaseModel):
    """所有插件配置的基类。"""

    @classmethod
    def get_field_defaults(cls) -> dict[str, str]:
        """获取所有字段及其默认值，用于生成 .env.example。"""
        result = {}
        for name, field in cls.model_fields.items():
            default = field.default
            if default is None:
                result[name] = ""
            elif isinstance(default, (list, dict, set)):
                result[name] = str(default)
            else:
                result[name] = str(default)
        return result


def create_plugin_settings(
    name: str,
    fields: dict[str, type],
    defaults: dict[str, ...] | None = None,
) -> type["BaseSettings"]:
    """动态创建插件 Settings 类。"""

    class DynamicPluginSettings(PluginSettingsBase):
        pass

    # 设置字段
    for field_name, field_type in fields.items():
        DynamicPluginSettings.model_fields[field_name] = field_type

    DynamicPluginSettings.__name__ = f"{name.title().replace('_', '')}Settings"
    return DynamicPluginSettings
