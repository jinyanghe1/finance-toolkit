# Finance Toolkit - Agent SOP

> **标准操作流程** | 稳定 + 可扩展 | for AI Agents

本文档定义了 Finance Toolkit 的标准操作流程，确保 AI Agents 能够稳定地执行金融分析任务。

---

## 目录

1. [核心原则](#核心原则)
2. [SOP-S1: 标准分析流程](#sop-s1-标准分析流程)
3. [SOP-S2: 深度研究流程](#sop-s2-深度研究流程)
4. [SOP-S3: 批量处理流程](#sop-s3-批量处理流程)
5. [质量门禁](#质量门禁)
6. [探索指南](./EXPLORATION.md)

---

## 核心原则

### 稳定性优先

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent 行为准则                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ 总是使用标准 API                                          │
│  ✅ 验证每个步骤的输出                                         │
│  ✅ 优雅处理错误                                              │
│  ✅ 记录进度到 .agentstalk/                                   │
│                                                              │
│  ❌ 不要直接读写 JSON 文件                                    │
│  ❌ 不要硬编码财务假设                                        │
│  ❌ 不要绕过类型检查                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 输入/输出契约

| 阶段 | 输入 | 输出 | 验证 |
|-----|------|------|------|
| 数据获取 | stock_code (str) | CompanyProfile | profile is not None |
| 指标计算 | FinancialStatement | FinancialMetrics | all metrics in valid range |
| 报告生成 | CompanyProfile + Metrics | Markdown str | len(report) > 100 |

---

## SOP-S1: 标准分析流程

### 目标
获取单个公司的标准财务分析报告

### 流程图

```
start
  │
  ├─→ 1. search_stocks(name) ─→ 获取股票代码
  │
  ├─→ 2. fetch_company(code) ─→ 获取公司档案
  │
  ├─→ 3. get_financial_summary() ─→ 财务摘要
  │
  ├─→ 4. generate_report() ─→ Markdown 报告
  │
  └─→ 5. (可选) markdown_to_pdf() ─→ PDF 导出
```

### 代码模板

```python
"""
SOP-S1: 标准公司分析
适用于: 快速了解一家公司的基本情况
"""

from finance_toolkit import CompanyAnalyzer
from finance_toolkit.data import search_stocks, fetch_company
from finance_toolkit.report import markdown_to_pdf

# ========== 步骤 1: 搜索公司 ==========
# 输入: 公司名称关键词
# 输出: [{"code": "600519", "name": "贵州茅台"}, ...]

search_results = search_stocks("茅台")
if not search_results:
    print("未找到匹配公司")
    exit()

# 选择第一个结果
target = search_results[0]
code = target["code"]
print(f"选择公司: {target['name']} ({code})")

# ========== 步骤 2: 获取公司档案 ==========
# 输入: 股票代码
# 输出: CompanyProfile 对象

profile = fetch_company(code)
if not profile:
    print(f"无法获取公司档案: {code}")
    exit()

# ========== 步骤 3: 财务摘要 (如已存储) ==========
# 输入: 股票代码
# 输出: dict 包含公司信息、市场数据、财务指标

analyzer = CompanyAnalyzer()
summary = analyzer.get_financial_summary(code)

# ========== 步骤 4: 生成报告 ==========
# 输入: 股票代码
# 输出: Markdown 格式字符串

report = analyzer.generate_report(code)
print(report)

# ========== 步骤 5: PDF 导出 (可选) ==========
# 输入: Markdown 字符串, 输出路径
# 输出: PDF 文件

markdown_to_pdf(report, f"/tmp/{code}_report.pdf")
print(f"PDF 已导出: /tmp/{code}_report.pdf")
```

### 验证点 (Quality Gates)

```python
# GATE-1: 搜索结果验证
assert len(search_results) > 0, "搜索结果为空"

# GATE-2: 档案验证
assert profile is not None, "档案获取失败"
assert profile.stock.code is not None, "股票代码缺失"
assert profile.stock.name is not None, "股票名称缺失"

# GATE-3: 报告验证
assert isinstance(report, str), "报告应为字符串"
assert len(report) > 100, "报告内容过短"
assert "ROE" in report or "毛利率" in report, "报告缺少关键指标"
```

---

## SOP-S2: 深度研究流程

### 目标
对公司进行全面的投资研究分析

### 流程图

```
start (SOP-S1 完成)
  │
  ├─→ 1. 估值分析
  │     ├─→ DCFValuation.calculate()
  │     ├─→ RelativeValuation.calculate()
  │     └─→ get_benchmark()
  │
  ├─→ 2. 趋势分析
  │     └─→ TrendAnalyzer.analyze()
  │
  ├─→ 3. 杜邦分析
  │     └─→ DupontAnalyzer.analyze()
  │
  ├─→ 4. 综合判断
  │     ├─→ 盈利能力评估
  │     ├─→ 成长性评估
  │     ├─→ 财务风险评估
  │     └─→ 估值合理性判断
  │
  └─→ 5. 生成深度报告
```

### 代码模板

```python
"""
SOP-S2: 深度投资研究
适用于: 投资决策前的全面分析
"""

from finance_toolkit import CompanyAnalyzer
from finance_toolkit.analyzer.valuation import DCFValuation, DCFAssumptions, RelativeValuation
from finance_toolkit.analyzer.dupont import DupontAnalyzer
from finance_toolkit.analyzer.trend import TrendAnalyzer
from finance_toolkit.analyzer.metrics import PeerComparator
from finance_toolkit.models import get_benchmark

code = "600519"
analyzer = CompanyAnalyzer()

# ========== 1. 基础分析 (SOP-S1) ==========
summary = analyzer.get_financial_summary(code)
report = analyzer.generate_report(code)

# ========== 2. 估值分析 ==========

# 2.1 DCF 估值
dcf_assumptions = DCFAssumptions(
    forecast_years=5,
    revenue_growth=0.10,      # 10% 增长率假设
    operating_margin=0.50,     # 50% 营业利润率
    wacc=0.09,                 # 9% 加权平均资本成本
    terminal_growth=0.03        # 3% 永续增长率
)

dcf_result = DCFValuation.calculate(
    current_revenue=1505,      # 当前营收 (亿元)
    current_operating_profit=800,
    current_depreciation=20,
    current_capex=30,
    current_nwc=50,
    net_debt=0,
    shares=12.56,              # 股本 (亿股)
    assumptions=dcf_assumptions
)

print(f"DCF 估值: {dcf_result.per_share_value:.2f} 元")
print(f"当前股价: {summary['市场数据']['PE(TTM)']}")

# 2.2 相对估值
peer_results = RelativeValuation.calculate(
    target_code=code,
    peers=["000858", "000568"],
    method="pe"  # PE/PB/PS
)

# 2.3 行业基准对比
industry = summary['公司信息']['行业']
benchmark = get_benchmark(industry)
print(f"行业 {industry} ROE 优秀标准: {benchmark['roe']['excellent']}%")

# ========== 3. 趋势分析 ==========
trend = TrendAnalyzer.analyze(code, periods=8)  # 8期财报
print(f"ROE 趋势: {trend.roe_trend}")  # "上升" / "下降" / "稳定"
print(f"营收增长趋势: {trend.revenue_trend}")

# ========== 4. 杜邦分析 ==========
dupont = DupontAnalyzer.analyze(code)
print(f"ROE = 净利率({dupont.components.net_margin:.1f}%) "
      f"× 周转率({dupont.components.asset_turnover:.2f}) "
      f"× 权益乘数({dupont.components.equity_multiplier:.2f})")

# ========== 5. 综合判断 ==========
def comprehensive_assessment(summary, dcf, peer, trend, dupont):
    """综合评估"""

    scores = {
        "profitability": 0,  # 盈利能力 (0-100)
        "growth": 0,         # 成长性
        "financial_health": 0,  # 财务健康
        "valuation": 0,      # 估值吸引力
    }

    # 盈利能力评分
    roe = summary['最新财务指标'].get('ROE', 0)
    if roe >= 20:
        scores["profitability"] = 100
    elif roe >= 15:
        scores["profitability"] = 80
    elif roe >= 10:
        scores["profitability"] = 60
    else:
        scores["profitability"] = 40

    # 估值评分 (基于 DCF vs 当前价格)
    dcf_value = dcf.per_share_value
    # (需要当前股价进行比较)
    # 如果 DCF > 当前价格，说明被低估

    return scores

scores = comprehensive_assessment(summary, dcf_result, peer_results, trend, dupont)
print(f"综合评分: {scores}")

# ========== 6. 深度报告 ==========
depth_report = f"""
# {summary['公司信息']['名称']} ({code}) 深度研究报告

## 估值分析
- DCF 估值: {dcf_result.per_share_value:.2f} 元
- 当前估值: (需实时价格)
- 相对估值 vs 同业: (见 peer_results)

## 趋势判断
- ROE 趋势: {trend.roe_trend}
- 营收增长: {trend.revenue_trend}

## 杜邦分解
{dupont.interpretation}

## 综合评分
{scores}
"""

print(depth_report)
```

---

## SOP-S3: 批量处理流程

### 目标
批量分析多家公司或整个行业

### 代码模板

```python
"""
SOP-S3: 批量处理
适用于: 行业扫描、组合分析、批量报告
"""

from finance_toolkit import CompanyAnalyzer
from finance_toolkit.data import search_stocks, AKShareProvider
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """标准化分析结果"""
    code: str
    name: str
    success: bool
    error: Optional[str] = None
    summary: Optional[Dict] = None
    report: Optional[str] = None

def batch_analyze(
    codes: List[str],
    min_data_quality: int = 3,  # 最少需要几个指标
    stop_on_error: bool = False
) -> List[AnalysisResult]:
    """
    批量分析公司

    Args:
        codes: 股票代码列表
        min_data_quality: 最少有效指标数
        stop_on_error: 遇到错误是否停止

    Returns:
        分析结果列表
    """
    analyzer = CompanyAnalyzer()
    results = []

    for i, code in enumerate(codes):
        print(f"[{i+1}/{len(codes)}] 分析 {code}...")

        result = AnalysisResult(
            code=code,
            name="",
            success=False
        )

        try:
            # 获取摘要
            summary = analyzer.get_financial_summary(code)

            # 质量检查
            metrics = summary.get('最新财务指标', {})
            valid_count = sum(1 for v in metrics.values()
                            if v and v != "N/A" and v != "N/A%")

            if valid_count < min_data_quality:
                result.error = f"数据质量不足 (有效指标: {valid_count}/{min_data_quality})"
                results.append(result)
                continue

            result.name = summary['公司信息']['名称']
            result.summary = summary
            result.success = True

            # 生成报告
            result.report = analyzer.generate_report(code)

        except Exception as e:
            result.error = str(e)
            if stop_on_error:
                break

        results.append(result)

        # 避免请求过快
        import time
        time.sleep(0.1)

    return results


def aggregate_results(results: List[AnalysisResult]) -> Dict:
    """
    聚合批量分析结果
    """
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    # 统计摘要
    if not successful:
        return {"total": len(results), "success": 0, "failed": len(results)}

    # 提取关键指标
    roes = []
    gross_margins = []
    market_caps = []

    for r in successful:
        m = r.summary['最新财务指标']
        roe_str = m.get('ROE', '0')
        # 解析 "34.63 (优秀)" 格式
        try:
            roe = float(str(roe_str).split()[0].replace('%', ''))
            roes.append(roe)
        except:
            pass

        # ... 类似处理其他指标

    return {
        "total": len(results),
        "success": len(successful),
        "failed": len(failed),
        "avg_roe": sum(roes) / len(roes) if roes else 0,
        "top_roe": max(roes) if roes else 0,
        "companies": [
            {"code": r.code, "name": r.name, "roe": r.summary['最新财务指标'].get('ROE')}
            for r in sorted(successful, key=lambda x: x.summary['最新财务指标'].get('ROE', 0), reverse=True)
        ]
    }


# ========== 使用示例 ==========

# 方式1: 直接指定代码
codes = ["600519", "000858", "000568", "600809", "002304"]
results = batch_analyze(codes)

# 方式2: 通过行业获取代码
provider = AKShareProvider()
industry_stocks = provider.get_industry_stocks("白酒")
codes = industry_stocks['代码'].tolist()[:10]  # 取前10只
results = batch_analyze(codes)

# 聚合结果
summary = aggregate_results(results)
print(f"分析完成: {summary['success']}/{summary['total']} 成功")
print(f"平均 ROE: {summary['avg_roe']:.2f}%")
print(f"最高 ROE: {summary['top_roe']:.2f}%")
```

---

## 质量门禁

### GATE-1: 数据获取

```python
def validate_profile(profile: CompanyProfile) -> bool:
    """验证公司档案"""
    assert profile is not None, "档案为空"
    assert profile.stock is not None, "股票信息缺失"
    assert profile.stock.code is not None, "股票代码缺失"
    assert profile.stock.name is not None, "股票名称缺失"
    return True
```

### GATE-2: 财务指标

```python
def validate_metrics(metrics: FinancialMetrics) -> bool:
    """验证财务指标"""

    # ROE 应该在合理范围
    if metrics.profitability.roe is not None:
        assert -50 <= metrics.profitability.roe <= 100, \
            f"ROE 异常: {metrics.profitability.roe}"

    # 毛利率应该在 0-100%
    if metrics.profitability.gross_margin is not None:
        assert 0 <= metrics.profitability.gross_margin <= 100, \
            f"毛利率异常: {metrics.profitability.gross_margin}"

    # 资产负债率应该在 0-100%
    if metrics.solvency.debt_to_asset is not None:
        assert 0 <= metrics.solvency.debt_to_asset <= 100, \
            f"资产负债率异常: {metrics.solvency.debt_to_asset}"

    return True
```

### GATE-3: 分析报告

```python
def validate_report(report: str, min_length: int = 200) -> bool:
    """验证报告"""

    assert isinstance(report, str), "报告应为字符串"
    assert len(report) >= min_length, \
        f"报告过短: {len(report)} < {min_length}"

    # 检查关键内容
    required_sections = ["ROE", "毛利率"]
    for section in required_sections:
        assert section in report, f"报告缺少: {section}"

    return True
```

---

## 快速参考

### 标准导入

```python
# 完整导入
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

### 常见任务

| 任务 | 方法 |
|-----|------|
| 搜索公司 | `search_stocks("关键词")` |
| 获取档案 | `fetch_company("600519")` |
| 财务摘要 | `analyzer.get_financial_summary("600519")` |
| 生成报告 | `analyzer.generate_report("600519")` |
| DCF 估值 | `DCFValuation.calculate(...)` |
| 导出 PDF | `markdown_to_pdf(md_content, path)` |

---

**继续阅读**: [探索指南 - EXPLORATION.md](./EXPLORATION.md)

---

<p align="center">
  <sub>遵循 SOP，稳步前行 | 敢于探索，创新无限 🤖</sub>
</p>
