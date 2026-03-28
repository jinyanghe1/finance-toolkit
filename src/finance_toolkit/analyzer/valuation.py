"""
Finance Toolkit - 估值模型
Valuation Models

包含:
- DCF (现金流折现)
- 相对估值 (PE/PB/PS)
- DDM (股利折现)
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum

from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


class ValuationMethod(str, Enum):
    """估值方法"""
    DCF = "dcf"
    PE = "pe"
    PB = "pb"
    PS = "ps"
    DDM = "ddm"


@dataclass
class DCFAssumptions:
    """DCF 估值假设"""
    forecast_years: int = 5           # 预测年数
    revenue_growth: float = 0.10      # 营收增长率
    operating_margin: float = 0.15    # 营业利润率
    tax_rate: float = 0.25            # 税率
    depreciation_rate: float = 0.05   # 折旧率
    capex_rate: float = 0.07          # 资本支出率
    nwc_rate: float = 0.02            # 营运资本变动率
    terminal_growth: float = 0.03     # 永续增长率
    wacc: float = 0.09                # 加权平均资本成本


@dataclass
class DCFResult:
    """DCF 估值结果"""
    enterprise_value: float           # 企业价值
    equity_value: float               # 股权价值
    per_share_value: float            # 每股价值
    
    # 明细
    pv_forecast_fcf: float            # 预测期自由现金流现值
    pv_terminal: float                # 终值现值
    terminal_value: float             # 终值
    
    # 假设
    assumptions: DCFAssumptions
    
    # 分析
    upside_downside: Optional[float] = None  # 相对当前价格的涨跌空间
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enterprise_value": round(self.enterprise_value, 2),
            "equity_value": round(self.equity_value, 2),
            "per_share_value": round(self.per_share_value, 2),
            "pv_forecast_fcf": round(self.pv_forecast_fcf, 2),
            "pv_terminal": round(self.pv_terminal, 2),
            "terminal_value": round(self.terminal_value, 2),
            "upside_downside": round(self.upside_downside, 2) if self.upside_downside else None,
            "assumptions": {
                "wacc": self.assumptions.wacc,
                "terminal_growth": self.assumptions.terminal_growth,
                "forecast_years": self.assumptions.forecast_years,
            },
        }


@dataclass
class RelativeValuationResult:
    """相对估值结果"""
    method: ValuationMethod           # 估值方法
    implied_value: float              # 隐含价值
    per_share_value: float            # 每股价值
    
    # 参考倍数
    reference_multiple: float         # 参考倍数
    company_metric: float             # 公司对应指标
    
    # 分析
    upside_downside: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method.value,
            "implied_value": round(self.implied_value, 2),
            "per_share_value": round(self.per_share_value, 2),
            "reference_multiple": self.reference_multiple,
            "company_metric": round(self.company_metric, 2),
            "upside_downside": round(self.upside_downside, 2) if self.upside_downside else None,
        }


class DCFValuation:
    """DCF 估值模型"""
    
    @staticmethod
    def calculate(
        current_revenue: float,
        current_operating_profit: float,
        current_depreciation: float,
        current_capex: float,
        current_nwc: float,
        net_debt: float,
        shares: float,
        assumptions: Optional[DCFAssumptions] = None,
    ) -> DCFResult:
        """
        执行 DCF 估值
        
        Args:
            current_revenue: 当前营收
            current_operating_profit: 当前营业利润
            current_depreciation: 当前折旧
            current_capex: 当前资本支出
            current_nwc: 当前营运资本变动
            net_debt: 净债务
            shares: 总股本
            assumptions: 估值假设
        
        Returns:
            DCF 估值结果
        """
        if assumptions is None:
            config = get_config()
            assumptions = DCFAssumptions(
                terminal_growth=config.valuation.terminal_growth_rate,
                forecast_years=config.valuation.forecast_years,
            )
        
        # 计算未来自由现金流
        fcf_list = []
        revenue = current_revenue
        
        for year in range(1, assumptions.forecast_years + 1):
            # 预测营收
            revenue = revenue * (1 + assumptions.revenue_growth)
            
            # 预测营业利润
            ebit = revenue * assumptions.operating_margin
            
            # 预测税后营业利润
            nopat = ebit * (1 - assumptions.tax_rate)
            
            # 预测折旧
            depreciation = revenue * assumptions.depreciation_rate
            
            # 预测资本支出
            capex = revenue * assumptions.capex_rate
            
            # 预测营运资本变动
            nwc_change = revenue * assumptions.nwc_rate
            
            # 自由现金流
            fcf = nopat + depreciation - capex - nwc_change
            fcf_list.append(fcf)
        
        # 计算现值
        pv_fcf = 0
        for i, fcf in enumerate(fcf_list):
            pv_fcf += fcf / ((1 + assumptions.wacc) ** (i + 1))
        
        # 计算终值
        terminal_fcf = fcf_list[-1] * (1 + assumptions.terminal_growth)
        terminal_value = terminal_fcf / (assumptions.wacc - assumptions.terminal_growth)
        pv_terminal = terminal_value / ((1 + assumptions.wacc) ** assumptions.forecast_years)
        
        # 企业价值和股权价值
        enterprise_value = pv_fcf + pv_terminal
        equity_value = enterprise_value - net_debt
        per_share_value = equity_value / shares if shares > 0 else 0
        
        return DCFResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            per_share_value=per_share_value,
            pv_forecast_fcf=pv_fcf,
            pv_terminal=pv_terminal,
            terminal_value=terminal_value,
            assumptions=assumptions,
        )
    
    @staticmethod
    def sensitivity_analysis(
        base_result: DCFResult,
        wacc_range: List[float] = None,
        growth_range: List[float] = None,
    ) -> Dict[str, Any]:
        """
        DCF 敏感性分析
        
        Args:
            base_result: 基础估值结果
            wacc_range: WACC 变化范围
            growth_range: 永续增长率变化范围
        
        Returns:
            敏感性分析结果
        """
        if wacc_range is None:
            wacc_range = [0.07, 0.08, 0.09, 0.10, 0.11]
        if growth_range is None:
            growth_range = [0.01, 0.02, 0.03, 0.04, 0.05]
        
        base = base_result.assumptions
        results = {}
        
        for wacc in wacc_range:
            results[f"wacc_{wacc:.0%}"] = {}
            for g in growth_range:
                # 简化的敏感性计算
                if wacc <= g:
                    value = None  # 无效
                else:
                    # 重新计算终值现值
                    terminal_fcf = base_result.terminal_value * (wacc - base.terminal_growth)
                    terminal_fcf = terminal_fcf * (1 + g)
                    terminal_value = terminal_fcf / (wacc - g)
                    pv_terminal = terminal_value / ((1 + wacc) ** base.forecast_years)
                    
                    ev = base_result.pv_forecast_fcf + pv_terminal
                    eq_value = ev - (base_result.enterprise_value - base_result.equity_value)
                    per_share = eq_value / (base_result.equity_value / base_result.per_share_value)
                    
                    value = round(per_share, 2)
                
                results[f"wacc_{wacc:.0%}"][f"g_{g:.0%}"] = value
        
        return {
            "base_per_share": round(base_result.per_share_value, 2),
            "matrix": results,
        }


class RelativeValuation:
    """相对估值模型"""
    
    @staticmethod
    def pe_valuation(
        net_profit: float,
        shares: float,
        pe_multiple: float,
        current_price: Optional[float] = None,
    ) -> RelativeValuationResult:
        """
        PE 估值
        
        Args:
            net_profit: 净利润
            shares: 总股本
            pe_multiple: 参考PE倍数
            current_price: 当前股价
        
        Returns:
            估值结果
        """
        eps = net_profit / shares if shares > 0 else 0
        per_share_value = eps * pe_multiple
        
        upside = None
        if current_price and current_price > 0:
            upside = (per_share_value - current_price) / current_price * 100
        
        return RelativeValuationResult(
            method=ValuationMethod.PE,
            implied_value=net_profit * pe_multiple,
            per_share_value=per_share_value,
            reference_multiple=pe_multiple,
            company_metric=eps,
            upside_downside=upside,
        )
    
    @staticmethod
    def pb_valuation(
        net_assets: float,
        shares: float,
        pb_multiple: float,
        current_price: Optional[float] = None,
    ) -> RelativeValuationResult:
        """
        PB 估值
        
        Args:
            net_assets: 净资产
            shares: 总股本
            pb_multiple: 参考PB倍数
            current_price: 当前股价
        
        Returns:
            估值结果
        """
        bps = net_assets / shares if shares > 0 else 0
        per_share_value = bps * pb_multiple
        
        upside = None
        if current_price and current_price > 0:
            upside = (per_share_value - current_price) / current_price * 100
        
        return RelativeValuationResult(
            method=ValuationMethod.PB,
            implied_value=net_assets * pb_multiple,
            per_share_value=per_share_value,
            reference_multiple=pb_multiple,
            company_metric=bps,
            upside_downside=upside,
        )
    
    @staticmethod
    def ps_valuation(
        revenue: float,
        shares: float,
        ps_multiple: float,
        current_price: Optional[float] = None,
    ) -> RelativeValuationResult:
        """
        PS 估值
        
        Args:
            revenue: 营业收入
            shares: 总股本
            ps_multiple: 参考PS倍数
            current_price: 当前股价
        
        Returns:
            估值结果
        """
        sps = revenue / shares if shares > 0 else 0
        per_share_value = sps * ps_multiple
        
        upside = None
        if current_price and current_price > 0:
            upside = (per_share_value - current_price) / current_price * 100
        
        return RelativeValuationResult(
            method=ValuationMethod.PS,
            implied_value=revenue * ps_multiple,
            per_share_value=per_share_value,
            reference_multiple=ps_multiple,
            company_metric=sps,
            upside_downside=upside,
        )
    
    @staticmethod
    def compare_multiples(
        company_metrics: Dict[str, float],
        peer_multiples: Dict[str, List[float]],
    ) -> Dict[str, Any]:
        """
        对比公司与同业的估值倍数
        
        Args:
            company_metrics: {"pe": 15.0, "pb": 2.0, ...}
            peer_multiples: {"pe": [10, 12, 15, 18, 20], ...}
        
        Returns:
            对比结果
        """
        result = {}
        
        for metric, company_value in company_metrics.items():
            peers = peer_multiples.get(metric, [])
            if not peers:
                continue
            
            avg = sum(peers) / len(peers)
            median = sorted(peers)[len(peers) // 2]
            min_val = min(peers)
            max_val = max(peers)
            
            # 计算百分位
            percentile = sum(1 for p in peers if p <= company_value) / len(peers) * 100
            
            result[metric] = {
                "company": company_value,
                "peer_average": round(avg, 2),
                "peer_median": round(median, 2),
                "peer_range": [round(min_val, 2), round(max_val, 2)],
                "percentile": round(percentile, 1),
                "vs_average": round((company_value - avg) / avg * 100, 1) if avg > 0 else 0,
            }
        
        return result


class ValuationAnalyzer:
    """估值分析器"""
    
    @staticmethod
    def comprehensive_valuation(
        dcf_params: Dict[str, Any],
        relative_params: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        综合估值分析
        
        Args:
            dcf_params: DCF 参数
            relative_params: 相对估值参数
            weights: 各方法权重
        
        Returns:
            综合估值结果
        """
        if weights is None:
            weights = {"dcf": 0.5, "pe": 0.3, "pb": 0.2}
        
        results = {}
        weighted_value = 0
        total_weight = 0
        
        # DCF
        if "dcf" in weights and dcf_params:
            dcf_result = DCFValuation.calculate(**dcf_params)
            results["dcf"] = dcf_result.to_dict()
            weighted_value += dcf_result.per_share_value * weights["dcf"]
            total_weight += weights["dcf"]
        
        # PE
        if "pe" in weights and relative_params.get("pe"):
            pe_result = RelativeValuation.pe_valuation(**relative_params["pe"])
            results["pe"] = pe_result.to_dict()
            weighted_value += pe_result.per_share_value * weights["pe"]
            total_weight += weights["pe"]
        
        # PB
        if "pb" in weights and relative_params.get("pb"):
            pb_result = RelativeValuation.pb_valuation(**relative_params["pb"])
            results["pb"] = pb_result.to_dict()
            weighted_value += pb_result.per_share_value * weights["pb"]
            total_weight += weights["pb"]
        
        # 加权平均
        if total_weight > 0:
            fair_value = weighted_value / total_weight
            results["fair_value"] = round(fair_value, 2)
            
            # 计算相对当前价格的涨跌空间
            if "current_price" in relative_params:
                current = relative_params["current_price"]
                upside = (fair_value - current) / current * 100
                results["upside_downside"] = round(upside, 2)
                
                # 投资建议
                if upside >= 30:
                    results["recommendation"] = "强烈买入"
                elif upside >= 15:
                    results["recommendation"] = "买入"
                elif upside >= -10:
                    results["recommendation"] = "持有"
                elif upside >= -25:
                    results["recommendation"] = "减持"
                else:
                    results["recommendation"] = "卖出"
        
        results["weights_used"] = weights
        return results
