"""
Finance Toolkit - 金融数据分析工具

系统化金融数据分析工具，用于A股公司投研分析和行业研究。

Usage:
    from finance_toolkit import CompanyAnalyzer
    
    analyzer = CompanyAnalyzer()
    analyzer.create_profile(code="600519", name="贵州茅台")
    report = analyzer.generate_report("600519")
"""

from .__version__ import (
    __version__,
    __title__,
    __description__,
    __author__,
    __license__,
)

from .models import (
    StockInfo,
    CompanyProfile,
    FinancialMetrics,
    Industry,
    Exchange,
)

from .analyzer.company import CompanyAnalyzer
from .data.db import CompanyDB, get_company_db
from .config import load_config, get_config
from .exceptions import FinanceToolkitError

__all__ = [
    # Metadata
    "__version__",
    "__title__",
    "__description__",
    "__author__",
    "__license__",
    # Models
    "StockInfo",
    "CompanyProfile",
    "FinancialMetrics",
    "Industry",
    "Exchange",
    # Main Classes
    "CompanyAnalyzer",
    "CompanyDB",
    # Functions
    "get_company_db",
    "load_config",
    "get_config",
    # Exceptions
    "FinanceToolkitError",
]
