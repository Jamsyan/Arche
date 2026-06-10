from ..scanner.frontend import ComposableInfo


def render(info: ComposableInfo, module_name: str) -> str:
    if info is None:
        return f"""\
import {{ describe, it, expect }} from 'vitest'

// TODO: 自动生成 - 未扫描到 Composable，请手动补充
// 文件：{module_name}.ts

describe('{module_name}', () => {{
  it('待补充', () => {{
    expect(true).toBe(true)
  }})
}})
"""

    lines = []
    lines.append("import { describe, it, expect } from 'vitest'")
    lines.append(f"import {{ {info.name} }} from '@/composables/{module_name}'")
    lines.append("")
    lines.append("// TODO: 自动生成的组合式函数测试骨架")
    lines.append("// 需要根据实际返回值类型补充精确断言")
    lines.append("")

    params_str = (
        ", ".join(f"'{p.name}' as any" for p in info.params) if info.params else ""
    )

    lines.append(f"describe('{info.name}', () => {{")

    # 初始状态测试
    if info.params:
        lines.append("  describe('初始状态', () => {")
        lines.append("    it('使用默认参数初始化', () => {")
        lines.append(f"      const result = {info.name}({params_str})")
        for key in info.return_keys:
            lines.append(f"      expect(result.{key}).toBeDefined()")
        lines.append("    })")
        lines.append("  })")
    else:
        lines.append("  it('无参数初始化', () => {")
        lines.append(f"    const result = {info.name}()")
        for key in info.return_keys:
            lines.append(f"    expect(result.{key}).toBeDefined()")
        lines.append("  })")

    lines.append("})")
    lines.append("")

    return "\n".join(lines)
