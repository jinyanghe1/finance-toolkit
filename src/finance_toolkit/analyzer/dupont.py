"""
Finance Toolkit - 杜邦分析模型
DuPont Analysis Model

ROE = 净利率 × 总资产周转率 × 权益乘数
    = (净利润/营业收入) × (营业收入/总资产) × (总资产/净资产)
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass

from ..logger import get_logger
from .metrics import FinancialStatement

logger = get_logger(__name__)


@dataclass
class DupontComponents:
    """杜邦分析三要素"""
    net_margin: float           # 净利率 (%)
    asset_turnover: float       # 总资产周转率 (次)
    equity_multiplier: float    # 权益乘数
    
    def __post_init__(self):
        """验证数据有效性"""
        if self.equity_multiplier < 1:
            logger.warning(f"权益乘数异常: {self.equity_multiplier}")


@dataclass
class DupontAnalysis:
    """杜邦分析结果"""
    # 核心指标
    roe: float                          # ROE (%)
    components: DupontComponents        # 三要素
    
    # 中间指标
    net_profit: float                   # 净利润
    revenue: float                      # 营业收入
    total_assets: float                 # 总资产
    shareholders_equity: float          # 股东权益
    
    # 分析
    interpretation: str = ""            # 分析解读
    
    @property
    def roa(self) -> float:
        """ROA = 净利率 × 总资产周转率"""
        return self.components.net_margin * self.components.asset_turnover
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "roe": round(self.roe, 2),
            "roa": round(self.roa, 2),
            "components": {
                "net_margin": round(self.components.net_margin, 2),
                "asset_turnover": round(self.components.asset_turnover, 2),
                "equity_multiplier": round(self.components.equity_multiplier, 2),
            },
            "interpretation": self.interpretation,
        }
    
    def generate_report(self) -> str:
        """生成分析报告"""
        lines = [
            "## 杜邦分析",
            "",
            f"**ROE**: {self.roe:.2f}%",
            "",
            "### 三要素分解",
            f"- **净利率**: {self.components.net_margin:.2f}%",
            f"- **总资产周转率**: {self.components.asset_turnover:.2f} 次",
            f"- **权益乘数**: {self.components.equity_multiplier:.2f}",
            "",
            f"**验证**: {self.components.net_margin:.2f}% × {self.components.asset_turnover:.2f} × {self.components.equity_multiplier:.2f} = {self.roe:.2f}%",
            "",
            "### 分析解读",
            self.interpretation,
        ]
        return "\n".join(lines)


class DupontAnalyzer:
    """杜邦分析器"""
    
    @staticmethod
    def analyze(statement: FinancialStatement) -> Optional[DupontAnalysis]:
        """
        执行杜邦分析
        
        Args:
            statement: 财务报表
        
        Returns:
            杜邦分析结果，数据不足则返回 None
        """
        # 检查数据完整性
        if (statement.net_profit == 0 or 
            statement.revenue == 0 or 
            statement.total_assets == 0 or 
            statement.shareholders_equity == 0):
            logger.warning("杜邦分析: 数据不完整")
            return None
        
        # 计算三要素
        net_margin = statement.net_profit / statement.revenue * 100
        asset_turnover = statement.revenue / statement.total_assets
        equity_multiplier = statement.total_assets / statement.shareholders_equity
        
        # 计算 ROE
        roe = net_margin * asset_turnover * equity_multiplier
        
        # 生成分析解读
        interpretation = DupontAnalyzer._generate_interpretation(
            roe, net_margin, asset_turnover, equity_multiplier
        )
        
        return DupontAnalysis(
            roe=roe,
            components=DupontComponents(
                net_margin=net_margin,
                asset_turnover=asset_turnover,
                equity_multiplier=equity_multiplier,
            ),
            net_profit=statement.net_profit,
            revenue=statement.revenue,
            total_assets=statement.total_assets,
            shareholders_equity=statement.shareholders_equity,
            interpretation=interpretation,
        )
    
    @staticmethod
    def _generate_interpretation(
        roe: float,
        net_margin: float,
        asset_turnover: float,
        equity_multiplier: float,
    ) -> str:
        """生成分析解读"""
        parts = []
        
        # ROE 水平评价
        if roe >= 20:
            parts.append(f"ROE 高达 {roe:.1f}%，盈利能力非常优秀。")
        elif roe >= 15:
            parts.append(f"ROE 为 {roe:.1f}%，盈利能力良好。")
        elif roe >= 10:
            parts.append(f"ROE 为 {roe:.1f}%，盈利能力尚可。")
        else:
            parts.append(f"ROE 仅 {roe:.1f}%，盈利能力较弱。")
        
        # 驱动因素分析
        drivers = []
        
        # 净利率分析
        if net_margin >= 20:
            drivers.append("高净利率驱动")
        elif net_margin >= 10:
            drivers.append("中高净利率")
        else:
            drivers.append("净利率偏低")
        
        # 周转率分析
        if asset_turnover >= 1.5:
            drivers.append("高资产周转")
        elif asset_turnover >= 0.8:
            drivers.append("中等周转效率")
        else:
            drivers.append("资产周转较慢")
        
        # 杠杆分析
        if equity_multiplier >= 3:
            drivers.append("高财务杠杆")
        elif equity_multiplier >= 2:
            drivers.append("适度杠杆")
        else:
            drivers.append("低杠杆保守")
        
        parts.append(f"驱动因素: {' | '.join(drivers)}。")
        
        # 模式判断
        if net_margin >= 15 and asset_turnover < 1:
            parts.append("属于**高利润率低周转**模式（如茅台、奢侈品）。")
        elif net_margin < 10 and asset_turnover >= 1.5:
            parts.append("属于**低利润率高周转**模式（如零售、超市）。")
        elif equity_multiplier >= 3:
            parts.append("**注意**: 使用了较高的财务杠杆提升ROE。")
        
        return "\n".join(parts)
    
    @staticmethod
    def compare_periods(
        current: FinancialStatement,
        previous: FinancialStatement,
    ) -> Dict[str, Any]:
        """
        对比两期杜邦分析
        
        Args:
            current: 当期报表
            previous: 上期报表
        
        Returns:
            对比结果
        """
        current_analysis = DupontAnalyzer.analyze(current)
        previous_analysis = DupontAnalyzer.analyze(previous)
        
        if not current_analysis or not previous_analysis:
            return {"error": "数据不完整，无法对比"}
        
        # 计算变化
        def pct_change(current_val: float, previous_val: float) -> float:
            if previous_val == 0:
                return 0
            return (current_val - previous_val) / previous_val * 100
        
        return {
            "roe_change": {
                "absolute": round(current_analysis.roe - previous_analysis.roe, 2),
                "percentage": round(pct_change(current_analysis.roe, previous_analysis.roe), 2),
            },
            "components_change": {
                "net_margin": round(
                    current_analysis.components.net_margin - previous_analysis.components.net_margin, 2
                ),
                "asset_turnover": round(
                    current_analysis.components.asset_turnover - previous_analysis.components.asset_turnover, 2
                ),
                "equity_multiplier": round(
                    current_analysis.components.equity_multiplier - previous_analysis.components.equity_multiplier, 2
                ),
            },
            "current": current_analysis.to_dict(),
            "previous": previous_analysis.to_dict(),
        }
    
    @staticmethod
    def compare_companies(
        companies: Dict[str, FinancialStatement],
    ) -> Dict[str, Any]:
        """
        对比多家公司的杜邦分析
        
        Args:
            companies: {公司名称: 财务报表}
        
        Returns:
            对比结果
        """
        results = {}
        for name, statement in companies.items():
            analysis = DupontAnalyzer.analyze(statement)
            if analysis:
                results[name] = analysis
        
        if len(results) < 2:
            return {"error": "需要至少两家公司的完整数据"}
        
        # 按 ROE 排序
        sorted_companies = sorted(
            results.items(), 
            key=lambda x: x[1].roe, 
            reverse=True
        )
        
        return {
            "ranking": [
                {"name": name, "roe": round(a.roe, 2)} 
                for name, a in sorted_companies
            ],
            "details": {name: a.to_dict() for name, a in results.items()},
        }
