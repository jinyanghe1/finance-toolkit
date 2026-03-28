"""
Finance Toolkit - 分析模块
"""

from .metrics import (
    FinancialStatement,
    MetricsCalculator,
    PeerComparator,
)
from .company import (
    CompanyAnalyzer,
    analyze_company,
    get_company_summary,
    list_companies,
)
from .dupont import (
    DupontAnalysis,
    DupontComponents,
    DupontAnalyzer,
)
from .valuation import (
    DCFAssumptions,
    DCFResult,
    DCFValuation,
    RelativeValuation,
    RelativeValuationResult,
    ValuationAnalyzer,
    ValuationMethod,
)
from .trend import (
    TrendAnalysis,
    TrendAnalyzer,
    TrendDirection,
)

__all__ = [
    # Metrics
    "FinancialStatement",
    "MetricsCalculator",
    "PeerComparator",
    # Company
    "CompanyAnalyzer",
    "analyze_company",
    "get_company_summary",
    "list_companies",
    # Dupont
    "DupontAnalysis",
    "DupontComponents",
    "DupontAnalyzer",
    # Valuation
    "DCFAssumptions",
    "DCFResult",
    "DCFValuation",
    "RelativeValuation",
    "RelativeValuationResult",
    "ValuationAnalyzer",
    "ValuationMethod",
    # Trend
    "TrendAnalysis",
    "TrendAnalyzer",
    "TrendDirection",
]
