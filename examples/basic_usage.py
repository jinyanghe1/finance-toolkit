#!/usr/bin/env python3
"""
Finance Toolkit - 基础使用示例
Basic Usage Example

适合: AI Agents, Python 开发者
"""

from finance_toolkit import CompanyAnalyzer
from finance_toolkit.analyzer.metrics import FinancialStatement


def demo_create_company():
    """示例1: 创建公司档案"""
    print("=" * 60)
    print("示例1: 创建公司档案")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    
    # 创建公司档案
    profile = analyzer.create_profile(
        code="600519",
        name="贵州茅台",
        full_name="贵州茅台酒股份有限公司",
        business_scope="茅台酒及系列酒的生产与销售",
        main_products=["飞天茅台", "茅台系列酒"],
    )
    
    # 更新市场数据（实际中可通过 AKShare 获取）
    analyzer.update_market_data(
        code="600519",
        market_cap=21000,  # 亿元
        pe_ttm=28.5,
        pb=8.2,
        dividend_yield=1.5,
    )
    
    print(f"✅ 已创建公司: {profile.stock.name} ({profile.stock.code})")
    print()


def demo_add_financials():
    """示例2: 添加财务数据"""
    print("=" * 60)
    print("示例2: 添加财务报表并计算指标")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    
    # 2024年报数据（示例）
    statement_2024 = FinancialStatement(
        revenue=1505.0,        # 营收 亿元
        cost_of_goods_sold=157.0,  # 成本
        gross_profit=1348.0,   # 毛利润
        net_profit=747.0,      # 净利润
        total_assets=2727.0,   # 总资产
        shareholders_equity=2157.0,  # 净资产
        total_liabilities=570.0,     # 总负债
        operating_cash_flow=665.0,   # 经营现金流
    )
    
    try:
        analyzer.add_financial_statement("600519", statement_2024, "2024-12-31")
        print("✅ 已添加2024年报数据")
    except Exception as e:
        print(f"⚠️  {e}")
    
    # 2023年报数据
    statement_2023 = FinancialStatement(
        revenue=1476.0,
        cost_of_goods_sold=156.0,
        net_profit=747.0,
        total_assets=2727.0,
        shareholders_equity=2157.0,
        total_liabilities=570.0,
        operating_cash_flow=665.0,
    )
    
    try:
        analyzer.add_financial_statement("600519", statement_2023, "2023-12-31")
        print("✅ 已添加2023年报数据")
    except Exception as e:
        print(f"⚠️  {e}")
    
    print()


def demo_view_summary():
    """示例3: 查看公司摘要"""
    print("=" * 60)
    print("示例3: 查看公司财务摘要")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    
    try:
        summary = analyzer.get_financial_summary("600519")
        
        print("\n📊 公司摘要:")
        for section, data in summary.items():
            print(f"\n【{section}】")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {data}")
    except Exception as e:
        print(f"⚠️  {e}")
    
    print()


def demo_generate_report():
    """示例4: 生成分析报告"""
    print("=" * 60)
    print("示例4: 生成分析报告")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    
    try:
        report = analyzer.generate_report("600519")
        # 只显示前50行
        lines = report.split('\n')
        print('\n'.join(lines[:50]))
        if len(lines) > 50:
            print(f"\n... (共 {len(lines)} 行)")
    except Exception as e:
        print(f"⚠️  {e}")


def demo_list_companies():
    """示例5: 列出所有公司"""
    print("=" * 60)
    print("示例5: 列出所有已存储的公司")
    print("=" * 60)
    
    analyzer = CompanyAnalyzer()
    companies = analyzer.list_all_companies()
    
    print(f"\n📁 共存储 {len(companies)} 家公司:\n")
    for c in companies:
        market_cap = f"{c.get('market_cap', 'N/A')}亿"
        print(f"  • {c['name']} ({c['code']})")
        print(f"    行业: {c['industry']} | 市值: {market_cap}")
        print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Finance Toolkit - 基础使用示例")
    print("=" * 60 + "\n")
    
    # 运行示例
    demo_create_company()
    demo_add_financials()
    demo_view_summary()
    demo_generate_report()
    demo_list_companies()
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)
    print("\n提示: 你可以使用 CLI 工具 ftk 进行交互式操作")
    print("例如: ftk analyze 600519")
