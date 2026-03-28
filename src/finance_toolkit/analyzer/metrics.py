"""
Finance Toolkit - 财务指标计算
Financial Metrics Calculator
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from functools import lru_cache

from ..models import (
    FinancialMetrics, 
    ProfitabilityMetrics,
    GrowthMetrics,
    SolvencyMetrics,
    EfficiencyMetrics,
    CashflowMetrics,
    get_benchmark,
    Industry,
)
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)


@dataclass
class FinancialStatement:
    """财务报表数据结构"""
    # 利润表
    revenue: float = 0                    # 营业收入
    cost_of_goods_sold: float = 0         # 营业成本
    gross_profit: float = 0               # 毛利润
    operating_expenses: float = 0         # 营业费用
    operating_profit: float = 0           # 营业利润
    net_profit: float = 0                 # 净利润
    interest_expense: float = 0           # 利息费用
    tax_expense: float = 0                # 所得税费用
    depreciation: float = 0               # 折旧
    amortization: float = 0               # 摊销
    
    # 资产负债表
    total_assets: float = 0               # 总资产
    current_assets: float = 0             # 流动资产
    inventory: float = 0                  # 存货
    accounts_receivable: float = 0        # 应收账款
    total_liabilities: float = 0          # 总负债
    current_liabilities: float = 0        # 流动负债
    shareholders_equity: float = 0        # 股东权益
    interest_bearing_debt: float = 0      # 有息负债
    
    # 现金流量表
    operating_cash_flow: float = 0        # 经营活动现金流
    investing_cash_flow: float = 0        # 投资活动现金流
    financing_cash_flow: float = 0        # 筹资活动现金流
    capex: float = 0                      # 资本支出
    
    # 其他
    total_shares: float = 0               # 总股本（亿股）
    
    @property
    def gross_margin(self) -> Optional[float]:
        """毛利率 (%)"""
        if self.revenue == 0:
            return None
        return (self.revenue - self.cost_of_goods_sold) / self.revenue * 100
    
    @property
    def net_margin(self) -> Optional[float]:
        """净利率 (%)"""
        if self.revenue == 0:
            return None
        return self.net_profit / self.revenue * 100
    
    @property
    def operating_margin(self) -> Optional[float]:
        """营业利润率 (%)"""
        if self.revenue == 0:
            return None
        return self.operating_profit / self.revenue * 100
    
    @property
    def ebitda(self) -> float:
        """EBITDA"""
        return self.operating_profit + self.depreciation + self.amortization
    
    @property
    def ebitda_margin(self) -> Optional[float]:
        """EBITDA利润率 (%)"""
        if self.revenue == 0:
            return None
        return self.ebitda / self.revenue * 100
    
    @property
    def roe(self) -> Optional[float]:
        """净资产收益率 ROE (%)"""
        if self.shareholders_equity == 0:
            return None
        return self.net_profit / self.shareholders_equity * 100
    
    @property
    def roa(self) -> Optional[float]:
        """总资产收益率 ROA (%)"""
        if self.total_assets == 0:
            return None
        return self.net_profit / self.total_assets * 100
    
    @property
    def roic(self) -> Optional[float]:
        """投入资本回报率 ROIC (%)"""
        nopat = self.operating_profit * (1 - 0.25)  # 假设税率25%
        invested_capital = self.shareholders_equity + self.interest_bearing_debt
        if invested_capital == 0:
            return None
        return nopat / invested_capital * 100
    
    @property
    def debt_to_asset(self) -> Optional[float]:
        """资产负债率 (%)"""
        if self.total_assets == 0:
            return None
        return self.total_liabilities / self.total_assets * 100
    
    @property
    def debt_to_equity(self) -> Optional[float]:
        """产权比率 (%)"""
        if self.shareholders_equity == 0:
            return None
        return self.total_liabilities / self.shareholders_equity * 100
    
    @property
    def current_ratio(self) -> Optional[float]:
        """流动比率"""
        if self.current_liabilities == 0:
            return None
        return self.current_assets / self.current_liabilities
    
    @property
    def quick_ratio(self) -> Optional[float]:
        """速动比率"""
        if self.current_liabilities == 0:
            return None
        return (self.current_assets - self.inventory) / self.current_liabilities
    
    @property
    def interest_coverage(self) -> Optional[float]:
        """利息保障倍数"""
        if self.interest_expense == 0:
            return None
        return (self.operating_profit + self.interest_expense) / self.interest_expense
    
    @property
    def inventory_turnover(self) -> Optional[float]:
        """存货周转率 (次)"""
        if self.inventory == 0:
            return None
        return self.cost_of_goods_sold / self.inventory
    
    @property
    def receivable_turnover(self) -> Optional[float]:
        """应收账款周转率 (次)"""
        if self.accounts_receivable == 0:
            return None
        return self.revenue / self.accounts_receivable
    
    @property
    def asset_turnover(self) -> Optional[float]:
        """总资产周转率 (次)"""
        if self.total_assets == 0:
            return None
        return self.revenue / self.total_assets
    
    @property
    def days_sales_outstanding(self) -> Optional[float]:
        """应收账款周转天数"""
        if self.receivable_turnover is None or self.receivable_turnover == 0:
            return None
        return 365 / self.receivable_turnover
    
    @property
    def days_inventory_outstanding(self) -> Optional[float]:
        """存货周转天数"""
        if self.inventory_turnover is None or self.inventory_turnover == 0:
            return None
        return 365 / self.inventory_turnover
    
    @property
    def cash_conversion_cycle(self) -> Optional[float]:
        """现金转换周期"""
        if (self.days_sales_outstanding is None or 
            self.days_inventory_outstanding is None):
            return None
        # 简化计算，假设应付账款周转天数为0
        return self.days_inventory_outstanding + self.days_sales_outstanding
    
    @property
    def free_cash_flow(self) -> float:
        """自由现金流 = 经营现金流 - 资本支出"""
        return self.operating_cash_flow - self.capex
    
    @property
    def ocf_to_net_profit(self) -> Optional[float]:
        """经营现金流/净利润"""
        if self.net_profit == 0:
            return None
        return self.operating_cash_flow / self.net_profit
    
    @property
    def ocf_to_revenue(self) -> Optional[float]:
        """经营现金流/营业收入"""
        if self.revenue == 0:
            return None
        return self.operating_cash_flow / self.revenue
    
    @property
    def eps(self) -> Optional[float]:
        """每股收益"""
        if self.total_shares == 0:
            return None
        return self.net_profit / self.total_shares
    
    @property
    def bps(self) -> Optional[float]:
        """每股净资产"""
        if self.total_shares == 0:
            return None
        return self.shareholders_equity / self.total_shares


class MetricsCalculator(LogMixin):
    """财务指标计算器"""
    
    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> Optional[float]:
        """
        计算增长率
        
        Args:
            current: 当期值
            previous: 上期值
        
        Returns:
            增长率 (%)
        """
        if previous == 0:
            return None
        return (current - previous) / previous * 100
    
    @staticmethod
    def calculate_cagr(begin_value: float, end_value: float, years: int) -> Optional[float]:
        """
        计算复合年增长率 CAGR
        
        Args:
            begin_value: 期初值
            end_value: 期末值
            years: 年数
        
        Returns:
            CAGR (%)
        """
        if begin_value <= 0 or years <= 0:
            return None
        return ((end_value / begin_value) ** (1 / years) - 1) * 100
    
    @staticmethod
    def calculate_all_metrics(statement: FinancialStatement) -> Dict[str, Optional[float]]:
        """
        计算所有财务指标
        
        Args:
            statement: 财务报表
        
        Returns:
            指标字典
        """
        return {
            "毛利率": statement.gross_margin,
            "净利率": statement.net_margin,
            "营业利润率": statement.operating_margin,
            "EBITDA利润率": statement.ebitda_margin,
            "ROE": statement.roe,
            "ROA": statement.roa,
            "ROIC": statement.roic,
            "资产负债率": statement.debt_to_asset,
            "产权比率": statement.debt_to_equity,
            "流动比率": statement.current_ratio,
            "速动比率": statement.quick_ratio,
            "利息保障倍数": statement.interest_coverage,
            "存货周转率": statement.inventory_turnover,
            "应收账款周转率": statement.receivable_turnover,
            "总资产周转率": statement.asset_turnover,
            "应收账款周转天数": statement.days_sales_outstanding,
            "存货周转天数": statement.days_inventory_outstanding,
            "现金转换周期": statement.cash_conversion_cycle,
            "自由现金流": statement.free_cash_flow,
            "经营现金流净利润比": statement.ocf_to_net_profit,
            "EPS": statement.eps,
            "BPS": statement.bps,
        }
    
    @staticmethod
    def evaluate_metric(
        metric_name: str, 
        value: Optional[float],
        industry: Optional[Industry] = None,
    ) -> str:
        """
        评估指标水平
        
        Args:
            metric_name: 指标名称
            value: 指标值
            industry: 行业，用于获取行业基准
        
        Returns:
            评估结果字符串
        """
        if value is None:
            return "N/A"
        
        # 获取基准值
        benchmarks = get_benchmark(industry, metric_name)
        if not benchmarks:
            return f"{value:.2f}"
        
        # 资产负债率、产权比率：越低越好
        if metric_name in ["资产负债率", "产权比率"]:
            for threshold, level in [("danger", "危险"), ("warning", "关注"), ("safe", "安全")]:
                if threshold in benchmarks and value <= benchmarks[threshold]:
                    return f"{value:.2f}% ({level})" if "%" in metric_name else f"{value:.2f} ({level})"
            return f"{value:.2f}% (危险)" if "%" in metric_name else f"{value:.2f} (危险)"
        
        # 其他指标：越高越好
        for threshold, level in [("excellent", "优秀"), ("good", "良好"), ("average", "一般")]:
            if threshold in benchmarks and value >= benchmarks[threshold]:
                return f"{value:.2f}% ({level})" if "%" in metric_name else f"{value:.2f} ({level})"
        return f"{value:.2f}% (一般)" if "%" in metric_name else f"{value:.2f} (一般)"
    
    @staticmethod
    def calculate_metrics_from_statement(
        statement: FinancialStatement,
        report_date: str,
    ) -> FinancialMetrics:
        """
        从财务报表计算完整指标
        
        Args:
            statement: 财务报表
            report_date: 报告期
        
        Returns:
            FinancialMetrics 对象
        """
        return FinancialMetrics(
            profitability=ProfitabilityMetrics(
                gross_margin=statement.gross_margin,
                net_margin=statement.net_margin,
                roe=statement.roe,
                roa=statement.roa,
                roic=statement.roic,
                ebitda_margin=statement.ebitda_margin,
            ),
            solvency=SolvencyMetrics(
                debt_to_asset=statement.debt_to_asset,
                current_ratio=statement.current_ratio,
                quick_ratio=statement.quick_ratio,
                interest_coverage=statement.interest_coverage,
                debt_to_equity=statement.debt_to_equity,
            ),
            efficiency=EfficiencyMetrics(
                inventory_turnover=statement.inventory_turnover,
                receivable_turnover=statement.receivable_turnover,
                asset_turnover=statement.asset_turnover,
                days_sales_outstanding=statement.days_sales_outstanding,
                days_inventory_outstanding=statement.days_inventory_outstanding,
                cash_conversion_cycle=statement.cash_conversion_cycle,
            ),
            cashflow=CashflowMetrics(
                operating_cash_flow=statement.operating_cash_flow,
                investing_cash_flow=statement.investing_cash_flow,
                financing_cash_flow=statement.financing_cash_flow,
                free_cash_flow=statement.free_cash_flow,
                ocf_to_net_profit=statement.ocf_to_net_profit,
                ocf_to_revenue=statement.ocf_to_revenue,
            ),
            report_date=report_date,
        )


class PeerComparator(LogMixin):
    """同业对比分析"""
    
    @staticmethod
    def compare_metrics(
        companies: List[Dict[str, Any]], 
        metrics: List[str],
    ) -> Dict[str, Any]:
        """
        对比多家公司的指标
        
        Args:
            companies: [{"name": "公司A", "metrics": {"ROE": 15, ...}}, ...]
            metrics: ["ROE", "毛利率", ...]
        
        Returns:
            对比结果，包含排名、均值、极值
        """
        result = {}
        
        for metric in metrics:
            values = []
            for company in companies:
                val = company.get("metrics", {}).get(metric)
                if val is not None:
                    values.append({
                        "name": company["name"],
                        "value": val,
                    })
            
            if not values:
                continue
            
            # 排序（数值越高越好，负债率除外）
            reverse = metric not in ["资产负债率", "产权比率"]
            values.sort(key=lambda x: x["value"], reverse=reverse)
            
            # 计算统计值
            all_vals = [v["value"] for v in values]
            result[metric] = {
                "ranking": values,
                "mean": sum(all_vals) / len(all_vals),
                "max": max(all_vals),
                "min": min(all_vals),
                "median": sorted(all_vals)[len(all_vals) // 2],
            }
        
        return result
    
    @staticmethod
    def generate_comparison_table(
        companies: List[Dict[str, Any]], 
        metrics: List[str],
    ) -> str:
        """
        生成对比表格（Markdown格式）
        
        Args:
            companies: 公司列表
            metrics: 指标列表
        
        Returns:
            Markdown 表格字符串
        """
        lines = ["| 指标 | " + " | ".join([c["name"] for c in companies]) + " | 行业平均 |"]
        lines.append("|" + "-" * 6 + "|" + "|".join(["-" * 10 for _ in companies]) + "|" + "-" * 10 + "|")
        
        for metric in metrics:
            row = [f"| {metric} |"]
            values = []
            for company in companies:
                val = company.get("metrics", {}).get(metric)
                values.append(val)
                if val is not None:
                    row.append(f" {val:.2f} |")
                else:
                    row.append(" N/A |")
            
            # 行业平均
            valid_values = [v for v in values if v is not None]
            if valid_values:
                avg = sum(valid_values) / len(valid_values)
                row.append(f" {avg:.2f} |")
            else:
                row.append(" N/A |")
            
            lines.append("".join(row))
        
        return "\n".join(lines)
