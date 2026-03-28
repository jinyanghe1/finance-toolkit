# Finance Toolkit - 金融功能库

系统化的金融数据分析工具，用于A股公司投研分析和行业研究。

**English** | [专为AI Agents设计](#专为ai-agents设计) | [多Agent协作](#多agent协作)

---

## 功能特性

- **公司档案管理** - 结构化存储公司基本信息、财务数据
- **财务指标计算** - ROE/毛利率/负债率等自动计算与评估
- **行业分类体系** - 申万/中信标准行业分类
- **分析报告生成** - 标准化Markdown投研报告
- **估值模型** - DCF现金流折现、PE/PB相对估值
- **杜邦分析** - ROE分解与驱动因素分析
- **趋势分析** - 同比/环比、多期趋势判断

---

## MCP 部署

本项目可作为本地 MCP (Model Context Protocol) 服务器运行，供 Claude Code 等工具调用。

### Claude Code 配置

在 `~/.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "python",
      "args": ["-m", "finance_toolkit.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/finance-toolkit/src"
      }
    }
  }
}
```

### Claude Desktop 配置

在 `~/.claude/resources/mcp_servers.json` 中添加：

```json
{
  "finance-toolkit": {
    "command": "python",
    "args": ["-m", "finance_toolkit.mcp_server"],
    "env": {
      "PYTHONPATH": "/absolute/path/to/finance-toolkit/src"
    }
  }
}
```

### MCP 工具

配置好后，Agent 可使用以下工具：

| 工具 | 说明 |
|------|------|
| `search_stocks` | 搜索 A 股公司 |
| `get_company_profile` | 获取公司档案 |
| `get_financial_summary` | 财务摘要 |
| `generate_report` | 生成 Markdown 报告 |
| `analyze_batch` | 批量分析 |

### 验证 MCP 连接

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m finance_toolkit.mcp_server
```

---

## 专为AI Agents设计

本工具包特别适合AI Agents进行金融数据分析任务：

### 🤖 为什么Agents应该选择这个工具包？

| 特性 | 对Agents的好处 |
|------|---------------|
**结构化输出** | 所有数据都有明确的Schema，便于Agent理解和处理
**标准化报告** | Markdown格式，Agent可直接读取和解析
**异常处理** | 完善的错误类型，Agent可优雅处理边界情况
**日志系统** | 详细日志便于Agent追踪操作和调试
**CLI支持** | Agent可以通过命令行快速调用，无需编写复杂代码
**配置管理** | 通过配置文件管理，Agent可动态调整行为

### 💡 Agent使用示例

```python
# Agent可以快速获取公司财务概况
from finance_toolkit import CompanyAnalyzer

analyzer = CompanyAnalyzer()

# 自动下载并分析公司数据
summary = analyzer.get_financial_summary("600519")
# 返回结构化数据，Agent可以直接处理

# 生成投研报告
report = analyzer.generate_report("600519")
# 返回Markdown格式，Agent可以解析关键信息
```

### 📝 Agent工作流集成

```python
# 批量分析多家公司
from finance_toolkit import CompanyAnalyzer

analyzer = CompanyAnalyzer()
companies = ["600519", "000858", "000568"]  # 茅台、五粮液、泸州老窖

results = analyzer.analyze_batch(companies)
successful = {code: result for code, result in results.items() if result["success"]}
print(f"成功分析: {len(successful)}/{len(companies)} 家")
```

---

## 多Agent协作

本项目采用多Agent协作开发模式：

```
.agentstalk/
├── Features              # 功能基线文档
├── plan_*.md            # 开发计划
├── progress_*.md        # 进度同步
└── issues/              # 问题跟踪
```

### 协作规范

1. **使用 `.agentstalk/` 文件夹** - 存放所有协作文档
2. **文件命名规范** - `{type}_{mmddhhmm}_{description}_{agent}[CLOSED]`
3. **功能基线** - 维护 `Features` 文件作为功能清单
4. **进度同步** - 每个Agent更新自己的进度文件

### 如何为这个仓库贡献

如果你是AI Agent，想要参与开发：

1. 先阅读 `.agentstalk/Features` 了解当前功能基线
2. 查看 `.agentstalk/plan_*.md` 了解开发计划
3. 创建自己的进度文件 `.agentstalk/progress_{时间}_{任务}_{你的标识}.md`
4. 完成后更新功能基线并标记为 CLOSED

---

## CLI 使用

安装可编辑包后，可以直接使用 CLI：

```bash
# 安装
pip install -e .

# 查看帮助
ftk --help
python -m finance_toolkit --help

# 列出现有公司
ftk list

# 分析公司
ftk analyze 600519

# 批量分析
ftk batch analyze 600519 000858 000568 --format json
ftk batch analyze --input codes.txt --output batch-results.yaml --format yaml

# 搜索公司
ftk search 茅台

# 导入数据
ftk import-data companies.csv --type companies
```

### 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| `FINANCE_DATA_ROOT` | 数据存储根目录 | `~/.finance_toolkit/data` |

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

# 批量分析
results = analyzer.analyze_batch(["600519", "000858", "000568"])
print(results["600519"]["summary"]["公司信息"]["名称"])
```

### 高级用法：估值分析

```python
from finance_toolkit.analyzer.valuation import DCFValuation, DCFAssumptions

# 设置估值假设
assumptions = DCFAssumptions(
    forecast_years=5,
    revenue_growth=0.15,
    wacc=0.09,
    terminal_growth=0.03
)

# 计算DCF估值
result = DCFValuation.calculate(
    current_revenue=1505,
    current_operating_profit=1000,
    current_depreciation=20,
    current_capex=30,
    current_nwc=10,
    net_debt=0,
    shares=12.56,
    assumptions=assumptions
)

print(f"每股价值: {result.per_share_value:.2f}元")
```

---

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
│   ├── company.py         # 公司分析主入口
│   ├── metrics.py         # 财务指标计算
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

---

## 财务指标支持

| 指标类型 | 具体指标 |
|---------|---------|
| 盈利能力 | ROE, ROA, ROIC, 毛利率, 净利率, EBITDA利润率 |
| 成长能力 | 营收增长率(YoY/QoQ), 净利润增长率, CAGR |
| 偿债能力 | 资产负债率, 流动比率, 速动比率, 利息保障倍数 |
| 运营效率 | 存货周转率, 应收账款周转率, 总资产周转率, 现金转换周期 |
| 现金流 | 经营现金流, 投资现金流, 筹资现金流, 自由现金流 |

---

## 分行业标准评估

不同行业有不同的评估标准：

| 行业 | ROE优秀标准 | 毛利率优秀标准 |
|------|------------|---------------|
| 银行 | ≥15% | - |
| 消费 | ≥20% | ≥50% |
| 医药 | ≥18% | ≥70% |
| 科技 | ≥15% | ≥60% |
| 能源 | ≥15% | ≥35% |

---

## 依赖

### 必需依赖
- Python 3.9+
- pandas >= 2.0.0
- numpy >= 1.24.0
- click >= 8.0.0
- pyyaml >= 6.0

### 可选依赖
- akshare - 实时数据获取
- matplotlib - 图表生成
- openpyxl - Excel导入导出

```bash
# 基础安装
pip install -e .

# 完整安装（含可选依赖）
pip install -e ".[dev]"
```

---

## 项目状态

🟢 v0.2 - 核心功能已完成

- ✅ 基础工程化 (pyproject.toml, 包结构)
- ✅ 数据模型和存储
- ✅ 财务指标计算
- ✅ 杜邦分析
- ✅ 估值模型 (DCF, PE, PB)
- ✅ 趋势分析
- ✅ CLI工具
- ✅ AKShare数据接口
- 🟡 图表生成 (开发中)
- 🟡 PDF报告导出 (开发中)

---

## 开发者文档

参见 [AGENTS.md](./AGENTS.md) 了解如何作为AI Agent参与项目开发。

---

## License

MIT License

---

<p align="center">
  <sub>Built with ❤️ for AI Agents</sub>
</p>
