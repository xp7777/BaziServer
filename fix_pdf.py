import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_pdf():
    """生成测试PDF文件"""
    result_id = 'RES1747843279684'  # 需要生成PDF的结果ID - 更新为新的ID
    
    # 确保PDF目录存在
    pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 输出路径
    pdf_path = os.path.join(pdf_dir, f'bazi_analysis_{result_id}.pdf')
    
    # 创建文档
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # 创建样式
    styles = getSampleStyleSheet()
    
    # 添加中文样式
    styles.add(ParagraphStyle(
        name='Chinese',
        fontName='Helvetica',
        fontSize=12,
        leading=14,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        fontName='Helvetica',
        fontSize=24,
        leading=28,
        alignment=1,  # 居中
        spaceAfter=20
    ))
    
    # 准备文档内容
    elements = []
    
    # 添加标题
    elements.append(Paragraph('八字命理分析报告', styles['ChineseTitle']))
    
    # 添加生成时间
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles['Chinese']
    ))
    
    # 添加八字
    elements.append(Paragraph('Bazi Chart:', styles['Chinese']))
    elements.append(Paragraph('年柱: 甲子 月柱: 丙寅 日柱: 戊午 时柱: 庚申', styles['Chinese']))
    
    # 添加分析
    elements.append(Paragraph('Health Analysis:', styles['Chinese']))
    elements.append(Paragraph('Your health looks good based on your Bazi chart.', styles['Chinese']))
    
    elements.append(Paragraph('Wealth Analysis:', styles['Chinese']))
    elements.append(Paragraph('Your wealth prospects are promising.', styles['Chinese']))
    
    elements.append(Paragraph('Career Analysis:', styles['Chinese']))
    elements.append(Paragraph('Your career will develop well in coming years.', styles['Chinese']))
    
    # 添加更多内容，确保PDF的大小更接近正常的分析报告
    elements.append(Paragraph('Relationship Analysis:', styles['Chinese']))
    elements.append(Paragraph('Your relationships will be harmonious and supportive.', styles['Chinese']))
    
    elements.append(Paragraph('Children Analysis:', styles['Chinese']))
    elements.append(Paragraph('You will have a good relationship with your children.', styles['Chinese']))
    
    elements.append(Paragraph('Overall Analysis:', styles['Chinese']))
    elements.append(Paragraph('Your overall fortune is positive. The coming years will bring opportunities for growth in all areas of your life.', styles['Chinese']))
    
    # 构建PDF
    doc.build(elements)
    
    print(f"PDF generated successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        generate_test_pdf()
        print("PDF generation complete!")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}") 