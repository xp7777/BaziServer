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

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 字体全局变量
FONT_REGISTERED = False
DEFAULT_FONT_NAME = 'SimHei'

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
        logger.info(f"格式化数据类型: {type(formatted_data)}")
        logger.info(f"格式化数据内容: {json.dumps(formatted_data, ensure_ascii=False)[:500]}")
        logger.info(f"分析内容: {json.dumps(analysis, ensure_ascii=False)[:500]}")
        
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
                'children': '暂无子女分析数据'
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

def generate_pdf(data):
    """
    生成PDF文件
    
    Args:
        data: 分析数据
        
    Returns:
        str: 文件路径
    """
    try:
        result_id = data.get('_id', '')
        if not result_id:
            result_id = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 确保PDF目录存在
        pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # 创建输出路径
        output_path = os.path.join(pdf_dir, f'bazi_analysis_{result_id}.pdf')
        
        # 生成PDF
        return generate_bazi_pdf(result_id, data, data.get('analysis', {}), title=data.get('title'), output_path=output_path)
    
    except Exception as e:
        logger.error(f"生成PDF失败: {str(e)}")
        return None 