import os
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def ensure_chinese_font():
    """确保中文字体文件存在"""
    try:
        # 查找系统字体
        system_font_path = "C:\\Windows\\Fonts\\simhei.ttf"
        
        if os.path.exists(system_font_path):
            print(f"使用系统字体: {system_font_path}")
            # 注册字体
            pdfmetrics.registerFont(TTFont('SimHei', system_font_path))
            return system_font_path
            
        # 如果系统字体不存在，尝试创建自己的字体目录
        font_dir = os.path.join(os.getcwd(), 'static', 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        
        # 字体文件路径
        font_path = os.path.join(font_dir, 'simhei.ttf')
        
        # 如果本地字体库中没有，尝试从系统复制
        if not os.path.exists(font_path) and os.path.exists(system_font_path):
            import shutil
            print(f"从系统复制字体到本地: {system_font_path} -> {font_path}")
            shutil.copy2(system_font_path, font_path)
        
        # 注册字体
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            return font_path
            
        return None
    except Exception as e:
        print(f"确保中文字体文件失败: {str(e)}")
        return None

def test_pdf_generation():
    # 确保pdf目录存在
    pdf_dir = "pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 生成PDF路径
    pdf_path = os.path.join(pdf_dir, "test.pdf")
    
    try:
        # 确保中文字体可用
        font_path = ensure_chinese_font()
        if not font_path:
            raise Exception("无法加载中文字体文件")
            
        # 使用ReportLab生成PDF
        print(f"正在生成测试PDF: {pdf_path}")
        
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
        my_title_style = ParagraphStyle(
            name='MyTitle',
            fontName='SimHei',  # 使用中文字体
            fontSize=18,
            leading=22,
            textColor=colors.blue,
            spaceAfter=20
        )
        
        chinese_style = ParagraphStyle(
            name='ChineseStyle',
            fontName='SimHei',  # 使用中文字体
            fontSize=12,
            leading=14
        )
        
        # 准备文档内容
        elements = []
        elements.append(Paragraph('ReportLab中文测试', my_title_style))
        elements.append(Paragraph('这是使用ReportLab生成的测试PDF文档，包含中文内容。', chinese_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('如果您看到这个文件的中文，说明PDF生成功能正常工作！', chinese_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('测试中文字符：你好世界！八字命理分析系统', chinese_style))
        
        # 构建PDF
        doc.build(elements)
        
        print(f"PDF生成成功: {pdf_path}")
        return True
    except Exception as e:
        print(f"生成PDF时出错: {str(e)}")
        return False

if __name__ == "__main__":
    test_pdf_generation() 