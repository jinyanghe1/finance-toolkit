# Finance Toolkit - 金融功能库

系统化的金融数据分析工具，用于A股公司投研分析和行业研究。

## 功能特性

- **公司档案管理** - 结构化存储公司基本信息、财务数据
- **财务指标计算** - ROE/毛利率/负债率等自动计算与评估
- **行业分类体系** - 申万/中信标准行业分类
- **分析报告生成** - 标准化Markdown投研报告

## MCP 配置

本项目支持通过 MCP (Model Context Protocol) 协议访问。以下是常用 MCP 服务器配置：

### Claude Code 集成

在 `~/.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "python",
      "args": ["-m", "scripts.finance.mcp_server"]
    }
  }
}
```

### Claude Desktop 集成

在 `~/.claude/resources/mcp_servers.json` 中添加：

```json
{
  "finance-toolkit": {
    "command": "python",
    "args": ["-m", "scripts.finance.mcp_server"],
    "env": {
      "FINANCE_DATA_ROOT": "~/.local/share/finance"
    }
  }
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| `FINANCE_DATA_ROOT` | 数据存储根目录 | `~/.local/share/finance` |

---

## 快速开始

```python
from scripts.finance.company_analyzer import CompanyAnalyzer

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
/scripts/finance/
├── models.py              # 数据模型定义
├── company_analyzer.py    # 公司分析主入口
├── industry.py            # 行业分类体系
├── storage/company_db.py  # 公司数据库管理
└── analyzers/financial_metrics.py  # 财务指标计算

/data/finance/company/{code}/
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
