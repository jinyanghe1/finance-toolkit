"""
pytest 配置文件
"""

import pytest
import tempfile
from pathlib import Path

from finance_toolkit.config import Config, DataConfig, LoggingConfig
from finance_toolkit.data.db import CompanyDB, reset_db_instance


@pytest.fixture
def temp_data_dir():
    """提供临时数据目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_db(temp_data_dir):
    """提供测试数据库实例"""
    reset_db_instance()
    db = CompanyDB(data_root=temp_data_dir)
    yield db
    reset_db_instance()


@pytest.fixture
def mock_config(temp_data_dir, monkeypatch):
    """提供测试配置"""
    config = Config(
        data=DataConfig(root_path=str(temp_data_dir)),
        logging=LoggingConfig(level="DEBUG"),
    )
    
    def mock_get_config():
        return config
    
    import finance_toolkit.config
    monkeypatch.setattr(finance_toolkit.config, "get_config", mock_get_config)
    monkeypatch.setattr(finance_toolkit.config, "_config", config)
    
    return config
