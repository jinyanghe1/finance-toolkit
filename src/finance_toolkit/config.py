"""
Finance Toolkit - 配置管理
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict

import yaml

from .exceptions import ConfigError
from .logger import get_logger

logger = get_logger(__name__)


# 默认配置
DEFAULT_CONFIG = {
    "data": {
        "root_path": "~/.finance_toolkit/data",
        "company_dir": "company",
        "export_dir": "exports",
    },
    "logging": {
        "level": "INFO",
        "console": True,
        "file": None,
    },
    "analysis": {
        "default_metrics_years": 5,
        "peers_compare_limit": 10,
        "trend_analysis_periods": 4,
    },
    "valuation": {
        "risk_free_rate": 0.03,
        "market_risk_premium": 0.06,
        "terminal_growth_rate": 0.03,
        "forecast_years": 5,
    },
}


@dataclass
class DataConfig:
    """数据配置"""
    root_path: str = "~/.finance_toolkit/data"
    company_dir: str = "company"
    export_dir: str = "exports"
    
    @property
    def root(self) -> Path:
        """获取数据根目录路径"""
        return Path(self.root_path).expanduser()
    
    @property
    def company(self) -> Path:
        """获取公司数据目录"""
        return self.root / self.company_dir
    
    @property
    def exports(self) -> Path:
        """获取导出目录"""
        return self.root / self.export_dir


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    console: bool = True
    file: Optional[str] = None
    
    @property
    def log_file_path(self) -> Optional[Path]:
        """获取日志文件路径"""
        if self.file:
            return Path(self.file).expanduser()
        return None


@dataclass
class AnalysisConfig:
    """分析配置"""
    default_metrics_years: int = 5
    peers_compare_limit: int = 10
    trend_analysis_periods: int = 4


@dataclass
class ValuationConfig:
    """估值配置"""
    risk_free_rate: float = 0.03
    market_risk_premium: float = 0.06
    terminal_growth_rate: float = 0.03
    forecast_years: int = 5


@dataclass
class Config:
    """主配置类"""
    data: DataConfig = field(default_factory=DataConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    valuation: ValuationConfig = field(default_factory=ValuationConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """从字典创建配置"""
        return cls(
            data=DataConfig(**data.get("data", {})),
            logging=LoggingConfig(**data.get("logging", {})),
            analysis=AnalysisConfig(**data.get("analysis", {})),
            valuation=ValuationConfig(**data.get("valuation", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "data": asdict(self.data),
            "logging": asdict(self.logging),
            "analysis": asdict(self.analysis),
            "valuation": asdict(self.valuation),
        }
    
    def ensure_directories(self) -> None:
        """确保所需目录存在"""
        self.data.root.mkdir(parents=True, exist_ok=True)
        self.data.company.mkdir(parents=True, exist_ok=True)
        self.data.exports.mkdir(parents=True, exist_ok=True)
        
        if self.logging.log_file_path:
            self.logging.log_file_path.parent.mkdir(parents=True, exist_ok=True)


# 全局配置实例
_config: Optional[Config] = None


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，None 则使用默认路径
    
    Returns:
        Config 实例
    """
    global _config
    
    if config_path is None:
        # 按优先级查找配置文件
        config_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path.home() / ".finance_toolkit" / "config.yaml",
            Path.home() / ".finance_toolkit" / "config.yml",
        ]
        for path in config_paths:
            if path.exists():
                config_path = path
                break
    
    if config_path and config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            logger.info(f"加载配置文件: {config_path}")
            _config = Config.from_dict(data)
        except yaml.YAMLError as e:
            raise ConfigError(f"配置文件解析错误: {e}")
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {e}")
    else:
        logger.debug("使用默认配置")
        _config = Config()
    
    # 确保目录存在
    _config.ensure_directories()
    
    return _config


def get_config() -> Config:
    """
    获取当前配置
    
    Returns:
        Config 实例
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def save_config(config: Config, path: Path) -> None:
    """
    保存配置到文件
    
    Args:
        config: 配置实例
        path: 保存路径
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config.to_dict(), f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"配置已保存到: {path}")
