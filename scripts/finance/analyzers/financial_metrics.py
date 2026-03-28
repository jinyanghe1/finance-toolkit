"""
金融功能库 - 财务指标计算
Financial Metrics Calculator
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

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
    
    # 资产负债表
    total_assets: float = 0               # 总资产
    current_assets: float = 0             # 流动资产
    inventory: float = 0                  # 存货
    accounts_receivable: float = 0        # 应收账款
    total_liabilities: float = 0          # 总负债
    current_liabilities: float = 0        # 流动负债
    shareholders_equity: float = 0        # 股东权益
    
    # 现金流量表
    operating_cash_flow: float = 0        # 经营活动现金流
    investing_cash_flow: float = 0        # 投资活动现金流
    financing_cash_flow: float = 0        # 筹资活动现金流
    
    # 其他
    total_shares: float = 0               # 总股本（亿股）
    
    @property
    def gross_margin(self) -> Optional[float]:
        """毛利率"""
        if self.revenue == 0:
            return None
        return (self.revenue - self.cost_of_goods_sold) / self.revenue * 100
    
    @property
    def net_margin(self) -> Optional[float]:
        """净利率"""
        if self.revenue == 0:
            return None
        return self.net_profit / self.revenue * 100
    
    @property
    def roe(self) -> Optional[float]:
        """净资产收益率 ROE"""
        if self.shareholders_equity == 0:
            return None
        return self.net_profit / self.shareholders_equity * 100
    
    @property
    def roa(self) -> Optional[float]:
        """总资产收益率 ROA"""
        if self.total_assets == 0:
            return None
        return self.net_profit / self.total_assets * 100
    
    @property
    def debt_to_asset(self) -> Optional[float]:
        """资产负债率"""
        if self.total_assets == 0:
            return None
        return self.total_liabilities / self.total_assets * 100
    
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
    def inventory_turnover(self) -> Optional[float]:
        """存货周转率"""
        if self.inventory == 0:
            return None
        return self.cost_of_goods_sold / self.inventory
    
    @property
    def receivable_turnover(self) -> Optional[float]:
        """应收账款周转率"""
        if self.accounts_receivable == 0:
            return None
        return self.revenue / self.accounts_receivable
    
    @property
    def asset_turnover(self) -> Optional[float]:
        """总资产周转率"""
        if self.total_assets == 0:
            return None
        return self.revenue / self.total_assets
    
    @property
    def free_cash_flow(self) -> float:
        """自由现金流 = 经营现金流 + 投资现金流"""
        return self.operating_cash_flow + self.investing_cash_flow
    
    @property
    def eps(self) -> Optional[float]:
        """每股收益"""
        if self.total_shares == 0:
            return None
        return self.net_profit / self.total_shares


class MetricsCalculator:
    """财务指标计算器"""
    
    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> Optional[float]:
        """计算增长率"""
        if previous == 0:
            return None
        return (current - previous) / previous * 100
    
    @staticmethod
    def calculate_cagr(begin_value: float, end_value: float, years: int) -> Optional[float]:
        """计算复合年增长率 CAGR"""
        if begin_value <= 0 or years <= 0:
            return None
        return ((end_value / begin_value) ** (1 / years) - 1) * 100
    
    @staticmethod
    def calculate_all_metrics(statement: FinancialStatement) -> Dict[str, Optional[float]]:
        """计算所有财务指标"""
        return {
            "毛利率": statement.gross_margin,
            "净利率": statement.net_margin,
            "ROE": statement.roe,
            "ROA": statement.roa,
            "资产负债率": statement.debt_to_asset,
            "流动比率": statement.current_ratio,
            "速动比率": statement.quick_ratio,
            "存货周转率": statement.inventory_turnover,
            "应收账款周转率": statement.receivable_turnover,
            "总资产周转率": statement.asset_turnover,
            "自由现金流": statement.free_cash_flow,
            "EPS": statement.eps,
        }
    
    @staticmethod
    def evaluate_metric(metric_name: str, value: Optional[float]) -> str:
        """评估指标水平"""
        if value is None:
            return "N/A"
        
        # 参考标准（可根据行业调整）
        benchmarks = {
            "ROE": [(20, "优秀"), (15, "良好"), (10, "一般")],
            "毛利率": [(40, "优秀"), (30, "良好"), (20, "一般")],
            "净利率": [(20, "优秀"), (10, "良好"), (5, "一般")],
            "资产负债率": [(50, "安全"), (70, "关注"), (80, "危险")],
            "流动比率": [(2.0, "优秀"), (1.5, "良好"), (1.0, "一般")],
            "速动比率": [(1.5, "优秀"), (1.0, "良好"), (0.8, "一般")],
        }
        
        if metric_name not in benchmarks:
            return f"{value:.2f}"
        
        thresholds = benchmarks[metric_name]
        
        # 对于资产负债率，数值越低越好，需要反向判断
        if metric_name == "资产负债率":
            for threshold, level in thresholds:
                if value <= threshold:
                    return f"{value:.2f}% ({level})"
            return f"{value:.2f}% (危险)"
        else:
            for threshold, level in thresholds:
                if value >= threshold:
                    return f"{value:.2f}% ({level})" if "%" in str(value) else f"{value:.2f} ({level})"
            return f"{value:.2f}% (一般)" if "%" in str(value) else f"{value:.2f} (一般)"


class PeerComparator:
    """同业对比分析"""
    
    @staticmethod
    def compare_metrics(companies: List[Dict], metrics: List[str]) -> Dict:
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
            reverse = metric != "资产负债率"
            values.sort(key=lambda x: x["value"], reverse=reverse)
            
            # 计算统计值
            all_vals = [v["value"] for v in values]
            result[metric] = {
                "ranking": values,
                "mean": sum(all_vals) / len(all_vals),
                "max": max(all_vals),
                "min": min(all_vals),
            }
        
        return result
    
    @staticmethod
    def generate_comparison_table(companies: List[Dict], metrics: List[str]) -> str:
        """生成对比表格（Markdown格式）"""
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
