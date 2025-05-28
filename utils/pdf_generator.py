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

# 添加一个自定义JSON编码器处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        <h3>总体分析</h3>
        <p>{{ ai_analysis.overall|default('暂无综合分析数据') }}</p>
    </div>
    
    <div class="section">
        <h3>健康分析</h3>
        <p>{{ ai_analysis.health|default('暂无健康分析数据') }}</p>
    </div>
    
    <div class="section">
        <h3>财富分析</h3>
        <p>{{ ai_analysis.wealth|default('暂无财富分析数据') }}</p>
    </div>
    
    <div class="section">
        <h3>事业分析</h3>
        <p>{{ ai_analysis.career|default('暂无事业分析数据') }}</p>
    </div>
    
    <div class="section">
        <h3>婚姻感情分析</h3>
        <p>{{ ai_analysis.relationship|default('暂无婚姻感情分析数据') }}</p>
    </div>
    
    <div class="section">
        <h3>子女分析</h3>
        <p>{{ ai_analysis.children|default('暂无子女分析数据') }}</p>
    </div>

    <div class="section">
        <h3>性格特点</h3>
        <p>{{ ai_analysis.personality|default('暂无性格特点分析数据') }}</p>
    </div>

    <div class="section">
        <h3>学业分析</h3>
        <p>{{ ai_analysis.education|default('暂无学业发展分析数据') }}</p>
    </div>

    <div class="section">
        <h3>父母情况</h3>
        <p>{{ ai_analysis.parents|default('暂无父母情况分析数据') }}</p>
    </div>

    <div class="section">
        <h3>人际关系</h3>
        <p>{{ ai_analysis.social|default('暂无人际关系分析数据') }}</p>
    </div>

    <div class="section">
        <h3>近五年运势</h3>
        <p>{{ ai_analysis.future|default('暂无近五年运势分析数据') }}</p>
    </div>
    
    <div class="footer">
        <p>© 2025 八字命理AI人生指导系统 - 本报告由AI生成，仅供参考</p>
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
            fontName=DEFAULT_FONT_NAME,
            fontSize=12,
            leading=14,
            spaceAfter=10,
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=DEFAULT_FONT_NAME,
            fontSize=24,
            leading=28,
            alignment=1,  # 居中
            spaceAfter=20,
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading1',
            fontName=DEFAULT_FONT_NAME,
            fontSize=18,
            leading=22,
            spaceAfter=15,
            spaceBefore=30,
            encoding='utf-8'
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            fontName=DEFAULT_FONT_NAME,
            fontSize=14,
            leading=18,
            spaceAfter=10,
            spaceBefore=20,
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
                fontSize=10,
                alignment=1,  # 居中
                encoding='utf-8'
            )
        ))
        elements.append(Spacer(1, 20))
        
        # 打印调试信息
        try:
            logger.info(f"格式化数据类型: {type(formatted_data)}")
            logger.info(f"格式化数据内容: {json.dumps(formatted_data, ensure_ascii=False, cls=DateTimeEncoder)[:500]}")
            logger.info(f"分析内容: {json.dumps(analysis, ensure_ascii=False, cls=DateTimeEncoder)[:500]}")
        except Exception as e:
            logger.warning(f"序列化数据时出错: {str(e)}")
            # 继续执行，不让序列化错误影响PDF生成
        
        # 添加八字命盘信息（从formatted_data获取，或从baziChart获取）
        elements.append(Paragraph('八字命盘', styles['ChineseHeading1']))
        
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
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONT', (0, 0), (-1, -1), DEFAULT_FONT_NAME),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
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

def generate_pdf(result_data):
    """生成PDF文件
    
    Args:
        result_data: 分析结果数据
        
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
            
        # 检查并记录AI分析结果中的字段
        analysis_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                           'personality', 'education', 'parents', 'social', 'future']
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