from scripts.testgen.scanner.frontend import ApiEndpoint


def _mock_value_for_type(type_hint: str) -> str:
    if type_hint in ("void", "None"):
        return ""
    return "{} as any"


def _mock_return_for_endpoint(ep: ApiEndpoint) -> str:
    """根据端点特征生成合理的 mock 返回值"""
    if ep.return_type in ("void", "None") or ep.method in ("del",):
        return "undefined"
    if "string" in ep.return_type.lower() or ep.return_type == "string":
        return "'mock-string'"
    if "boolean" in ep.return_type.lower() or ep.return_type == "boolean":
        return "true"
    if "number" in ep.return_type.lower() or ep.return_type == "number":
        return "1"
    if "[]" in ep.return_type or ep.return_type.endswith("[]"):
        return "[]"
    if ep.is_paginated:
        return "{ items: [], total: 0, page: 1, page_size: 20, list: [] }"
    if "Record<string," in ep.return_type:
        return "{}"
    if ep.return_type and ep.return_type != "any":
        return f"{{}} as {ep.return_type}"
    return "{}"


def _http_method_call(ep: ApiEndpoint) -> str:
    """生成正确的 HTTP 方法调用"""
    if ep.method in ("get", "del"):
        return f"{ep.method}<{ep.return_type}>({ep.url!r}, params, undefined)"
    return f"{ep.method}<{ep.return_type}>({ep.url!r}, params, undefined)"


_TEMPLATE = """\
import {{ describe, it, expect, vi, beforeEach }} from 'vitest'

vi.mock('@/services/request', () => ({{
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  del: vi.fn(),
  upload: vi.fn(),
}}))

beforeEach(() => {{
  vi.clearAllMocks()
}})

{describe_blocks}
"""

_DESCRIBE_BLOCK = """\
describe('{api_name}', () => {{
  it('发送正确 URL{params_desc}', async () => {{
    const {{ {api_name} }} = await import('./{module_path}')
    const {{ {http_method} }} = await import('@/services/request')
    vi.mocked({http_method}).mockResolvedValue({mock_return})
    {params_setup}
    await {api_name}({call_args})
    expect({http_method}).toHaveBeenCalledWith({url_repr}, {params_repr}, undefined)
  }})

  it('处理错误响应', async () => {{
    const {{ {api_name} }} = await import('./{module_path}')
    const {{ {http_method} }} = await import('@/services/request')
    vi.mocked({http_method}).mockRejectedValue(new Error('network error'))
    await expect({api_name}({error_call_args})).rejects.toThrow('network error')
  }})
}})
"""

_SIMPLE_DESCRIBE_BLOCK = """\
describe('{api_name}', () => {{
  it('发送正确 URL{params_desc}', async () => {{
    const {{ {api_name} }} = await import('./{module_path}')
    const {{ {http_method} }} = await import('@/services/request')
    vi.mocked({http_method}).mockResolvedValue({mock_return})
    await {api_name}({call_args})
    expect({http_method}).toHaveBeenCalledWith({url_repr}, undefined, undefined)
  }})
}})
"""


def render(apis: list[ApiEndpoint], module_name: str) -> str:
    if not apis:
        return _generate_fallback(module_name)

    # 按 HTTP 方法分组以识别 get/delete 与 post/put
    blocks = []
    for ep in apis:
        params_desc = ""
        params_setup = ""
        call_args = ""
        error_call_args = ""

        if ep.url_params:
            params_desc = " 和路径参数"
            path_args = ", ".join(ep.url_params)
            call_args = path_args
            error_call_args = path_args
            params_setup = f"    vi.mocked({ep.method}).mockResolvedValue({_mock_return_for_endpoint(ep)})"
        elif ep.method in ("get", "del"):
            call_args = "{ page: 1, page_size: 20 }"
            error_call_args = "{ page: 1 }"
            params_desc = " 和参数"
            params_setup = f"    vi.mocked({ep.method}).mockResolvedValue({_mock_return_for_endpoint(ep)})"
        else:
            call_args = "{ /* TODO: fill payload */ } as any"
            error_call_args = "{ /* TODO: fill payload */ } as any"
            params_desc = " 和 payload"
            params_setup = f"    vi.mocked({ep.method}).mockResolvedValue({_mock_return_for_endpoint(ep)})"

        if ep.url_params:
            block = _SIMPLE_DESCRIBE_BLOCK.format(
                api_name=ep.name,
                params_desc=params_desc,
                module_path=module_name,
                http_method=ep.method,
                mock_return=_mock_return_for_endpoint(ep),
                params_setup=params_setup,
                call_args=call_args,
                url_repr=repr(ep.url),
                params_repr="undefined",
                error_call_args=error_call_args,
            )
        else:
            block = _TEMPLATE_BLOCK.format(
                api_name=ep.name,
                params_desc=params_desc,
                module_path=module_name,
                http_method=ep.method,
                mock_return=_mock_return_for_endpoint(ep),
                params_setup=params_setup,
                call_args=call_args,
                url_repr=repr(ep.url),
                error_call_args=error_call_args,
            )
        blocks.append(block)

    return (
        "import { describe, it, expect, vi, beforeEach } from 'vitest'\n"
        "\n"
        "vi.mock('@/services/request', () => ({\n"
        "  get: vi.fn(),\n"
        "  post: vi.fn(),\n"
        "  put: vi.fn(),\n"
        "  del: vi.fn(),\n"
        "  upload: vi.fn(),\n"
        "}))\n"
        "\n"
        "beforeEach(() => {\n"
        "  vi.clearAllMocks()\n"
        "})\n"
        "\n" + "\n".join(blocks)
    )


_TEMPLATE_BLOCK = """\
describe('{api_name}', () => {{
  it('发送正确 URL{params_desc}', async () => {{
    const {{ {api_name} }} = await import('./{module_path}')
    const {{ {http_method} }} = await import('@/services/request')
    {params_setup}
    await {api_name}({call_args})
    expect({http_method}).toHaveBeenCalledWith({url_repr}, {error_call_args})
  }})

  it('处理错误响应', async () => {{
    const {{ {api_name} }} = await import('./{module_path}')
    const {{ {http_method} }} = await import('@/services/request')
    vi.mocked({http_method}).mockRejectedValue(new Error('network error'))
    await expect({api_name}({error_call_args})).rejects.toThrow('network error')
  }})
}})
"""


def _generate_fallback(module_name: str) -> str:
    return f"""\
import {{ describe, it, expect }} from 'vitest'

// TODO: 自动生成 - 未扫描到 API 端点，请手动补充
// 文件：{module_name}.ts

describe('{module_name} API', () => {{
  it('待补充', () => {{
    expect(true).toBe(true)
  }})
}})
"""
