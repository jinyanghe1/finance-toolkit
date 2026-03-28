"""
Finance Toolkit - 日志系统
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
    
    Returns:
        配置好的 Logger 实例
    """
    return logging.getLogger(f"finance_toolkit.{name}")


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
) -> None:
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，None 则不写入文件
        console: 是否输出到控制台
    """
    # 获取根日志记录器
    logger = logging.getLogger("finance_toolkit")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有处理器
    logger.handlers = []
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # 控制台输出
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件输出
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


class LogMixin:
    """为类提供日志功能的 Mixin"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        return get_logger(self.__class__.__name__)
