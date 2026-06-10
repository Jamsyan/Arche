from scripts.testgen.scanner.frontend import FuncInfo


def _mock_input(param_name: str, type_hint: str) -> str:
    """根据参数类型生成 mock 输入"""
    t = type_hint.lower()
    if "string" in t or t in ("str", "unknown"):
        if "phone" in param_name:
            return "'13800138000'"
        if "email" in param_name:
            return "'test@example.com'"
        if "url" in param_name:
            return "'https://example.com'"
        if "password" in param_name:
            return "'password123'"
        if "name" in param_name or "slug" in param_name:
            return "'test-input'"
        return "''"
    if "number" in t or t in ("int", "float"):
        return "1"
    if "boolean" in t or t in ("bool",):
        return "true"
    if "date" in t:
        return "new Date()"
    if "any" in t or "unknown" in t:
        return "'test' as any"
    return "'test' as any"


def _expected_assertion(func: FuncInfo) -> tuple[str, str]:
    """根据返回类型生成断言"""
    rt = func.return_type.lower()
    if rt in ("string", "str"):
        return "toBeDefined", "toBeDefined()"
    if rt in ("number", "int", "float"):
        return "toBeGreaterThanOrEqual", "toBeGreaterThanOrEqual(0)"
    if rt in ("boolean", "bool"):
        return "toBe", "toBe(true)"
    if func.return_type == "void" or func.return_type == "None":
        return "toBeDefined", "toBeDefined()"
    return "toBeDefined", "toBeDefined()"


def render(funcs: list[FuncInfo], module_name: str) -> str:
    block_lines = []
    for func in funcs:
        params_str = ", ".join(_mock_input(p.name, p.type_hint) for p in func.params)
        assert_fn, assert_call = _expected_assertion(func)

        desc_part = ""
        if func.params:
            desc_part = " 参数"
        if func.name.startswith("is") or func.name.startswith("has"):
            desc_part += "返回布尔值"

        block_lines.append(f"  describe('{func.name}', () => {{")
        block_lines.append(f"    it('{desc_part.strip() or '基本功能'}', () => {{")
        block_lines.append(f"      const result = {func.name}({params_str})")
        block_lines.append(f"      expect(result).{assert_call}")
        block_lines.append("    })")
        block_lines.append("  })")
        block_lines.append("")

    return (
        "import { describe, it, expect } from 'vitest'\n"
        "\n"
        "// TODO: 自动生成的测试骨架 - 请补充预期的断言值\n"
        "\n" + "\n".join(block_lines)
    )
