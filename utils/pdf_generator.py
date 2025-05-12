import os
import logging
import pdfkit
import time
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_pdf_content(result):
    """
    生成PDF内容的HTML
    
    Args:
        result: 八字分析结果
        
    Returns:
        str: HTML内容
    """
    # 获取基本信息
    gender = "男" if result["gender"] == "male" else "女"
    birth_time = result["birthTime"]
    birth_date = f"{birth_time['year']}年{birth_time['month']}月{birth_time['day']}日 {birth_time['hour']}时"
    lunar_text = "（农历）" if birth_time.get("isLunar", False) else "（公历）"
    
    # 获取八字信息
    bazi_data = result["baziData"]
    year_pillar = f"{bazi_data['yearPillar']['heavenlyStem']}{bazi_data['yearPillar']['earthlyBranch']}"
    month_pillar = f"{bazi_data['monthPillar']['heavenlyStem']}{bazi_data['monthPillar']['earthlyBranch']}"
    day_pillar = f"{bazi_data['dayPillar']['heavenlyStem']}{bazi_data['dayPillar']['earthlyBranch']}"
    hour_pillar = f"{bazi_data['hourPillar']['heavenlyStem']}{bazi_data['hourPillar']['earthlyBranch']}"
    
    # 获取五行分布
    five_elements = bazi_data["fiveElements"]
    
    # 获取AI分析结果
    ai_analysis = result["aiAnalysis"]
    
    # 生成HTML内容
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>八字命理AI人生指导报告</title>
        <style>
            body {{
                font-family: "宋体", serif;
                padding: 20px;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .subtitle {{
                font-size: 18px;
                color: #666;
                margin-bottom: 20px;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .info-table td {{
                padding: 5px;
                border: 1px solid #ccc;
            }}
            .info-table .label {{
                width: 30%;
                background-color: #f0f0f0;
                font-weight: bold;
                text-align: right;
            }}
            .bazi-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                text-align: center;
            }}
            .bazi-table th, .bazi-table td {{
                padding: 8px;
                border: 1px solid #ccc;
            }}
            .bazi-table th {{
                background-color: #f0f0f0;
            }}
            .elements-chart {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
            }}
            .element-bar {{
                width: 18%;
                text-align: center;
            }}
            .element-name {{
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .element-value {{
                height: 20px;
                background-color: #4CAF50;
                margin-bottom: 5px;
            }}
            .analysis {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #999;
                margin-top: 50px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">八字命理AI人生指导报告</div>
            <div class="subtitle">生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}</div>
        </div>
        
        <div class="section">
            <div class="section-title">基本信息</div>
            <table class="info-table">
                <tr>
                    <td class="label">性别：</td>
                    <td>{gender}</td>
                </tr>
                <tr>
                    <td class="label">出生日期：</td>
                    <td>{birth_date} {lunar_text}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">八字命盘</div>
            <table class="bazi-table">
                <tr>
                    <th>年柱</th>
                    <th>月柱</th>
                    <th>日柱</th>
                    <th>时柱</th>
                </tr>
                <tr>
                    <td>{year_pillar}</td>
                    <td>{month_pillar}</td>
                    <td>{day_pillar}</td>
                    <td>{hour_pillar}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">五行分布</div>
            <div class="elements-chart">
                <div class="element-bar">
                    <div class="element-name">金</div>
                    <div class="element-value" style="height: {five_elements['金'] * 20}px; background-color: #FFD700;"></div>
                    <div>{five_elements['金']}</div>
                </div>
                <div class="element-bar">
                    <div class="element-name">木</div>
                    <div class="element-value" style="height: {five_elements['木'] * 20}px; background-color: #228B22;"></div>
                    <div>{five_elements['木']}</div>
                </div>
                <div class="element-bar">
                    <div class="element-name">水</div>
                    <div class="element-value" style="height: {five_elements['水'] * 20}px; background-color: #1E90FF;"></div>
                    <div>{five_elements['水']}</div>
                </div>
                <div class="element-bar">
                    <div class="element-name">火</div>
                    <div class="element-value" style="height: {five_elements['火'] * 20}px; background-color: #FF4500;"></div>
                    <div>{five_elements['火']}</div>
                </div>
                <div class="element-bar">
                    <div class="element-name">土</div>
                    <div class="element-value" style="height: {five_elements['土'] * 20}px; background-color: #8B4513;"></div>
                    <div>{five_elements['土']}</div>
                </div>
            </div>
        </div>
    """
    
    # 添加分析结果
    if "health" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">健康分析</div>
            <div class="analysis">{ai_analysis["health"]}</div>
        </div>
        """
    
    if "wealth" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">财运分析</div>
            <div class="analysis">{ai_analysis["wealth"]}</div>
        </div>
        """
    
    if "career" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">事业分析</div>
            <div class="analysis">{ai_analysis["career"]}</div>
        </div>
        """
    
    if "relationship" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">婚姻感情分析</div>
            <div class="analysis">{ai_analysis["relationship"]}</div>
        </div>
        """
    
    if "children" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">子女分析</div>
            <div class="analysis">{ai_analysis["children"]}</div>
        </div>
        """
    
    if "overall" in ai_analysis:
        html += f"""
        <div class="section">
            <div class="section-title">综合分析</div>
            <div class="analysis">{ai_analysis["overall"]}</div>
        </div>
        """
    
    # 添加页脚
    html += f"""
        <div class="footer">
            本报告由八字命理AI人生指导系统生成，仅供参考。<br>
            报告ID：{result["_id"]}
        </div>
    </body>
    </html>
    """
    
    return html

def save_pdf_to_local(result_id, html_content):
    """
    将PDF保存到本地
    
    Args:
        result_id: 结果ID
        html_content: HTML内容
        
    Returns:
        str: PDF文件路径
    """
    # 创建PDF目录
    pdf_dir = os.path.join(os.getcwd(), 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 生成PDF文件路径
    pdf_path = os.path.join(pdf_dir, f"{result_id}.pdf")
    
    try:
        # 配置wkhtmltopdf选项
        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        
        # 生成PDF
        pdfkit.from_string(html_content, pdf_path, options=options)
        
        return pdf_path
    
    except Exception as e:
        logger.exception(f"生成PDF文件异常: {str(e)}")
        return None

def upload_to_storage(pdf_path, result_id):
    """
    将PDF上传到对象存储
    
    Args:
        pdf_path: PDF文件路径
        result_id: 结果ID
        
    Returns:
        str: PDF文件URL
    """
    # 获取存储配置
    access_key = os.getenv('STORAGE_ACCESS_KEY')
    secret_key = os.getenv('STORAGE_SECRET_KEY')
    bucket = os.getenv('STORAGE_BUCKET')
    region = os.getenv('STORAGE_REGION')
    endpoint = os.getenv('STORAGE_ENDPOINT')
    
    # 如果没有配置存储服务，返回本地URL
    if not all([access_key, secret_key, bucket, region, endpoint]):
        logger.warning("存储服务未配置，返回本地URL")
        return f"/api/bazi/pdf/{result_id}"
    
    try:
        # 这里应该实现对象存储上传逻辑
        # 由于上传逻辑依赖于具体的存储服务（阿里云OSS/腾讯云COS等）
        # 这里只做一个简单的模拟
        
        # 模拟上传成功，返回URL
        return f"https://{bucket}.{endpoint}/{result_id}.pdf"
    
    except Exception as e:
        logger.exception(f"上传PDF文件异常: {str(e)}")
        return None

def generate_pdf(result):
    """
    生成PDF文档
    
    Args:
        result: 八字分析结果
        
    Returns:
        str: PDF文件URL
    """
    try:
        # 生成HTML内容
        html_content = generate_pdf_content(result)
        
        # 保存PDF到本地
        pdf_path = save_pdf_to_local(result["_id"], html_content)
        
        if not pdf_path:
            logger.error(f"保存PDF文件失败: {result['_id']}")
            return None
        
        # 上传PDF到存储服务
        pdf_url = upload_to_storage(pdf_path, result["_id"])
        
        return pdf_url
    
    except Exception as e:
        logger.exception(f"生成PDF异常: {str(e)}")
        return None 