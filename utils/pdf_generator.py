import os
import logging
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import urllib.request
import shutil
import pdfkit
from jinja2 import Template

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入Markdown处理模块
try:
    from utils.markdown_handler import parse_markdown, parse_analysis_data
    markdown_support = True
    logger.info("Markdown解析支持已启用")
except ImportError:
    markdown_support = False
    logger.warning("未找到markdown_handler模块，Markdown解析将不可用")

# 添加一个自定义JSON编码器处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# 字体全局变量
FONT_REGISTERED = False
DEFAULT_FONT_NAME = 'SimHei'

# 创建PDF保存目录
PDF_DIR = os.path.join(os.getcwd(), 'static', 'pdfs')
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR, exist_ok=True)

# 尝试导入reportlab
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # 注册中文字体
    fonts_registered = False
    try:
        # 尝试注册系统字体
        if os.name == 'nt':  # Windows
            font_paths = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                os.path.join(os.getcwd(), 'fonts')
            ]
            
            # 创建fonts目录
            os.makedirs(os.path.join(os.getcwd(), 'fonts'), exist_ok=True)
            
            # 尝试注册宋体
            for font_path in font_paths:
                simsun_path = os.path.join(font_path, 'simsun.ttc')
                if os.path.exists(simsun_path):
                    try:
                        pdfmetrics.registerFont(TTFont('SimSun', simsun_path))
                        logger.info(f"成功注册宋体字体: {simsun_path}")
                        fonts_registered = True
                        break
                    except Exception as e:
                        logger.warning(f"注册宋体字体失败: {str(e)}")
        
        if not fonts_registered:
            logger.warning("未能注册中文字体，PDF中可能无法正确显示中文")
    except Exception as e:
        logger.warning(f"注册字体时出错: {str(e)}")
    
    reportlab_available = True
    logger.info("reportlab库已加载，可以用作PDF生成备选方案")
except ImportError:
    reportlab_available = False
    logger.warning("reportlab库不可用，无法使用备选PDF生成方案")

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>八字命理分析报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        .info {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 25px;
        }
        .pillar {
            display: inline-block;
            width: 22%;
            text-align: center;
            margin-right: 3%;
            vertical-align: top;
        }
        .pillar-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stem {
            background-color: #4a90e2;
            color: white;
            padding: 5px 0;
            margin-bottom: 5px;
        }
        .branch {
            background-color: #50c878;
            color: white;
            padding: 5px 0;
        }
        .five-elements {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }
        .element {
            text-align: center;
            width: 18%;
        }
        .element-name {
            font-weight: bold;
        }
        .element-value {
            font-size: 18px;
            color: #4a90e2;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #777;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        /* 增加Markdown样式支持 */
        .markdown-content h1, 
        .markdown-content h2, 
        .markdown-content h3, 
        .markdown-content h4, 
        .markdown-content h5, 
        .markdown-content h6 {
            margin-top: 1em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        .markdown-content ul, 
        .markdown-content ol {
            margin-left: 2em;
            margin-bottom: 1em;
        }
        .markdown-content ul {
            list-style-type: disc;
        }
        .markdown-content ol {
            list-style-type: decimal;
        }
        .markdown-content li {
            margin-bottom: 0.5em;
        }
        .markdown-content p {
            margin-bottom: 1em;
        }
        .markdown-content strong {
            font-weight: bold;
        }
        .markdown-content em {
            font-style: italic;
        }
        .markdown-content blockquote {
            border-left: 4px solid #ddd;
            padding-left: 1em;
            margin-left: 0;
            color: #666;
        }
        .markdown-content hr {
            height: 1px;
            background-color: #ddd;
            border: none;
            margin: 1.5em 0;
        }
        .markdown-content code {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>八字命理分析报告</h1>
    <div class="info">
        <p>生成时间：{{ generate_time }}</p>
    </div>

    <h2>八字命盘</h2>
    <div class="section">
        <div class="pillar">
            <div class="pillar-title">年柱</div>
            <div class="stem">{{ year_stem }}</div>
            <div class="branch">{{ year_branch }}</div>
        </div>
        <div class="pillar">
            <div class="pillar-title">月柱</div>
            <div class="stem">{{ month_stem }}</div>
            <div class="branch">{{ month_branch }}</div>
        </div>
        <div class="pillar">
            <div class="pillar-title">日柱</div>
            <div class="stem">{{ day_stem }}</div>
            <div class="branch">{{ day_branch }}</div>
        </div>
        <div class="pillar">
            <div class="pillar-title">时柱</div>
            <div class="stem">{{ hour_stem }}</div>
            <div class="branch">{{ hour_branch }}</div>
        </div>
    </div>

    <h2>五行分布</h2>
    <div class="section">
        <table>
            <tr>
                <th>金</th>
                <th>木</th>
                <th>水</th>
                <th>火</th>
                <th>土</th>
            </tr>
            <tr>
                <td>{{ five_elements.metal }}</td>
                <td>{{ five_elements.wood }}</td>
                <td>{{ five_elements.water }}</td>
                <td>{{ five_elements.fire }}</td>
                <td>{{ five_elements.earth }}</td>
            </tr>
        </table>
    </div>

    <h2>AI分析结果</h2>
    
    <div class="section">
        <h3>八字命局核心分析</h3>
        <div class="markdown-content">{{ ai_analysis.coreAnalysis|safe }}</div>
    </div>
    
    <div class="section">
        <h3>五行旺衰与用神</h3>
        <div class="markdown-content">{{ ai_analysis.fiveElements|safe }}</div>
    </div>
    
    <div class="section">
        <h3>神煞解析</h3>
        <div class="markdown-content">{{ ai_analysis.shenShaAnalysis|safe }}</div>
    </div>
    
    <div class="section">
        <h3>大运与流年关键节点</h3>
        <div class="markdown-content">{{ ai_analysis.keyPoints|safe }}</div>
    </div>
    
    <div class="section">
        <h3>健康分析</h3>
        <div class="markdown-content">{{ ai_analysis.health|safe }}</div>
    </div>
    
    <div class="section">
        <h3>财富分析</h3>
        <div class="markdown-content">{{ ai_analysis.wealth|safe }}</div>
    </div>
    
    <div class="section">
        <h3>事业分析</h3>
        <div class="markdown-content">{{ ai_analysis.career|safe }}</div>
    </div>
    
    <div class="section">
        <h3>婚姻感情</h3>
        <div class="markdown-content">{{ ai_analysis.relationship|safe }}</div>
    </div>
    
    <div class="section">
        <h3>子女情况</h3>
        <div class="markdown-content">{{ ai_analysis.children|safe }}</div>
    </div>
    
    <div class="section">
        <h3>父母情况</h3>
        <div class="markdown-content">{{ ai_analysis.parents|safe }}</div>
    </div>
    
    <div class="section">
        <h3>学业分析</h3>
        <div class="markdown-content">{{ ai_analysis.education|safe }}</div>
    </div>
    
    <div class="section">
        <h3>人际关系</h3>
        <div class="markdown-content">{{ ai_analysis.social|safe }}</div>
    </div>
    
    <div class="section">
        <h3>近五年运势</h3>
        <div class="markdown-content">{{ ai_analysis.future|safe }}</div>
    </div>

    <div class="footer">
        © {{ generate_time.split('年')[0] }} 八字命理AI指导系统
    </div>
</body>
</html>
"""

def ensure_chinese_font():
    """
    确保中文字体文件存在并正确注册
    """
    global FONT_REGISTERED, DEFAULT_FONT_NAME
    
    # 如果字体已经注册，直接返回
    if FONT_REGISTERED:
        logger.info("字体已注册，跳过重复注册")
        return True
        
    try:
        # Windows系统字体路径
        windows_fonts = [
            ("C:\\Windows\\Fonts\\simhei.ttf", "SimHei"),      # 黑体
            ("C:\\Windows\\Fonts\\simfang.ttf", "SimFang"),    # 仿宋
            ("C:\\Windows\\Fonts\\simkai.ttf", "SimKai"),      # 楷体
            ("C:\\Windows\\Fonts\\simsun.ttc", "SimSun"),      # 宋体
            ("C:\\Windows\\Fonts\\msyh.ttc", "MicrosoftYaHei") # 微软雅黑
        ]
        
        # 本地字体目录
        font_dir = os.path.join(os.getcwd(), 'static', 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        
        # 检查系统字体
        for font_path, font_name in windows_fonts:
            if os.path.exists(font_path):
                logger.info(f"找到系统字体: {font_path}")
                
                # 复制到本地目录以确保访问权限
                local_font_path = os.path.join(font_dir, os.path.basename(font_path))
                try:
                    if not os.path.exists(local_font_path):
                        shutil.copy2(font_path, local_font_path)
                        logger.info(f"复制字体到本地: {local_font_path}")
                except Exception as e:
                    logger.warning(f"复制字体文件失败: {str(e)}")
                
                # 注册字体 - 尝试直接使用系统字体，如果失败则使用复制的本地字体
                try:
                    # 先尝试系统字体
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    DEFAULT_FONT_NAME = font_name
                    FONT_REGISTERED = True
                    logger.info(f"成功注册系统字体: {font_name}")
                    return True
                except Exception as e1:
                    logger.warning(f"注册系统字体失败: {str(e1)}，尝试使用本地复制的字体")
                    try:
                        # 如果系统字体失败，尝试本地复制的字体
                        if os.path.exists(local_font_path):
                            pdfmetrics.registerFont(TTFont(font_name, local_font_path))
                            DEFAULT_FONT_NAME = font_name
                            FONT_REGISTERED = True
                            logger.info(f"成功注册本地复制的字体: {font_name}")
                            return True
                    except Exception as e2:
                        logger.warning(f"注册本地复制的字体也失败: {str(e2)}")
        
        # 尝试使用内置的中文字体
        try:
            logger.info("尝试使用ReportLab内置中文字体")
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            DEFAULT_FONT_NAME = 'STSong-Light'
            FONT_REGISTERED = True
            logger.info("成功注册内置中文字体: STSong-Light")
            return True
        except Exception as e:
            logger.warning(f"注册内置中文字体失败: {str(e)}")
        
        # 如果以上都失败，尝试下载并使用开源中文字体
        for font_url, font_filename in [
            ('https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf', 'SourceHanSansSC-Regular.otf'),
            ('https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf', 'NotoSansSC-Regular.otf')
        ]:
            try:
                local_font_path = os.path.join(font_dir, font_filename)
                if not os.path.exists(local_font_path):
                    logger.info(f"下载开源中文字体: {font_url}")
                    urllib.request.urlretrieve(font_url, local_font_path)
                
                if os.path.exists(local_font_path):
                    font_name = os.path.splitext(font_filename)[0]
                    pdfmetrics.registerFont(TTFont(font_name, local_font_path))
                    DEFAULT_FONT_NAME = font_name
                    FONT_REGISTERED = True
                    logger.info(f"成功注册下载的字体: {font_name}")
                    return True
            except Exception as e:
                logger.warning(f"下载和注册字体 {font_filename} 失败: {str(e)}")
        
        # 最后的备选方案，使用一个空白占位字体
        logger.error("所有字体注册尝试都失败，将使用基本字体")
        DEFAULT_FONT_NAME = 'Helvetica'  # 使用ReportLab默认的西文字体
        FONT_REGISTERED = True
        return False
    except Exception as e:
        logger.exception(f"字体注册过程中发生未知错误: {str(e)}")
        DEFAULT_FONT_NAME = 'Helvetica'
        FONT_REGISTERED = True
        return False

def generate_bazi_pdf(analysis_id, formatted_data, analysis, title=None, output_path=None):
    """
    生成八字分析PDF
    
    Args:
        analysis_id: 分析ID
        formatted_data: 格式化的八字数据
        analysis: 分析结果
        title: PDF标题
        output_path: 输出PDF路径，默认为自动生成
    
    Returns:
        str: 生成的文件路径
    """
    try:
        # 确保中文字体文件存在
        font_success = ensure_chinese_font()
        
        if not output_path:
            # 创建临时输出路径
            pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            output_path = os.path.join(pdf_dir, f'bazi_analysis_{analysis_id}.pdf')
        
        logger.info(f"正在生成PDF: {output_path}, 使用字体: {DEFAULT_FONT_NAME}")
        
        # 创建文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=60,  # 减小页边距
            leftMargin=60,   # 减小页边距
            topMargin=60,    # 减小页边距
            bottomMargin=60  # 减小页边距
        )
        
        # 创建样式
        styles = getSampleStyleSheet()
        
        # 添加中文样式 - 增加字体大小
        styles.add(ParagraphStyle(
            name='Chinese',
            fontName=DEFAULT_FONT_NAME,
            fontSize=16,     # 增加字体大小，从14到16
            leading=22,      # 增加行间距，从18到22
            spaceAfter=12,   # 保持段落后空间不变
            spaceBefore=6,   # 保持段落前空间不变
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=DEFAULT_FONT_NAME,
            fontSize=32,     # 增加标题字体大小，从28到32
            leading=36,      # 增加行间距，从32到36
            alignment=1,     # 居中
            spaceAfter=24,   # 保持标题后空间不变
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading1',
            fontName=DEFAULT_FONT_NAME,
            fontSize=26,     # 增加一级标题字体大小，从22到26
            leading=30,      # 增加行间距，从26到30
            spaceAfter=18,   # 保持标题后空间不变
            spaceBefore=36,  # 保持标题前空间不变
            textColor=colors.blue,  # 保持颜色不变
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            fontName=DEFAULT_FONT_NAME,
            fontSize=22,     # 增加二级标题字体大小，从18到22
            leading=26,      # 增加行间距，从22到26
            spaceAfter=12,   # 保持标题后空间不变
            spaceBefore=24,  # 保持标题前空间不变
            textColor=colors.darkblue,  # 保持颜色不变
            encoding='utf-8'
        ))
        
        # 添加新的强调样式
        styles.add(ParagraphStyle(
            name='ChineseEmphasis',
            fontName=DEFAULT_FONT_NAME,
            fontSize=15,     # 强调文字稍大一些
            leading=19,      
            textColor=colors.darkred,  # 使用红色强调重要内容
            encoding='utf-8'
        ))
        
        # 添加新的段落分隔样式
        styles.add(ParagraphStyle(
            name='ChineseSeparator',
            fontName=DEFAULT_FONT_NAME,
            fontSize=14,
            leading=18,
            alignment=1,     # 居中
            textColor=colors.gray,
            encoding='utf-8'
        ))
        
        # 准备文档内容
        elements = []
        
        # 添加标题
        elements.append(Paragraph(title or '八字命理分析报告', styles['ChineseTitle']))
        
        # 添加生成时间
        elements.append(Paragraph(
            f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            ParagraphStyle(
                name='ChineseSubtitle',
                fontName=DEFAULT_FONT_NAME,
                fontSize=12,  # 增加字体大小，从10到12
                alignment=1,  # 居中
                encoding='utf-8'
            )
        ))
        elements.append(Spacer(1, 30))  # 增加空间，从20到30
        
        # 打印调试信息
        try:
            logger.info(f"格式化数据类型: {type(formatted_data)}")
            logger.info(f"格式化数据内容: {json.dumps(formatted_data, ensure_ascii=False, cls=DateTimeEncoder)[:500]}")
            logger.info(f"分析内容: {json.dumps(analysis, ensure_ascii=False, cls=DateTimeEncoder)[:500]}")
        except Exception as e:
            logger.warning(f"转换数据为JSON时出错: {str(e)}")
        
        # 添加八字命盘信息
        elements.append(Paragraph('八字命盘', styles['ChineseHeading1']))
        
        # 改进表格样式
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # 表头背景色
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),    # 表头文字颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # 所有单元格居中
            ('FONTNAME', (0, 0), (-1, -1), DEFAULT_FONT_NAME), # 表格字体
            ('FONTSIZE', (0, 0), (-1, 0), 14),                 # 表头字体大小增加
            ('FONTSIZE', (0, 1), (-1, -1), 13),                # 表格内容字体大小增加
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),            # 单元格内边距增加
            ('TOPPADDING', (0, 0), (-1, -1), 8),               # 单元格内边距增加
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),      # 表格边框颜色改进
            ('BOX', (0, 0), (-1, -1), 1, colors.black),        # 表格外框加粗
        ])
        
        # 尝试从多个来源获取命盘数据
        bazi_text = ""
        if isinstance(formatted_data, dict):
            # 直接从formatted_data获取
            if 'bazi' in formatted_data:
                bazi_text = formatted_data.get('bazi', '')
            # 或者从baziChart构建
            elif 'baziChart' in formatted_data:
                bazi_chart = formatted_data.get('baziChart', {})
                if isinstance(bazi_chart, dict):
                    try:
                        # 构建八字信息文本
                        year_pillar = bazi_chart.get('yearPillar', {})
                        month_pillar = bazi_chart.get('monthPillar', {})
                        day_pillar = bazi_chart.get('dayPillar', {})
                        hour_pillar = bazi_chart.get('hourPillar', {})
                        
                        year_stem = year_pillar.get('heavenlyStem', '')
                        year_branch = year_pillar.get('earthlyBranch', '')
                        month_stem = month_pillar.get('heavenlyStem', '')
                        month_branch = month_pillar.get('earthlyBranch', '')
                        day_stem = day_pillar.get('heavenlyStem', '')
                        day_branch = day_pillar.get('earthlyBranch', '')
                        hour_stem = hour_pillar.get('heavenlyStem', '')
                        hour_branch = hour_pillar.get('earthlyBranch', '')
                        
                        bazi_text = f"年柱: {year_stem}{year_branch} 月柱: {month_stem}{month_branch} 日柱: {day_stem}{day_branch} 时柱: {hour_stem}{hour_branch}"
                    except Exception as e:
                        logger.warning(f"从baziChart构建八字信息失败: {str(e)}")
        
        # 如果bazi_text为空，则使用默认值
        if not bazi_text:
            bazi_text = "无法获取八字命盘数据，请联系客服。"
            
        elements.append(Paragraph(bazi_text, styles['Chinese']))
        
        # 添加五行分布
        elements.append(Paragraph('五行分布', styles['ChineseHeading1']))
        
        # 从多个可能的来源获取五行数据
        five_elements = None
        if isinstance(formatted_data, dict):
            if 'five_elements' in formatted_data:
                five_elements = formatted_data.get('five_elements')
            elif 'baziChart' in formatted_data and 'fiveElements' in formatted_data.get('baziChart', {}):
                five_elements = formatted_data.get('baziChart', {}).get('fiveElements')
        
        # 如果有五行分布数据，添加表格
        if five_elements:
            try:
                # 获取五行数值
                metal_val = five_elements.get('metal', 0)
                wood_val = five_elements.get('wood', 0)
                water_val = five_elements.get('water', 0)
                fire_val = five_elements.get('fire', 0)
                earth_val = five_elements.get('earth', 0)
                
                data = [
                    ['金', '木', '水', '火', '土'],
                    [metal_val, wood_val, water_val, fire_val, earth_val]
                ]
                
                table = Table(data, colWidths=[80] * 5)
                table.setStyle(table_style)
                
                elements.append(table)
            except Exception as e:
                logger.warning(f"生成五行分布表格失败: {str(e)}")
                elements.append(Paragraph("五行分布数据获取失败", styles['Chinese']))
        else:
            elements.append(Paragraph("五行分布数据不可用", styles['Chinese']))
            
        elements.append(Spacer(1, 10))
        
        # 添加神煞信息
        shen_sha = formatted_data.get('shen_sha', {})
        if shen_sha and isinstance(shen_sha, dict):
            elements.append(Paragraph('神煞信息', styles['ChineseHeading1']))
            for category, items in shen_sha.items():
                elements.append(Paragraph(category, styles['ChineseHeading2']))
                if isinstance(items, list):
                    for item in items:
                        elements.append(Paragraph(f"• {item}", styles['Chinese']))
        
        # 添加大运流年
        flowing_years = formatted_data.get('da_yun', [])
        if flowing_years:
            elements.append(Paragraph('大运流年', styles['ChineseHeading1']))
            elements.append(Paragraph(formatted_data.get('da_yun', ''), styles['Chinese']))
        
        # 添加起运信息
        if 'qi_yun' in formatted_data:
            elements.append(Paragraph('起运信息', styles['ChineseHeading2']))
            elements.append(Paragraph(formatted_data.get('qi_yun', ''), styles['Chinese']))
        
        # 添加AI分析结果
        elements.append(Paragraph('AI分析结果', styles['ChineseHeading1']))
        
        # 检查分析结果是否为字典类型
        if not isinstance(analysis, dict):
            analysis = {}
            logger.warning(f"分析结果不是字典类型，实际类型: {type(analysis)}")
            if isinstance(formatted_data, dict) and 'analysis' in formatted_data and isinstance(formatted_data['analysis'], dict):
                analysis = formatted_data['analysis']
                logger.info("从formatted_data中获取分析结果")
            else:
                logger.warning("无法获取有效的分析结果")
        
        if not analysis:
            # 使用默认分析结果
            analysis = {
                'overall': '暂无综合分析数据',
                'health': '暂无健康分析数据',
                'wealth': '暂无财富分析数据',
                'career': '暂无事业分析数据',
                'relationship': '暂无婚姻感情分析数据',
                'children': '暂无子女分析数据',
                'personality': '暂无性格特点分析数据',
                'education': '暂无学业发展分析数据'
            }
        
        # 添加总体分析
        if 'overall' in analysis:
            elements.append(Paragraph('总体分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['overall'], styles['Chinese']))
        
        # 添加健康分析
        if 'health' in analysis:
            elements.append(Paragraph('健康分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['health'], styles['Chinese']))
        
        # 添加财富分析
        if 'wealth' in analysis:
            elements.append(Paragraph('财富分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['wealth'], styles['Chinese']))
        
        # 添加事业分析
        if 'career' in analysis:
            elements.append(Paragraph('事业分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['career'], styles['Chinese']))
        
        # 添加婚姻感情分析
        if 'relationship' in analysis:
            elements.append(Paragraph('婚姻感情分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['relationship'], styles['Chinese']))
        
        # 添加子女分析
        if 'children' in analysis:
            elements.append(Paragraph('子女分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['children'], styles['Chinese']))
        
        # 添加学业分析
        if 'education' in analysis:
            elements.append(Paragraph('学业分析', styles['ChineseHeading2']))
            elements.append(Paragraph(analysis['education'], styles['Chinese']))
        
        # 添加页脚
        elements.append(Spacer(1, 50))
        elements.append(Paragraph(
            f"© {datetime.now().year} 八字命理AI指导系统",
            ParagraphStyle(
                name='Footer',
                fontName=DEFAULT_FONT_NAME,
                fontSize=10,
                alignment=1,  # 居中
                textColor=colors.gray,
                encoding='utf-8'
            )
        ))
        
        # 构建PDF
        doc.build(elements)
        
        logger.info(f"PDF生成成功: {output_path}")
        return output_path
    
    except Exception as e:
        logger.exception(f"生成八字分析PDF失败: {str(e)}")
        return None

def generate_pdf(result_data, parse_md=False):
    """生成PDF文件
    
    Args:
        result_data: 分析结果数据
        parse_md: 是否解析Markdown内容
        
    Returns:
        生成的PDF文件URL
    """
    try:
        logger.info("开始生成PDF")
        
        # 提取必要数据
        result_id = str(result_data.get('_id', 'unknown'))
        
        # 获取八字命盘数据
        bazi_chart = result_data.get('baziChart', {})
        if not bazi_chart:
            logger.warning("八字命盘数据为空")
            bazi_chart = {}
        
        # 获取年月日时四柱
        year_pillar = bazi_chart.get('yearPillar', {})
        month_pillar = bazi_chart.get('monthPillar', {})
        day_pillar = bazi_chart.get('dayPillar', {})
        hour_pillar = bazi_chart.get('hourPillar', {})
        
        # 获取五行分布
        five_elements = bazi_chart.get('fiveElements', {})
        if not five_elements:
            five_elements = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
        
        # 获取AI分析结果
        ai_analysis = result_data.get('aiAnalysis', {})
        if not ai_analysis:
            logger.warning("AI分析结果为空")
            ai_analysis = {}
            
        # 如果需要解析Markdown
        if parse_md and markdown_support:
            logger.info("解析Markdown内容")
            try:
                # 解析整个分析数据对象中的Markdown内容
                ai_analysis = parse_analysis_data(ai_analysis)
                logger.info("Markdown解析完成")
            except Exception as e:
                logger.error(f"解析Markdown内容时出错: {str(e)}")
        else:
            logger.info("跳过Markdown解析")
            
        # 检查并记录AI分析结果中的字段
        analysis_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                           'personality', 'education', 'parents', 'social', 'future', 
                           'coreAnalysis', 'fiveElements', 'shenShaAnalysis', 'keyPoints']
        for field in analysis_fields:
            if field in ai_analysis:
                logger.info(f"AI分析结果包含字段: {field}")
                # 截取前50个字符用于日志记录
                content = ai_analysis[field]
                if content and isinstance(content, str):
                    logger.info(f"{field}内容: {content[:50]}...")
            else:
                logger.warning(f"AI分析结果缺少字段: {field}")
                # 添加默认值
                ai_analysis[field] = f"暂无{field}分析数据"
        
        # 确定输出路径
        html_path = os.path.join(PDF_DIR, f"bazi_analysis_{result_id}.html")
        pdf_path = os.path.join(PDF_DIR, f"bazi_analysis_{result_id}.pdf")
        
        # 首先尝试使用reportlab直接生成PDF
        pdf_generated = False
        
        if reportlab_available:
            try:
                logger.info("尝试使用reportlab直接生成PDF...")
                # 确保目录存在
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                
                # 先删除可能存在的旧文件
                if os.path.exists(pdf_path):
                    try:
                        os.remove(pdf_path)
                        logger.info(f"已删除旧的PDF文件: {pdf_path}")
                    except Exception as e:
                        logger.warning(f"删除旧PDF文件失败: {str(e)}")
                
                # 生成PDF
                fallback_pdf_path = generate_bazi_pdf(result_id, result_data, ai_analysis, output_path=pdf_path)
                
                # 验证生成的PDF文件
                if fallback_pdf_path and os.path.exists(fallback_pdf_path) and os.path.getsize(fallback_pdf_path) > 0:
                    logger.info(f"使用reportlab成功生成PDF: {fallback_pdf_path}, 文件大小: {os.path.getsize(fallback_pdf_path)} 字节")
                    
                    # 尝试验证PDF文件是否有效
                    try:
                        with open(fallback_pdf_path, 'rb') as f:
                            header = f.read(5)
                            if header.startswith(b'%PDF-'):
                                logger.info("PDF文件头验证通过")
                                pdf_generated = True
                                return f"/static/pdfs/bazi_analysis_{result_id}.pdf"
                            else:
                                logger.warning(f"生成的文件不是有效的PDF文件，文件头: {header}")
                    except Exception as e:
                        logger.warning(f"验证PDF文件时出错: {str(e)}")
                else:
                    logger.error("reportlab生成PDF失败或文件无效")
            except Exception as e:
                logger.error(f"reportlab生成PDF出错: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 如果reportlab失败，尝试生成HTML文件然后转换为PDF
        if not pdf_generated:
            try:
                # 渲染HTML模板
                template = Template(HTML_TEMPLATE)
                html_content = template.render(
                    generate_time=datetime.now().strftime('%Y年%m月%d日 %H:%M'),
                    year_stem=year_pillar.get('heavenlyStem', ''),
                    year_branch=year_pillar.get('earthlyBranch', ''),
                    month_stem=month_pillar.get('heavenlyStem', ''),
                    month_branch=month_pillar.get('earthlyBranch', ''),
                    day_stem=day_pillar.get('heavenlyStem', ''),
                    day_branch=day_pillar.get('earthlyBranch', ''),
                    hour_stem=hour_pillar.get('heavenlyStem', ''),
                    hour_branch=hour_pillar.get('earthlyBranch', ''),
                    five_elements=five_elements,
                    ai_analysis=ai_analysis
                )
                
                # 保存HTML文件
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"HTML文件已保存: {html_path}")
                
                # 检查wkhtmltopdf是否可用
                wkhtmltopdf_available = False
                config = None
                
                # 检查系统中是否有wkhtmltopdf
                try:
                    import subprocess
                    result = subprocess.run(['wkhtmltopdf', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if result.returncode == 0:
                        logger.info("系统中已安装wkhtmltopdf")
                        wkhtmltopdf_available = True
                except:
                    logger.warning("系统中未找到wkhtmltopdf命令")
                
                # 检查本地bin目录中是否有wkhtmltopdf
                if not wkhtmltopdf_available and os.name == 'nt':  # Windows
                    wkhtmltopdf_path = os.path.join(os.getcwd(), 'bin', 'wkhtmltopdf.exe')
                    if os.path.exists(wkhtmltopdf_path):
                        logger.info(f"找到本地wkhtmltopdf: {wkhtmltopdf_path}")
                        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                        wkhtmltopdf_available = True
                
                # 尝试使用pdfkit生成PDF
                try:
                    if wkhtmltopdf_available:
                        # 先删除可能存在的旧文件
                        if os.path.exists(pdf_path):
                            try:
                                os.remove(pdf_path)
                                logger.info(f"已删除旧的PDF文件: {pdf_path}")
                            except Exception as e:
                                logger.warning(f"删除旧PDF文件失败: {str(e)}")
                        
                        # 设置pdfkit选项
                        options = {
                            'encoding': 'UTF-8',
                            'page-size': 'A4',
                            'margin-top': '1cm',
                            'margin-right': '1cm',
                            'margin-bottom': '1cm',
                            'margin-left': '1cm',
                            'enable-local-file-access': None,
                            'quiet': '',
                            'no-outline': None
                        }
                        
                        # 生成PDF
                        if config:
                            logger.info(f"使用本地wkhtmltopdf生成PDF: {pdf_path}")
                            pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
                        else:
                            logger.info(f"使用系统wkhtmltopdf生成PDF: {pdf_path}")
                            pdfkit.from_file(html_path, pdf_path, options=options)
                        
                        # 检查PDF是否成功生成
                        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                            logger.info(f"PDF文件已生成: {pdf_path}, 文件大小: {os.path.getsize(pdf_path)} 字节")
                            
                            # 尝试验证PDF文件是否有效
                            try:
                                with open(pdf_path, 'rb') as f:
                                    header = f.read(5)
                                    if header.startswith(b'%PDF-'):
                                        logger.info("PDF文件头验证通过")
                                        pdf_generated = True
                                        return f"/static/pdfs/bazi_analysis_{result_id}.pdf"
                                    else:
                                        logger.warning(f"生成的文件不是有效的PDF文件，文件头: {header}")
                            except Exception as e:
                                logger.warning(f"验证PDF文件时出错: {str(e)}")
                        else:
                            logger.error(f"PDF文件生成失败或为空: {pdf_path}")
                    else:
                        logger.error("无法生成PDF：wkhtmltopdf不可用")
                except Exception as e:
                    logger.error(f"wkhtmltopdf生成PDF失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"HTML生成过程出错: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 如果所有方法都失败，返回HTML
        logger.warning(f"所有PDF生成方法都失败，返回HTML: {html_path}")
        return f"/static/pdfs/bazi_analysis_{result_id}.html"
    
    except Exception as e:
        logger.error(f"PDF生成过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None 

def generate_pdf_content(result_data, parse_md=False):
    """生成PDF内容并返回二进制数据，不保存到文件系统
    
    Args:
        result_data: 分析结果数据
        parse_md: 是否解析Markdown内容
        
    Returns:
        bytes: PDF文件的二进制内容
    """
    try:
        logger.info("开始生成PDF内容")
        
        # 提取必要数据
        result_id = str(result_data.get('_id', 'unknown'))
        
        # 获取八字命盘数据
        bazi_chart = result_data.get('baziChart', {})
        if not bazi_chart:
            logger.warning("八字命盘数据为空")
            bazi_chart = {}
        
        # 获取年月日时四柱
        year_pillar = bazi_chart.get('yearPillar', {})
        month_pillar = bazi_chart.get('monthPillar', {})
        day_pillar = bazi_chart.get('dayPillar', {})
        hour_pillar = bazi_chart.get('hourPillar', {})
        
        # 获取五行分布
        five_elements = bazi_chart.get('fiveElements', {})
        if not five_elements:
            five_elements = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
        
        # 获取AI分析结果
        ai_analysis = result_data.get('aiAnalysis', {})
        if not ai_analysis:
            logger.warning("AI分析结果为空")
            ai_analysis = {}
            
        # 如果需要解析Markdown
        if parse_md and markdown_support:
            logger.info("解析Markdown内容")
            try:
                # 解析整个分析数据对象中的Markdown内容
                ai_analysis = parse_analysis_data(ai_analysis)
                logger.info("Markdown解析完成")
            except Exception as e:
                logger.error(f"解析Markdown内容时出错: {str(e)}")
        else:
            logger.info("跳过Markdown解析")
            
        # 获取追问分析结果
        followups = result_data.get('followups', {})
        if not followups:
            logger.info("追问分析结果为空")
            followups = {}
        else:
            logger.info(f"追问分析结果包含字段: {list(followups.keys())}")
            # 如果需要解析Markdown并且启用了markdown支持
            if parse_md and markdown_support and followups:
                try:
                    # 解析追问分析结果中的Markdown
                    followups = parse_analysis_data(followups)
                    logger.info("追问分析Markdown解析完成")
                except Exception as e:
                    logger.error(f"解析追问分析Markdown内容时出错: {str(e)}")
        
        # 检查并记录AI分析结果中的字段
        analysis_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                           'personality', 'education', 'parents', 'social', 'future',
                           'coreAnalysis', 'fiveElements', 'shenShaAnalysis', 'keyPoints']
        for field in analysis_fields:
            if field not in ai_analysis:
                logger.warning(f"AI分析结果缺少字段: {field}")
                # 添加默认值
                ai_analysis[field] = f"暂无{field}分析数据"
        
        # 使用BytesIO作为输出目标
        from io import BytesIO
        output_buffer = BytesIO()
        
        # 尝试使用reportlab生成PDF
        if reportlab_available:
            try:
                logger.info("尝试使用reportlab生成PDF内容...")
                
                # 确保中文字体可用
                ensure_chinese_font()
                
                # 创建PDF文档对象
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib import colors
                doc = SimpleDocTemplate(
                    output_buffer,
                    pagesize=A4,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                
                # 定义表格样式
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONT', (0, 0), (-1, -1), DEFAULT_FONT_NAME),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 0), (-1, -1), 14),  # 增加表格中的字体大小，从10到14
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # 增加单元格内边距，从6到8
                    ('TOPPADDING', (0, 0), (-1, -1), 8),  # 增加单元格内边距，从6到8
                ])
                
                # 创建样式
                styles = getSampleStyleSheet()
                styles.add(ParagraphStyle(
                    name='Chinese',
                    fontName=DEFAULT_FONT_NAME,
                    fontSize=16,     # 增加字体大小，从14到16
                    leading=22,      # 增加行间距，从18到22
                    spaceAfter=12,   # 保持段落后空间不变
                    spaceBefore=6,   # 保持段落前空间不变
                    encoding='utf-8'
                ))
                styles.add(ParagraphStyle(
                    name='ChineseHeading1',
                    fontName=DEFAULT_FONT_NAME,
                    fontSize=26,     # 增加一级标题字体大小，从22到26
                    leading=30,      # 增加行间距，从26到30
                    spaceAfter=18,   # 保持标题后空间不变
                    spaceBefore=36,  # 保持标题前空间不变
                    textColor=colors.blue,  # 保持颜色不变
                    alignment=1,     # 居中
                    encoding='utf-8'
                ))
                styles.add(ParagraphStyle(
                    name='ChineseHeading2',
                    fontName=DEFAULT_FONT_NAME,
                    fontSize=22,     # 增加二级标题字体大小，从18到22
                    leading=26,      # 增加行间距，从22到26
                    spaceAfter=12,   # 保持标题后空间不变
                    spaceBefore=24,  # 保持标题前空间不变
                    textColor=colors.darkblue,  # 保持颜色不变
                    encoding='utf-8'
                ))
                
                # 创建内容元素
                elements = []
                
                # 添加标题
                elements.append(Paragraph("八字命理分析报告", styles['ChineseHeading1']))
                elements.append(Spacer(1, 12))
                
                # 添加生成信息
                elements.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", styles['Chinese']))
                elements.append(Paragraph(f"分析ID: {result_id}", styles['Chinese']))
                elements.append(Spacer(1, 24))
                
                # 添加八字命盘信息
                elements.append(Paragraph("八字命盘", styles['ChineseHeading2']))
                
                # 四柱数据
                pillar_data = [
                    ['', '年柱', '月柱', '日柱', '时柱'],
                    ['天干', 
                     year_pillar.get('heavenlyStem', ''), 
                     month_pillar.get('heavenlyStem', ''), 
                     day_pillar.get('heavenlyStem', ''), 
                     hour_pillar.get('heavenlyStem', '')],
                    ['地支', 
                     year_pillar.get('earthlyBranch', ''), 
                     month_pillar.get('earthlyBranch', ''), 
                     day_pillar.get('earthlyBranch', ''), 
                     hour_pillar.get('earthlyBranch', '')],
                    ['纳音', 
                     year_pillar.get('naYin', ''), 
                     month_pillar.get('naYin', ''), 
                     day_pillar.get('naYin', ''), 
                     hour_pillar.get('naYin', '')],
                    ['十神', 
                     year_pillar.get('shiShen', ''), 
                     month_pillar.get('shiShen', ''), 
                     day_pillar.get('shiShen', ''), 
                     hour_pillar.get('shiShen', '')],
                    ['旺衰', 
                     year_pillar.get('wangShuai', ''), 
                     month_pillar.get('wangShuai', ''), 
                     day_pillar.get('wangShuai', ''), 
                     hour_pillar.get('wangShuai', '')]
                ]
                
                # 创建四柱表格
                pillar_table = Table(pillar_data, colWidths=[80, 80, 80, 80, 80])
                pillar_table.setStyle(table_style)
                elements.append(pillar_table)
                elements.append(Spacer(1, 12))
                
                # 添加五行分布
                elements.append(Paragraph("五行分布", styles['ChineseHeading2']))
                five_element_names = {
                    'metal': '金',
                    'wood': '木',
                    'water': '水',
                    'fire': '火',
                    'earth': '土'
                }
                
                five_element_data = [['五行', '数量']]
                for element, count in five_elements.items():
                    element_name = five_element_names.get(element, element)
                    five_element_data.append([element_name, str(count)])
                
                five_element_table = Table(five_element_data, colWidths=[100, 100])
                five_element_table.setStyle(table_style)
                elements.append(five_element_table)
                elements.append(Spacer(1, 12))
                
                # 添加八字命局核心分析
                if 'coreAnalysis' in ai_analysis and ai_analysis['coreAnalysis']:
                    elements.append(Paragraph("八字命局核心分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['coreAnalysis'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加五行旺衰与用神
                if 'fiveElements' in ai_analysis and ai_analysis['fiveElements']:
                    elements.append(Paragraph("五行旺衰与用神", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['fiveElements'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加神煞解析
                if 'shenShaAnalysis' in ai_analysis and ai_analysis['shenShaAnalysis']:
                    elements.append(Paragraph("神煞解析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['shenShaAnalysis'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加大运与流年关键节点
                if 'keyPoints' in ai_analysis and ai_analysis['keyPoints']:
                    elements.append(Paragraph("大运与流年关键节点", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['keyPoints'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加大运信息
                da_yun = bazi_chart.get('daYun', {})
                if da_yun and da_yun.get('daYunList'):
                    elements.append(Paragraph("大运信息", styles['ChineseHeading2']))
                    elements.append(Paragraph(f"起运年龄: {da_yun.get('startAge', '')}岁", styles['Chinese']))
                    elements.append(Paragraph(f"起运年份: {da_yun.get('startYear', '')}年", styles['Chinese']))
                    elements.append(Paragraph(f"大运顺序: {'顺行' if da_yun.get('isForward', True) else '逆行'}", styles['Chinese']))
                    elements.append(Spacer(1, 12))
                    
                    da_yun_data = [['年龄', '年份', '天干', '地支', '纳音', '吉凶']]
                    
                    for yun in da_yun['daYunList']:
                        da_yun_data.append([
                            f"{yun.get('startAge', '')}-{yun.get('endAge', '')}", 
                            f"{yun.get('startYear', '')}-{yun.get('endYear', '')}", 
                            yun.get('heavenlyStem', ''), 
                            yun.get('earthlyBranch', ''), 
                            yun.get('naYin', ''),
                            yun.get('jiXiong', '')
                        ])
                    
                    da_yun_table = Table(da_yun_data)
                    da_yun_table.setStyle(table_style)
                    elements.append(da_yun_table)
                    elements.append(Spacer(1, 12))
                
                # 添加流年信息
                flowing_years = bazi_chart.get('flowingYears', [])
                if flowing_years:
                    elements.append(Paragraph("流年信息", styles['ChineseHeading2']))
                    flowing_years_data = [['年份', '年龄', '天干', '地支', '五行', '神煞', '吉凶']]
                    
                    for year in flowing_years[:10]:  # 只显示前10年
                        flowing_years_data.append([
                            year.get('year', ''),
                            year.get('age', ''),
                            year.get('heavenlyStem', ''),
                            year.get('earthlyBranch', ''),
                            f"{five_element_names.get(year.get('ganElement', ''), '')}/{five_element_names.get(year.get('zhiElement', ''), '')}",
                            ', '.join(year.get('shenSha', [])) if isinstance(year.get('shenSha', []), list) else year.get('shenSha', ''),
                            year.get('jiXiong', '')
                        ])
                    
                    flowing_years_table = Table(flowing_years_data)
                    flowing_years_table.setStyle(table_style)
                    elements.append(flowing_years_table)
                    elements.append(Spacer(1, 12))
                
                # 添加健康分析
                if 'health' in ai_analysis and ai_analysis['health']:
                    elements.append(Paragraph("健康分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['health'], styles['Chinese']))
                    # 添加健康追问分析（如果存在）
                    if 'health' in followups and followups['health']:
                        elements.append(Paragraph("健康深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(followups['health'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加事业财运分析
                if 'career' in ai_analysis and ai_analysis['career']:
                    elements.append(Paragraph("事业财运分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['career'], styles['Chinese']))
                    # 添加事业财运追问分析（如果存在）
                    career_followup = followups.get('career') or followups.get('work') or followups.get('money') or followups.get('wealth')
                    if career_followup:
                        elements.append(Paragraph("事业财运深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(career_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加婚姻感情分析
                if 'relationship' in ai_analysis and ai_analysis['relationship']:
                    elements.append(Paragraph("婚姻感情分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['relationship'], styles['Chinese']))
                    # 添加婚姻感情追问分析（如果存在）
                    relationship_followup = followups.get('relationship') or followups.get('marriage')
                    if relationship_followup:
                        elements.append(Paragraph("婚姻感情深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(relationship_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加子女分析
                if 'children' in ai_analysis and ai_analysis['children']:
                    elements.append(Paragraph("子女分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['children'], styles['Chinese']))
                    # 添加子女追问分析（如果存在）
                    children_followup = followups.get('children') or followups.get('family')
                    if children_followup:
                        elements.append(Paragraph("子女深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(children_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加父母分析
                if 'parents' in ai_analysis and ai_analysis['parents']:
                    elements.append(Paragraph("父母分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['parents'], styles['Chinese']))
                    # 添加父母追问分析（如果存在）
                    if 'parents' in followups and followups['parents']:
                        elements.append(Paragraph("父母深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(followups['parents'], styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加人际关系分析
                if 'social' in ai_analysis and ai_analysis['social']:
                    elements.append(Paragraph("人际关系分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['social'], styles['Chinese']))
                    # 添加人际关系追问分析（如果存在）
                    social_followup = followups.get('social') or followups.get('relationship') or followups.get('friends')
                    if social_followup:
                        elements.append(Paragraph("人际关系深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(social_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加学业分析
                if 'education' in ai_analysis and ai_analysis['education']:
                    elements.append(Paragraph("学业分析", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['education'], styles['Chinese']))
                    # 添加学业追问分析（如果存在）
                    education_followup = followups.get('education') or followups.get('study')
                    if education_followup:
                        elements.append(Paragraph("学业深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(education_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加近五年运势
                if 'future' in ai_analysis and ai_analysis['future']:
                    elements.append(Paragraph("近五年运势", styles['ChineseHeading2']))
                    elements.append(Paragraph(ai_analysis['future'], styles['Chinese']))
                    # 添加近五年运势追问分析（如果存在）
                    future_followup = followups.get('future') or followups.get('fiveYears')
                    if future_followup:
                        elements.append(Paragraph("近五年运势深度分析", styles['ChineseHeading2']))
                        elements.append(Paragraph(future_followup, styles['Chinese']))
                    elements.append(Spacer(1, 12))
                
                # 添加页脚
                elements.append(Spacer(1, 50))
                elements.append(Paragraph(
                    f"© {datetime.now().year} 八字命理AI指导系统",
                    ParagraphStyle(
                        name='Footer',
                        fontName=DEFAULT_FONT_NAME,
                        fontSize=10,
                        alignment=1,  # 居中
                        textColor=colors.gray,
                        encoding='utf-8'
                    )
                ))
                
                # 构建PDF
                doc.build(elements)
                
                # 获取PDF内容
                pdf_content = output_buffer.getvalue()
                
                logger.info(f"PDF内容生成成功，大小: {len(pdf_content)} 字节")
                return pdf_content
                
            except Exception as e:
                logger.exception(f"使用reportlab生成PDF内容失败: {str(e)}")
                # 继续尝试其他方法
        
        # 如果reportlab失败，尝试使用HTML模板
        try:
            # 渲染HTML模板
            template = Template(HTML_TEMPLATE)
            html_content = template.render(
                generate_time=datetime.now().strftime('%Y年%m月%d日 %H:%M'),
                year_stem=year_pillar.get('heavenlyStem', ''),
                year_branch=year_pillar.get('earthlyBranch', ''),
                month_stem=month_pillar.get('heavenlyStem', ''),
                month_branch=month_pillar.get('earthlyBranch', ''),
                day_stem=day_pillar.get('heavenlyStem', ''),
                day_branch=day_pillar.get('earthlyBranch', ''),
                hour_stem=hour_pillar.get('heavenlyStem', ''),
                hour_branch=hour_pillar.get('earthlyBranch', ''),
                five_elements=five_elements,
                ai_analysis=ai_analysis
            )
            
            # 检查wkhtmltopdf是否可用
            wkhtmltopdf_available = False
            config = None
            
            # 检查系统中是否有wkhtmltopdf
            try:
                import subprocess
                result = subprocess.run(['wkhtmltopdf', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    logger.info("系统中已安装wkhtmltopdf")
                    wkhtmltopdf_available = True
            except:
                logger.warning("系统中未找到wkhtmltopdf命令")
            
            # 检查本地bin目录中是否有wkhtmltopdf
            if not wkhtmltopdf_available and os.name == 'nt':  # Windows
                wkhtmltopdf_path = os.path.join(os.getcwd(), 'bin', 'wkhtmltopdf.exe')
                if os.path.exists(wkhtmltopdf_path):
                    logger.info(f"找到本地wkhtmltopdf: {wkhtmltopdf_path}")
                    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                    wkhtmltopdf_available = True
            
            # 尝试使用pdfkit直接生成PDF内容
            if wkhtmltopdf_available:
                pdf_content = pdfkit.from_string(
                    html_content,
                    False,  # 不保存到文件
                    configuration=config,
                    options={
                        'encoding': 'UTF-8',
                        'page-size': 'A4',
                        'margin-top': '20mm',
                        'margin-right': '20mm',
                        'margin-bottom': '20mm',
                        'margin-left': '20mm',
                        'title': f'八字命理分析_{result_id}'
                    }
                )
                
                logger.info(f"使用pdfkit生成PDF内容成功，大小: {len(pdf_content)} 字节")
                return pdf_content
                
        except Exception as e:
            logger.exception(f"生成PDF内容失败: {str(e)}")
        
        logger.error("所有PDF生成方法都失败")
        return None
        
    except Exception as e:
        logger.exception(f"生成PDF内容失败: {str(e)}")
        return None 