"""
Finance Toolkit - 报告生成器
Report Generator
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..models import CompanyProfile, FinancialMetrics
from ..analyzer.metrics import MetricsCalculator
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)


class ReportGenerator(LogMixin):
    """报告生成器"""
    
    def __init__(self):
        self.calculator = MetricsCalculator()
    
    def generate_markdown(
        self,
        profile: CompanyProfile,
        metrics_list: list[FinancialMetrics],
        include_trend: bool = True,
    ) -> str:
        """
        生成 Markdown 报告
        
        Args:
            profile: 公司档案
            metrics_list: 财务指标列表
            include_trend: 是否包含趋势分析
        
        Returns:
            Markdown 格式报告
        """
        lines = [
            f"# {profile.stock.name} ({profile.stock.code}) 投资分析报告",
            "",
            f"*生成时间: {datetime.now().strftime('%Y年%m月%d日')}*",
            "",
            "---",
            "",
            "## 一、公司概况",
            "",
            f"- **公司全称**: {profile.full_name}",
            f"- **所属行业**: {profile.industry.value if profile.industry else '未知'}",
        ]
        
        if profile.sub_industry:
            lines.append(f"- **细分行业**: {profile.sub_industry.value}")
        
        if profile.business_scope:
            lines.extend([
                "",
                "### 主营业务",
                profile.business_scope,
            ])
        
        lines.extend([
            "",
            "## 二、市场数据",
            "",
        ])
        
        md = profile.market_data
        if any([md.market_cap, md.pe_ttm, md.pb]):
            lines.append("| 指标 | 数值 |")
            lines.append("|------|------|")
            if md.market_cap:
                lines.append(f"| 总市值 | {md.market_cap:,.2f} 亿元 |")
            if md.pe_ttm:
                lines.append(f"| 市盈率(TTM) | {md.pe_ttm:.2f} |")
            if md.pb:
                lines.append(f"| 市净率 | {md.pb:.2f} |")
            if md.ps_ttm:
                lines.append(f"| 市销率(TTM) | {md.ps_ttm:.2f} |")
            if md.dividend_yield:
                lines.append(f"| 股息率 | {md.dividend_yield:.2f}% |")
        else:
            lines.append("暂无市场数据")
        
        lines.extend([
            "",
            "## 三、财务分析",
            "",
        ])
        
        if metrics_list:
            latest = metrics_list[0]
            
            lines.extend([
                f"**最新报告期**: {latest.report_date}",
                "",
                "### 盈利能力",
                "",
                "| 指标 | 数值 | 评估 |",
                "|------|------|------|",
            ])
            
            profitability_metrics = [
                ("ROE", latest.profitability.roe, "ROE"),
                ("ROA", latest.profitability.roa, "ROA"),
                ("毛利率", latest.profitability.gross_margin, "毛利率"),
                ("净利率", latest.profitability.net_margin, "净利率"),
            ]
            
            for name, value, eval_key in profitability_metrics:
                if value is not None:
                    eval_result = self.calculator.evaluate_metric(eval_key, value, profile.industry)
                    level = eval_result.split('(')[-1].replace(')', '') if '(' in eval_result else '-'
                    lines.append(f"| {name} | {value:.2f}% | {level} |")
            
            lines.extend([
                "",
                "### 偿债能力",
                "",
                "| 指标 | 数值 | 评估 |",
                "|------|------|------|",
            ])
            
            solvency_metrics = [
                ("资产负债率", latest.solvency.debt_to_asset, "资产负债率"),
                ("流动比率", latest.solvency.current_ratio, "流动比率"),
                ("速动比率", latest.solvency.quick_ratio, "速动比率"),
            ]
            
            for name, value, eval_key in solvency_metrics:
                if value is not None:
                    eval_result = self.calculator.evaluate_metric(eval_key, value, profile.industry)
                    level = eval_result.split('(')[-1].replace(')', '') if '(' in eval_result else '-'
                    unit = "%" if "比率" not in name else ""
                    lines.append(f"| {name} | {value:.2f}{unit} | {level} |")
            
            # 趋势分析
            if include_trend and len(metrics_list) >= 2:
                from ..analyzer.trend import TrendAnalyzer
                lines.extend([
                    "",
                    "## 四、趋势分析",
                    "",
                ])
                
                trends = TrendAnalyzer.analyze_financial_metrics(metrics_list)
                if trends:
                    lines.append(TrendAnalyzer.generate_trend_report(trends))
                else:
                    lines.append("数据不足，无法进行趋势分析。")
        else:
            lines.append("暂无财务数据")
        
        lines.extend([
            "",
            "---",
            "",
            "*免责声明: 本报告仅供参考，不构成投资建议。*",
        ])
        
        return "\n".join(lines)
    
    def save_report(
        self,
        content: str,
        filepath: Path,
    ) -> None:
        """
        保存报告
        
        Args:
            content: 报告内容
            filepath: 保存路径
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"报告已保存: {filepath}")
