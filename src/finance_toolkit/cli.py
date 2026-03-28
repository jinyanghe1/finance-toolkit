"""Finance Toolkit CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

import click
import yaml

from .__version__ import __title__, __version__
from .config import get_config
from .analyzer.company import CompanyAnalyzer


def _emit_payload(payload: dict[str, Any], output_format: str) -> None:
    """Emit a payload in the requested format."""
    if output_format == "json":
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    click.echo(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        nl=False,
    )


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
