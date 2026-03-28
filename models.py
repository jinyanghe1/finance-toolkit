"""
金融功能库 - 数据模型定义
Company Profile Schema 和 Financial Data Models
"""

from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Industry(str, Enum):
    """一级行业分类"""
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

class SubIndustry(str, Enum):
    """二级行业分类（示例）"""
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

@dataclass
class StockInfo:
    """股票基本信息"""
    code: str                          # 股票代码，如 "600519.SH"
    name: str                          # 股票名称
    exchange: str                      # 交易所 (SH/SZ/BJ/HK/NYSE/NASDAQ)
    listing_date: Optional[str] = None # 上市日期
    sector: Optional[str] = None       # 所属板块
    is_shanghai: bool = False          # 是否沪股通
    is_shenzhen: bool = False          # 是否深股通

@dataclass
class CompanyProfile:
    """公司档案Schema"""
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
    
    # 公司网站、总部地址等
    website: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    
    # 股本信息
    total_shares: Optional[float] = None    # 总股本（亿股）
    float_shares: Optional[float] = None    # 流通股本（亿股）
    
    # 市场数据（最新）
    market_cap: Optional[float] = None      # 总市值（亿元）
    pe_ttm: Optional[float] = None          # 市盈率TTM
    pb: Optional[float] = None              # 市净率
    ps_ttm: Optional[float] = None          # 市销率TTM
    dividend_yield: Optional[float] = None  # 股息率
    
    # 更新时间
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """转换为字典，用于JSON序列化"""
        result = {
            "stock": {
                "code": self.stock.code,
                "name": self.stock.name,
                "exchange": self.stock.exchange,
                "listing_date": self.stock.listing_date,
                "sector": self.stock.sector,
            },
            "full_name": self.full_name,
            "english_name": self.english_name,
            "established_date": self.established_date,
            "business_scope": self.business_scope,
            "main_products": self.main_products,
            "industry": self.industry.value if self.industry else None,
            "sub_industry": self.sub_industry.value if self.sub_industry else None,
            "website": self.website,
            "address": self.address,
            "contact": {"phone": self.phone},
            "shares": {
                "total": self.total_shares,
                "float": self.float_shares,
            },
            "market_data": {
                "market_cap": self.market_cap,
                "pe_ttm": self.pe_ttm,
                "pb": self.pb,
                "ps_ttm": self.ps_ttm,
                "dividend_yield": self.dividend_yield,
            },
            "updated_at": self.updated_at,
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CompanyProfile":
        """从字典创建实例"""
        stock = StockInfo(**data["stock"])
        profile = cls(
            stock=stock,
            full_name=data["full_name"],
            english_name=data.get("english_name"),
            established_date=data.get("established_date"),
            business_scope=data.get("business_scope", ""),
            main_products=data.get("main_products", []),
            industry=Industry(data["industry"]) if data.get("industry") else None,
            sub_industry=SubIndustry(data["sub_industry"]) if data.get("sub_industry") else None,
            website=data.get("website"),
            address=data.get("address"),
            phone=data.get("contact", {}).get("phone"),
            total_shares=data.get("shares", {}).get("total"),
            float_shares=data.get("shares", {}).get("float"),
            market_cap=data.get("market_data", {}).get("market_cap"),
            pe_ttm=data.get("market_data", {}).get("pe_ttm"),
            pb=data.get("market_data", {}).get("pb"),
            ps_ttm=data.get("market_data", {}).get("ps_ttm"),
            dividend_yield=data.get("market_data", {}).get("dividend_yield"),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
        return profile


@dataclass
class FinancialMetrics:
    """财务指标数据模型"""
    # 盈利能力
    gross_margin: Optional[float] = None       # 毛利率
    net_margin: Optional[float] = None         # 净利率
    roe: Optional[float] = None                # ROE
    roa: Optional[float] = None                # ROA
    roic: Optional[float] = None               # ROIC
    
    # 成长能力
    revenue_growth_yoy: Optional[float] = None # 营收增长率（同比）
    profit_growth_yoy: Optional[float] = None  # 净利润增长率（同比）
    
    # 偿债能力
    debt_to_asset: Optional[float] = None      # 资产负债率
    current_ratio: Optional[float] = None      # 流动比率
    quick_ratio: Optional[float] = None        # 速动比率
    
    # 运营效率
    inventory_turnover: Optional[float] = None # 存货周转率
    receivable_turnover: Optional[float] = None # 应收账款周转率
    asset_turnover: Optional[float] = None     # 总资产周转率
    
    # 现金流
    operating_cash_flow: Optional[float] = None # 经营现金流（亿元）
    free_cash_flow: Optional[float] = None      # 自由现金流（亿元）
    
    # 时间戳
    report_date: Optional[str] = None           # 报告期
    
    def to_dict(self) -> Dict:
        return {
            "profitability": {
                "gross_margin": self.gross_margin,
                "net_margin": self.net_margin,
                "roe": self.roe,
                "roa": self.roa,
                "roic": self.roic,
            },
            "growth": {
                "revenue_growth_yoy": self.revenue_growth_yoy,
                "profit_growth_yoy": self.profit_growth_yoy,
            },
            "solvency": {
                "debt_to_asset": self.debt_to_asset,
                "current_ratio": self.current_ratio,
                "quick_ratio": self.quick_ratio,
            },
            "efficiency": {
                "inventory_turnover": self.inventory_turnover,
                "receivable_turnover": self.receivable_turnover,
                "asset_turnover": self.asset_turnover,
            },
            "cashflow": {
                "operating_cash_flow": self.operating_cash_flow,
                "free_cash_flow": self.free_cash_flow,
            },
            "report_date": self.report_date,
        }


# A股交易所映射
EXCHANGE_MAP = {
    "SH": "上海证券交易所",
    "SZ": "深圳证券交易所",
    "BJ": "北京证券交易所",
}

# 常用财务指标参考值
BENCHMARKS = {
    "roe": {"excellent": 20, "good": 15, "average": 10},
    "gross_margin": {"excellent": 40, "good": 30, "average": 20},
    "debt_to_asset": {"safe": 50, "warning": 70, "danger": 80},
    "current_ratio": {"safe": 2.0, "warning": 1.5, "danger": 1.0},
}
