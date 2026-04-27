"""后端组件测试覆盖盘点脚本。

用途：
1) 统计每个后端组件（core + plugins）的源码文件数；
2) 统计对应单元/集成测试文件与测试用例函数数量；
3) 输出命令行表格，快速识别未覆盖组件。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


TEST_FUNC_PATTERN = re.compile(r"^\s*(?:async\s+)?def\s+test_[A-Za-z0-9_]*\s*\(", re.MULTILINE)


# 插件目录名与测试文件名前缀的别名映射。
#
# 默认匹配规则是 ``plugin_name in test_file.stem``，但部分插件的测试文件
# 不直接以插件目录名开头（例如 ``cloud_integration`` 的测试文件统一前缀
# 为 ``test_cloud_``）。这里通过别名表显式声明每个插件需要匹配的测试文件
# 前缀（不含 ``test_``），保持脚本输出与实际测试布局一致。
PLUGIN_TEST_PREFIX_ALIASES: dict[str, tuple[str, ...]] = {
    "cloud_integration": ("cloud_integration", "cloud"),
}


@dataclass
class ComponentStats:
    """单个组件的测试覆盖统计。"""

    name: str
    source_files: int
    unit_files: int
    integration_files: int
    unit_cases: int
    integration_cases: int

    @property
    def total_test_files(self) -> int:
        return self.unit_files + self.integration_files

    @property
    def total_test_cases(self) -> int:
        return self.unit_cases + self.integration_cases

    @property
    def covered(self) -> bool:
        return self.total_test_cases > 0


def _count_test_functions(test_file: Path) -> int:
    content = test_file.read_text(encoding="utf-8")
    return len(TEST_FUNC_PATTERN.findall(content))


def _component_source_count(component_dir: Path) -> int:
    return sum(
        1
        for path in component_dir.rglob("*.py")
        if path.is_file() and path.name != "__init__.py"
    )


def _plugin_test_files(tests_root: Path, plugin_name: str, test_type: str) -> list[Path]:
    """基于插件名与别名表收集测试文件，避免命名前缀漂移导致漏匹配。

    匹配规则：
    1. 默认按插件目录名作为子串匹配；
    2. 若 ``PLUGIN_TEST_PREFIX_ALIASES`` 存在该插件，则改用别名（按
       ``test_<alias>_*.py`` 前缀匹配，命中即认为属于该插件，避免子串
       误伤其它插件的测试文件）。
    """
    files: set[Path] = set()
    aliases = PLUGIN_TEST_PREFIX_ALIASES.get(plugin_name)
    candidates = list((tests_root / test_type).rglob("test_*.py"))

    if aliases:
        for test_file in candidates:
            stem = test_file.stem  # e.g. test_cloud_orchestrator
            for alias in aliases:
                if stem == f"test_{alias}" or stem.startswith(f"test_{alias}_"):
                    files.add(test_file)
                    break
    else:
        for test_file in candidates:
            if plugin_name in test_file.stem:
                files.add(test_file)

    return sorted(files)


def build_inventory(repo_root: Path) -> list[ComponentStats]:
    backend_root = repo_root / "backend"
    tests_root = backend_root / "tests"
    plugins_root = backend_root / "plugins"

    inventory: list[ComponentStats] = []

    # core 组件单独处理
    core_source_files = _component_source_count(backend_root / "core")
    core_unit_files = sorted((tests_root / "unit" / "core").glob("test_*.py"))
    core_integration_files: list[Path] = []
    inventory.append(
        ComponentStats(
            name="core",
            source_files=core_source_files,
            unit_files=len(core_unit_files),
            integration_files=len(core_integration_files),
            unit_cases=sum(_count_test_functions(path) for path in core_unit_files),
            integration_cases=0,
        )
    )

    # 插件组件
    for plugin_dir in sorted(
        path
        for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    ):
        plugin_name = plugin_dir.name
        source_files = _component_source_count(plugin_dir)
        unit_files = _plugin_test_files(tests_root, plugin_name, "unit")
        integration_files = _plugin_test_files(tests_root, plugin_name, "integration")
        inventory.append(
            ComponentStats(
                name=plugin_name,
                source_files=source_files,
                unit_files=len(unit_files),
                integration_files=len(integration_files),
                unit_cases=sum(_count_test_functions(path) for path in unit_files),
                integration_cases=sum(_count_test_functions(path) for path in integration_files),
            )
        )

    return inventory


def _print_inventory_table(inventory: list[ComponentStats]) -> None:
    header = (
        f"{'Component':<22}"
        f"{'Source':>8}"
        f"{'UnitFiles':>11}"
        f"{'IntFiles':>10}"
        f"{'UnitCases':>11}"
        f"{'IntCases':>10}"
        f"{'Status':>10}"
    )
    print(header)
    print("-" * len(header))

    for item in inventory:
        status = "COVERED" if item.covered else "EMPTY"
        print(
            f"{item.name:<22}"
            f"{item.source_files:>8}"
            f"{item.unit_files:>11}"
            f"{item.integration_files:>10}"
            f"{item.unit_cases:>11}"
            f"{item.integration_cases:>10}"
            f"{status:>10}"
        )

    covered = sum(1 for item in inventory if item.covered)
    total = len(inventory)
    coverage_ratio = (covered / total * 100) if total else 0.0
    print()
    print(f"Components covered: {covered}/{total} ({coverage_ratio:.1f}%)")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    inventory = build_inventory(repo_root)
    _print_inventory_table(inventory)


if __name__ == "__main__":
    main()
