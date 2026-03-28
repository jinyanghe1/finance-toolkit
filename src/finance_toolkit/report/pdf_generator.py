"""
Finance Toolkit - PDF 报告生成器
PDF Report Generator

将 Markdown 投研报告转换为 PDF 格式
"""

from typing import Optional, List
from pathlib import Path
from datetime import datetime
import tempfile

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

from ..logger import LogMixin, get_logger

logger = get_logger(__name__)


class PDFReportGenerator(LogMixin):
    """PDF 报告生成器"""

    def __init__(self):
        if not FPDF_AVAILABLE:
            raise ImportError(
                "PDF 功能需要安装 fpdf2: pip install finance-toolkit[pdf]"
            )

    def generate_from_markdown(self, markdown_content: str, output_path: str) -> bool:
        """
        从 Markdown 内容生成 PDF

        Args:
            markdown_content: Markdown 格式的报告内容
            output_path: 输出 PDF 文件路径

        Returns:
            是否生成成功
        """
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_font("NotoSans", "", "/System/Library/Fonts/Supplemental/NotoSans-Regular.ttf", uni=True)
            pdf.add_font("NotoSans", "B", "/System/Library/Fonts/Supplemental/NotoSans-Bold.ttf", uni=True)

            # 解析 Markdown
            lines = markdown_content.split('\n')
            in_table = False
            table_data = []

            for line in lines:
                line = line.strip()

                # 标题处理
                if line.startswith('# '):
                    pdf.add_page()
                    pdf.set_font("NotoSans", "B", 18)
                    pdf.cell(0, 10, line[2:], ln=True)
                    pdf.ln(5)
                elif line.startswith('## '):
                    pdf.set_font("NotoSans", "B", 14)
                    pdf.cell(0, 8, line[3:], ln=True)
                    pdf.ln(3)
                elif line.startswith('### '):
                    pdf.set_font("NotoSans", "B", 12)
                    pdf.cell(0, 7, line[4:], ln=True)
                    pdf.ln(2)
                # 表格处理（简化）
                elif line.startswith('|'):
                    # 跳过分隔行
                    if '---' in line:
                        continue
                    # 解析表格行
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    table_data.append(cells)
                # 空行或段落结束
                elif not line and table_data:
                    # 输出表格
                    self._draw_table(pdf, table_data)
                    table_data = []
                elif line and not line.startswith('|'):
                    # 普通文本
                    if table_data:
                        self._draw_table(pdf, table_data)
                        table_data = []
                    pdf.set_font("NotoSans", "", 10)
                    # 处理粗体标记
                    self._draw_text_line(pdf, line)
                    pdf.ln(3)
            # 处理剩余表格
            if table_data:
                self._draw_table(pdf, table_data)

            pdf.output(output_path)
            self.logger.info(f"PDF 报告已生成: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"生成 PDF 失败: {e}")
            return False

    def _draw_text_line(self, pdf: "FPDF", text: str) -> None:
        """绘制一行文本，处理粗体"""
        parts = text.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                pdf.set_font("NotoSans", "B", 10)
            else:
                pdf.set_font("NotoSans", "", 10)
            pdf.cell(0, 5, part, ln=True)

    def _draw_table(self, pdf: "FPDF", data: List[List[str]]) -> None:
        """绘制简单表格"""
        if not data:
            return

        col_count = len(data[0]) if data else 0
        if col_count == 0:
            return

        col_width = (pdf.w - 20) / col_count

        # 表头
        pdf.set_font("NotoSans", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        for cell in data[0]:
            pdf.cell(col_width, 6, cell[:15], border=1, fill=True, align="C")
        pdf.ln()

        # 数据行
        pdf.set_font("NotoSans", "", 8)
        for row in data[1:]:
            for cell in row:
                pdf.cell(col_width, 5, cell[:15], border=1, align="C")
            pdf.ln()

        pdf.ln(3)

    def generate_from_file(self, markdown_path: str, output_path: str) -> bool:
        """
        从 Markdown 文件生成 PDF

        Args:
            markdown_path: Markdown 文件路径
            output_path: 输出 PDF 文件路径

        Returns:
            是否生成成功
        """
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.generate_from_markdown(content, output_path)
        except Exception as e:
            self.logger.error(f"读取 Markdown 文件失败: {e}")
            return False


def markdown_to_pdf(markdown_content: str, output_path: str) -> bool:
    """
    将 Markdown 转换为 PDF（便捷函数）

    Args:
        markdown_content: Markdown 内容
        output_path: 输出路径

    Returns:
        是否成功
    """
    generator = PDFReportGenerator()
    return generator.generate_from_markdown(markdown_content, output_path)


def markdown_file_to_pdf(markdown_path: str, output_path: str) -> bool:
    """
    将 Markdown 文件转换为 PDF（便捷函数）

    Args:
        markdown_path: Markdown 文件路径
        output_path: 输出路径

    Returns:
        是否成功
    """
    generator = PDFReportGenerator()
    return generator.generate_from_file(markdown_path, output_path)


if __name__ == "__main__":
    # 测试
    test_markdown = """# 贵州茅台 (600519) 分析报告

## 基本信息
- **股票代码**: 600519.SH
- **上市日期**: 2001-08-27
- **所属行业**: 食品饮料

## 财务指标

| 指标 | 2024 | 2023 | 同比 |
|------|------|------|------|
| 营收 (亿) | 1505 | 1476 | +2.0% |
| 净利润 (亿) | 747 | 747 | +0.0% |
| ROE | 34.6% | 34.5% | +0.1pp |

## 估值

| 指标 | 数值 | 行业平均 |
|------|------|----------|
| PE | 28.5 | 35.0 |
| PB | 8.2 | 6.5 |
"""

    output = tempfile.mktemp(suffix=".pdf")
    success = markdown_to_pdf(test_markdown, output)
    print(f"PDF 生成 {'成功' if success else '失败'}: {output}")
