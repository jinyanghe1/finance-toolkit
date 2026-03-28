"""
Finance Toolkit - 趋势分析
Trend Analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models import FinancialMetrics
from ..logger import get_logger

logger = get_logger(__name__)


class TrendDirection(str, Enum):
    """趋势方向"""
    UP = "up"           # 上升
    DOWN = "down"       # 下降
    STABLE = "stable"   # 平稳
    VOLATILE = "volatile"  # 波动


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    metric_name: str
    direction: TrendDirection
    change_pct: float           # 变化百分比
    avg_value: float            # 平均值
    latest_value: float         # 最新值
    volatility: float           # 波动率
    consistency: float          # 趋势一致性 (0-1)
    interpretation: str = ""    # 解读


class TrendAnalyzer:
    """趋势分析器"""
    
    @staticmethod
    def calculate_yoy(current: float, previous: float) -> Optional[float]:
        """
        计算同比增长率 (Year-over-Year)
        
        Args:
            current: 当期值
            previous: 去年同期值
        
        Returns:
            同比增长率 (%)
        """
        if previous == 0 or previous is None:
            return None
        return (current - previous) / previous * 100
    
    @staticmethod
    def calculate_qoq(current: float, previous: float) -> Optional[float]:
        """
        计算环比增长率 (Quarter-over-Quarter)
        
        Args:
            current: 当期值
            previous: 上期值
        
        Returns:
            环比增长率 (%)
        """
        if previous == 0 or previous is None:
            return None
        return (current - previous) / previous * 100
    
    @staticmethod
    def analyze_metric_trend(
        values: List[float],
        periods: List[str],
        metric_name: str = "",
        threshold: float = 5.0,
    ) -> Optional[TrendAnalysis]:
        """
        分析单个指标的趋势
        
        Args:
            values: 指标值列表（时间倒序）
            periods: 对应期间列表
            metric_name: 指标名称
            threshold: 变化阈值 (%)
        
        Returns:
            趋势分析结果
        """
        if len(values) < 2:
            return None
        
        # 过滤 None 值
        valid_data = [(v, p) for v, p in zip(values, periods) if v is not None]
        if len(valid_data) < 2:
            return None
        
        valid_values = [v for v, _ in valid_data]
        latest = valid_values[0]
        previous = valid_values[1]
        
        # 计算变化
        if previous != 0:
            change_pct = (latest - previous) / abs(previous) * 100
        else:
            change_pct = 0
        
        # 计算平均值
        avg_value = sum(valid_values) / len(valid_values)
        
        # 计算波动率（标准差/平均值）
        if len(valid_values) > 1 and avg_value != 0:
            variance = sum((v - avg_value) ** 2 for v in valid_values) / len(valid_values)
            std = variance ** 0.5
            volatility = std / abs(avg_value) * 100
        else:
            volatility = 0
        
        # 判断趋势方向
        if abs(change_pct) < threshold:
            direction = TrendDirection.STABLE
        elif change_pct > 0:
            # 检查是否持续上升
            increases = sum(1 for i in range(len(valid_values)-1) if valid_values[i] > valid_values[i+1])
            consistency = increases / (len(valid_values) - 1)
            direction = TrendDirection.UP if consistency > 0.6 else TrendDirection.VOLATILE
        else:
            # 检查是否持续下降
            decreases = sum(1 for i in range(len(valid_values)-1) if valid_values[i] < valid_values[i+1])
            consistency = decreases / (len(valid_values) - 1)
            direction = TrendDirection.DOWN if consistency > 0.6 else TrendDirection.VOLATILE
        
        # 生成解读
        interpretation = TrendAnalyzer._generate_interpretation(
            metric_name, direction, change_pct, volatility
        )
        
        return TrendAnalysis(
            metric_name=metric_name,
            direction=direction,
            change_pct=change_pct,
            avg_value=avg_value,
            latest_value=latest,
            volatility=volatility,
            consistency=consistency if 'consistency' in dir() else 0.5,
            interpretation=interpretation,
        )
    
    @staticmethod
    def _generate_interpretation(
        metric_name: str,
        direction: TrendDirection,
        change_pct: float,
        volatility: float,
    ) -> str:
        """生成趋势解读"""
        parts = []
        
        # 方向描述
        if direction == TrendDirection.UP:
            parts.append(f"{metric_name}呈上升趋势")
        elif direction == TrendDirection.DOWN:
            parts.append(f"{metric_name}呈下降趋势")
        elif direction == TrendDirection.STABLE:
            parts.append(f"{metric_name}保持平稳")
        else:
            parts.append(f"{metric_name}波动较大")
        
        # 变化幅度
        if abs(change_pct) >= 20:
            parts.append(f"变化显著 ({change_pct:+.1f}%)")
        elif abs(change_pct) >= 10:
            parts.append(f"变化明显 ({change_pct:+.1f}%)")
        elif abs(change_pct) >= 5:
            parts.append(f"小幅变化 ({change_pct:+.1f}%)")
        
        # 波动率
        if volatility > 30:
            parts.append("历史波动较大")
        elif volatility < 10:
            parts.append("历史表现稳定")
        
        return "。".join(parts) + "。"
    
    @staticmethod
    def analyze_financial_metrics(
        metrics_list: List[FinancialMetrics],
    ) -> Dict[str, TrendAnalysis]:
        """
        分析财务指标趋势
        
        Args:
            metrics_list: 财务指标列表（时间倒序）
        
        Returns:
            各指标的趋势分析
        """
        if len(metrics_list) < 2:
            return {}
        
        results = {}
        periods = [m.report_date for m in metrics_list]
        
        # 盈利能力指标
        roe_values = [m.profitability.roe for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(roe_values, periods, "ROE")
        if trend:
            results["roe"] = trend
        
        gross_margin_values = [m.profitability.gross_margin for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(gross_margin_values, periods, "毛利率")
        if trend:
            results["gross_margin"] = trend
        
        net_margin_values = [m.profitability.net_margin for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(net_margin_values, periods, "净利率")
        if trend:
            results["net_margin"] = trend
        
        # 成长能力指标
        revenue_growth_values = [m.growth.revenue_growth_yoy for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(revenue_growth_values, periods, "营收增长")
        if trend:
            results["revenue_growth"] = trend
        
        # 偿债能力指标
        debt_values = [m.solvency.debt_to_asset for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(debt_values, periods, "资产负债率")
        if trend:
            results["debt_to_asset"] = trend
        
        # 现金流指标
        fcf_values = [m.cashflow.free_cash_flow for m in metrics_list]
        trend = TrendAnalyzer.analyze_metric_trend(fcf_values, periods, "自由现金流")
        if trend:
            results["free_cash_flow"] = trend
        
        return results
    
    @staticmethod
    def generate_trend_report(trends: Dict[str, TrendAnalysis]) -> str:
        """
        生成趋势分析报告
        
        Args:
            trends: 趋势分析结果
        
        Returns:
            Markdown 格式报告
        """
        lines = ["## 趋势分析", ""]
        
        if not trends:
            lines.append("数据不足，无法进行趋势分析。")
            return "\n".join(lines)
        
        # 按方向分类
        up_trends = []
        down_trends = []
        stable_trends = []
        
        for name, trend in trends.items():
            if trend.direction == TrendDirection.UP:
                up_trends.append((name, trend))
            elif trend.direction == TrendDirection.DOWN:
                down_trends.append((name, trend))
            else:
                stable_trends.append((name, trend))
        
        # 积极信号
        if up_trends:
            lines.append("### 📈 积极信号")
            for name, trend in up_trends:
                lines.append(f"- **{trend.metric_name}**: {trend.change_pct:+.1f}% {trend.interpretation}")
            lines.append("")
        
        # 风险提示
        if down_trends:
            lines.append("### 📉 风险提示")
            for name, trend in down_trends:
                lines.append(f"- **{trend.metric_name}**: {trend.change_pct:+.1f}% {trend.interpretation}")
            lines.append("")
        
        # 稳定指标
        if stable_trends:
            lines.append("### 📊 稳定指标")
            for name, trend in stable_trends:
                lines.append(f"- **{trend.metric_name}**: {trend.interpretation}")
            lines.append("")
        
        return "\n".join(lines)
