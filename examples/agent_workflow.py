#!/usr/bin/env python3
"""
Finance Toolkit - AI Agent 工作流示例
AI Agent Workflow Example

展示 AI Agents 如何高效使用本工具包
"""

from typing import List, Dict, Any
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.analyzer.metrics import PeerComparator


def batch_analyze_with_error_handling(codes: List[str]) -> Dict[str, Any]:
    """
    Agent 工作流: 批量分析多家公司
    
    展示如何:
    - 批量处理
    - 错误处理
    - 结果结构化
    """
    analyzer = CompanyAnalyzer()
    results = {}
    
    for code in codes:
        try:
            summary = analyzer.get_financial_summary(code)
            results[code] = {
                "success": True,
                "name": summary["公司信息"]["名称"],
                "industry": summary["公司信息"]["行业"],
                "metrics": summary.get("最新财务指标", {}),
            }
        except Exception as e:
            results[code] = {
                "success": False,
                "error": str(e),
            }
    
    return results


def compare_peers(codes: List[str]) -> Dict[str, Any]:
    """
    Agent 工作流: 比较同业公司
    
    展示如何:
    - 获取多家公司数据
    - 使用 PeerComparator
    - 生成比较结果
    """
    analyzer = CompanyAnalyzer()
    companies = []
    
    for code in codes:
        try:
            summary = analyzer.get_financial_summary(code)
            metrics_summary = summary.get("最新财务指标", {})
            
            # 解析指标值
            company_data = {
                "name": summary["公司信息"]["名称"],
                "metrics": {}
            }
            
            # 从评估字符串中提取数值
            for metric_name, metric_value in metrics_summary.items():
                if metric_name in ["ROE", "毛利率", "净利率", "资产负债率"]:
                    # 解析 "25.50% (优秀)" 格式
                    if isinstance(metric_value, str) and "%" in metric_value:
                        try:
                            value = float(metric_value.split("%")[0])
                            company_data["metrics"][metric_name] = value
                        except:
                            pass
            
            if company_data["metrics"]:
                companies.append(company_data)
        
        except Exception as e:
            print(f"获取 {code} 数据失败: {e}")
    
    if len(companies) < 2:
        return {"error": "数据不足以进行比较"}
    
    # 进行比较
    comparison = PeerComparator.compare_metrics(
        companies,
        metrics=["ROE", "毛利率", "净利率"]
    )
    
    return {
        "companies": [c["name"] for c in companies],
        "comparison": comparison,
    }


def extract_key_insights(code: str) -> Dict[str, Any]:
    """
    Agent 工作流: 提取关键洞察
    
    展示如何:
    - 从报告中提取关键信息
    - 结构化输出
    """
    analyzer = CompanyAnalyzer()
    
    try:
        summary = analyzer.get_financial_summary(code)
        
        insights = {
            "code": code,
            "name": summary["公司信息"]["名称"],
            "industry": summary["公司信息"]["行业"],
            "key_metrics": {},
            "assessment": "",
        }
        
        # 提取关键指标
        metrics = summary.get("最新财务指标", {})
        
        # 评估盈利能力
        roe_str = metrics.get("ROE", "")
        if "优秀" in roe_str:
            insights["assessment"] = "盈利能力优秀"
        elif "良好" in roe_str:
            insights["assessment"] = "盈利能力良好"
        elif "一般" in roe_str:
            insights["assessment"] = "盈利能力一般"
        else:
            insights["assessment"] = "盈利能力待评估"
        
        # 提取数值
        for key in ["ROE", "毛利率", "净利率", "资产负债率"]:
            value = metrics.get(key, "")
            if isinstance(value, str) and "%" in value:
                try:
                    num = float(value.split("%")[0])
                    insights["key_metrics"][key] = num
                except:
                    pass
        
        return insights
    
    except Exception as e:
        return {
            "code": code,
            "error": str(e),
        }


def main():
    """主函数 - Agent 工作流演示"""
    print("=" * 60)
    print("AI Agent 工作流示例")
    print("=" * 60)
    
    # 示例1: 批量分析
    print("\n1️⃣  批量分析")
    print("-" * 40)
    codes = ["600519", "000858", "000568"]  # 白酒公司
    results = batch_analyze_with_error_handling(codes)
    
    for code, result in results.items():
        if result["success"]:
            print(f"✅ {code}: {result['name']} ({result['industry']})")
        else:
            print(f"❌ {code}: {result['error']}")
    
    # 示例2: 同业比较
    print("\n2️⃣  同业比较")
    print("-" * 40)
    comparison = compare_peers(codes)
    
    if "error" in comparison:
        print(f"⚠️  {comparison['error']}")
    else:
        print(f"比较公司: {', '.join(comparison['companies'])}")
        for metric, data in comparison.get("comparison", {}).items():
            print(f"\n{metric}:")
            print(f"  行业平均: {data['mean']:.2f}")
            print(f"  最高: {data['max']:.2f} ({data['ranking'][0]['name']})")
            print(f"  最低: {data['min']:.2f} ({data['ranking'][-1]['name']})")
    
    # 示例3: 提取洞察
    print("\n3️⃣  提取关键洞察")
    print("-" * 40)
    
    for code in codes:
        insights = extract_key_insights(code)
        if "error" not in insights:
            print(f"\n{insights['name']} ({code}):")
            print(f"  评估: {insights['assessment']}")
            print(f"  关键指标: {insights['key_metrics']}")
        else:
            print(f"\n{code}: 获取失败 - {insights['error']}")
    
    print("\n" + "=" * 60)
    print("Agent 工作流演示完成！")
    print("=" * 60)
    print("\n提示: 这些模式可以帮助 Agents:")
    print("  • 批量处理大量公司数据")
    print("  • 优雅处理错误和边界情况")
    print("  • 结构化输出便于后续分析")


if __name__ == "__main__":
    main()
