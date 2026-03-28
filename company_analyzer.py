"""
金融功能库 - 公司分析主入口
Company Analysis Tool
"""

import sys
import json
from pathlib import Path
from typing import Optional, List

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.finance.models import CompanyProfile, StockInfo, FinancialMetrics, Industry
from scripts.finance.storage.company_db import CompanyDB, get_company_db
from scripts.finance.analyzers.financial_metrics import (
    FinancialStatement, MetricsCalculator, PeerComparator
)


class CompanyAnalyzer:
    """公司分析器"""
    
    def __init__(self):
        self.db = get_company_db()
        self.calculator = MetricsCalculator()
    
    def create_profile(self, code: str, name: str, **kwargs) -> CompanyProfile:
        """创建公司档案"""
        # 解析代码和交易所
        if '.' in code:
            code_clean, exchange = code.split('.')
        else:
            code_clean = code
            # 根据代码判断交易所
            if code.startswith('6'):
                exchange = 'SH'
            elif code.startswith('0') or code.startswith('3'):
                exchange = 'SZ'
            else:
                exchange = 'SZ'
        
        stock = StockInfo(
            code=f"{code_clean}.{exchange}",
            name=name,
            exchange=exchange,
        )
        
        profile = CompanyProfile(
            stock=stock,
            full_name=kwargs.get('full_name', name),
            industry=kwargs.get('industry'),
            business_scope=kwargs.get('business_scope', ''),
            main_products=kwargs.get('main_products', []),
        )
        
        # 保存
        self.db.save_profile(profile)
        return profile
    
    def get_profile(self, code: str) -> Optional[CompanyProfile]:
        """获取公司档案"""
        return self.db.load_profile(code)
    
    def update_market_data(self, code: str, **kwargs) -> None:
        """更新市场数据"""
        profile = self.db.load_profile(code)
        if not profile:
            print(f"❌ 公司档案不存在: {code}")
            return
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # 更新时间戳
        from datetime import datetime
        profile.updated_at = datetime.now().isoformat()
        
        self.db.save_profile(profile)
        print(f"✅ 已更新市场数据: {profile.stock.name}")
    
    def add_financial_statement(self, code: str, statement: FinancialStatement, report_date: str) -> None:
        """添加财务报表并计算指标"""
        # 计算所有指标
        metrics_data = self.calculator.calculate_all_metrics(statement)
        
        # 创建FinancialMetrics对象
        metrics = FinancialMetrics(
            gross_margin=metrics_data["毛利率"],
            net_margin=metrics_data["净利率"],
            roe=metrics_data["ROE"],
            roa=metrics_data["ROA"],
            debt_to_asset=metrics_data["资产负债率"],
            current_ratio=metrics_data["流动比率"],
            quick_ratio=metrics_data["速动比率"],
            inventory_turnover=metrics_data["存货周转率"],
            receivable_turnover=metrics_data["应收账款周转率"],
            asset_turnover=metrics_data["总资产周转率"],
            operating_cash_flow=statement.operating_cash_flow,
            free_cash_flow=metrics_data["自由现金流"],
            report_date=report_date,
        )
        
        # 保存
        self.db.save_metrics(code, metrics)
    
    def get_financial_summary(self, code: str) -> dict:
        """获取财务摘要"""
        profile = self.db.load_profile(code)
        if not profile:
            return {"error": f"公司档案不存在: {code}"}
        
        metrics_list = self.db.load_metrics(code, limit=4)
        
        summary = {
            "公司信息": {
                "代码": profile.stock.code,
                "名称": profile.stock.name,
                "行业": profile.industry.value if profile.industry else "未知",
            },
            "市场数据": {
                "总市值": f"{profile.market_cap:.2f}亿元" if profile.market_cap else "N/A",
                "PE(TTM)": f"{profile.pe_ttm:.2f}" if profile.pe_ttm else "N/A",
                "PB": f"{profile.pb:.2f}" if profile.pb else "N/A",
            },
            "最新财务指标": {},
            "历史趋势": {},
        }
        
        if metrics_list:
            latest = metrics_list[0]
            summary["最新财务指标"] = {
                "报告期": latest.report_date,
                "ROE": self.calculator.evaluate_metric("ROE", latest.roe),
                "毛利率": self.calculator.evaluate_metric("毛利率", latest.gross_margin),
                "净利率": self.calculator.evaluate_metric("净利率", latest.net_margin),
                "资产负债率": self.calculator.evaluate_metric("资产负债率", latest.debt_to_asset),
                "流动比率": self.calculator.evaluate_metric("流动比率", latest.current_ratio),
            }
            
            # 趋势分析
            if len(metrics_list) >= 2:
                prev = metrics_list[1]
                summary["历史趋势"] = {
                    "ROE变化": f"{latest.roe:.2f}% → {prev.roe:.2f}%" if latest.roe and prev.roe else "N/A",
                    "毛利率变化": f"{latest.gross_margin:.2f}% → {prev.gross_margin:.2f}%" if latest.gross_margin and prev.gross_margin else "N/A",
                }
        
        return summary
    
    def list_all_companies(self) -> List[dict]:
        """列出所有公司摘要"""
        codes = self.db.list_companies()
        summaries = []
        for code in codes:
            summary = self.db.get_summary(code)
            if summary:
                summaries.append(summary)
        return summaries
    
    def generate_report(self, code: str) -> str:
        """生成简单分析报告"""
        profile = self.db.load_profile(code)
        if not profile:
            return f"❌ 公司档案不存在: {code}"
        
        metrics_list = self.db.load_metrics(code, limit=2)
        
        lines = [
            f"# {profile.stock.name} ({profile.stock.code}) 分析简报",
            "",
            "## 基本信息",
            f"- **全称**: {profile.full_name}",
            f"- **行业**: {profile.industry.value if profile.industry else '未知'}",
            f"- **主营业务**: {profile.business_scope[:100]}..." if len(profile.business_scope) > 100 else f"- **主营业务**: {profile.business_scope}",
            "",
            "## 市场数据",
        ]
        
        if profile.market_cap:
            lines.append(f"- **总市值**: {profile.market_cap:.2f}亿元")
        if profile.pe_ttm:
            lines.append(f"- **PE(TTM)**: {profile.pe_ttm:.2f}")
        if profile.pb:
            lines.append(f"- **PB**: {profile.pb:.2f}")
        
        lines.append("")
        lines.append("## 财务指标")
        
        if metrics_list:
            latest = metrics_list[0]
            lines.append(f"\n**最新报告期**: {latest.report_date}")
            lines.append("")
            lines.append("| 指标 | 数值 | 评估 |")
            lines.append("|-----|-----|-----|")
            
            metrics_display = [
                ("ROE", latest.roe, "ROE"),
                ("毛利率", latest.gross_margin, "毛利率"),
                ("净利率", latest.net_margin, "净利率"),
                ("资产负债率", latest.debt_to_asset, "资产负债率"),
                ("流动比率", latest.current_ratio, "流动比率"),
            ]
            
            for name, value, eval_key in metrics_display:
                eval_result = self.calculator.evaluate_metric(eval_key, value)
                val_str = f"{value:.2f}%" if value is not None else "N/A"
                lines.append(f"| {name} | {val_str} | {eval_result.split('(')[-1].replace(')', '') if '(' in eval_result else '-'} |")
        else:
            lines.append("暂无财务数据")
        
        return "\n".join(lines)


# 便捷函数
def analyze_company(code: str) -> str:
    """快速分析公司"""
    analyzer = CompanyAnalyzer()
    return analyzer.generate_report(code)


def get_company_summary(code: str) -> dict:
    """快速获取公司摘要"""
    analyzer = CompanyAnalyzer()
    return analyzer.get_financial_summary(code)


def list_companies() -> List[dict]:
    """列出所有公司"""
    analyzer = CompanyAnalyzer()
    return analyzer.list_all_companies()


if __name__ == "__main__":
    # 测试代码
    analyzer = CompanyAnalyzer()
    
    # 列出所有公司
    companies = analyzer.list_all_companies()
    print(f"📊 已存储公司数量: {len(companies)}")
    
    if companies:
        print("\n公司列表:")
        for c in companies:
            print(f"  - {c['name']} ({c['code']}) | {c['industry']} | 市值: {c.get('market_cap', 'N/A')}")
