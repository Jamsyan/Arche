#!/usr/bin/env python3
"""后端组件测试覆盖盘点脚本。

用途：
1) 按文件路径扫描每个后端组件（core + plugins）的源码覆盖情况；
2) 统计对应单元/集成测试文件与测试用例函数数量；
3) 输出终端表格 + Markdown 报告到 docs/coverage-reports/<日期>/。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re


TEST_FUNC_PATTERN = re.compile(
    r"^\s*(?:async\s+)?def\s+test_[A-Za-z0-9_]*\s*\(", re.MULTILINE
)

# 插件目录名与测试文件名前缀的别名映射。
#
# 默认匹配规则是 ``plugin_name in test_file.stem``，但部分插件的测试文件
# 不直接以插件目录名开头（例如 ``cloud_integration`` 的测试文件统一前缀
# 为 ``test_cloud_``）。这里通过别名表显式声明每个插件需要匹配的测试文件
# 前缀（不含 ``test_``），保持脚本输出与实际测试布局一致。
PLUGIN_TEST_PREFIX_ALIASES: dict[str, tuple[str, ...]] = {
    "cloud_integration": ("cloud_integration", "cloud"),
}


# ── 数据结构 ──


@dataclass
class FileCoverageDetail:
    """单个源码文件的覆盖详情。"""

    source_rel_path: str  # 相对于 backend/ 的路径
    match_unit_files: list[str] = field(default_factory=list)
    match_int_files: list[str] = field(default_factory=list)
    unit_case_count: int = 0
    int_case_count: int = 0

    @property
    def covered(self) -> bool:
        return self.unit_case_count + self.int_case_count > 0

    @property
    def total_cases(self) -> int:
        return self.unit_case_count + self.int_case_count


@dataclass
class ComponentStats:
    """单个组件的测试覆盖统计（汇总 + 文件明细）。"""

    name: str
    source_count: int
    unit_file_count: int
    int_file_count: int
    unit_case_count: int
    int_case_count: int
    file_details: list[FileCoverageDetail] = field(default_factory=list)

    @property
    def total_test_files(self) -> int:
        return self.unit_file_count + self.int_file_count

    @property
    def total_test_cases(self) -> int:
        return self.unit_case_count + self.int_case_count

    @property
    def covered(self) -> bool:
        return self.total_test_cases > 0

    @property
    def covered_file_count(self) -> int:
        return sum(1 for f in self.file_details if f.covered)


# ── 辅助函数 ──


def _count_test_functions(test_file: Path) -> int:
    content = test_file.read_text(encoding="utf-8")
    return len(TEST_FUNC_PATTERN.findall(content))


def _component_source_files(component_dir: Path) -> list[Path]:
    """返回组件目录下所有非 __init__.py 的源码文件。"""
    return sorted(
        path for path in component_dir.rglob("*.py")
        if path.is_file() and path.name != "__init__.py"
    )


def _plugin_test_files(
    tests_root: Path, plugin_name: str, test_type: str
) -> list[Path]:
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
            stem = test_file.stem
            for alias in aliases:
                if stem == f"test_{alias}" or stem.startswith(f"test_{alias}_"):
                    files.add(test_file)
                    break
    else:
        for test_file in candidates:
            if plugin_name in test_file.stem:
                files.add(test_file)

    return sorted(files)


def _match_source_to_tests(
    source_stem: str,
    plugin_name: str,
    unit_files: list[Path],
    int_files: list[Path],
) -> tuple[list[Path], list[Path], int, int]:
    """将单个源文件与测试文件做名称匹配。

    两轮匹配：
    1. 精确匹配：测试文件去掉 ``test_`` 前缀后，包含源文件名称。
       例如 ``test_crawler_services.py`` 匹配 ``services.py``。
    2. 兜底匹配：若精确匹配无结果，将包含插件名的测试文件作为通配匹配，
       覆盖 ``test_<plugin>.py`` 这类单文件覆盖整个插件的情况。
    """
    matched_unit, matched_int = _exact_match_tests(source_stem, unit_files, int_files)

    # 精确匹配无结果时，尝试将插件级通用测试文件计入
    if not matched_unit and not matched_int:
        matched_unit, matched_int = _fallback_plugin_match(
            plugin_name, unit_files, int_files
        )

    unit_cases = sum(_count_test_functions(f) for f in matched_unit)
    int_cases = sum(_count_test_functions(f) for f in matched_int)

    return matched_unit, matched_int, unit_cases, int_cases


def _exact_match_tests(
    source_stem: str,
    unit_files: list[Path],
    int_files: list[Path],
) -> tuple[list[Path], list[Path]]:
    """精确匹配：测试文件名称中包含源文件名称。"""
    matched_unit: list[Path] = []
    matched_int: list[Path] = []

    for tf in unit_files:
        tf_name = tf.stem.removeprefix("test_")
        if source_stem in tf_name:
            matched_unit.append(tf)

    for tf in int_files:
        tf_name = tf.stem.removeprefix("test_")
        if source_stem in tf_name:
            matched_int.append(tf)

    return matched_unit, matched_int


def _fallback_plugin_match(
    plugin_name: str,
    unit_files: list[Path],
    int_files: list[Path],
) -> tuple[list[Path], list[Path]]:
    """兜底匹配：将包含插件名的测试文件作为通用测试计入。"""
    matched_unit: list[Path] = []
    matched_int: list[Path] = []

    for tf in unit_files:
        tf_name = tf.stem.removeprefix("test_")
        if plugin_name in tf_name or tf_name == plugin_name:
            matched_unit.append(tf)

    for tf in int_files:
        tf_name = tf.stem.removeprefix("test_")
        if plugin_name in tf_name or tf_name == plugin_name:
            matched_int.append(tf)

    return matched_unit, matched_int


# ── 核心扫描 ──


def build_inventory(repo_root: Path) -> list[ComponentStats]:
    """扫描所有组件，返回包含文件级明细的覆盖统计。"""
    backend_root = repo_root / "backend"
    tests_root = backend_root / "tests"
    plugins_root = backend_root / "plugins"

    inventory: list[ComponentStats] = []

    # ── core 组件 ──
    core_source = _component_source_files(backend_root / "core")
    core_unit_files = sorted((tests_root / "unit" / "core").glob("test_*.py"))
    core_int_files: list[Path] = []

    core_details: list[FileCoverageDetail] = []
    for sf in core_source:
        rel = sf.relative_to(backend_root).as_posix()
        mu, mi, uc, ic = _match_source_to_tests(
            sf.stem, "core", core_unit_files, core_int_files
        )
        core_details.append(FileCoverageDetail(
            source_rel_path=rel,
            match_unit_files=[f.name for f in mu],
            match_int_files=[f.name for f in mi],
            unit_case_count=uc,
            int_case_count=ic,
        ))

    inventory.append(ComponentStats(
        name="core",
        source_count=len(core_source),
        unit_file_count=len(core_unit_files),
        int_file_count=len(core_int_files),
        unit_case_count=sum(_count_test_functions(f) for f in core_unit_files),
        int_case_count=0,
        file_details=core_details,
    ))

    # ── 插件组件 ──
    for plugin_dir in sorted(
        path for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    ):
        plugin_name = plugin_dir.name
        source_files = _component_source_files(plugin_dir)
        unit_files = _plugin_test_files(tests_root, plugin_name, "unit")
        int_files = _plugin_test_files(tests_root, plugin_name, "integration")

        details: list[FileCoverageDetail] = []
        for sf in source_files:
            rel = sf.relative_to(backend_root).as_posix()
            mu, mi, uc, ic = _match_source_to_tests(sf.stem, plugin_name, unit_files, int_files)
            details.append(FileCoverageDetail(
                source_rel_path=rel,
                match_unit_files=[f.name for f in mu],
                match_int_files=[f.name for f in mi],
                unit_case_count=uc,
                int_case_count=ic,
            ))

        inventory.append(ComponentStats(
            name=plugin_name,
            source_count=len(source_files),
            unit_file_count=len(unit_files),
            int_file_count=len(int_files),
            unit_case_count=sum(_count_test_functions(f) for f in unit_files),
            int_case_count=sum(_count_test_functions(f) for f in int_files),
            file_details=details,
        ))

    return inventory


# ── 终端输出 ──


def print_terminal_report(inventory: list[ComponentStats]) -> None:
    """打印组件级汇总表格到终端。"""
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
            f"{item.source_count:>8}"
            f"{item.unit_file_count:>11}"
            f"{item.int_file_count:>10}"
            f"{item.unit_case_count:>11}"
            f"{item.int_case_count:>10}"
            f"{status:>10}"
        )

    covered = sum(1 for item in inventory if item.covered)
    total = len(inventory)
    coverage_ratio = (covered / total * 100) if total else 0.0
    print()
    print(f"Components covered: {covered}/{total} ({coverage_ratio:.1f}%)")


# ── Markdown 报告 ──


def generate_markdown_report(inventory: list[ComponentStats]) -> str:
    """生成完整的 Markdown 覆盖报告。"""
    now = datetime.now()
    lines: list[str] = []

    # 标题
    lines.append("# 测试覆盖报告\n")
    lines.append(f"生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ── 概览表 ──
    lines.append("## 概览\n")
    header = "| 组件 | 源文件数 | 已覆盖文件 | 测试文件数 | 测试用例数 | 状态 |"
    sep = "|------|---------|-----------|-----------|-----------|------|"
    lines.append(header)
    lines.append(sep)

    covered_components = 0
    total_source = 0
    total_covered_files = 0
    total_test_files = 0
    total_cases = 0

    for item in inventory:
        status_icon = "✅" if item.covered else "❌"
        lines.append(
            f"| {item.name} "
            f"| {item.source_count} "
            f"| {item.covered_file_count}/{item.source_count} "
            f"| {item.total_test_files} "
            f"| {item.total_test_cases} "
            f"| {status_icon} |"
        )
        if item.covered:
            covered_components += 1
        total_source += item.source_count
        total_covered_files += item.covered_file_count
        total_test_files += item.total_test_files
        total_cases += item.total_test_cases

    lines.append("")
    lines.append(
        f"- **组件覆盖率**：{covered_components}/{len(inventory)} "
        f"({covered_components / len(inventory) * 100:.1f}%)"
    )
    lines.append(
        f"- **文件覆盖率**：{total_covered_files}/{total_source} "
        f"({total_covered_files / total_source * 100:.1f}%)"
    )
    lines.append(f"- **测试用例总数**：{total_cases}")
    lines.append("")

    # ── 详细文件清单 ──
    lines.append("## 详细文件清单\n")

    for item in inventory:
        status_icon = "✅" if item.covered else "❌"
        lines.append(f"### {item.name} {status_icon}\n")
        lines.append(
            f"源文件 {item.source_count} 个，测试文件 {item.total_test_files} 个，"
            f"测试用例 {item.total_test_cases} 个\n"
        )

        # 文件级表格
        tbl_header = "| 源文件 | 单元测试 | 集成测试 | 用例数 | 状态 |"
        tbl_sep = "|--------|---------|---------|-------|------|"
        lines.append(tbl_header)
        lines.append(tbl_sep)

        for fd in item.file_details:
            unit_str = ", ".join(fd.match_unit_files) if fd.match_unit_files else "-"
            int_str = ", ".join(fd.match_int_files) if fd.match_int_files else "-"
            file_status = "✅" if fd.covered else "❌"
            lines.append(
                f"| `{fd.source_rel_path}` "
                f"| {unit_str} "
                f"| {int_str} "
                f"| {fd.total_cases} "
                f"| {file_status} |"
            )
        lines.append("")

    return "\n".join(lines)


def save_report(report: str, repo_root: Path) -> Path:
    """将 Markdown 报告写入 docs/coverage-reports/coverage-report-<日期>.md。"""
    now = datetime.now()
    report_dir = repo_root / "docs" / "coverage-reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    filename = f"coverage-report-{now.strftime('%Y-%m-%d')}.md"
    output_path = report_dir / filename
    output_path.write_text(report, encoding="utf-8")
    return output_path


# ── 入口 ──


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    inventory = build_inventory(repo_root)

    # 终端输出
    print_terminal_report(inventory)

    # Markdown 报告
    report = generate_markdown_report(inventory)
    path = save_report(report, repo_root)
    print(f"\nMarkdown 报告已生成：{path}")


if __name__ == "__main__":
    main()
