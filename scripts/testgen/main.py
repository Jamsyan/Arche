import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="testgen",
    help="基于代码扫描的测试代码生成器",
    no_args_is_help=True,
)


@app.callback()
def callback():
    pass


@app.command("gen")
def generate(
    source: str = typer.Argument(
        ..., help="源文件路径，如 frontend/src/services/api/blog.ts"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="输出路径，默认自动推断"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="仅输出生成的代码，不写入文件"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="覆盖已存在的测试文件"),
):
    """根据源码文件自动生成测试代码"""
    source_path = Path(source).resolve()

    if not source_path.exists():
        typer.echo(f"错误：文件不存在 - {source_path}", err=True)
        raise typer.Exit(code=1)

    from scripts.testgen.orchestrator import detect_type, generate_test

    file_type = detect_type(source_path)
    typer.echo(f"检测到文件类型：{file_type}")

    result = generate_test(source_path, file_type)

    if dry_run:
        typer.echo("=" * 60)
        typer.echo(f"生成路径：{result.output_path}")
        typer.echo("=" * 60)
        typer.echo(result.content)
        return

    output_path = Path(output) if output else result.output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force:
        typer.echo(f"文件已存在：{output_path} （使用 --force 覆盖）", err=True)
        raise typer.Exit(code=1)

    output_path.write_text(result.content, encoding="utf-8")
    typer.echo(f"测试文件已生成：{output_path}")


@app.command("batch")
def batch_generate(
    directory: str = typer.Argument(
        ..., help="源码目录，如 frontend/src/services/api/"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output-dir", "-o", help="输出目录"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="仅预览"),
    force: bool = typer.Option(False, "--force", "-f", help="覆盖已有文件"),
):
    """批量生成整个目录的测试代码"""
    dir_path = Path(directory).resolve()
    if not dir_path.is_dir():
        typer.echo(f"错误：目录不存在 - {dir_path}", err=True)
        raise typer.Exit(code=1)

    from scripts.testgen.orchestrator import (
        SUPPORTED_PATTERNS,
        detect_type,
        generate_test,
    )

    matched = []
    for pattern in SUPPORTED_PATTERNS.values():
        for f in dir_path.rglob(pattern):
            file_type = detect_type(f)
            if file_type:
                matched.append((f, file_type))

    if not matched:
        typer.echo("未找到可生成测试的源码文件")
        return

    typer.echo(f"找到 {len(matched)} 个可处理的文件")
    for source_path, file_type in matched:
        rel = source_path.relative_to(Path.cwd())
        typer.echo(f"  [{file_type}] {rel}")
        result = generate_test(source_path, file_type)

        if dry_run:
            typer.echo(f"  → {result.output_path}")
            continue

        output_path = (
            Path(output_dir) / result.output_path.name
            if output_dir
            else result.output_path
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists() and not force:
            typer.echo(f"  跳过（已存在）：{output_path.name}")
            continue

        output_path.write_text(result.content, encoding="utf-8")
        typer.echo(f"  已生成：{output_path}")

    typer.echo("批量生成完成！")


@app.command("list-templates")
def list_templates():
    """列出支持的文件类型和对应的模板"""
    from scripts.testgen.orchestrator import SUPPORTED_PATTERNS, FILE_TYPE_LABELS

    typer.echo("支持的文件类型：")
    for type_id, pattern in SUPPORTED_PATTERNS.items():
        label = FILE_TYPE_LABELS.get(type_id, type_id)
        typer.echo(f"  {type_id:20s} {label}")
        typer.echo(f"    {'匹配模式:':12s} {pattern}")
        typer.echo()
