"""
测试数据模型
"""

import pytest

from finance_toolkit.models import (
    StockInfo,
    CompanyProfile,
    FinancialMetrics,
    Industry,
    Exchange,
    detect_exchange,
    get_benchmark,
)


class TestStockInfo:
    """测试股票信息模型"""
    
    def test_create_stock(self):
        """测试创建股票信息"""
        stock = StockInfo(
            code="600519.SH",
            name="贵州茅台",
            exchange=Exchange.SH,
        )
        assert stock.code == "600519.SH"
        assert stock.name == "贵州茅台"
        assert stock.exchange == Exchange.SH
    
    def test_auto_complete_code(self):
        """测试自动补全代码"""
        stock = StockInfo(
            code="600519",
            name="贵州茅台",
            exchange=Exchange.SH,
        )
        assert stock.code == "600519.SH"
    
    def test_to_dict(self):
        """测试转换为字典"""
        stock = StockInfo(
            code="600519.SH",
            name="贵州茅台",
            exchange=Exchange.SH,
        )
        data = stock.to_dict()
        assert data["code"] == "600519.SH"
        assert data["name"] == "贵州茅台"
        assert data["exchange"] == "SH"
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "code": "600519.SH",
            "name": "贵州茅台",
            "exchange": "SH",
        }
        stock = StockInfo.from_dict(data)
        assert stock.code == "600519.SH"
        assert stock.name == "贵州茅台"
        assert stock.exchange == Exchange.SH


class TestCompanyProfile:
    """测试公司档案模型"""
    
    def test_create_profile(self):
        """测试创建公司档案"""
        stock = StockInfo(code="600519.SH", name="贵州茅台", exchange=Exchange.SH)
        profile = CompanyProfile(
            stock=stock,
            full_name="贵州茅台酒股份有限公司",
            industry=Industry.CONSUMER,
        )
        assert profile.stock.name == "贵州茅台"
        assert profile.full_name == "贵州茅台酒股份有限公司"
        assert profile.industry == Industry.CONSUMER
    
    def test_to_from_dict(self):
        """测试序列化和反序列化"""
        stock = StockInfo(code="600519.SH", name="贵州茅台", exchange=Exchange.SH)
        profile = CompanyProfile(
            stock=stock,
            full_name="贵州茅台酒股份有限公司",
            industry=Industry.CONSUMER,
        )
        
        data = profile.to_dict()
        restored = CompanyProfile.from_dict(data)
        
        assert restored.stock.name == profile.stock.name
        assert restored.full_name == profile.full_name
        assert restored.industry == profile.industry


class TestDetectExchange:
    """测试交易所检测"""
    
    def test_shanghai_code(self):
        """测试上海股票代码"""
        assert detect_exchange("600519") == Exchange.SH
        assert detect_exchange("601398") == Exchange.SH
        assert detect_exchange("688981") == Exchange.SH  # 科创板
    
    def test_shenzhen_code(self):
        """测试深圳股票代码"""
        assert detect_exchange("000001") == Exchange.SZ
        assert detect_exchange("300750") == Exchange.SZ  # 创业板
    
    def test_beijing_code(self):
        """测试北京股票代码"""
        assert detect_exchange("835305") == Exchange.BJ
    
    def test_code_with_suffix(self):
        """测试带后缀的代码"""
        assert detect_exchange("600519.SH") == Exchange.SH


class TestBenchmarks:
    """测试基准值"""
    
    def test_default_benchmark(self):
        """测试默认基准"""
        benchmark = get_benchmark()
        assert "roe" in benchmark
        assert benchmark["roe"]["excellent"] == 20
    
    def test_industry_benchmark(self):
        """测试行业基准"""
        benchmark = get_benchmark(Industry.BANK)
        assert "roe" in benchmark
        # 银行 ROE 标准较低
        assert benchmark["roe"]["excellent"] == 15
    
    def test_specific_metric(self):
        """测试获取特定指标基准"""
        benchmark = get_benchmark(metric="roe")
        assert "excellent" in benchmark
