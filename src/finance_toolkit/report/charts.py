"""
Finance Toolkit - 图表生成器
Chart Generator for Financial Data Visualization

需要安装: pip install matplotlib
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from ..models import FinancialMetrics, CompanyProfile
from ..logger import LogMixin, get_logger

logger = get_logger(__name__)


class ChartGenerator(LogMixin):
    """财务图表生成器"""
    
    # 默认配色方案
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ffbb78',
        'info': '#98df8a',
        'purple': '#9467bd',
        'brown': '#8c564b',
    }
    
    # 图表样式
    STYLE = {
        'figure.figsize': (12, 6),
        'figure.dpi': 100,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
    }
    
    def __init__(self, style: Optional[str] = 'seaborn-v0_8-whitegrid'):
        """
        初始化图表生成器
        
        Args:
            style: matplotlib 样式名称
        """
        self.style = style
        self._setup_style()
    
    def _setup_style(self):
        """设置图表样式"""
        if self.style:
            plt.style.use(self.style)
        
        # 尝试设置中文字体
        self._setup_chinese_font()
    
    def _setup_chinese_font(self):
        """设置中文字体支持"""
        # 常见中文字体
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei',
            'Noto Sans CJK SC', 'Source Han Sans CN',
            'Arial Unicode MS', 'DejaVu Sans'
        ]
        
        # 查找可用的中文字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        font = None
        
        for cf in chinese_fonts:
            if cf in available_fonts:
                font = cf
                break
        
        if font:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    @staticmethod
    def _save_or_show(fig: Figure, filepath: Optional[Path] = None, show: bool = True):
        """
        保存或显示图表
        
        Args:
            fig: 图表对象
            filepath: 保存路径，None 则不保存
            show: 是否显示
        """
        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")
        
        if show:
            plt.show()
    
    def plot_trend(
        self,
        metrics_list: List[FinancialMetrics],
        metrics: List[str] = None,
        title: Optional[str] = None,
        filepath: Optional[Path] = None,
        show: bool = True,
    ) -> Figure:
        """
        绘制财务指标趋势图
        
        Args:
            metrics_list: 财务指标列表（时间倒序）
            metrics: 要绘制的指标列表，None 则绘制所有关键指标
            title: 图表标题
            filepath: 保存路径
            show: 是否显示
        
        Returns:
            matplotlib Figure 对象
        """
        if not metrics_list:
            raise ValueError("metrics_list 不能为空")
        
        # 默认指标
        if metrics is None:
            metrics = ['roe', 'gross_margin', 'net_margin']
        
        # 准备数据
        periods = [m.report_date for m in reversed(metrics_list)]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 指标名称映射
        metric_names = {
            'roe': 'ROE (%)',
            'roa': 'ROA (%)',
            'gross_margin': '毛利率 (%)',
            'net_margin': '净利率 (%)',
            'debt_to_asset': '资产负债率 (%)',
            'current_ratio': '流动比率',
            'revenue_growth_yoy': '营收增长率 (%)',
            'profit_growth_yoy': '净利润增长率 (%)',
        }
        
        colors = list(self.COLORS.values())
        
        for i, metric in enumerate(metrics):
            values = []
            for m in reversed(metrics_list):
                if metric == 'roe':
                    val = m.profitability.roe
                elif metric == 'roa':
                    val = m.profitability.roa
                elif metric == 'gross_margin':
                    val = m.profitability.gross_margin
                elif metric == 'net_margin':
                    val = m.profitability.net_margin
                elif metric == 'debt_to_asset':
                    val = m.solvency.debt_to_asset
                elif metric == 'current_ratio':
                    val = m.solvency.current_ratio
                elif metric == 'revenue_growth_yoy':
                    val = m.growth.revenue_growth_yoy
                elif metric == 'profit_growth_yoy':
                    val = m.growth.profit_growth_yoy
                else:
                    val = None
                values.append(val)
            
            # 过滤 None 值
            valid_pairs = [(p, v) for p, v in zip(periods, values) if v is not None]
            if valid_pairs:
                valid_periods, valid_values = zip(*valid_pairs)
                ax.plot(valid_periods, valid_values, marker='o', linewidth=2,
                       label=metric_names.get(metric, metric), color=colors[i % len(colors)])
        
        # 设置图表
        ax.set_xlabel('报告期', fontsize=12)
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title(title or '财务指标趋势', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 旋转 x 轴标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self._save_or_show(fig, filepath, show)
        return fig
    
    def plot_radar(
        self,
        metrics: FinancialMetrics,
        categories: Optional[List[str]] = None,
        title: Optional[str] = None,
        filepath: Optional[Path] = None,
        show: bool = True,
    ) -> Figure:
        """
        绘制财务能力雷达图
        
        Args:
            metrics: 财务指标
            categories: 分析维度，None 则使用默认维度
            title: 图表标题
            filepath: 保存路径
            show: 是否显示
        
        Returns:
            matplotlib Figure 对象
        """
        if categories is None:
            categories = ['盈利能力', '偿债能力', '运营效率', '成长能力', '现金流']
        
        # 提取各维度得分（归一化到0-100）
        values = []
        
        # 盈利能力 (ROE权重40%, 毛利率30%, 净利率30%)
        if '盈利能力' in categories:
            roe_score = min((metrics.profitability.roe or 0) / 25 * 100, 100)
            gm_score = min((metrics.profitability.gross_margin or 0) / 50 * 100, 100)
            nm_score = min((metrics.profitability.net_margin or 0) / 25 * 100, 100)
            values.append(roe_score * 0.4 + gm_score * 0.3 + nm_score * 0.3)
        
        # 偿债能力 (流动比率权重50%, 资产负债率50%)
        if '偿债能力' in categories:
            cr = metrics.solvency.current_ratio or 0
            cr_score = min(cr / 2.5 * 100, 100) if cr > 0 else 0
            dta = metrics.solvency.debt_to_asset or 0
            dta_score = max(0, (100 - dta)) if dta > 0 else 50
            values.append(cr_score * 0.5 + dta_score * 0.5)
        
        # 运营效率 (总资产周转率)
        if '运营效率' in categories:
            at = metrics.efficiency.asset_turnover or 0
            values.append(min(at / 1.5 * 100, 100))
        
        # 成长能力 (营收增长率)
        if '成长能力' in categories:
            rg = metrics.growth.revenue_growth_yoy or 0
            values.append(min(max(rg + 20, 0) / 40 * 100, 100))
        
        # 现金流 (经营现金流/净利润)
        if '现金流' in categories:
            ocf_ratio = metrics.cashflow.ocf_to_net_profit or 0
            values.append(min(max(ocf_ratio, 0) / 1.5 * 100, 100))
        
        # 创建雷达图
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # 闭合图形
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, color=self.COLORS['primary'])
        ax.fill(angles, values, alpha=0.25, color=self.COLORS['primary'])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True)
        
        ax.set_title(title or '财务能力雷达图', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._save_or_show(fig, filepath, show)
        return fig
    
    def plot_comparison(
        self,
        companies: List[Dict[str, Any]],
        metric: str = 'ROE',
        title: Optional[str] = None,
        filepath: Optional[Path] = None,
        show: bool = True,
    ) -> Figure:
        """
        绘制同业对比柱状图
        
        Args:
            companies: 公司列表 [{"name": "公司A", "ROE": 15, ...}, ...]
            metric: 对比的指标
            title: 图表标题
            filepath: 保存路径
            show: 是否显示
        
        Returns:
            matplotlib Figure 对象
        """
        if not companies:
            raise ValueError("companies 不能为空")
        
        names = [c['name'] for c in companies]
        values = [c.get(metric, 0) or 0 for c in companies]
        
        # 排序（降序）
        sorted_pairs = sorted(zip(names, values), key=lambda x: x[1], reverse=True)
        names, values = zip(*sorted_pairs)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 根据数值选择颜色
        colors = []
        max_val = max(values) if values else 1
        for v in values:
            if v >= max_val * 0.8:
                colors.append(self.COLORS['success'])
            elif v >= max_val * 0.5:
                colors.append(self.COLORS['primary'])
            else:
                colors.append(self.COLORS['warning'])
        
        bars = ax.barh(names, values, color=colors, edgecolor='white', linewidth=1.5)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f' {value:.2f}',
                   ha='left', va='center', fontsize=10)
        
        ax.set_xlabel(metric, fontsize=12)
        ax.set_title(title or f'{metric} 同业对比', fontsize=14, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        
        plt.tight_layout()
        self._save_or_show(fig, filepath, show)
        return fig
    
    def plot_dupont(
        self,
        roe: float,
        net_margin: float,
        asset_turnover: float,
        equity_multiplier: float,
        title: Optional[str] = None,
        filepath: Optional[Path] = None,
        show: bool = True,
    ) -> Figure:
        """
        绘制杜邦分析分解图
        
        Args:
            roe: ROE 值
            net_margin: 净利率
            asset_turnover: 总资产周转率
            equity_multiplier: 权益乘数
            title: 图表标题
            filepath: 保存路径
            show: 是否显示
        
        Returns:
            matplotlib Figure 对象
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(title or '杜邦分析分解', fontsize=16, fontweight='bold')
        
        components = [
            ('ROE', roe, axes[0, 0]),
            ('净利率', net_margin, axes[0, 1]),
            ('总资产周转率', asset_turnover, axes[1, 0]),
            ('权益乘数', equity_multiplier, axes[1, 1]),
        ]
        
        for name, value, ax in components:
            # 创建仪表盘样式
            theta = np.linspace(0, np.pi, 100)
            r = np.ones_like(theta)
            
            ax.fill_between(theta, 0, r, alpha=0.1, color='gray')
            
            # 根据值设置指针位置
            if name == 'ROE':
                angle = min(value / 30, 1) * np.pi
                color = self.COLORS['success'] if value >= 15 else self.COLORS['warning']
            elif name == '净利率':
                angle = min(value / 40, 1) * np.pi
                color = self.COLORS['success'] if value >= 15 else self.COLORS['warning']
            elif name == '总资产周转率':
                angle = min(value / 2, 1) * np.pi
                color = self.COLORS['success'] if value >= 1 else self.COLORS['warning']
            else:  # 权益乘数
                angle = min(value / 5, 1) * np.pi
                color = self.COLORS['warning'] if value >= 4 else self.COLORS['success']
            
            ax.plot([0, angle], [0, 0.8], linewidth=4, color=color)
            ax.scatter(angle, 0.8, s=100, color=color)
            
            ax.set_ylim(0, 1.2)
            ax.set_xlim(0, np.pi)
            ax.set_xticks([0, np.pi/2, np.pi])
            ax.set_xticklabels(['低', '中', '高'])
            ax.set_yticks([])
            ax.set_title(f'{name}\n{value:.2f}', fontsize=12, fontweight='bold')
        
        # 添加公式
        fig.text(0.5, 0.02, 'ROE = 净利率 × 总资产周转率 × 权益乘数',
                ha='center', fontsize=12, style='italic')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        self._save_or_show(fig, filepath, show)
        return fig


def create_chart_generator(style: Optional[str] = None) -> ChartGenerator:
    """创建图表生成器实例"""
    return ChartGenerator(style)
