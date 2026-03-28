# Finance Toolkit - 金融功能库

系统化的金融数据分析工具，用于A股公司投研分析和行业研究。

## 功能特性

- **公司档案管理** - 结构化存储公司基本信息、财务数据
- **财务指标计算** - ROE/毛利率/负债率等自动计算与评估
- **行业分类体系** - 申万/中信标准行业分类
- **分析报告生成** - 标准化Markdown投研报告

## CLI 使用

安装可编辑包后，可以直接使用 CLI：

```bash
pip install -e .
ftk --help
python -m finance_toolkit --help
```

### 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| `FINANCE_DATA_ROOT` | 数据存储根目录，优先级高于 `config.yaml` | `~/.finance_toolkit/data` |

---

## 快速开始

```python
from finance_toolkit import CompanyAnalyzer

analyzer = CompanyAnalyzer()

# 创建公司档案
analyzer.create_profile(
    code="600519",
    name="贵州茅台",
    full_name="贵州茅台酒股份有限公司",
    business_scope="茅台酒及系列酒的生产与销售"
)

# 更新市场数据
analyzer.update_market_data(
    code="600519",
    market_cap=21000,
    pe_ttm=28.5,
    pb=8.2
)

# 生成分析报告
report = analyzer.generate_report("600519")
print(report)
```

## 项目结构

```
src/finance_toolkit/
├── __init__.py            # 包入口
├── __version__.py        # 版本信息
├── models.py              # 数据模型定义
├── config.py              # 配置管理
├── logger.py              # 日志模块
├── exceptions.py          # 异常定义
├── cli.py                 # CLI 入口
├── analyzer/
│   ├── company.py         # 公司分析
│   ├── metrics.py         # 财务指标
│   ├── dupont.py          # 杜邦分析
│   ├── valuation.py       # 估值模型
│   └── trend.py           # 趋势分析
├── data/
│   ├── db.py              # 数据库管理
│   ├── akshare.py         # AKShare 数据接口
│   └── importer.py        # 数据导入
├── industry/
│   ├── classification.py   # 行业分类
│   └── chain.py           # 产业链
└── report/
    └── generator.py       # 报告生成

~/.finance_toolkit/data/company/{code}/
├── profile.json           # 公司档案
└── metrics.json           # 财务指标历史
```

## 财务指标支持

| 指标类型 | 具体指标 |
|---------|---------|
| 盈利能力 | ROE, ROA, 毛利率, 净利率 |
| 成长能力 | 营收增长率, 净利润增长率 |
| 偿债能力 | 资产负债率, 流动比率, 速动比率 |
| 运营效率 | 存货周转率, 应收账款周转率 |
| 现金流 | 经营现金流, 自由现金流 |

## 依赖

- Python 3.8+
- 标准库：json, pathlib, dataclasses, typing

## 项目状态

🟡 v0.1 开发中 - 核心框架已完成

## License

MIT
