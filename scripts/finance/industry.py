"""
金融功能库 - 行业分类体系
Industry Classification System
"""

from typing import Dict, List, Optional
from enum import Enum

class Industry(Enum):
    """一级行业（申万/中信标准）"""
    # 金融
    BANK = ("银行", "金融")
    INSURANCE = ("保险", "金融")
    SECURITIES = ("证券", "金融")
    
    # 房地产
    REAL_ESTATE_DEV = ("房地产开发", "房地产")
    REAL_ESTATE_SERVICE = ("房地产服务", "房地产")
    
    # 制造业
    AUTOMOTIVE = ("汽车", "制造")
    MACHINERY = ("机械设备", "制造")
    ELECTRICAL_EQUIP = ("电力设备", "制造")
    
    # 科技
    SEMICONDUCTOR = ("半导体", "科技")
    SOFTWARE = ("软件开发", "科技")
    ELECTRONICS = ("电子", "科技")
    COMMUNICATION = ("通信", "科技")
    COMPUTER_HARDWARE = ("计算机设备", "科技")
    
    # 医药健康
    PHARMACEUTICAL = ("化学制药", "医药")
    BIOTECH = ("生物制品", "医药")
    MEDICAL_EQUIP = ("医疗器械", "医药")
    MEDICAL_SERVICE = ("医疗服务", "医药")
    
    # 消费
    FOOD_BEVERAGE = ("食品饮料", "消费")
    HOUSEHOLD = ("家用电器", "消费")
    TEXTILE_APPAREL = ("纺织服饰", "消费")
    RETAIL = ("商贸零售", "消费")
    
    # 能源
    OIL_GAS = ("石油石化", "能源")
    COAL = ("煤炭", "能源")
    
    # 材料
    STEEL = ("钢铁", "材料")
    NONFERROUS = ("有色金属", "材料")
    CHEMICAL = ("基础化工", "材料")
    BUILDING_MAT = ("建筑材料", "材料")
    
    # 公用事业
    POWER = ("电力", "公用事业")
    GAS_WATER = ("燃气水务", "公用事业")
    
    # 交通运输
    TRANSPORTATION = ("交通运输", "交运")
    
    # 传媒
    MEDIA = ("传媒", "传媒")
    
    # 其他
    AGRICULTURE = ("农林牧渔", "农业")
    MINING = ("基础化工", "采矿")
    CONSTRUCTION = ("建筑装饰", "建筑")
    ENVIRONMENTAL = ("环保", "环保")
    COMPREHENSIVE = ("综合", "综合")

    def __init__(self, cn_name: str, sector: str):
        self.cn_name = cn_name
        self.sector = sector

    @classmethod
    def from_cn_name(cls, cn_name: str) -> Optional["Industry"]:
        """通过中文名称查找行业枚举"""
        for item in cls:
            if item.cn_name == cn_name:
                return item
        return None


class SubIndustry(str, Enum):
    """二级行业分类（细分领域）"""
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


class IndustryChain:
    """产业链定义"""
    
    # 示例：新能源汽车产业链
    NEW_ENERGY_VEHICLE = {
        "上游": {
            "锂矿": ["天齐锂业", "赣锋锂业"],
            "钴矿": ["华友钴业", "洛阳钼业"],
            "正极材料": ["当升科技", "容百科技"],
            "负极材料": ["璞泰来", "贝特瑞"],
            "电解液": ["天赐材料", "新宙邦"],
            "隔膜": ["恩捷股份", "星源材质"],
        },
        "中游": {
            "电池": ["宁德时代", "比亚迪", "亿纬锂能"],
            "电机电控": ["汇川技术", "卧龙电驱"],
        },
        "下游": {
            "整车": ["比亚迪", "蔚来", "小鹏", "理想"],
            "充电桩": ["特锐德", "盛弘股份"],
        }
    }
    
    # 白酒产业链
    BAIJIU = {
        "上游": {
            "粮食种植": ["北大荒"],
            "包装材料": ["裕同科技"],
        },
        "中游": {
            "白酒生产": ["贵州茅台", "五粮液", "泸州老窖", "山西汾酒", "洋河股份"],
        },
        "下游": {
            "经销商": ["华致酒行"],
            "终端零售": [],
        }
    }
    
    # 半导体产业链
    SEMICONDUCTOR = {
        "上游": {
            "设备": ["北方华创", "中微公司", "拓荆科技"],
            "材料": ["沪硅产业", "安集科技", "鼎龙股份"],
            "EDA": ["华大九天"],
        },
        "中游": {
            "设计": ["韦尔股份", "兆易创新", "紫光国微"],
            "制造": ["中芯国际"],
            "封测": ["长电科技", "通富微电"],
        },
        "下游": {
            "消费电子": ["立讯精密", "歌尔股份"],
            "汽车电子": ["舜宇光学"],
        }
    }


class IndustryDB:
    """行业数据库"""
    
    def __init__(self):
        self.industries = {ind for ind in Industry}
        self.chains = {
            "新能源汽车": IndustryChain.NEW_ENERGY_VEHICLE,
            "白酒": IndustryChain.BAIJIU,
            "半导体": IndustryChain.SEMICONDUCTOR,
        }
    
    def get_by_name(self, name: str) -> Optional[Industry]:
        """通过中文名获取行业"""
        for ind in self.industries:
            if ind.cn_name == name or ind.name == name:
                return ind
        return None
    
    def get_by_sector(self, sector: str) -> List[Industry]:
        """获取某大板块下的所有行业"""
        return [ind for ind in self.industries if ind.sector == sector]
    
    def list_all(self) -> List[Dict]:
        """列出所有行业"""
        return [
            {
                "code": ind.name,
                "name": ind.cn_name,
                "sector": ind.sector,
            }
            for ind in sorted(self.industries, key=lambda x: x.sector)
        ]
    
    def get_chain(self, chain_name: str) -> Optional[Dict]:
        """获取产业链信息"""
        return self.chains.get(chain_name)
    
    def list_chains(self) -> List[str]:
        """列出所有产业链"""
        return list(self.chains.keys())


# 便捷函数
def get_industry_db() -> IndustryDB:
    """获取行业数据库实例"""
    return IndustryDB()


def get_industry_by_name(name: str) -> Optional[Industry]:
    """通过名称获取行业"""
    db = get_industry_db()
    return db.get_by_name(name)


def get_industry_chain(chain_name: str) -> Optional[Dict]:
    """获取产业链"""
    db = get_industry_db()
    return db.get_chain(chain_name)
