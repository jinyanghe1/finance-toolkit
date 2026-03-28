# AGENTS.md - AI Agent 开发者指南

> 本文档专为 AI Agents 设计，介绍如何使用和扩展 Finance Toolkit。

---

## 📋 目录

1. [Agent 快速入门](#agent-快速入门)
2. [核心使用模式](#核心使用模式)
3. [数据结构说明](#数据结构说明)
4. [错误处理指南](#错误处理指南)
5. [多 Agent 协作规范](#多-agent-协作规范)
6. [扩展开发指南](#扩展开发指南)

---

## Agent 快速入门

### 1. 理解项目定位

Finance Toolkit 是一个**结构化的金融数据分析框架**，适合 Agents：

- 不需要理解金融专业知识，只需要调用API
- 所有输出都有明确的数据结构
- 异常处理完善，不会崩溃

### 2. 最简单的使用示例

```python
# 步骤1: 导入主类
from finance_toolkit import CompanyAnalyzer

# 步骤2: 创建分析器实例
analyzer = CompanyAnalyzer()

# 步骤3: 获取分析结果
try:
    summary = analyzer.get_financial_summary("600519")
    # summary 是一个字典，包含结构化数据
    print(f"公司名称: {summary['公司信息']['名称']}")
    print(f"ROE: {summary['最新财务指标'].get('ROE', 'N/A')}")
except Exception as e:
    # 优雅处理错误
    print(f"分析失败: {e}")
```

### 3. 作为 Agent 你应该记住的3个类

| 类名 | 用途 | 关键方法 |
|------|------|----------|
| `CompanyAnalyzer` | 主要入口 | `get_financial_summary()`, `generate_report()` |
| `CompanyProfile` | 公司信息 | 数据模型，读取属性即可 |
| `FinancialMetrics` | 财务指标 | `to_dict()` 转为字典 |

---

## 核心使用模式

### 模式1: 批量分析多家公司

```python
from finance_toolkit import CompanyAnalyzer
from typing import List, Dict

analyzer = CompanyAnalyzer()

def batch_analyze(codes: List[str]) -> Dict[str, dict]:
    """
    批量分析公司，返回结构化结果
    
    Args:
        codes: 股票代码列表
    
    Returns:
        {代码: 分析结果} 的字典
    """
    results = {}
    
    for code in codes:
        try:
            summary = analyzer.get_financial_summary(code)
            results[code] = {
                "success": True,
                "data": summary,
            }
        except Exception as e:
            results[code] = {
                "success": False,
                "error": str(e),
            }
    
    return results

# 使用示例
codes = ["600519", "000858", "000568"]  # 白酒三巨头
results = batch_analyze(codes)

# 筛选出分析成功的
successful = {k: v for k, v in results.items() if v["success"]}
print(f"成功分析: {len(successful)}/{len(codes)} 家")
```

### 模式2: 比较多家公司

```python
from finance_toolkit.analyzer.metrics import PeerComparator

companies = [
    {"name": "茅台", "metrics": {"ROE": 25.5, "毛利率": 91.5}},
    {"name": "五粮液", "metrics": {"ROE": 20.3, "毛利率": 75.2}},
    {"name": "老窖", "metrics": {"ROE": 22.1, "毛利率": 86.4}},
]

comparison = PeerComparator.compare_metrics(
    companies,
    metrics=["ROE", "毛利率"]
)

# comparison 包含排名、均值、极值
# Agent可以直接使用这些数据进行进一步分析
```

### 模式3: 生成并解析报告

```python
report = analyzer.generate_report("600519")

# report 是 Markdown 格式的字符串
# Agent可以使用正则表达式或字符串处理提取关键信息

import re

# 提取ROE
roe_match = re.search(r'ROE\s*\|\s*([\d.]+)%', report)
if roe_match:
    roe = float(roe_match.group(1))
    print(f"ROE: {roe}%")
```

### 模式4: 使用实时数据

```python
from finance_toolkit.data import fetch_company, search_stocks

# 搜索公司
results = search_stocks("茅台")
# 返回: [{"code": "600519", "name": "贵州茅台"}, ...]

# 获取完整档案
profile = fetch_company("600519")
# profile 是 CompanyProfile 对象
```

---

## 数据结构说明

### CompanyProfile (公司档案)

```python
{
    "stock": {
        "code": "600519.SH",          # 股票代码
        "name": "贵州茅台",            # 股票名称
        "exchange": "SH",             # 交易所
        "listing_date": "2001-08-27", # 上市日期
    },
    "full_name": "贵州茅台酒股份有限公司",
    "business_scope": "茅台酒及系列酒的生产与销售",
    "industry": "消费",               # 所属行业
    "market_data": {
        "market_cap": 21000.0,        # 总市值(亿元)
        "pe_ttm": 28.5,               # 市盈率
        "pb": 8.2,                    # 市净率
    },
    "updated_at": "2024-01-01T00:00:00"
}
```

### FinancialMetrics (财务指标)

```python
{
    "profitability": {
        "roe": 25.5,                  # ROE (%)
        "gross_margin": 91.5,         # 毛利率 (%)
        "net_margin": 52.0,           # 净利率 (%)
    },
    "growth": {
        "revenue_growth_yoy": 15.0,   # 营收增长 (%)
        "profit_growth_yoy": 18.0,    # 净利润增长 (%)
    },
    "solvency": {
        "debt_to_asset": 35.0,        # 资产负债率 (%)
        "current_ratio": 2.5,         # 流动比率
    },
    "cashflow": {
        "operating_cash_flow": 665.0, # 经营现金流(亿元)
        "free_cash_flow": 600.0,      # 自由现金流
    },
    "report_date": "2023-12-31"       # 报告期
}
```

---

## 错误处理指南

### 常见异常类型

```python
from finance_toolkit.exceptions import (
    CompanyNotFoundError,    # 公司不存在
    DataError,               # 数据错误
    ValidationError,         # 验证错误
    ImportError,             # 导入错误
    ConfigError,             # 配置错误
)
```

### 推荐的错误处理模式

```python
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.exceptions import CompanyNotFoundError, DataError

analyzer = CompanyAnalyzer()

def safe_analyze(code: str) -> dict:
    """安全地分析公司，返回统一格式"""
    try:
        return {
            "code": code,
            "status": "success",
            "data": analyzer.get_financial_summary(code)
        }
    except CompanyNotFoundError:
        return {
            "code": code,
            "status": "not_found",
            "message": f"公司 {code} 不存在"
        }
    except DataError as e:
        return {
            "code": code,
            "status": "data_error",
            "message": str(e)
        }
    except Exception as e:
        # 捕获未知异常
        return {
            "code": code,
            "status": "error",
            "message": f"未知错误: {e}"
        }
```

---

## 多 Agent 协作规范

### 文件结构

```
.agentstalk/
├── Features                  # 功能基线 (必须保持最新)
├── Features.md               # 详细功能文档
├── plan_*.md                 # 开发计划
├── progress_*.md             # 进度同步
└── issues/                   # 问题跟踪
    └── issue_{id}_{描述}.md
```

### 作为 Agent，你应该：

1. **开始前**
   - 阅读 `.agentstalk/Features` 了解当前功能
   - 查看 `.agentstalk/plan_*.md` 了解开发计划
   - 确认没有重复工作

2. **进行中**
   - 创建自己的进度文件: `.agentstalk/progress_{mmddhhmm}_{任务}_{你的标识}.md`
   - 定期更新进度
   - 遇到问题创建 `.agentstalk/issues/issue_{id}_{描述}.md`

3. **完成后**
   - 将进度文件重命名为 `_CLOSED`
   - 更新 `.agentstalk/Features`
   - 关闭相关 issues

### 进度文件模板

```markdown
# 任务名称

**时间**: YYYY-MM-DD HH:MM
**Agent**: 你的标识
**状态**: 🟡 进行中 / ✅ 完成

## 目标
描述本次任务的目标

## 进度
- [x] 已完成项1
- [ ] 待完成项2

## 阻塞
如果有阻塞问题，在此说明

## 产出
列出创建或修改的文件
```

---

## 扩展开发指南

### 添加新的分析模块

1. 在 `src/finance_toolkit/analyzer/` 创建新文件
2. 继承 `LogMixin` 获取日志功能
3. 使用 `get_logger(__name__)` 创建日志器
4. 在 `analyzer/__init__.py` 中导出

示例：

```python
# src/finance_toolkit/analyzer/my_analysis.py
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)

class MyAnalyzer(LogMixin):
    """我的分析器"""
    
    def analyze(self, code: str) -> dict:
        self.logger.info(f"开始分析: {code}")
        # 你的分析逻辑
        return result
```

### 添加新的数据源

1. 在 `src/finance_toolkit/data/` 创建接口文件
2. 实现数据获取方法
3. 在 `data/__init__.py` 中导出
4. 使用 try/except 处理可选依赖

---

## 快速参考

### 导入速查

```python
# 主入口
from finance_toolkit import CompanyAnalyzer

# 数据获取
from finance_toolkit.data import fetch_company, search_stocks

# 分析工具
from finance_toolkit.analyzer import (
    MetricsCalculator,
    DupontAnalyzer,
    DCFValuation,
    TrendAnalyzer,
)

# 行业数据
from finance_toolkit.industry import Industry, get_industry_by_name
```

### CLI 速查

```bash
# 查看帮助
ftk --help

# 列出现有公司
ftk list

# 分析公司
ftk analyze 600519

# 搜索公司
ftk search 茅台

# 显示配置
ftk config
```

---

## 常见问题 (Agent FAQ)

**Q: 我不知道股票代码，只知道公司名称怎么办？**
```python
from finance_toolkit.data import search_stocks
results = search_stocks("茅台")
# 返回匹配的股票列表
```

**Q: 如何批量获取多家公司的数据？**
使用循环 + try/except 包裹，参见上方的"批量分析"模式。

**Q: 数据存储在哪里？**
默认在 `~/.finance_toolkit/data/`，可通过环境变量 `FINANCE_DATA_ROOT` 修改。

**Q: 如何导出分析结果？**
```python
analyzer = CompanyAnalyzer()
analyzer.export_report("600519", "/path/to/report.md")
```

**Q: 我是Agent，如何参与开发？**
阅读[多 Agent 协作规范](#多-agent-协作规范)部分，遵循 `.agentstalk/` 的协作流程。

---

<p align="center">
  <sub>Happy Coding, Agents! 🤖</sub>
</p>
