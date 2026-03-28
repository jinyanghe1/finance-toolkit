"""
Finance Toolkit - 公司分析主入口
Company Analysis Tool
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from ..models import CompanyProfile, StockInfo, FinancialMetrics, detect_exchange
from ..data.db import CompanyDB, get_company_db
from .metrics import FinancialStatement, MetricsCalculator
from .dupont import DupontAnalyzer
from .trend import TrendAnalyzer
from .valuation import DCFValuation, RelativeValuation, DCFAssumptions
from ..exceptions import CompanyNotFoundError, ValidationError
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)


class CompanyAnalyzer(LogMixin):
    """公司分析器 - 主入口类"""
    
    def __init__(self, db: Optional[CompanyDB] = None):
        """
        初始化分析器
        
        Args:
            db: 数据库实例，None 则使用默认
        """
        self.db = db or get_company_db()
        self.calculator = MetricsCalculator()
    
    def create_profile(
        self, 
        code: str, 
        name: str, 
        **kwargs
    ) -> CompanyProfile:
        """
        创建公司档案
        
        Args:
            code: 股票代码
            name: 股票名称
            **kwargs: 其他字段
        
        Returns:
            创建的公司档案
        """
        # 检测交易所
        exchange = detect_exchange(code)
        
        # 标准化代码
        code_clean = code.split('.')[0] if '.' in code else code
        full_code = f"{code_clean}.{exchange.value}"
        
        stock = StockInfo(
            code=full_code,
            name=name,
            exchange=exchange,
        )
        
        profile = CompanyProfile(
            stock=stock,
            full_name=kwargs.get('full_name', name),
            business_scope=kwargs.get('business_scope', ''),
            main_products=kwargs.get('main_products', []),
        )
        
        # 保存
        self.db.save_profile(profile)
        self.logger.info(f"创建公司档案: {name} ({full_code})")
        
        return profile
    
    def get_profile(self, code: str) -> Optional[CompanyProfile]:
        """
        获取公司档案
        
        Args:
            code: 股票代码
        
        Returns:
            公司档案，不存在则返回 None
        """
        return self.db.load_profile(code)
    
    def update_market_data(self, code: str, **kwargs) -> None:
        """
        更新市场数据
        
        Args:
            code: 股票代码
            **kwargs: 市场数据字段
        """
        profile = self.db.load_profile(code)
        if not profile:
            raise CompanyNotFoundError(code)
        
        # 更新字段
        profile.update_market_data(**kwargs)
        
        # 保存
        self.db.save_profile(profile)
        self.logger.info(f"更新市场数据: {profile.stock.name}")
    
    def add_financial_statement(
        self, 
        code: str, 
        statement: FinancialStatement, 
        report_date: str,
    ) -> FinancialMetrics:
        """
        添加财务报表并计算指标
        
        Args:
            code: 股票代码
            statement: 财务报表
            report_date: 报告期 (YYYY-MM-DD)
        
        Returns:
            计算的财务指标
        """
        # 检查公司是否存在
        if not self.db.exists(code):
            raise CompanyNotFoundError(code)
        
        # 计算指标
        metrics = self.calculator.calculate_metrics_from_statement(
            statement, report_date
        )
        
        # 保存
        self.db.save_metrics(code, metrics)
        self.logger.info(f"添加财务报表: {code} ({report_date})")
        
        return metrics
    
    def get_financial_summary(self, code: str) -> Dict[str, Any]:
        """
        获取财务摘要
        
        Args:
            code: 股票代码
        
        Returns:
            财务摘要字典
        """
        profile = self.db.load_profile(code)
        if not profile:
            raise CompanyNotFoundError(code)
        
        metrics_list = self.db.load_metrics(code, limit=4)
        
        summary = {
            "公司信息": {
                "代码": profile.stock.code,
                "名称": profile.stock.name,
                "行业": profile.industry.value if profile.industry else "未知",
            },
            "市场数据": {
                "总市值": f"{profile.market_data.market_cap:.2f}亿元" if profile.market_data.market_cap else "N/A",
                "PE(TTM)": f"{profile.market_data.pe_ttm:.2f}" if profile.market_data.pe_ttm else "N/A",
                "PB": f"{profile.market_data.pb:.2f}" if profile.market_data.pb else "N/A",
                "股息率": f"{profile.market_data.dividend_yield:.2f}%" if profile.market_data.dividend_yield else "N/A",
            },
            "最新财务指标": {},
            "历史趋势": {},
        }
        
        if metrics_list:
            latest = metrics_list[0]
            summary["最新财务指标"] = {
                "报告期": latest.report_date,
                "ROE": self.calculator.evaluate_metric("ROE", latest.profitability.roe, profile.industry),
                "毛利率": self.calculator.evaluate_metric("毛利率", latest.profitability.gross_margin, profile.industry),
                "净利率": self.calculator.evaluate_metric("净利率", latest.profitability.net_margin, profile.industry),
                "资产负债率": self.calculator.evaluate_metric("资产负债率", latest.solvency.debt_to_asset, profile.industry),
                "流动比率": self.calculator.evaluate_metric("流动比率", latest.solvency.current_ratio, profile.industry),
            }
            
            # 趋势分析
            if len(metrics_list) >= 2:
                prev = metrics_list[1]
                summary["历史趋势"] = {
                    "ROE变化": f"{latest.profitability.roe:.2f}% → {prev.profitability.roe:.2f}%" if latest.profitability.roe and prev.profitability.roe else "N/A",
                    "毛利率变化": f"{latest.profitability.gross_margin:.2f}% → {prev.profitability.gross_margin:.2f}%" if latest.profitability.gross_margin and prev.profitability.gross_margin else "N/A",
                }
        
        return summary
    
    def analyze_dupont(self, code: str) -> Optional[Dict[str, Any]]:
        """
        执行杜邦分析
        
        Args:
            code: 股票代码
        
        Returns:
            杜邦分析结果
        """
        # 获取最新财务数据
        metrics_list = self.db.load_metrics(code, limit=1)
        if not metrics_list:
            return None
        
        # 这里简化处理，实际需要从原始财务数据构建 FinancialStatement
        # 返回基本分析
        metrics = metrics_list[0]
        return {
            "roe": metrics.profitability.roe,
            "note": "杜邦分析需要完整财务报表数据",
        }
    
    def analyze_trend(self, code: str) -> Dict[str, Any]:
        """
        分析财务趋势
        
        Args:
            code: 股票代码
        
        Returns:
            趋势分析结果
        """
        metrics_list = self.db.load_metrics(code, limit=8)
        if len(metrics_list) < 2:
            return {"error": "历史数据不足"}
        
        trends = TrendAnalyzer.analyze_financial_metrics(metrics_list)
        
        return {
            "trends": {name: trend.to_dict() for name, trend in trends.items()},
            "report": TrendAnalyzer.generate_trend_report(trends),
        }
    
    def list_all_companies(self) -> List[Dict[str, Any]]:
        """列出所有公司摘要"""
        codes = self.db.list_companies()
        summaries = []
        for code in codes:
            summary = self.db.get_summary(code)
            if summary:
                summaries.append(summary)
        return summaries
    
    def search_companies(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索公司
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的公司列表
        """
        return self.db.search(keyword)
    
    def generate_report(self, code: str, include_trend: bool = True) -> str:
        """
        生成分析报告
        
        Args:
            code: 股票代码
            include_trend: 是否包含趋势分析
        
        Returns:
            Markdown 格式报告
        """
        profile = self.db.load_profile(code)
        if not profile:
            raise CompanyNotFoundError(code)
        
        metrics_list = self.db.load_metrics(code, limit=4)
        
        lines = [
            f"# {profile.stock.name} ({profile.stock.code}) 分析简报",
            "",
            "## 基本信息",
            f"- **全称**: {profile.full_name}",
            f"- **行业**: {profile.industry.value if profile.industry else '未知'}",
        ]
        
        if profile.sub_industry:
            lines.append(f"- **细分行业**: {profile.sub_industry.value}")
        
        if profile.business_scope:
            scope = profile.business_scope[:100] + "..." if len(profile.business_scope) > 100 else profile.business_scope
            lines.append(f"- **主营业务**: {scope}")
        
        lines.extend([
            "",
            "## 市场数据",
        ])
        
        if profile.market_data.market_cap:
            lines.append(f"- **总市值**: {profile.market_data.market_cap:.2f}亿元")
        if profile.market_data.pe_ttm:
            lines.append(f"- **PE(TTM)**: {profile.market_data.pe_ttm:.2f}")
        if profile.market_data.pb:
            lines.append(f"- **PB**: {profile.market_data.pb:.2f}")
        if profile.market_data.dividend_yield:
            lines.append(f"- **股息率**: {profile.market_data.dividend_yield:.2f}%")
        
        lines.extend([
            "",
            "## 财务指标",
        ])
        
        if metrics_list:
            latest = metrics_list[0]
            lines.extend([
                f"\n**最新报告期**: {latest.report_date}",
                "",
                "| 指标 | 数值 | 评估 |",
                "|-----|-----|-----|",
            ])
            
            metrics_display = [
                ("ROE", latest.profitability.roe, "ROE"),
                ("毛利率", latest.profitability.gross_margin, "毛利率"),
                ("净利率", latest.profitability.net_margin, "净利率"),
                ("资产负债率", latest.solvency.debt_to_asset, "资产负债率"),
                ("流动比率", latest.solvency.current_ratio, "流动比率"),
            ]
            
            for name, value, eval_key in metrics_display:
                eval_result = self.calculator.evaluate_metric(eval_key, value, profile.industry)
                val_str = f"{value:.2f}%" if value is not None else "N/A"
                level = eval_result.split('(')[-1].replace(')', '') if '(' in eval_result else '-'
                lines.append(f"| {name} | {val_str} | {level} |")
            
            # 趋势分析
            if include_trend and len(metrics_list) >= 2:
                lines.extend(["", "## 趋势分析"])
                trends = TrendAnalyzer.analyze_financial_metrics(metrics_list)
                if trends:
                    for name, trend in trends.items():
                        emoji = "📈" if trend.direction.value == "up" else "📉" if trend.direction.value == "down" else "📊"
                        lines.append(f"- {emoji} **{trend.metric_name}**: {trend.change_pct:+.1f}%")
                else:
                    lines.append("数据不足，无法进行趋势分析。")
        else:
            lines.append("暂无财务数据")
        
        lines.extend([
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])
        
        return "\n".join(lines)
    
    def export_report(self, code: str, filepath: str, format: str = "md") -> None:
        """
        导出报告到文件
        
        Args:
            code: 股票代码
            filepath: 文件路径
            format: 格式 (md, txt)
        """
        report = self.generate_report(code)
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"报告已导出: {filepath}")


# 便捷函数
def analyze_company(code: str, db: Optional[CompanyDB] = None) -> str:
    """快速分析公司"""
    analyzer = CompanyAnalyzer(db)
    return analyzer.generate_report(code)


def get_company_summary(code: str, db: Optional[CompanyDB] = None) -> Dict[str, Any]:
    """快速获取公司摘要"""
    analyzer = CompanyAnalyzer(db)
    return analyzer.get_financial_summary(code)


def list_companies(db: Optional[CompanyDB] = None) -> List[Dict[str, Any]]:
    """列出所有公司"""
    analyzer = CompanyAnalyzer(db)
    return analyzer.list_all_companies()
