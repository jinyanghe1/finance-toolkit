"""
Finance Toolkit - 自定义异常类
"""


class FinanceToolkitError(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ConfigError(FinanceToolkitError):
    """配置错误"""
    
    def __init__(self, message: str):
        super().__init__(message, code="CONFIG_ERROR")


class DataError(FinanceToolkitError):
    """数据错误"""
    
    def __init__(self, message: str):
        super().__init__(message, code="DATA_ERROR")


class CompanyNotFoundError(DataError):
    """公司不存在"""
    
    def __init__(self, code: str):
        super().__init__(f"公司档案不存在: {code}")
        self.company_code = code


class ValidationError(DataError):
    """数据验证错误"""
    
    def __init__(self, message: str, field: str = ""):
        super().__init__(message)
        self.field = field


class CalculationError(FinanceToolkitError):
    """计算错误"""
    
    def __init__(self, message: str):
        super().__init__(message, code="CALC_ERROR")


class ImportError(FinanceToolkitError):
    """数据导入错误"""
    
    def __init__(self, message: str, filename: str = ""):
        super().__init__(message, code="IMPORT_ERROR")
        self.filename = filename


class IndustryError(FinanceToolkitError):
    """行业分类错误"""
    
    def __init__(self, message: str):
        super().__init__(message, code="INDUSTRY_ERROR")
