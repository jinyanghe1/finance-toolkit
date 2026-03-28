#!/usr/bin/env python3
"""
Finance Toolkit - 批量分析示例
"""

from finance_toolkit import CompanyAnalyzer


def seed_demo_data(analyzer: CompanyAnalyzer) -> None:
    companies = [
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("000568", "泸州老窖"),
    ]
    for code, name in companies:
        analyzer.create_profile(code=code, name=name, full_name=name)


def demo_batch_analysis() -> None:
    analyzer = CompanyAnalyzer()
    seed_demo_data(analyzer)

    results = analyzer.analyze_batch(["600519", "000858", "000568", "999999"])

    print("=" * 60)
    print("Finance Toolkit - 批量分析示例")
    print("=" * 60)
    print()

    success_count = sum(1 for item in results.values() if item["success"])
    print(f"成功分析: {success_count}/{len(results)} 家")
    print()

    for requested_code, result in results.items():
        if result["success"]:
            print(f"✅ {result['name']} ({result['code']})")
            print(f"   行业: {result['industry']}")
        else:
            print(f"❌ {requested_code}")
            print(f"   错误: {result['error']}")
        print()

    print("CLI 示例:")
    print("  ftk batch analyze 600519 000858 000568 --format json")


if __name__ == "__main__":
    demo_batch_analysis()
