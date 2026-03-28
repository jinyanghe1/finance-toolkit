# Finance Toolkit - Agent 探索指南

> **创新空间** | 扩展工具链 | for AI Agents

本文档为 AI Agents 提供在稳定 SOP 基础上进行创新探索的指南。

---

## 目录

1. [探索原则](#探索原则)
2. [扩展点地图](#扩展点地图)
3. [扩展指南](#扩展指南)
4. [验证与测试](#验证与测试)
5. [案例参考](#案例参考)

---

## 探索原则

```
┌─────────────────────────────────────────────────────────────┐
│                      探索行为准则                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎯 目标明确: 探索应有目的，不是漫无边际                    │
│                                                              │
│  📐 边界清晰: 知道什么是稳定区，什么是实验区                │
│                                                              │
│  🧪 测试验证: 扩展必须经过验证，不能破坏现有功能            │
│                                                              │
│  📝 文档记录: 探索过程和结果应记录在 .agentstalk/          │
│                                                              │
│  🔄 可回滚: 探索失败应能恢复到稳定状态                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 稳定区 vs 实验区

| 区域 | 说明 | 行为 |
|-----|------|------|
| **稳定区** | SOP 定义的流程、核心 API | 只使用，不修改 |
| **接口区** | 定义良好的扩展点 | 按规范扩展 |
| **实验区** | 创新尝试 | 大胆探索，小心验证 |

---

## 扩展点地图

```
┌─────────────────────────────────────────────────────────────┐
│                    Finance Toolkit 扩展点                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   数据获取   │    │    分析模块  │    │    报告模块  │     │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤     │
│  │ akshare.py  │    │metrics.py   │    │generator.py │     │
│  │  ↑ 可扩展   │    │  ↑ 可扩展   │    │  ↑ 可扩展   │     │
│  │  新数据源   │    │  新分析方法 │    │  新报告格式  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   估值模型   │    │   行业分类   │    │   可视化模块  │     │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤     │
│  │valuation.py │    │industry/    │    │  (待扩展)    │     │
│  │  ↑ 可扩展   │    │  ↑ 可扩展   │    │  ↑ 实验区   │     │
│  │  新估值法   │    │  新行业定义  │    │  图表生成   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 扩展指南

### 扩展-1: 添加新的数据源

**适用场景**: 接入 Tushare、Wind 等其他数据源

```python
# src/finance_toolkit/data/tushare_provider.py

from typing import Optional, Dict, List
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)

class TushareProvider(LogMixin):
    """
    Tushare 数据提供者

    使用方式:
        from finance_toolkit.data import get_data_provider
        provider = get_data_provider()  # 可切换数据源
    """

    def __init__(self, token: str = None):
        """
        初始化

        Args:
            token: Tushare API Token
        """
        self.token = token or os.environ.get("TUSHARE_TOKEN")
        if not self.token:
            raise ValueError("需要设置 TUSHARE_TOKEN 环境变量")

    def get_stock_info(self, code: str) -> Optional[Dict]:
        """获取股票信息"""
        # TODO: 实现 Tushare API 调用
        pass

    def get_market_data(self, code: str) -> Optional[Dict]:
        """获取市场数据"""
        # TODO: 实现
        pass
```

**扩展检查清单**:
- [ ] 遵循 `DataProvider` 接口
- [ ] 处理可选依赖 (tushare)
- [ ] 添加单元测试
- [ ] 更新 `data/__init__.py`

---

### 扩展-2: 添加新的分析方法

**适用场景**: 实现特殊财务指标或自定义分析逻辑

```python
# src/finance_toolkit/analyzer/quality.py

from typing import Dict, Optional
from ..logger import LogMixin, get_logger
from ..models import FinancialMetrics

logger = get_logger(__name__)

class QualityAnalyzer(LogMixin):
    """
    财务质量分析器

    分析维度:
    - 利润质量
    - 现金流质量
    - 资产质量
    """

    def analyze(self, code: str) -> Dict[str, float]:
        """
        执行质量分析

        Returns:
            {
                "profit_quality": 0-100,
                "cashflow_quality": 0-100,
                "asset_quality": 0-100,
                "overall_quality": 0-100,
            }
        """
        # 1. 获取财务数据
        # ...

        # 2. 计算质量指标
        profit_quality = self._calc_profit_quality()
        cashflow_quality = self._calc_cashflow_quality()

        # 3. 综合评分
        overall = (profit_quality + cashflow_quality) / 2

        return {
            "profit_quality": profit_quality,
            "cashflow_quality": cashflow_quality,
            "overall_quality": overall,
        }

    def _calc_profit_quality(self) -> float:
        """计算利润质量"""
        # 利润质量 = 经营现金流 / 净利润
        # 越接近 1 越好
        pass
```

**扩展检查清单**:
- [ ] 继承 `LogMixin`
- [ ] 返回类型注解
- [ ] 添加日志
- [ ] 在 `analyzer/__init__.py` 导出

---

### 扩展-3: 添加新的报告格式

**适用场景**: HTML 报告、JSON 报告、Email 报告等

```python
# src/finance_toolkit/report/html_generator.py

from typing import Optional
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)

class HTMLReportGenerator(LogMixin):
    """
    HTML 报告生成器

    特性:
    - 响应式布局
    - 可交互图表
    - 导出为单文件 HTML
    """

    def generate(self, markdown_content: str, output_path: str) -> bool:
        """Markdown 转 HTML"""
        # 1. Markdown 解析
        # 2. HTML 模板渲染
        # 3. 嵌入图表 (可选)
        pass

    def generate_dashboard(self, data: Dict) -> str:
        """生成可交互仪表板 HTML"""
        # 使用 Chart.js 等库
        pass
```

---

### 扩展-4: 添加新的估值模型

**适用场景**: DDM (股利折现模型)、PEG 估值、EV/EBITDA 等

```python
# src/finance_toolkit/analyzer/advanced_valuation.py

from typing import Optional
from dataclasses import dataclass
from ..logger import LogMixin

@dataclass
class DDMAssumptions:
    """DDM 估值假设"""
    dividend_per_share: float      # 当前每股股利
    dividend_growth_rate: float   # 股利增长率
    discount_rate: float          # 折现率
    forecast_years: int = 5       # 预测年数

class DDMValuation(LogMixin):
    """股利折现模型 (Dividend Discount Model)"""

    def calculate(
        self,
        current_price: float,
        assumptions: DDMAssumptions
    ) -> Dict:
        """
        计算 DDM 估值

        Returns:
            {
                "intrinsic_value": 理论价值,
                "upside": 上涨空间 (%),
                "verdict": "低估/合理/高估"
            }
        """
        # DDM 公式: V = D1 / (r - g)
        # 其中 D1 = D0 * (1 + g)
        pass
```

---

## 验证与测试

### 必须通过的测试

```bash
# 1. 语法检查
python -m py_compile your_new_module.py

# 2. 导入测试
python -c "from finance_toolkit import YourNewClass"

# 3. 运行现有测试 (不能被破坏)
pytest tests/ -v

# 4. 你的新测试
pytest tests/test_your_module.py -v
```

### 回归测试

```python
# tests/test_regression.py

def test_no_regression_standard_workflow():
    """确保标准工作流没有被破坏"""

    # SOP-S1
    from finance_toolkit import CompanyAnalyzer
    analyzer = CompanyAnalyzer()

    # 确保基本方法存在
    assert hasattr(analyzer, 'get_financial_summary')
    assert hasattr(analyzer, 'generate_report')

    # 确保返回类型正确
    summary = analyzer.get_financial_summary("600519")
    assert isinstance(summary, dict)
```

### 性能基准

```python
# benchmarks/test_performance.py

def test_analyze_performance():
    """确保分析性能在可接受范围"""

    import time
    analyzer = CompanyAnalyzer()

    start = time.time()
    analyzer.generate_report("600519")
    elapsed = time.time() - start

    assert elapsed < 5.0, f"报告生成太慢: {elapsed}s"
```

---

## 案例参考

### 案例 1: 添加情绪分析扩展

**探索目标**: 通过新闻情感分析补充财务数据

**实现思路**:
1. 创建 `analyzer/sentiment.py`
2. 集成情感分析 API
3. 在报告中添加"市场情绪"维度

**风险评估**:
- 数据依赖: 外部 API
- 影响范围: 低 (仅新增模块)
- 回滚方案: 删除文件即可

**实施步骤**:
```bash
# 1. 创建模块
touch src/finance_toolkit/analyzer/sentiment.py

# 2. 实现
# ... (编写代码)

# 3. 测试
pytest tests/test_sentiment.py

# 4. 文档
# 更新 AGENTS.md
```

---

### 案例 2: 国际化扩展

**探索目标**: 支持英文财报数据

**实现思路**:
1. 添加 i18n 支持到数据模型
2. 支持 Bloomberg/FactSet 数据源
3. 中英文双语报告

**风险评估**:
- 数据依赖: 外部英文数据源
- 影响范围: 中 (涉及数据模型修改)
- 回滚方案: 保留中文默认

---

### 案例 3: 实时监控扩展

**探索目标**: 股价异动提醒

**实现思路**:
1. 创建 `monitor/alerter.py`
2. 定时任务检查价格变动
3. 触发条件后发送通知

**风险评估**:
- 数据依赖: 实时行情 API
- 影响范围: 低 (后台任务)
- 回滚方案: 禁用定时任务

---

## 探索记录

在 `.agentstalk/explorations/` 目录下记录你的探索:

```
.agentstalk/explorations/
├── 20260328_sentiment_analysis.md    # 情绪分析探索
├── 20260329_internationalization.md  # 国际化探索
└── README.md                         # 探索索引
```

### 探索记录模板

```markdown
# 探索: [标题]

**日期**: YYYY-MM-DD
**Agent**: 你的标识
**状态**: 🟡 进行中 / ✅ 完成 / ❌ 放弃

## 背景
为什么进行这个探索

## 目标
预期的产出

## 实施过程
1. 步骤1
2. 步骤2

## 结果
- 成功: 产出描述
- 失败: 原因分析

## 经验教训
下次如何改进
```

---

## 相关文档

- [SOP.md](./SOP.md) - 标准操作流程
- [AGENTS.md](./AGENTS.md) - Agent 开发者指南
- [.agentstalk/](../.agentstalk/Features) - 功能基线

---

<p align="center">
  <sub>创新是灵魂，探索无止境 🚀</sub>
</p>
