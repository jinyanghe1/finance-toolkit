"""
Finance Toolkit - 行业分类体系
Industry Classification System
"""

from typing import Dict, List, Optional, Any
from enum import Enum

from ..logger import get_logger

logger = get_logger(__name__)


class Industry(str, Enum):
    """一级行业分类 (申万/中信标准)"""
    # 金融
    FINANCE = "金融"
    BANK = "银行"
    INSURANCE = "保险"
    SECURITIES = "证券"
    
    # 房地产
    REAL_ESTATE = "房地产"
    REAL_ESTATE_DEV = "房地产开发"
    REAL_ESTATE_SERVICE = "房地产服务"
    
    # 制造业
    MANUFACTURING = "制造业"
    AUTOMOTIVE = "汽车"
    MACHINERY = "机械设备"
    ELECTRICAL_EQUIP = "电力设备"
    
    # 科技
    TECHNOLOGY = "科技"
    SEMICONDUCTOR = "半导体"
    SOFTWARE = "软件开发"
    ELECTRONICS = "电子"
    COMMUNICATION = "通信"
    COMPUTER_HARDWARE = "计算机设备"
    
    # 医药健康
    HEALTHCARE = "医药健康"
    PHARMACEUTICAL = "化学制药"
    BIOTECH = "生物制品"
    MEDICAL_EQUIP = "医疗器械"
    MEDICAL_SERVICE = "医疗服务"
    
    # 消费
    CONSUMER = "消费"
    FOOD_BEVERAGE = "食品饮料"
    HOUSEHOLD = "家用电器"
    TEXTILE_APPAREL = "纺织服饰"
    RETAIL = "商贸零售"
    
    # 能源
    ENERGY = "能源"
    OIL_GAS = "石油石化"
    COAL = "煤炭"
    
    # 材料
    MATERIALS = "材料"
    STEEL = "钢铁"
    NONFERROUS = "有色金属"
    CHEMICAL = "基础化工"
    BUILDING_MAT = "建筑材料"
    
    # 公用事业
    UTILITIES = "公用事业"
    POWER = "电力"
    GAS_WATER = "燃气水务"
    
    # 交通运输
    TRANSPORTATION = "交通运输"
    
    # 传媒
    MEDIA = "传媒"
    
    # 农业
    AGRICULTURE = "农林牧渔"
    
    # 其他
    MINING = "采矿"
    CONSTRUCTION = "建筑"
    ENVIRONMENTAL = "环保"
    COMPREHENSIVE = "综合"


class Sector(str, Enum):
    """大板块分类"""
    FINANCIAL = "金融地产"
    CYCLICAL = "周期"
    CONSUMER = "消费"
    HEALTHCARE = "医药"
    TECHNOLOGY = "科技"
    INFRASTRUCTURE = "基建"


# 行业到大板块的映射
INDUSTRY_TO_SECTOR = {
    Industry.FINANCE: Sector.FINANCIAL,
    Industry.BANK: Sector.FINANCIAL,
    Industry.INSURANCE: Sector.FINANCIAL,
    Industry.SECURITIES: Sector.FINANCIAL,
    Industry.REAL_ESTATE: Sector.FINANCIAL,
    
    Industry.MANUFACTURING: Sector.CYCLICAL,
    Industry.AUTOMOTIVE: Sector.CYCLICAL,
    Industry.MACHINERY: Sector.CYCLICAL,
    Industry.ELECTRICAL_EQUIP: Sector.CYCLICAL,
    Industry.STEEL: Sector.CYCLICAL,
    Industry.NONFERROUS: Sector.CYCLICAL,
    Industry.CHEMICAL: Sector.CYCLICAL,
    Industry.BUILDING_MAT: Sector.CYCLICAL,
    
    Industry.CONSUMER: Sector.CONSUMER,
    Industry.FOOD_BEVERAGE: Sector.CONSUMER,
    Industry.HOUSEHOLD: Sector.CONSUMER,
    Industry.RETAIL: Sector.CONSUMER,
    Industry.TEXTILE_APPAREL: Sector.CONSUMER,
    
    Industry.HEALTHCARE: Sector.HEALTHCARE,
    Industry.PHARMACEUTICAL: Sector.HEALTHCARE,
    Industry.BIOTECH: Sector.HEALTHCARE,
    Industry.MEDICAL_EQUIP: Sector.HEALTHCARE,
    
    Industry.TECHNOLOGY: Sector.TECHNOLOGY,
    Industry.SEMICONDUCTOR: Sector.TECHNOLOGY,
    Industry.SOFTWARE: Sector.TECHNOLOGY,
    Industry.ELECTRONICS: Sector.TECHNOLOGY,
    Industry.COMMUNICATION: Sector.TECHNOLOGY,
    
    Industry.UTILITIES: Sector.INFRASTRUCTURE,
    Industry.TRANSPORTATION: Sector.INFRASTRUCTURE,
    Industry.CONSTRUCTION: Sector.INFRASTRUCTURE,
}


def get_sector(industry: Industry) -> Sector:
    """获取行业所属板块"""
    return INDUSTRY_TO_SECTOR.get(industry, Sector.CYCLICAL)


class IndustryDB:
    """行业数据库"""
    
    def __init__(self):
        self.industries = {ind for ind in Industry}
    
    def get_by_name(self, name: str) -> Optional[Industry]:
        """通过中文名或代码获取行业"""
        name = name.strip()
        
        # 尝试直接匹配
        for ind in self.industries:
            if ind.value == name or ind.name == name:
                return ind
        
        # 模糊匹配
        for ind in self.industries:
            if name in ind.value or name in ind.name:
                return ind
        
        return None
    
    def get_by_sector(self, sector: Sector) -> List[Industry]:
        """获取板块下的所有行业"""
        return [ind for ind in self.industries if get_sector(ind) == sector]
    
    def list_all(self) -> List[Dict[str, str]]:
        """列出所有行业"""
        return [
            {
                "code": ind.name,
                "name": ind.value,
                "sector": get_sector(ind).value,
            }
            for ind in sorted(self.industries, key=lambda x: x.value)
        ]
    
    def list_sectors(self) -> List[Dict[str, Any]]:
        """列出所有板块及下属行业"""
        result = []
        for sector in Sector:
            industries = self.get_by_sector(sector)
            result.append({
                "name": sector.value,
                "industries": [ind.value for ind in industries],
            })
        return result


# 行业基准数据 (用于评估指标)
INDUSTRY_BENCHMARKS = {
    "default": {
        "roe": {"excellent": 20, "good": 15, "average": 10},
        "gross_margin": {"excellent": 40, "good": 30, "average": 20},
        "net_margin": {"excellent": 20, "good": 10, "average": 5},
        "debt_to_asset": {"safe": 50, "warning": 70, "danger": 80},
        "current_ratio": {"safe": 2.0, "warning": 1.5, "danger": 1.0},
    },
    Industry.BANK: {
        "roe": {"excellent": 15, "good": 12, "average": 8},
        "net_margin": {"excellent": 40, "good": 35, "average": 25},
        "debt_to_asset": {"safe": 92, "warning": 95, "danger": 97},
        "current_ratio": {"safe": 1.0, "warning": 0.9, "danger": 0.8},
    },
    Industry.INSURANCE: {
        "roe": {"excellent": 15, "good": 12, "average": 8},
        "debt_to_asset": {"safe": 90, "warning": 93, "danger": 95},
    },
    Industry.TECHNOLOGY: {
        "roe": {"excellent": 15, "good": 10, "average": 5},
        "gross_margin": {"excellent": 60, "good": 45, "average": 30},
        "net_margin": {"excellent": 25, "good": 15, "average": 8},
    },
    Industry.SEMICONDUCTOR: {
        "roe": {"excellent": 12, "good": 8, "average": 5},
        "gross_margin": {"excellent": 50, "good": 40, "average": 25},
        "rd_ratio": {"excellent": 20, "good": 15, "average": 10},
    },
    Industry.CONSUMER: {
        "roe": {"excellent": 20, "good": 15, "average": 10},
        "gross_margin": {"excellent": 50, "good": 35, "average": 20},
    },
    Industry.FOOD_BEVERAGE: {
        "roe": {"excellent": 25, "good": 18, "average": 12},
        "gross_margin": {"excellent": 60, "good": 45, "average": 30},
        "net_margin": {"excellent": 25, "good": 18, "average": 10},
    },
    Industry.HEALTHCARE: {
        "roe": {"excellent": 18, "good": 12, "average": 8},
        "gross_margin": {"excellent": 70, "good": 55, "average": 40},
        "net_margin": {"excellent": 20, "good": 15, "average": 8},
    },
    Industry.PHARMACEUTICAL: {
        "roe": {"excellent": 15, "good": 12, "average": 8},
        "gross_margin": {"excellent": 75, "good": 60, "average": 45},
        "rd_ratio": {"excellent": 15, "good": 10, "average": 6},
    },
    Industry.ENERGY: {
        "roe": {"excellent": 15, "good": 10, "average": 6},
        "gross_margin": {"excellent": 35, "good": 25, "average": 15},
        "debt_to_asset": {"safe": 55, "warning": 70, "danger": 80},
    },
    Industry.MATERIALS: {
        "roe": {"excellent": 15, "good": 10, "average": 6},
        "gross_margin": {"excellent": 25, "good": 18, "average": 12},
    },
    Industry.UTILITIES: {
        "roe": {"excellent": 12, "good": 9, "average": 6},
        "gross_margin": {"excellent": 30, "good": 25, "average": 20},
        "debt_to_asset": {"safe": 65, "warning": 75, "danger": 85},
    },
    Industry.REAL_ESTATE: {
        "roe": {"excellent": 18, "good": 12, "average": 8},
        "debt_to_asset": {"safe": 70, "warning": 80, "danger": 85},
    },
}


def get_industry_benchmark(industry: Optional[Industry] = None, metric: Optional[str] = None) -> Dict:
    """
    获取行业基准值
    
    Args:
        industry: 行业
        metric: 指标名
    
    Returns:
        基准值字典
    """
    if industry and industry in INDUSTRY_BENCHMARKS:
        benchmarks = INDUSTRY_BENCHMARKS[industry].copy()
        # 合并默认值
        for key, value in INDUSTRY_BENCHMARKS["default"].items():
            if key not in benchmarks:
                benchmarks[key] = value
    else:
        benchmarks = INDUSTRY_BENCHMARKS["default"]
    
    if metric:
        return benchmarks.get(metric, {})
    return benchmarks


# 便捷函数
def get_industry_db() -> IndustryDB:
    """获取行业数据库实例"""
    return IndustryDB()


def get_industry_by_name(name: str) -> Optional[Industry]:
    """通过名称获取行业"""
    db = get_industry_db()
    return db.get_by_name(name)
