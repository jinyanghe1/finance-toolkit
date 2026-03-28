# Finance Toolkit - Agent 操作指南

> **面向 AI Agents** | 稳定执行框架 + 扩展指南

本文档是 Agent 使用 Finance Toolkit 的完整指南。

---

## 快速开始

```python
from finance_toolkit import CompanyAnalyzer

analyzer = CompanyAnalyzer()
report = analyzer.generate_report("600519")
print(report)
```

---

## 目录

1. [核心原则](#核心原则)
2. [标准流程 (SOP)](#标准流程-sop)
3. [扩展能力](#扩展能力)
4. [质量门禁](#质量门禁)
5. [常见任务](#常见任务)

---

## 核心原则

### Agent 行为准则

```
✅ 总是使用标准 API
✅ 验证每个步骤的输出
✅ 优雅处理错误
✅ 记录进度到 .agentstalk/

❌ 不要直接读写 JSON 文件
❌ 不要硬编码财务假设
❌ 不要绕过类型检查
```

### 输入/输出契约

| 阶段 | 输入 | 输出 | 验证 |
|------|------|------|------|
| 数据获取 | stock_code | CompanyProfile | `profile is not None` |
| 指标计算 | FinancialStatement | FinancialMetrics | 指标在有效范围 |
| 报告生成 | CompanyProfile + Metrics | Markdown str | `len(report) > 100` |

---

## 标准流程 (SOP)

### SOP-S1: 标准分析

获取单个公司的标准财务分析报告。

```python
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.data import search_stocks, fetch_company

# 1. 搜索公司
results = search_stocks("茅台")
code = results[0]["code"]

# 2. 获取档案
profile = fetch_company(code)

# 3. 财务摘要
analyzer = CompanyAnalyzer()
summary = analyzer.get_financial_summary(code)

# 4. 生成报告
report = analyzer.generate_report(code)
print(report)
```

**验证点**:
```python
assert len(results) > 0, "搜索结果为空"
assert profile is not None, "档案获取失败"
assert isinstance(report, str) and len(report) > 100
```

---

### SOP-S2: 深度研究

对公司进行全面的投资研究分析。

```python
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.analyzer.valuation import DCFValuation, DCFAssumptions
from finance_toolkit.analyzer.dupont import DupontAnalyzer
from finance_toolkit.analyzer.trend import TrendAnalyzer

code = "600519"
analyzer = CompanyAnalyzer()

# 1. 基础分析
summary = analyzer.get_financial_summary(code)

# 2. DCF 估值
dcf_result = DCFValuation.calculate(
    current_revenue=1505,
    current_operating_profit=800,
    current_depreciation=20,
    current_capex=30,
    current_nwc=50,
    net_debt=0,
    shares=12.56,
    assumptions=DCFAssumptions(
        forecast_years=5,
        revenue_growth=0.10,
        operating_margin=0.50,
        wacc=0.09,
        terminal_growth=0.03
    )
)
print(f"DCF 估值: {dcf_result.per_share_value:.2f} 元")

# 3. 趋势分析
trend = TrendAnalyzer.analyze(code, periods=8)
print(f"ROE 趋势: {trend.roe_trend}")

# 4. 杜邦分析
dupont = DupontAnalyzer.analyze(code)
print(f"ROE = {dupont.components.net_margin:.1f}% × {dupont.components.asset_turnover:.2f} × {dupont.components.equity_multiplier:.2f}")
```

---

### SOP-S3: 批量处理

批量分析多家公司或整个行业。

```python
# 直接批量分析
codes = ["600519", "000858", "000568", "600809"]
results = analyzer.analyze_batch(codes, output="results.json")

# 按行业批量
from finance_toolkit.data import AKShareProvider
provider = AKShareProvider()
industry_stocks = provider.get_industry_stocks("白酒")
codes = industry_stocks['代码'].tolist()[:10]

results = analyzer.analyze_batch(codes, output="liquor_analysis.json")
```

**结果聚合**:
```python
# 提取成功结果
successful = [r for r in results if r.get("success")]
avg_roe = sum(r["metrics"]["roe"] for r in successful) / len(successful)
print(f"平均 ROE: {avg_roe:.2f}%")
```

---

## 扩展能力

### 扩展原则

```
🎯 目标明确: 探索应有目的
📐 边界清晰: 稳定区不修改，实验区可探索
🧪 测试验证: 扩展必须经过验证
📝 文档记录: 探索过程记录到 .agentstalk/explorations/
```

### 扩展点地图

| 扩展领域 | 文件位置 | 说明 |
|---------|---------|------|
| 数据源 | `data/tushare.py` | 新增 Tushare 等数据源 |
| 分析方法 | `analyzer/quality.py` | 财务质量、情绪分析等 |
| 报告格式 | `report/html_generator.py` | HTML、JSON 报告 |
| 估值模型 | `analyzer/ddm.py` | DDM、PEG 等 |

### 扩展模板

**新数据源**:
```python
# src/finance_toolkit/data/tushare_provider.py
from ..logger import LogMixin

class TushareProvider(LogMixin):
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("TUSHARE_TOKEN")

    def get_stock_info(self, code: str):
        # TODO: 实现
        pass
```

**新分析方法**:
```python
# src/finance_toolkit/analyzer/quality.py
from ..logger import LogMixin

class QualityAnalyzer(LogMixin):
    def analyze(self, code: str) -> dict:
        """返回质量评分"""
        # TODO: 实现
        return {"score": 0-100}
```

### 扩展检查清单

- [ ] 继承 `LogMixin`
- [ ] 返回类型注解
- [ ] 添加日志
- [ ] 在 `__init__.py` 导出
- [ ] 添加单元测试
- [ ] 运行 `pytest tests/` 不破坏现有功能

---

## 质量门禁

### GATE-1: 数据获取

```python
def validate_profile(profile: CompanyProfile) -> bool:
    assert profile is not None, "档案为空"
    assert profile.stock is not None, "股票信息缺失"
    assert profile.stock.code is not None, "股票代码缺失"
    return True
```

### GATE-2: 财务指标

```python
def validate_metrics(metrics: FinancialMetrics) -> bool:
    if metrics.profitability.roe is not None:
        assert -50 <= metrics.profitability.roe <= 100
    if metrics.profitability.gross_margin is not None:
        assert 0 <= metrics.profitability.gross_margin <= 100
    if metrics.solvency.debt_to_asset is not None:
        assert 0 <= metrics.solvency.debt_to_asset <= 100
    return True
```

### GATE-3: 分析报告

```python
def validate_report(report: str, min_length: int = 200) -> bool:
    assert isinstance(report, str), "报告应为字符串"
    assert len(report) >= min_length, f"报告过短: {len(report)}"
    assert "ROE" in report or "毛利率" in report, "缺少关键指标"
    return True
```

---

## 常见任务

### 任务速查

| 任务 | 方法 |
|------|------|
| 搜索公司 | `search_stocks("关键词")` |
| 获取档案 | `fetch_company("600519")` |
| 财务摘要 | `analyzer.get_financial_summary("600519")` |
| 生成报告 | `analyzer.generate_report("600519")` |
| 批量分析 | `analyzer.analyze_batch(codes)` |
| DCF 估值 | `DCFValuation.calculate(...)` |
| 杜邦分析 | `DupontAnalyzer.analyze(code)` |
| 趋势分析 | `TrendAnalyzer.analyze(code)` |
| 导出 PDF | `markdown_to_pdf(md_content, path)` |
| 导出 JSON | `analyzer.export_report(code, "out.json", format="json")` |

### 标准导入

```python
from finance_toolkit import CompanyAnalyzer
from finance_toolkit.data import search_stocks, fetch_company
from finance_toolkit.analyzer import (
    MetricsCalculator,
    DupontAnalyzer,
    DCFValuation,
    TrendAnalyzer,
)
from finance_toolkit.report import markdown_to_pdf
```

### CLI 使用

```bash
ftk list                    # 列出现有公司
ftk analyze 600519          # 分析公司
ftk search 茅台             # 搜索公司
ftk batch analyze codes.txt  # 批量分析
```

---

## 数据结构

### CompanyProfile

```python
{
    "stock": {"code": "600519.SH", "name": "贵州茅台", "exchange": "SH"},
    "full_name": "贵州茅台酒股份有限公司",
    "industry": "消费",
    "market_data": {"market_cap": 21000.0, "pe_ttm": 28.5, "pb": 8.2},
    "updated_at": "2024-01-01T00:00:00"
}
```

### FinancialMetrics

```python
{
    "profitability": {"roe": 25.5, "gross_margin": 91.5, "net_margin": 52.0},
    "growth": {"revenue_growth_yoy": 15.0, "profit_growth_yoy": 18.0},
    "solvency": {"debt_to_asset": 35.0, "current_ratio": 2.5},
    "cashflow": {"operating_cash_flow": 665.0, "free_cash_flow": 600.0},
    "report_date": "2023-12-31"
}
```

---

## 异常处理

```python
from finance_toolkit.exceptions import (
    CompanyNotFoundError,
    DataError,
    ValidationError,
)

try:
    summary = analyzer.get_financial_summary(code)
except CompanyNotFoundError:
    print(f"公司 {code} 不存在")
except DataError as e:
    print(f"数据错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 数据存储

默认路径: `~/.finance_toolkit/data/`

可通过环境变量配置:
```bash
export FINANCE_DATA_ROOT=/path/to/data
```

---

<p align="center">
  <sub>Finance Toolkit | 稳定 + 可扩展 | for AI Agents</sub>
</p>
