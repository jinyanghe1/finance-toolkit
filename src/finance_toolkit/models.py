"""
Finance Toolkit - 数据模型定义
Company Profile Schema 和 Financial Data Models
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from .logger import LogMixin


class Industry(str, Enum):
    """一级行业分类 (申万/中信标准)"""
    # 金融
    FINANCE = "金融"
    REAL_ESTATE = "房地产"
    MANUFACTURING = "制造业"
    TECHNOLOGY = "科技"
    HEALTHCARE = "医药健康"
    CONSUMER = "消费"
    ENERGY = "能源"
    MATERIALS = "材料"
    TELECOM = "电信"
    UTILITIES = "公用事业"
    TRANSPORTATION = "交通运输"
    MEDIA = "传媒"
    AGRICULTURE = "农林牧渔"
    CONSTRUCTION = "建筑"
    ENVIRONMENTAL = "环保"


class SubIndustry(str, Enum):
    """二级行业分类"""
    # 金融
    BANK = "银行"
    INSURANCE = "保险"
    SECURITIES = "证券"
    # 科技
    SEMICONDUCTOR = "半导体"
    SOFTWARE = "软件"
    ELECTRONICS = "电子"
    # 消费
    FOOD_BEVERAGE = "食品饮料"
    RETAIL = "零售"
    AUTOMOTIVE = "汽车"
    HOUSEHOLD = "家用电器"
    # 医药
    PHARMACEUTICAL = "化学制药"
    BIOTECH = "生物制品"
    MEDICAL_EQUIP = "医疗器械"


class Exchange(str, Enum):
    """交易所"""
    SH = "SH"  # 上海证券交易所
    SZ = "SZ"  # 深圳证券交易所
    BJ = "BJ"  # 北京证券交易所
    HK = "HK"  # 香港交易所
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"


EXCHANGE_NAMES = {
    Exchange.SH: "上海证券交易所",
    Exchange.SZ: "深圳证券交易所",
    Exchange.BJ: "北京证券交易所",
    Exchange.HK: "香港交易所",
    Exchange.NYSE: "纽约证券交易所",
    Exchange.NASDAQ: "纳斯达克",
}


def detect_exchange(code: str) -> Exchange:
    """
    根据股票代码检测交易所
    
    Args:
        code: 股票代码 (如 "600519" 或 "600519.SH")
    
    Returns:
        Exchange 枚举值
    """
    # 去除后缀
    if '.' in code:
        code = code.split('.')[0]
    
    # A股规则
    if code.startswith('6'):
        return Exchange.SH
    elif code.startswith('0') or code.startswith('3'):
        return Exchange.SZ
    elif code.startswith('8') or code.startswith('4'):
        return Exchange.BJ
    # 港股
    elif code.startswith('0') and len(code) == 5:
        return Exchange.HK
    else:
        return Exchange.SZ  # 默认深圳


@dataclass
class StockInfo:
    """股票基本信息"""
    code: str                          # 股票代码，如 "600519.SH"
    name: str                          # 股票名称
    exchange: Exchange                 # 交易所
    listing_date: Optional[str] = None # 上市日期 (YYYY-MM-DD)
    sector: Optional[str] = None       # 所属板块
    is_shanghai_connect: bool = False  # 是否沪股通
    is_shenzhen_connect: bool = False  # 是否深股通
    
    def __post_init__(self):
        """初始化后处理"""
        # 自动补全交易所后缀
        if '.' not in self.code:
            self.code = f"{self.code}.{self.exchange.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "name": self.name,
            "exchange": self.exchange.value,
            "listing_date": self.listing_date,
            "sector": self.sector,
            "is_shanghai_connect": self.is_shanghai_connect,
            "is_shenzhen_connect": self.is_shenzhen_connect,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockInfo":
        """从字典创建"""
        return cls(
            code=data["code"],
            name=data["name"],
            exchange=Exchange(data.get("exchange", "SZ")),
            listing_date=data.get("listing_date"),
            sector=data.get("sector"),
            is_shanghai_connect=data.get("is_shanghai_connect", False),
            is_shenzhen_connect=data.get("is_shenzhen_connect", False),
        )


@dataclass
class ShareStructure:
    """股本结构"""
    total_shares: Optional[float] = None    # 总股本（亿股）
    float_shares: Optional[float] = None    # 流通股本（亿股）
    restricted_shares: Optional[float] = None  # 限售股本（亿股）
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShareStructure":
        return cls(**data)


@dataclass
class MarketData:
    """市场数据"""
    market_cap: Optional[float] = None      # 总市值（亿元）
    pe_ttm: Optional[float] = None          # 市盈率TTM
    pb: Optional[float] = None              # 市净率
    ps_ttm: Optional[float] = None          # 市销率TTM
    dividend_yield: Optional[float] = None  # 股息率 (%)
    beta: Optional[float] = None            # Beta系数
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketData":
        return cls(**data)


@dataclass
class CompanyProfile:
    """公司档案"""
    # 基础信息
    stock: StockInfo
    full_name: str                     # 公司全称
    english_name: Optional[str] = None # 英文名称
    established_date: Optional[str] = None  # 成立日期
    
    # 业务信息
    business_scope: str = ""           # 经营范围
    main_products: List[str] = field(default_factory=list)  # 主要产品/服务
    industry: Optional[Industry] = None # 所属行业
    sub_industry: Optional[SubIndustry] = None  # 细分行业
    
    # 联系信息
    website: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # 股本和市场数据
    shares: ShareStructure = field(default_factory=ShareStructure)
    market_data: MarketData = field(default_factory=MarketData)
    
    # 元数据
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于JSON序列化"""
        return {
            "stock": self.stock.to_dict(),
            "full_name": self.full_name,
            "english_name": self.english_name,
            "established_date": self.established_date,
            "business_scope": self.business_scope,
            "main_products": self.main_products,
            "industry": self.industry.value if self.industry else None,
            "sub_industry": self.sub_industry.value if self.sub_industry else None,
            "website": self.website,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "shares": self.shares.to_dict(),
            "market_data": self.market_data.to_dict(),
            "updated_at": self.updated_at,
            "tags": self.tags,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyProfile":
        """从字典创建实例"""
        return cls(
            stock=StockInfo.from_dict(data["stock"]),
            full_name=data["full_name"],
            english_name=data.get("english_name"),
            established_date=data.get("established_date"),
            business_scope=data.get("business_scope", ""),
            main_products=data.get("main_products", []),
            industry=Industry(data["industry"]) if data.get("industry") else None,
            sub_industry=SubIndustry(data["sub_industry"]) if data.get("sub_industry") else None,
            website=data.get("website"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            shares=ShareStructure.from_dict(data.get("shares", {})),
            market_data=MarketData.from_dict(data.get("market_data", {})),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
        )
    
    def update_market_data(self, **kwargs) -> None:
        """更新市场数据"""
        for key, value in kwargs.items():
            if hasattr(self.market_data, key):
                setattr(self.market_data, key, value)
        self.updated_at = datetime.now().isoformat()


@dataclass
class ProfitabilityMetrics:
    """盈利能力指标"""
    gross_margin: Optional[float] = None       # 毛利率 (%)
    net_margin: Optional[float] = None         # 净利率 (%)
    roe: Optional[float] = None                # ROE (%)
    roa: Optional[float] = None                # ROA (%)
    roic: Optional[float] = None               # ROIC (%)
    ebitda_margin: Optional[float] = None      # EBITDA利润率 (%)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GrowthMetrics:
    """成长能力指标"""
    revenue_growth_yoy: Optional[float] = None # 营收增长率（同比）(%)
    profit_growth_yoy: Optional[float] = None  # 净利润增长率（同比）(%)
    revenue_growth_qoq: Optional[float] = None # 营收增长率（环比）(%)
    profit_growth_qoq: Optional[float] = None  # 净利润增长率（环比）(%)
    cagr_3y: Optional[float] = None            # 3年复合增长率 (%)
    cagr_5y: Optional[float] = None            # 5年复合增长率 (%)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SolvencyMetrics:
    """偿债能力指标"""
    debt_to_asset: Optional[float] = None      # 资产负债率 (%)
    current_ratio: Optional[float] = None      # 流动比率
    quick_ratio: Optional[float] = None        # 速动比率
    interest_coverage: Optional[float] = None  # 利息保障倍数
    debt_to_equity: Optional[float] = None     # 产权比率 (%)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EfficiencyMetrics:
    """运营效率指标"""
    inventory_turnover: Optional[float] = None # 存货周转率 (次)
    receivable_turnover: Optional[float] = None # 应收账款周转率 (次)
    asset_turnover: Optional[float] = None     # 总资产周转率 (次)
    days_sales_outstanding: Optional[float] = None  # 应收账款周转天数
    days_inventory_outstanding: Optional[float] = None  # 存货周转天数
    cash_conversion_cycle: Optional[float] = None  # 现金转换周期
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CashflowMetrics:
    """现金流指标"""
    operating_cash_flow: Optional[float] = None # 经营现金流（亿元）
    investing_cash_flow: Optional[float] = None # 投资现金流（亿元）
    financing_cash_flow: Optional[float] = None # 筹资现金流（亿元）
    free_cash_flow: Optional[float] = None      # 自由现金流（亿元）
    ocf_to_net_profit: Optional[float] = None   # 经营现金流/净利润
    ocf_to_revenue: Optional[float] = None      # 经营现金流/营业收入
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FinancialMetrics:
    """财务指标数据模型 (组合)"""
    # 各维度指标
    profitability: ProfitabilityMetrics = field(default_factory=ProfitabilityMetrics)
    growth: GrowthMetrics = field(default_factory=GrowthMetrics)
    solvency: SolvencyMetrics = field(default_factory=SolvencyMetrics)
    efficiency: EfficiencyMetrics = field(default_factory=EfficiencyMetrics)
    cashflow: CashflowMetrics = field(default_factory=CashflowMetrics)
    
    # 元数据
    report_date: Optional[str] = None           # 报告期 (YYYY-MM-DD)
    report_type: Optional[str] = None           # 报告类型 (年报/中报/季报)
    currency: str = "CNY"                       # 货币单位
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "profitability": self.profitability.to_dict(),
            "growth": self.growth.to_dict(),
            "solvency": self.solvency.to_dict(),
            "efficiency": self.efficiency.to_dict(),
            "cashflow": self.cashflow.to_dict(),
            "report_date": self.report_date,
            "report_type": self.report_type,
            "currency": self.currency,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialMetrics":
        """从字典创建"""
        return cls(
            profitability=ProfitabilityMetrics(**data.get("profitability", {})),
            growth=GrowthMetrics(**data.get("growth", {})),
            solvency=SolvencyMetrics(**data.get("solvency", {})),
            efficiency=EfficiencyMetrics(**data.get("efficiency", {})),
            cashflow=CashflowMetrics(**data.get("cashflow", {})),
            report_date=data.get("report_date"),
            report_type=data.get("report_type"),
            currency=data.get("currency", "CNY"),
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            "ROE": self.profitability.roe,
            "毛利率": self.profitability.gross_margin,
            "净利率": self.profitability.net_margin,
            "营收增长": self.growth.revenue_growth_yoy,
            "净利润增长": self.growth.profit_growth_yoy,
            "资产负债率": self.solvency.debt_to_asset,
            "流动比率": self.solvency.current_ratio,
            "经营现金流": self.cashflow.operating_cash_flow,
        }


# 财务指标参考值 (分行业)
BENCHMARKS = {
    "default": {
        "roe": {"excellent": 20, "good": 15, "average": 10},
        "gross_margin": {"excellent": 40, "good": 30, "average": 20},
        "net_margin": {"excellent": 20, "good": 10, "average": 5},
        "debt_to_asset": {"safe": 50, "warning": 70, "danger": 80},
        "current_ratio": {"safe": 2.0, "warning": 1.5, "danger": 1.0},
        "quick_ratio": {"safe": 1.5, "warning": 1.0, "danger": 0.8},
    },
    Industry.BANK: {
        "roe": {"excellent": 15, "good": 12, "average": 8},
        "net_margin": {"excellent": 40, "good": 30, "average": 20},
        "debt_to_asset": {"safe": 92, "warning": 95, "danger": 97},
    },
    Industry.TECHNOLOGY: {
        "roe": {"excellent": 15, "good": 10, "average": 5},
        "gross_margin": {"excellent": 60, "good": 45, "average": 30},
    },
    Industry.CONSUMER: {
        "roe": {"excellent": 20, "good": 15, "average": 10},
        "gross_margin": {"excellent": 50, "good": 35, "average": 20},
    },
    Industry.HEALTHCARE: {
        "roe": {"excellent": 18, "good": 12, "average": 8},
        "gross_margin": {"excellent": 70, "good": 55, "average": 40},
    },
}


def get_benchmark(industry: Optional[Industry] = None, metric: Optional[str] = None) -> Dict:
    """
    获取行业基准值
    
    Args:
        industry: 行业，None 则返回默认基准
        metric: 指标名称，None 则返回全部
    
    Returns:
        基准值字典
    """
    if industry and industry in BENCHMARKS:
        benchmarks = BENCHMARKS[industry].copy()
        # 合并默认值
        for key, value in BENCHMARKS["default"].items():
            if key not in benchmarks:
                benchmarks[key] = value
    else:
        benchmarks = BENCHMARKS["default"]
    
    if metric:
        return benchmarks.get(metric, {})
    return benchmarks
