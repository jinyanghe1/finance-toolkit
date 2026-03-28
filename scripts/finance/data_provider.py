"""
金融功能库 - 数据获取接口
基于 AKShare 的 A股数据获取
"""

from typing import Optional, Dict, List
import akshare as ak
import pandas as pd
from datetime import datetime

from scripts.finance.models import StockInfo, CompanyProfile, FinancialMetrics
from scripts.finance.industry import Industry


class AKShareProvider:
    """AKShare 数据提供者"""

    @staticmethod
    def get_stock_info(code: str) -> Optional[Dict]:
        """
        获取股票基本信息

        Args:
            code: 股票代码，如 "600519" 或 "600519.SH"

        Returns:
            股票信息字典
        """
        try:
            # 标准化代码
            if "." not in code:
                code = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"

            # 获取股票详细信息
            df = ak.stock_individual_info_em(symbol=code)

            info = {}
            for _, row in df.iterrows():
                info[row["item"]] = row["value"]

            return {
                "code": code,
                "name": info.get("股票简称", ""),
                "exchange": code.split(".")[-1],
                "listing_date": info.get("上市时间", None),
                "total_shares": info.get("总股本", None),
                "float_shares": info.get("流通股本", None),
            }
        except Exception as e:
            print(f"获取股票信息失败 {code}: {e}")
            return None

    @staticmethod
    def get_market_data(code: str) -> Optional[Dict]:
        """
        获取实时市场数据

        Args:
            code: 股票代码

        Returns:
            市场数据字典
        """
        try:
            # 标准化代码
            if "." not in code:
                code = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"

            df = ak.stock_brief_list_em()

            # 查找对应股票
            code_clean = code.split(".")[0]
            row = df[df["代码"] == code_clean]

            if row.empty:
                return None

            row = row.iloc[0]
            return {
                "code": code,
                "name": row["名称"],
                "market_cap": row["总市值"] if "总市值" in row else None,
                "pe_ttm": row["市盈率-动态"] if "市盈率-动态" in row else None,
                "pb": row["市净率"] if "市净率" in row else None,
                "dividend_yield": row["股息率"] if "股息率" in row else None,
                "revenue": row["营业收入"] if "营业收入" in row else None,
                "profit": row["净利润"] if "净利润" in row else None,
            }
        except Exception as e:
            print(f"获取市场数据失败 {code}: {e}")
            return None

    @staticmethod
    def get_financial_statement(code: str, report_type: str = "年报") -> Optional[pd.DataFrame]:
        """
        获取财务报表

        Args:
            code: 股票代码
            report_type: 报告类型 "年报" 或 "季报"

        Returns:
            财务报表 DataFrame
        """
        try:
            # 标准化代码
            if "." not in code:
                code = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"

            code_clean = code.split(".")[0]

            if report_type == "年报":
                # 获取年报财务数据
                df = ak.stock_financial_report_sina(stock=code_clean, symbol="资产负债表")
                return df
            else:
                # 季报
                df = ak.stock_financial_report_sina(stock=code_clean, symbol="利润表")
                return df
        except Exception as e:
            print(f"获取财务报表失败 {code}: {e}")
            return None

    @staticmethod
    def get_historical_prices(code: str, period: str = "daily",
                               start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取历史价格数据

        Args:
            code: 股票代码
            period: 周期 "daily"/"weekly"/"monthly"
            start_date: 开始日期 "YYYYMMDD"
            end_date: 结束日期 "YYYYMMDD"

        Returns:
            价格数据 DataFrame
        """
        try:
            # 标准化代码
            if "." not in code:
                code = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"

            code_clean = code.split(".")[0]

            df = ak.stock_zh_a_hist(symbol=code_clean, period=period,
                                     start_date=start_date, end_date=end_date,
                                     adjust="qfq")
            return df
        except Exception as e:
            print(f"获取历史价格失败 {code}: {e}")
            return None

    @staticmethod
    def get_industry_classification(code: str) -> Optional[str]:
        """
        获取行业分类（申万行业）

        Args:
            code: 股票代码

        Returns:
            行业名称
        """
        try:
            code_clean = code.split(".")[0] if "." in code else code
            df = ak.stock_board_industry_name_em()
            return None  # 需要进一步匹配
        except Exception as e:
            print(f"获取行业分类失败 {code}: {e}")
            return None

    @staticmethod
    def search_stocks(keyword: str) -> List[Dict]:
        """
        搜索股票

        Args:
            keyword: 搜索关键词（代码或名称）

        Returns:
            匹配的股票列表
        """
        try:
            df = ak.stock_info_a_code_name()
            mask = df["code"].str.contains(keyword) | df["name"].str.contains(keyword)
            results = df[mask].head(10)

            return [
                {"code": row["code"], "name": row["name"]}
                for _, row in results.iterrows()
            ]
        except Exception as e:
            print(f"搜索股票失败 {keyword}: {e}")
            return []


class DataProvider:
    """统一数据接口，封装 AKShare"""

    def __init__(self):
        self.ak = AKShareProvider()

    def fetch_company_profile(self, code: str) -> Optional[CompanyProfile]:
        """获取公司完整档案"""
        info = self.ak.get_stock_info(code)
        if not info:
            return None

        # 获取市场数据
        market = self.ak.get_market_data(code)

        stock = StockInfo(
            code=info["code"],
            name=info["name"],
            exchange=info["exchange"],
            listing_date=info.get("listing_date"),
        )

        profile = CompanyProfile(
            stock=stock,
            full_name=info.get("name", info["name"]),
            total_shares=float(info["total_shares"].replace("亿", ""))
                         if info.get("total_shares") and "亿" in str(info["total_shares"]) else None,
            float_shares=float(info["float_shares"].replace("亿", ""))
                         if info.get("float_shares") and "亿" in str(info["float_shares"]) else None,
        )

        # 更新市场数据
        if market:
            if market.get("market_cap"):
                profile.market_cap = market["market_cap"]
            if market.get("pe_ttm"):
                profile.pe_ttm = market["pe_ttm"]
            if market.get("pb"):
                profile.pb = market["pb"]
            if market.get("dividend_yield"):
                profile.dividend_yield = market["dividend_yield"]

        return profile

    def fetch_market_data(self, code: str) -> Optional[Dict]:
        """获取市场数据"""
        return self.ak.get_market_data(code)

    def fetch_historical_prices(self, code: str, days: int = 365) -> Optional[pd.DataFrame]:
        """获取历史价格"""
        import datetime
        end = datetime.datetime.now().strftime("%Y%m%d")
        start = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
        return self.ak.get_historical_prices(code, start_date=start, end_date=end)

    def search(self, keyword: str) -> List[Dict]:
        """搜索股票"""
        return self.ak.search_stocks(keyword)


# 便捷函数
def get_data_provider() -> DataProvider:
    """获取数据提供者实例"""
    return DataProvider()


def search_stocks(keyword: str) -> List[Dict]:
    """搜索股票"""
    provider = DataProvider()
    return provider.search(keyword)


def fetch_company(code: str) -> Optional[CompanyProfile]:
    """获取公司档案"""
    provider = DataProvider()
    return provider.fetch_company_profile(code)


if __name__ == "__main__":
    # 测试
    provider = DataProvider()

    # 搜索贵州茅台
    print("搜索 '茅台':")
    results = provider.search("茅台")
    for r in results:
        print(f"  {r['code']} - {r['name']}")

    # 获取市场数据
    print("\n获取 600519 市场数据:")
    data = provider.fetch_market_data("600519")
    if data:
        for k, v in data.items():
            print(f"  {k}: {v}")
