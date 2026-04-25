#!/usr/bin/env python3
"""
自定义代码规范检查

检查规则：
1. lambda 禁止（DI 容器工厂模式除外）
2. 嵌套列表推导式禁止（超过 1 层）
"""

import ast
import sys
from pathlib import Path


class LambdaAndComprehensionVisitor(ast.NodeVisitor):
    """检测 lambda 表达式和嵌套推导式"""

    def __init__(self, filepath: str, source: str):
        self.filepath = filepath
        self._file_source = source
        self.errors: list[dict] = []
        self._comp_depth = 0  # 推导式嵌套深度

    # ── 嵌套推导式检测 ──────────────────────────────────────

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._check_comp_depth(node, "list")
        super().generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._check_comp_depth(node, "set")
        super().generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._check_comp_depth(node, "generator")
        super().generic_visit(node)

    def _check_comp_depth(
        self, node: ast.ListComp | ast.SetComp | ast.GeneratorExp, kind: str
    ) -> None:
        depth = self._calc_depth(node)
        if depth > 1:
            line = node.elt.lineno if hasattr(node, "elt") and node.elt else node.lineno
            self.errors.append(
                {
                    "file": self.filepath,
                    "line": line,
                    "kind": "nested-comprehension",
                    "msg": f"[{kind} comprehension] 嵌套超过 1 层（depth={depth}），请拆解为普通循环",
                }
            )

    def _calc_depth(self, node: ast.ListComp | ast.SetComp | ast.GeneratorExp) -> int:
        """计算推导式嵌套深度"""
        max_depth = 1
        for elt in node.generators:
            inner = self._inner_comp_depth(elt.iter)
            max_depth = max(max_depth, inner)
        return max_depth

    def _inner_comp_depth(self, node: ast.AST) -> int:
        """计算迭代器节点的嵌套深度"""
        if isinstance(node, ast.ListComp):
            return 1 + self._calc_depth(node)
        if isinstance(node, ast.SetComp):
            return 1 + self._calc_depth(node)
        if isinstance(node, ast.GeneratorExp):
            return 1 + self._calc_depth(node)
        return 0

    # ── Lambda 检测 ──────────────────────────────────────────

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # 白名单：SQLAlchemy Column default（形如 default=lambda: expr）
        # 特征：lambda 无参数，body 是单个表达式
        is_sqlalchemy_default = len(node.args.args) == 0 and isinstance(
            node.body, ast.expr
        )

        # 白名单：iter() 的 sentinel 模式，iter(lambda: f.read(N), sentinel)
        # 特征：父节点是 Call，func 是 Name(id='iter')
        is_iter_sentinel = self._is_iter_sentinel(node)

        # 白名单：DI 容器工厂，lambda c: Something(c)
        # 特征：单参数 + body 是 Call + 参数出现在实参中
        is_di_factory = False
        if len(node.args.args) == 1 and isinstance(node.body, ast.Call):
            arg_name = node.args.args[0].arg
            for arg in node.body.args:
                if isinstance(arg, ast.Name) and arg.id == arg_name:
                    is_di_factory = True
                    break
            if not is_di_factory:
                for kw in node.body.keywords:
                    if isinstance(kw.value, ast.Name) and kw.value.id == arg_name:
                        is_di_factory = True
                        break

        if not (is_sqlalchemy_default or is_iter_sentinel or is_di_factory):
            self.errors.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "kind": "lambda",
                    "msg": f"[lambda] line {node.lineno}: lambda detected, use a named function instead",
                }
            )
        self.generic_visit(node)

    def _is_iter_sentinel(self, node: ast.Lambda) -> bool:
        """通过源码上下文判断 lambda 是否在 iter() sentinel 模式中"""
        # sentinel 模式: iter(lambda: <call>, <sentinel>)
        # 特征: lambda 无参数，body 是 Call 表达式
        if len(node.args.args) != 0:
            return False
        if not isinstance(node.body, ast.Call):
            return False
        # 通过源码行首查找 iter( 往回判断（粗略但有效）
        source = self._file_source
        line_start = node.lineno - 1
        line_end = node.lineno
        lines_around = "\n".join(source.splitlines()[max(0, line_start - 2) : line_end])
        return "iter(" in lines_around and "lambda" in lines_around


def check_file(filepath: Path) -> list[dict]:
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return [
            {
                "file": str(filepath),
                "line": e.lineno or 0,
                "kind": "syntax-error",
                "msg": f"syntax error: {e.msg}",
            }
        ]
    visitor = LambdaAndComprehensionVisitor(str(filepath), source)
    visitor.visit(tree)
    return visitor.errors


def check_paths(paths: list[Path]) -> list[dict]:
    all_errors: list[dict] = []
    py_files = [p for p in paths if p.is_file() and p.suffix == ".py"]
    for p in py_files:
        all_errors.extend(check_file(p))
    return all_errors


def print_report(errors: list[dict]) -> None:
    if not errors:
        print("[PASS] Custom lint rules passed")
        return
    print(f"[FAIL] Found {len(errors)} violation(s):\n")
    errors.sort(key=lambda e: (e["file"], e["line"]))
    for e in errors:
        print(f"  {e['file']}:{e['line']}  {e['msg']}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="自定义代码规范检查")
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="要检查的文件或目录",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="有违规时以非零退出码退出（CI 用）",
    )
    args = parser.parse_args()

    paths: list[Path] = []
    for p in args.paths:
        if p.is_dir():
            paths.extend(p.rglob("*.py"))
        else:
            paths.append(p)

    errors = check_paths(paths)
    print_report(errors)

    if args.fail and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
