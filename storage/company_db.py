"""
金融功能库 - 公司数据管理
Company Database Manager
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from scripts.finance.models import CompanyProfile, FinancialMetrics

# 数据根目录
DATA_ROOT = Path("/root/.openclaw/workspace/data/finance")

class CompanyDB:
    """公司数据库管理器"""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.data_root = data_root or DATA_ROOT
        self.company_dir = self.data_root / "company"
        self.company_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_company_path(self, code: str) -> Path:
        """获取公司数据目录"""
        # 标准化代码（去除后缀）
        code_clean = code.split('.')[0] if '.' in code else code
        return self.company_dir / code_clean
    
    def exists(self, code: str) -> bool:
        """检查公司档案是否存在"""
        path = self._get_company_path(code)
        return (path / "profile.json").exists()
    
    def save_profile(self, profile: CompanyProfile) -> None:
        """保存公司档案"""
        path = self._get_company_path(profile.stock.code)
        path.mkdir(parents=True, exist_ok=True)
        
        profile_file = path / "profile.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存公司档案: {profile.stock.name} ({profile.stock.code})")
    
    def load_profile(self, code: str) -> Optional[CompanyProfile]:
        """加载公司档案"""
        path = self._get_company_path(code)
        profile_file = path / "profile.json"
        
        if not profile_file.exists():
            return None
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return CompanyProfile.from_dict(data)
    
    def save_metrics(self, code: str, metrics: FinancialMetrics) -> None:
        """保存财务指标"""
        path = self._get_company_path(code)
        path.mkdir(parents=True, exist_ok=True)
        
        metrics_file = path / "metrics.json"
        
        # 读取已有数据
        all_metrics = []
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
        
        # 添加新数据
        new_data = metrics.to_dict()
        # 去重：相同报告期替换
        all_metrics = [m for m in all_metrics if m.get("report_date") != new_data["report_date"]]
        all_metrics.append(new_data)
        # 按报告期排序
        all_metrics.sort(key=lambda x: x.get("report_date", ""), reverse=True)
        
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(all_metrics, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存财务指标: {code} ({metrics.report_date})")
    
    def load_metrics(self, code: str, limit: int = 8) -> List[FinancialMetrics]:
        """加载财务指标历史"""
        path = self._get_company_path(code)
        metrics_file = path / "metrics.json"
        
        if not metrics_file.exists():
            return []
        
        with open(metrics_file, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        # 转换为FinancialMetrics对象
        metrics_list = []
        for data in data_list[:limit]:
            m = FinancialMetrics(
                gross_margin=data.get("profitability", {}).get("gross_margin"),
                net_margin=data.get("profitability", {}).get("net_margin"),
                roe=data.get("profitability", {}).get("roe"),
                roa=data.get("profitability", {}).get("roa"),
                roic=data.get("profitability", {}).get("roic"),
                revenue_growth_yoy=data.get("growth", {}).get("revenue_growth_yoy"),
                profit_growth_yoy=data.get("growth", {}).get("profit_growth_yoy"),
                debt_to_asset=data.get("solvency", {}).get("debt_to_asset"),
                current_ratio=data.get("solvency", {}).get("current_ratio"),
                quick_ratio=data.get("solvency", {}).get("quick_ratio"),
                inventory_turnover=data.get("efficiency", {}).get("inventory_turnover"),
                receivable_turnover=data.get("efficiency", {}).get("receivable_turnover"),
                asset_turnover=data.get("efficiency", {}).get("asset_turnover"),
                operating_cash_flow=data.get("cashflow", {}).get("operating_cash_flow"),
                free_cash_flow=data.get("cashflow", {}).get("free_cash_flow"),
                report_date=data.get("report_date"),
            )
            metrics_list.append(m)
        
        return metrics_list
    
    def list_companies(self) -> List[str]:
        """列出所有已存储的公司代码"""
        codes = []
        for item in self.company_dir.iterdir():
            if item.is_dir() and (item / "profile.json").exists():
                codes.append(item.name)
        return sorted(codes)
    
    def get_summary(self, code: str) -> Optional[Dict]:
        """获取公司摘要信息"""
        profile = self.load_profile(code)
        if not profile:
            return None
        
        metrics_list = self.load_metrics(code, limit=1)
        latest_metrics = metrics_list[0] if metrics_list else None
        
        return {
            "code": profile.stock.code,
            "name": profile.stock.name,
            "industry": profile.industry.value if profile.industry else "未知",
            "market_cap": profile.market_cap,
            "pe_ttm": profile.pe_ttm,
            "pb": profile.pb,
            "roe": latest_metrics.roe if latest_metrics else None,
            "updated_at": profile.updated_at,
        }
    
    def delete_company(self, code: str) -> bool:
        """删除公司数据"""
        import shutil
        path = self._get_company_path(code)
        if path.exists():
            shutil.rmtree(path)
            print(f"✅ 已删除公司数据: {code}")
            return True
        return False


# 便捷函数
def get_company_db() -> CompanyDB:
    """获取默认数据库实例"""
    return CompanyDB()


def quick_save_profile(profile: CompanyProfile) -> None:
    """快速保存公司档案"""
    db = get_company_db()
    db.save_profile(profile)


def quick_load_profile(code: str) -> Optional[CompanyProfile]:
    """快速加载公司档案"""
    db = get_company_db()
    return db.load_profile(code)
