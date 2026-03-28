#!/usr/bin/env python3
"""
Finance Toolkit - 图表功能演示
Chart Functionality Demo

展示如何使用图表功能可视化财务数据
"""

from pathlib import Path
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.analyzer.metrics import FinancialStatement
from finance_toolkit.report.charts import ChartGenerator


def prepare_demo_data():
    """准备演示数据"""
    print("准备演示数据...")
    
    analyzer = CompanyAnalyzer()
    
    # 创建公司档案
    try:
        profile = analyzer.create_profile(
            code="600519",
            name="贵州茅台",
            full_name="贵州茅台酒股份有限公司",
            business_scope="茅台酒及系列酒的生产与销售",
        )
        
        # 添加多期财务数据
        data = [
            ("2020-12-31", 979.0, 523.0, 2134.0, 1615.0, 519.0, 517.0),
            ("2021-12-31", 1095.0, 558.0, 2552.0, 1970.0, 582.0, 565.0),
            ("2022-12-31", 1276.0, 654.0, 2544.0, 1975.0, 569.0, 640.0),
            ("2023-12-31", 1476.0, 747.0, 2727.0, 2157.0, 570.0, 665.0),
            ("2024-12-31", 1505.0, 747.0, 2727.0, 2157.0, 570.0, 665.0),
        ]
        
        for date, revenue, net_profit, total_assets, equity, liabilities, ocf in data:
            statement = FinancialStatement(
                revenue=revenue,
                cost_of_goods_sold=revenue * 0.1,
                net_profit=net_profit,
                total_assets=total_assets,
                shareholders_equity=equity,
                total_liabilities=liabilities,
                operating_cash_flow=ocf,
            )
            try:
                analyzer.add_financial_statement("600519", statement, date)
            except:
                pass  # 忽略重复添加的错误
        
        print("✅ 演示数据准备完成\n")
        return True
    
    except Exception as e:
        print(f"⚠️  数据准备出现问题 (可能已存在): {e}\n")
        return True  # 继续演示


def demo_trend_chart():
    """演示趋势图"""
    print("=" * 60)
    print("演示1: 财务指标趋势图")
    print("=" * 60)
    
    from finance_toolkit.data.db import get_company_db
    
    db = get_company_db()
    metrics_list = db.load_metrics("600519", limit=8)
    
    if not metrics_list:
        print("❌ 没有找到财务数据")
        return
    
    chart_gen = ChartGenerator()
    
    # 绘制趋势图
    fig = chart_gen.plot_trend(
        metrics_list,
        metrics=["roe", "gross_margin", "net_margin"],
        title="贵州茅台 - 盈利能力趋势",
        filepath=Path("~/.finance_toolkit/exports/trend_chart.png").expanduser(),
        show=True,
    )
    
    print("✅ 趋势图已生成并保存\n")


def demo_radar_chart():
    """演示雷达图"""
    print("=" * 60)
    print("演示2: 财务能力雷达图")
    print("=" * 60)
    
    from finance_toolkit.data.db import get_company_db
    
    db = get_company_db()
    metrics_list = db.load_metrics("600519", limit=1)
    
    if not metrics_list:
        print("❌ 没有找到财务数据")
        return
    
    chart_gen = ChartGenerator()
    
    # 绘制雷达图
    fig = chart_gen.plot_radar(
        metrics_list[0],
        categories=["盈利能力", "偿债能力", "运营效率", "成长能力", "现金流"],
        title="贵州茅台 - 财务能力雷达图",
        filepath=Path("~/.finance_toolkit/exports/radar_chart.png").expanduser(),
        show=True,
    )
    
    print("✅ 雷达图已生成并保存\n")


def demo_comparison_chart():
    """演示对比图"""
    print("=" * 60)
    print("演示3: 同业对比图")
    print("=" * 60)
    
    # 模拟多家公司的 ROE 数据
    companies = [
        {"name": "贵州茅台", "ROE": 25.5},
        {"name": "五粮液", "ROE": 20.3},
        {"name": "泸州老窖", "ROE": 22.1},
        {"name": "山西汾酒", "ROE": 35.0},
        {"name": "洋河股份", "ROE": 18.5},
    ]
    
    chart_gen = ChartGenerator()
    
    fig = chart_gen.plot_comparison(
        companies,
        metric="ROE",
        title="白酒行业 ROE 对比",
        filepath=Path("~/.finance_toolkit/exports/comparison_chart.png").expanduser(),
        show=True,
    )
    
    print("✅ 对比图已生成并保存\n")


def demo_dupont_chart():
    """演示杜邦分析图"""
    print("=" * 60)
    print("演示4: 杜邦分析图")
    print("=" * 60)
    
    chart_gen = ChartGenerator()
    
    fig = chart_gen.plot_dupont(
        roe=25.5,
        net_margin=52.0,
        asset_turnover=0.55,
        equity_multiplier=1.4,
        title="贵州茅台 - 杜邦分析",
        filepath=Path("~/.finance_toolkit/exports/dupont_chart.png").expanduser(),
        show=True,
    )
    
    print("✅ 杜邦分析图已生成并保存\n")


def demo_cli_usage():
    """演示 CLI 图表命令"""
    print("=" * 60)
    print("CLI 图表命令示例")
    print("=" * 60)
    
    examples = """
生成趋势图:
  ftk chart 600519 --type trend --metric roe,gross_margin

生成雷达图:
  ftk chart 600519 --type radar -o radar.png

生成杜邦分析图:
  ftk chart 600519 --type dupont -o dupont.png

仅保存不显示:
  ftk chart 600519 --type trend -o trend.png --no-show
"""
    print(examples)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Finance Toolkit - 图表功能演示")
    print("=" * 60 + "\n")
    
    # 准备数据
    prepare_demo_data()
    
    # 运行演示
    try:
        demo_trend_chart()
    except Exception as e:
        print(f"趋势图演示失败: {e}\n")
    
    try:
        demo_radar_chart()
    except Exception as e:
        print(f"雷达图演示失败: {e}\n")
    
    try:
        demo_comparison_chart()
    except Exception as e:
        print(f"对比图演示失败: {e}\n")
    
    try:
        demo_dupont_chart()
    except Exception as e:
        print(f"杜邦图演示失败: {e}\n")
    
    demo_cli_usage()
    
    print("=" * 60)
    print("图表演示完成！")
    print("=" * 60)
    print("\n图表已保存到: ~/.finance_toolkit/exports/")
