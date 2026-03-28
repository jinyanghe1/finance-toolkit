# Finance Toolkit 全栈专业版改进计划

**创建时间**: 2026-03-28 18:30  
**计划类型**: 全面重构与增强  
**预计工期**: 3-4 天  
**负责人**: Kimi  
**状态**: 🟡 进行中

> 集成更新: 2026-03-28 10:41
>
> - 已确认可编辑安装 `pip install -e .` 正常。
> - 已完成包入口修复：`ftk --help` 与 `python -m finance_toolkit --help` 正常。
> - 已发现并发开发文件，当前整合时避免重复开发这些区域：`src/finance_toolkit/analyzer/{company,metrics,trend,dupont,valuation}.py`、`src/finance_toolkit/industry/{classification,chain}.py`、`src/finance_toolkit/report/generator.py`、`tests/{conftest.py,test_models.py}`。
> - 当前优先级：在不重复实现上述模块的前提下，做接口打通、编译修复、验证补齐和基线同步。

---

## 执行阶段

### Phase 1: 基础工程化 ⏳
**时间**: Day 1 上午 (4h)  
**状态**: 部分完成

- [ ] 1.1 完善包结构，添加所有 `__init__.py`
- [x] 1.2 创建 pyproject.toml 项目配置
- [x] 1.3 添加 requirements.txt 和 requirements-dev.txt
- [x] 1.4 实现配置管理模块 (支持 YAML/JSON 配置)
- [ ] 1.5 将代码从 scripts/finance/ 迁移到 src/finance_toolkit/

### Phase 2: 代码质量提升 ⏳
**时间**: Day 1 下午 (4h)  
**状态**: 部分完成

- [ ] 2.1 统一 Industry 定义，消除 models.py 和 industry.py 的重复
- [x] 2.2 添加日志系统 (logging)
- [x] 2.3 添加异常处理机制 (自定义异常类)
- [x] 2.4 建立 pytest 测试框架
- [ ] 2.5 为核心模块添加单元测试 (覆盖率 >80%)
- [ ] 2.6 添加 mypy 类型检查配置

### Phase 3: 核心功能增强 ⏳
**时间**: Day 2 (6h)  
**状态**: 待开始

- [ ] 3.1 实现 CSV/Excel 数据导入器 (pandas)
- [ ] 3.2 建立行业基准数据库 (JSON 格式)
- [ ] 3.3 实现杜邦分析模型 (ROE 分解)
- [ ] 3.4 添加趋势分析 (同比/环比计算)
- [ ] 3.5 添加财务健康评分系统

### Phase 4: 估值模型 ⏳
**时间**: Day 3 上午 (4h)  
**状态**: 待开始

- [ ] 4.1 实现 DCF 现金流折现模型
- [ ] 4.2 实现相对估值 (PE/PB/PS 估值)
- [ ] 4.3 添加估值结果解释和建议
- [ ] 4.4 实现估值敏感性分析

### Phase 5: 用户体验 ⏳
**时间**: Day 3 下午 - Day 4 上午 (4h)  
**状态**: 已启动

- [x] 5.1 添加 CLI 命令行工具 (click)
- [ ] 5.2 实现报告导出 (Markdown/HTML)
- [ ] 5.3 添加 matplotlib 可视化图表
- [ ] 5.4 编写 Jupyter Notebook 示例
- [ ] 5.5 添加数据缓存机制 (LRU)

### Phase 6: 文档完善 ⏳
**时间**: Day 4 下午 (2h)  
**状态**: 待开始

- [ ] 6.1 完善 API 文档 (docstring)
- [ ] 6.2 编写用户指南
- [ ] 6.3 更新 README.md
- [ ] 6.4 添加 CHANGELOG.md

---

## 项目结构目标

```
finance-toolkit/
├── pyproject.toml              # 项目配置
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖
├── README.md                   # 说明文档
├── CHANGELOG.md               # 变更日志
├── config.yaml                # 默认配置
├── .gitignore                 # Git 忽略
├── .agentstalk/               # 协作目录
│   ├── Features.md            # 功能基线
│   ├── plan_*.md              # 开发计划
│   └── progress_*.md          # 进度记录
├── src/
│   └── finance_toolkit/       # 主包
│       ├── __init__.py
│       ├── __version__.py     # 版本信息
│       ├── config.py          # 配置管理
│       ├── logger.py          # 日志系统
│       ├── exceptions.py      # 自定义异常
│       ├── models.py          # 数据模型
│       ├── analyzer/          # 分析模块
│       │   ├── __init__.py
│       │   ├── company.py     # 公司分析
│       │   ├── metrics.py     # 指标计算
│       │   ├── dupont.py      # 杜邦分析
│       │   ├── trend.py       # 趋势分析
│       │   └── valuation.py   # 估值模型
│       ├── data/              # 数据模块
│       │   ├── __init__.py
│       │   ├── db.py          # 数据库
│       │   ├── importer.py    # 数据导入
│       │   └── benchmarks/    # 行业基准
│       │       └── industries.json
│       ├── industry/          # 行业模块
│       │   ├── __init__.py
│       │   ├── classification.py
│       │   └── chain.py
│       ├── report/            # 报告模块
│       │   ├── __init__.py
│       │   ├── generator.py
│       │   └── charts.py      # 可视化
│       └── cli.py             # 命令行工具
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # pytest 配置
│   ├── test_models.py
│   ├── test_analyzer/
│   │   ├── test_company.py
│   │   ├── test_metrics.py
│   │   └── test_valuation.py
│   └── test_data/
│       └── test_importer.py
└── examples/                  # 示例代码
    ├── basic_usage.ipynb
    ├── valuation_demo.ipynb
    └── cli_demo.py
```

---

## 依赖规划

### 核心依赖 (requirements.txt)
```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
click>=8.0.0
pyyaml>=6.0
openpyxl>=3.1.0  # Excel 支持
```

### 开发依赖 (requirements-dev.txt)
```
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.5.0
black>=23.0.0
ruff>=0.1.0
jupyter>=1.0.0
```

---

## 关键设计决策

1. **包名**: `finance_toolkit` (下划线命名，PEP8 规范)
2. **代码位置**: `src/` 目录结构 (推荐做法)
3. **配置格式**: YAML (可读性好)
4. **日志**: Python 标准库 logging
5. **CLI**: Click (简单易用)
6. **测试**: pytest (行业标准)
7. **类型检查**: mypy

---

## 风险与应对

| 风险 | 可能性 | 应对措施 |
|------|--------|----------|
| 迁移引入 bug | 中 | 保持原有代码在 scripts/ 直到新代码测试通过 |
| 依赖冲突 | 低 | 使用虚拟环境，明确版本要求 |
| 工期延误 | 中 | 按 Phase 交付，可阶段性验收 |

---

## 验收标准

- [x] `pip install -e .` 可正常安装
- [ ] `pytest` 全部通过，覆盖率 >80%
- [ ] `mypy src/` 无类型错误
- [x] `python -m finance_toolkit --help` 正常显示
- [ ] 原有 demo.py 功能在新结构中可用

---

**最后更新**: 2026-03-28 10:41  
**更新说明**: 完成 CLI/配置修复，整合并发 `src` 代码，打通行业定义与 analyzer 导出，pytest 当前 16 项通过
