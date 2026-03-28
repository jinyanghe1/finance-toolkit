# Finance Toolkit - 功能基线文档

> 最后更新: 2026-03-28 18:16
> 版本: v0.1

## 项目概述

系统化金融数据分析工具，用于A股公司投研分析和行业研究。

## 项目结构

```
finance-toolkit/
├── models.py                    # 数据模型定义
├── company_analyzer.py          # 公司分析主入口
├── industry.py                  # 行业分类体系
├── analyzers/
│   └── financial_metrics.py     # 财务指标计算
├── storage/
│   └── company_db.py            # 公司数据库管理
├── demo.py                      # 快速示例脚本
├── README.md                    # 项目说明文档
└── .gitignore                   # Git忽略配置
```

## 核心功能模块

### 1. 数据模型 (models.py)

| 模型 | 描述 | 关键字段 |
|------|------|----------|
| `StockInfo` | 股票基本信息 | code, name, exchange, listing_date |
| `CompanyProfile` | 公司档案 | stock, full_name, business_scope, industry, market_data |
| `FinancialMetrics` | 财务指标 | profitability, growth, solvency, efficiency, cashflow |

**支持的财务指标类型:**
- 盈利能力: ROE, ROA, 毛利率, 净利率
- 成长能力: 营收增长率, 净利润增长率
- 偿债能力: 资产负债率, 流动比率, 速动比率
- 运营效率: 存货周转率, 应收账款周转率
- 现金流: 经营现金流, 自由现金流

### 2. 公司分析器 (company_analyzer.py)

**CompanyAnalyzer 类功能:**
- `create_profile()` - 创建公司档案
- `get_profile()` - 获取公司档案
- `update_market_data()` - 更新市场数据
- `add_financial_statement()` - 添加财务报表并计算指标
- `get_financial_summary()` - 获取财务摘要
- `list_all_companies()` - 列出所有公司
- `generate_report()` - 生成Markdown分析报告

**便捷函数:**
- `analyze_company(code)` - 快速分析公司
- `get_company_summary(code)` - 快速获取摘要
- `list_companies()` - 列出所有公司

### 3. 财务指标计算 (analyzers/financial_metrics.py)

**FinancialStatement 数据结构:**
- 利润表: revenue, cost_of_goods_sold, gross_profit, net_profit
- 资产负债表: total_assets, current_assets, inventory, accounts_receivable, liabilities, equity
- 现金流量表: operating_cash_flow, investing_cash_flow, financing_cash_flow

**MetricsCalculator 功能:**
- `calculate_all_metrics()` - 计算所有财务指标
- `calculate_growth_rate()` - 计算增长率
- `calculate_cagr()` - 计算复合年增长率
- `evaluate_metric()` - 评估指标水平（优秀/良好/一般）

**PeerComparator 功能:**
- `compare_metrics()` - 同业对比分析
- `generate_comparison_table()` - 生成对比表格

### 4. 数据存储 (storage/company_db.py)

**CompanyDB 功能:**
- `save_profile()` / `load_profile()` - 公司档案存取
- `save_metrics()` / `load_metrics()` - 财务指标存取
- `list_companies()` - 列出所有公司
- `get_summary()` - 获取公司摘要
- `delete_company()` - 删除公司数据

**数据存储路径:** `/root/.openclaw/workspace/data/finance/company/{code}/`
- `profile.json` - 公司档案
- `metrics.json` - 财务指标历史

### 5. 行业分类 (industry.py)

**Industry 枚举:** 申万/中信标准一级行业分类
- 金融、房地产、制造、科技、医药健康、消费、能源、材料、公用事业、交运、传媒、农业等

**IndustryChain 产业链定义:**
- 新能源汽车产业链
- 白酒产业链
- 半导体产业链

**IndustryDB 功能:**
- `get_by_name()` - 通过中文名获取行业
- `get_by_sector()` - 获取板块下的行业
- `get_chain()` - 获取产业链信息

## 参考标准

```python
BENCHMARKS = {
    "roe": {"excellent": 20, "good": 15, "average": 10},
    "gross_margin": {"excellent": 40, "good": 30, "average": 20},
    "debt_to_asset": {"safe": 50, "warning": 70, "danger": 80},
    "current_ratio": {"safe": 2.0, "warning": 1.5, "danger": 1.0},
}
```

## 依赖要求

- Python 3.8+
- 标准库: json, pathlib, dataclasses, typing, datetime, enum

## 已知问题/TODO

1. 数据存储路径硬编码为 `/root/.openclaw/workspace/data/finance`，需要支持可配置
2. 缺少单元测试
3. 缺少数据导入接口（如从CSV/Excel读取财务数据）
4. 缺少实时数据获取接口（需要与kimi_finance模块集成）
5. 行业分类仅覆盖部分行业，需要扩充

## 多Agent协作记录

| 时间 | Agent | 操作 | 状态 |
|------|-------|------|------|
| 03281816 | Kimi | 全面仓库扫描 + Features文档创建 | ✅ 完成 |
