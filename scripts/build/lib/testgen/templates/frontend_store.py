from ..scanner.frontend import StoreInfo


def render(info: StoreInfo, module_name: str) -> str:
    if info is None:
        return f"""\
import {{ describe, it, expect }} from 'vitest'

// TODO: 自动生成 - 未扫描到 Store，请手动补充
// 文件：{module_name}.ts

describe('{module_name}', () => {{
  it('待补充', () => {{
    expect(true).toBe(true)
  }})
}})
"""

    block_lines = []
    block_lines.append("import { describe, it, expect, vi, beforeEach } from 'vitest'")
    block_lines.append("import { setActivePinia, createPinia } from 'pinia'")
    block_lines.append(
        f"import {{ use{info.store_id[0].upper() + info.store_id[1:]}Store }} from '@/store/modules/{module_name}'"
    )
    block_lines.append("")
    block_lines.append("beforeEach(() => {")
    block_lines.append("  setActivePinia(createPinia())")
    block_lines.append("})")
    block_lines.append("")

    store_name = f"use{info.store_id[0].upper() + info.store_id[1:]}Store"
    store_var = info.store_id + "Store"

    block_lines.append(f"describe('{store_name}', () => {{")

    # 初始状态测试
    if info.state_keys:
        block_lines.append("  describe('初始状态', () => {")
        block_lines.append("    it('所有状态字段默认值正确', () => {")
        block_lines.append(f"      const {store_var} = {store_name}()")
        for key in info.state_keys:
            block_lines.append(f"      expect({store_var}.{key}).toBeDefined()")
        block_lines.append("    })")
        block_lines.append("  })")
        block_lines.append("")

    # Action 测试（带参数的）
    action_blocks = [a for a in info.actions if a.params]
    if action_blocks:
        block_lines.append("  // TODO: 请根据实际 API 签名 mock 依赖")
        for action in action_blocks[:3]:  # 最多生成 3 个 action 测试
            params_str = ", ".join(f"'{p.name}' as any" for p in action.params)
            block_lines.append(f"  describe('{action.name}', () => {{")
            block_lines.append("    it('调用成功', async () => {")
            block_lines.append(f"      const {store_var} = {store_name}()")
            block_lines.append("      // TODO: mock 依赖的 API")
            block_lines.append(
                f"      await expect({store_var}.{action.name}({params_str})).resolves.toBeDefined()"
            )
            block_lines.append("    })")
            block_lines.append("  })")
            block_lines.append("")

    block_lines.append("})")
    block_lines.append("")

    return "\n".join(block_lines)
