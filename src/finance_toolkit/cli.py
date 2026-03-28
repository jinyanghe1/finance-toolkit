"""Finance Toolkit CLI."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Optional

import click
import yaml

from .__version__ import __title__, __version__
from .config import get_config
from .analyzer.company import CompanyAnalyzer


def _format_payload(payload: dict[str, Any], output_format: str) -> str:
    """Format a payload for stdout or file output."""
    if output_format == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)

    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def _emit_payload(payload: dict[str, Any], output_format: str) -> None:
    """Emit a payload in the requested format."""
    click.echo(_format_payload(payload, output_format), nl=False)


def _load_codes_from_input(input_path: Path, code_column: str) -> list[str]:
    """Load stock codes from a plain text file or CSV."""
    if input_path.suffix.lower() == ".csv":
        with input_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if code_column not in fieldnames:
                raise click.ClickException(f"CSV 文件缺少代码列: {code_column}")

            return [
                row[code_column].strip()
                for row in reader
                if row.get(code_column, "").strip()
            ]

    return [
        line.strip()
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _write_payload(payload: dict[str, Any], output_format: str, output_path: Path) -> None:
    """Write a formatted payload to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_format_payload(payload, output_format), encoding="utf-8")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="ftk")
def main() -> None:
    """Finance Toolkit CLI."""


@main.command("version")
def version_command() -> None:
    """Show the installed version."""
    click.echo(f"{__title__} {__version__}")


@main.group("config")
def config_group() -> None:
    """Inspect runtime configuration."""


@config_group.command("show")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    show_default=True,
)
def show_config(output_format: str) -> None:
    """Show the configured values."""
    config = get_config()
    _emit_payload(config.to_dict(), output_format.lower())


@config_group.command("paths")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    show_default=True,
)
def show_paths(output_format: str) -> None:
    """Show resolved filesystem paths after env overrides."""
    config = get_config()
    payload = {
        "root": str(config.data.root),
        "company": str(config.data.company),
        "exports": str(config.data.exports),
    }
    _emit_payload(payload, output_format.lower())


@main.command("list")
@click.option("--format", "-f", "fmt", type=click.Choice(["table", "json", "yaml"]),
              default="table", help="输出格式")
def list_companies(fmt: str):
    """列出所有已存储的公司"""
    analyzer = CompanyAnalyzer()
    companies = analyzer.list_all_companies()
    
    if not companies:
        click.echo("暂无公司数据")
        return
    
    if fmt == "json":
        click.echo(json.dumps(companies, ensure_ascii=False, indent=2))
    elif fmt == "yaml":
        click.echo(yaml.safe_dump(companies, allow_unicode=True))
    else:
        click.echo(f"\n{'代码':<12} {'名称':<20} {'行业':<12} {'市值(亿)':>10}")
        click.echo("-" * 60)
        for c in companies:
            market_cap = f"{c.get('market_cap', 'N/A'):,.0f}" if c.get('market_cap') else 'N/A'
            click.echo(f"{c['code']:<12} {c['name']:<20} {c['industry']:<12} {market_cap:>10}")
        click.echo(f"\n共 {len(companies)} 家公司\n")


@main.command("analyze")
@click.argument("code")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
@click.option("--format", "-f", "fmt", type=click.Choice(["md", "txt"]),
              default="md", help="输出格式")
def analyze_company(code: str, output: Optional[str], fmt: str):
    """分析指定公司"""
    try:
        analyzer = CompanyAnalyzer()
        report = analyzer.generate_report(code)
        
        if output:
            filepath = Path(output)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
            click.echo(f"✅ 报告已保存到: {filepath}")
        else:
            click.echo(report)
    
    except Exception as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)


@main.group("batch")
def batch_group() -> None:
    """批量处理多家公司。"""


@batch_group.command("analyze")
@click.argument("codes", nargs=-1, required=False)
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="输入文件，支持 txt(每行一个代码) 或 csv。",
)
@click.option(
    "--code-column",
    default="code",
    show_default=True,
    help="CSV 文件中的股票代码列名。",
)
@click.option(
    "--skip-errors/--fail-fast",
    default=True,
    show_default=True,
    help="遇到错误时继续处理，或在首个错误时立即失败。",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    default="json",
    show_default=True,
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="将结果写入文件；默认输出到终端。",
)
def batch_analyze_command(
    codes: tuple[str, ...],
    input_path: Optional[Path],
    code_column: str,
    skip_errors: bool,
    output_format: str,
    output_path: Optional[Path],
) -> None:
    """批量分析多家公司并输出结构化结果。"""
    all_codes = [code.strip() for code in codes if code.strip()]

    if input_path is not None:
        all_codes.extend(_load_codes_from_input(input_path, code_column))

    if not all_codes:
        raise click.ClickException("请提供股票代码参数，或通过 --input 指定输入文件。")

    analyzer = CompanyAnalyzer()
    results = analyzer.analyze_batch(all_codes, skip_errors=skip_errors)

    success_count = sum(1 for item in results.values() if item["success"])
    failed_count = len(results) - success_count
    payload = {
        "input": {
            "requested": len(all_codes),
            "unique": len(results),
            "input_file": str(input_path) if input_path else None,
        },
        "results": results,
        "summary": {
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": round(success_count / len(results), 4) if results else 0.0,
        },
    }

    normalized_format = output_format.lower()
    if output_path is not None:
        _write_payload(payload, normalized_format, output_path)
        click.echo(f"已写入: {output_path}")
        return

    _emit_payload(payload, normalized_format)


@main.command("chart")
@click.argument("code")
@click.option("--type", "-t", "chart_type",
              type=click.Choice(["trend", "radar", "dupont"]),
              default="trend", help="图表类型")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径 (PNG)")
@click.option("--metric", "-m", default="roe", help="指标名称，逗号分隔 (用于趋势图)")
@click.option("--no-show", is_flag=True, help="不显示图表，仅保存")
def generate_chart(code: str, chart_type: str, output: Optional[str], 
                   metric: str, no_show: bool):
    """生成财务图表"""
    try:
        from .report.charts import ChartGenerator
        from .data.db import get_company_db
        
        db = get_company_db()
        
        # 获取财务数据
        metrics_list = db.load_metrics(code, limit=8)
        profile = db.load_profile(code)
        
        if not metrics_list:
            click.echo(f"❌ 没有找到 {code} 的财务数据", err=True)
            sys.exit(1)
        
        chart_gen = ChartGenerator()
        company_name = profile.stock.name if profile else code
        filepath = Path(output) if output else None
        show = not no_show
        
        if chart_type == "trend":
            metrics = metric.split(",")
            fig = chart_gen.plot_trend(
                metrics_list,
                metrics=metrics,
                title=f"{company_name} 财务指标趋势",
                filepath=filepath,
                show=show,
            )
            click.echo(f"✅ 趋势图已生成")
            
        elif chart_type == "radar":
            fig = chart_gen.plot_radar(
                metrics_list[-1],
                title=f"{company_name} 财务能力雷达图",
                filepath=filepath,
                show=show,
            )
            click.echo(f"✅ 雷达图已生成")
            
        elif chart_type == "dupont":
            latest = metrics_list[-1]
            fig = chart_gen.plot_dupont(
                roe=latest.profitability.roe or 0,
                net_margin=latest.profitability.net_margin or 0,
                asset_turnover=latest.efficiency.asset_turnover or 0,
                equity_multiplier=1.5,
                title=f"{company_name} 杜邦分析",
                filepath=filepath,
                show=show,
            )
            click.echo(f"✅ 杜邦分析图已生成")
        
        if output:
            click.echo(f"📁 保存位置: {output}")
    
    except ImportError:
        click.echo("❌ 需要安装 matplotlib: pip install matplotlib", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 生成图表失败: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
