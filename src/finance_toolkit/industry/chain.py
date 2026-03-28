"""
Finance Toolkit - 产业链定义
Industry Chain Definitions
"""

from typing import Dict, List, Optional


class IndustryChain:
    """产业链定义"""
    
    # 新能源汽车产业链
    NEW_ENERGY_VEHICLE = {
        "name": "新能源汽车",
        "upstream": {
            "锂矿": ["天齐锂业", "赣锋锂业"],
            "钴矿": ["华友钴业", "洛阳钼业"],
            "正极材料": ["当升科技", "容百科技"],
            "负极材料": ["璞泰来", "贝特瑞"],
            "电解液": ["天赐材料", "新宙邦"],
            "隔膜": ["恩捷股份", "星源材质"],
        },
        "midstream": {
            "电池": ["宁德时代", "比亚迪", "亿纬锂能", "国轩高科"],
            "电机电控": ["汇川技术", "卧龙电驱", "精进电动"],
            "热管理": ["三花智控", "银轮股份"],
        },
        "downstream": {
            "整车": ["比亚迪", "蔚来", "小鹏", "理想", "特斯拉(美)"],
            "充电桩": ["特锐德", "盛弘股份", "星星充电"],
        }
    }
    
    # 白酒产业链
    BAIJIU = {
        "name": "白酒",
        "upstream": {
            "粮食种植": ["北大荒"],
            "包装材料": ["裕同科技", "合兴包装"],
        },
        "midstream": {
            "高端白酒": ["贵州茅台", "五粮液", "泸州老窖"],
            "次高端白酒": ["山西汾酒", "洋河股份", "古井贡酒", "水井坊"],
            "中端白酒": ["今世缘", "迎驾贡酒", "口子窖"],
        },
        "downstream": {
            "经销商": ["华致酒行"],
            "终端零售": [],
        }
    }
    
    # 半导体产业链
    SEMICONDUCTOR = {
        "name": "半导体",
        "upstream": {
            "设备": ["北方华创", "中微公司", "拓荆科技", "芯源微"],
            "材料": ["沪硅产业", "安集科技", "鼎龙股份", "南大光电"],
            "EDA": ["华大九天", "概伦电子"],
        },
        "midstream": {
            "设计": ["韦尔股份", "兆易创新", "紫光国微", "卓胜微", "圣邦股份"],
            "制造": ["中芯国际", "华虹半导体"],
            "封测": ["长电科技", "通富微电", "华天科技"],
        },
        "downstream": {
            "消费电子": ["立讯精密", "歌尔股份", "蓝思科技"],
            "汽车电子": ["舜宇光学", "联创电子"],
            "通信设备": ["华为(未上市)", "中兴通讯"],
        }
    }
    
    # 光伏产业链
    SOLAR = {
        "name": "光伏",
        "upstream": {
            "硅料": ["通威股份", "大全能源", "协鑫科技"],
            "硅片": ["隆基绿能", "TCL中环", "晶澳科技"],
        },
        "midstream": {
            "电池片": ["通威股份", "爱旭股份", "晶科能源"],
            "组件": ["隆基绿能", "晶科能源", "天合光能", "晶澳科技"],
            "逆变器": ["阳光电源", "锦浪科技", "固德威", "德业股份"],
        },
        "downstream": {
            "电站运营": ["太阳能", "晶科科技", "正泰电器"],
            "EPC": ["特变电工", "阳光电源"],
        }
    }
    
    # 医药产业链
    PHARMA = {
        "name": "医药",
        "upstream": {
            "原料药": ["华海药业", "普洛药业", "九洲药业"],
            "CXO": ["药明康德", "康龙化成", "泰格医药", "凯莱英"],
        },
        "midstream": {
            "创新药": ["恒瑞医药", "百济神州", "信达生物", "君实生物"],
            "仿制药": ["科伦药业", "华东医药", "人福医药"],
            "中药": ["片仔癀", "云南白药", "同仁堂"],
            "疫苗": ["智飞生物", "万泰生物", "沃森生物"],
        },
        "downstream": {
            "医院": ["爱尔眼科", "通策医疗"],
            "药店": ["益丰药房", "老百姓", "大参林"],
        }
    }


class ChainDB:
    """产业链数据库"""
    
    def __init__(self):
        self.chains = {
            "新能源汽车": IndustryChain.NEW_ENERGY_VEHICLE,
            "白酒": IndustryChain.BAIJIU,
            "半导体": IndustryChain.SEMICONDUCTOR,
            "光伏": IndustryChain.SOLAR,
            "医药": IndustryChain.PHARMA,
        }
    
    def get_chain(self, name: str) -> Optional[Dict]:
        """获取产业链"""
        return self.chains.get(name)
    
    def list_chains(self) -> List[str]:
        """列出所有产业链"""
        return list(self.chains.keys())
    
    def find_company_position(self, company_name: str) -> Optional[Dict]:
        """
        查找公司在产业链中的位置
        
        Args:
            company_name: 公司名称
        
        Returns:
            位置信息
        """
        for chain_name, chain in self.chains.items():
            for segment, sub_segments in chain.items():
                if segment == "name":
                    continue
                for sub_name, companies in sub_segments.items():
                    if company_name in companies:
                        return {
                            "chain": chain_name,
                            "segment": segment,
                            "sub_segment": sub_name,
                        }
        return None
    
    def get_chain_companies(self, chain_name: str) -> List[str]:
        """
        获取产业链中的所有公司
        
        Args:
            chain_name: 产业链名称
        
        Returns:
            公司列表
        """
        chain = self.chains.get(chain_name)
        if not chain:
            return []
        
        companies = []
        for segment, sub_segments in chain.items():
            if segment == "name":
                continue
            for sub_name, sub_companies in sub_segments.items():
                companies.extend(sub_companies)
        
        return companies


# 便捷函数
def get_chain_db() -> ChainDB:
    """获取产业链数据库"""
    return ChainDB()


def get_industry_chain(name: str) -> Optional[Dict]:
    """获取产业链"""
    db = get_chain_db()
    return db.get_chain(name)
