from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel
from utils.bazi_calculator import calculate_bazi, calculate_flowing_years
from utils.ai_service import generate_bazi_analysis
from utils.pdf_generator import generate_pdf
import logging
import requests
import json
from datetime import datetime
from bson.objectid import ObjectId

bazi_bp = Blueprint('bazi', __name__)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def calculate_bazi(birth_date, birth_time, gender):
    """
    计算八字命盘
    
    参数:
        birth_date: 出生日期 (YYYY-MM-DD)
        birth_time: 出生时辰
        gender: 性别 ('male'/'female')
    
    返回:
        dict: 八字命盘数据
    """
    # 实际项目中应该调用专业的八字排盘算法
    # 这里使用简化的示例数据
    
    # 解析出生年月日
    birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day
    
    # 简化的天干地支映射
    heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    elements = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水']
    
    # 简化的八字计算（实际应用中需要更复杂的算法）
    year_stem_index = (year - 4) % 10
    year_branch_index = (year - 4) % 12
    
    month_stem_index = (year_stem_index * 2 + month) % 10
    month_branch_index = (month + 1) % 12
    
    day_stem_index = (day + month * 2 + year % 100 + (year % 100) // 4) % 10
    day_branch_index = (day + month * 2 + year) % 12
    
    # 根据时辰选择地支
    hour_branch_map = {
        '子时 (23:00-01:00)': 0,
        '丑时 (01:00-03:00)': 1,
        '寅时 (03:00-05:00)': 2,
        '卯时 (05:00-07:00)': 3,
        '辰时 (07:00-09:00)': 4,
        '巳时 (09:00-11:00)': 5,
        '午时 (11:00-13:00)': 6,
        '未时 (13:00-15:00)': 7,
        '申时 (15:00-17:00)': 8,
        '酉时 (17:00-19:00)': 9,
        '戌时 (19:00-21:00)': 10,
        '亥时 (21:00-23:00)': 11
    }
    
    hour_branch_index = hour_branch_map.get(birth_time, 0)
    hour_stem_index = (day_stem_index * 2 + hour_branch_index) % 10
    
    # 计算五行分布
    five_elements = {'wood': 0, 'fire': 0, 'earth': 0, 'metal': 0, 'water': 0}
    
    # 添加天干的五行
    element_map = {
        '甲': 'wood', '乙': 'wood',
        '丙': 'fire', '丁': 'fire',
        '戊': 'earth', '己': 'earth',
        '庚': 'metal', '辛': 'metal',
        '壬': 'water', '癸': 'water'
    }
    
    for stem in [heavenly_stems[year_stem_index], 
                 heavenly_stems[month_stem_index], 
                 heavenly_stems[day_stem_index], 
                 heavenly_stems[hour_stem_index]]:
        five_elements[element_map[stem]] += 1
    
    # 计算未来5年的流年
    current_year = datetime.now().year
    flowing_years = []
    
    for i in range(5):
        flow_year = current_year + i
        flow_stem_index = (flow_year - 4) % 10
        flow_branch_index = (flow_year - 4) % 12
        
        flowing_years.append({
            'year': flow_year,
            'heavenlyStem': heavenly_stems[flow_stem_index],
            'earthlyBranch': earthly_branches[flow_branch_index],
            'element': elements[flow_stem_index]
        })
    
    # 生成八字命盘
    bazi_chart = {
        'yearPillar': {
            'heavenlyStem': heavenly_stems[year_stem_index],
            'earthlyBranch': earthly_branches[year_branch_index],
            'element': elements[year_stem_index]
        },
        'monthPillar': {
            'heavenlyStem': heavenly_stems[month_stem_index],
            'earthlyBranch': earthly_branches[month_branch_index],
            'element': elements[month_stem_index]
        },
        'dayPillar': {
            'heavenlyStem': heavenly_stems[day_stem_index],
            'earthlyBranch': earthly_branches[day_branch_index],
            'element': elements[day_stem_index]
        },
        'hourPillar': {
            'heavenlyStem': heavenly_stems[hour_stem_index],
            'earthlyBranch': earthly_branches[hour_branch_index],
            'element': elements[hour_stem_index]
        },
        'fiveElements': five_elements,
        'flowingYears': flowing_years
    }
    
    return bazi_chart

def generate_ai_analysis(bazi_chart, focus_areas, gender):
    """
    调用DeepSeek AI生成八字分析
    
    参数:
        bazi_chart: 八字命盘数据
        focus_areas: 分析侧重点
        gender: 性别
    
    返回:
        dict: AI分析结果
    """
    # 如果没有API密钥，返回模拟数据
    if not DEEPSEEK_API_KEY:
        return {
            'health': '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
            'wealth': '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
            'career': '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
            'relationship': '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
            'children': '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
            'overall': '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
        }
    
    # 构建提示词
    gender_text = "男性" if gender == "male" else "女性"
    
    prompt = f"""
    你是一位专业的八字命理分析师，具有深厚的传统命理学和现代心理学知识。请根据以下八字命盘信息，为这位{gender_text}提供专业的分析和建议。
    
    八字命盘:
    年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
    月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
    日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
    时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}
    
    五行分布:
    木: {bazi_chart['fiveElements']['wood']}
    火: {bazi_chart['fiveElements']['fire']}
    土: {bazi_chart['fiveElements']['earth']}
    金: {bazi_chart['fiveElements']['metal']}
    水: {bazi_chart['fiveElements']['water']}
    
    请特别关注以下方面: {', '.join(focus_areas)}
    
    请用温和积极的语言，提供以下格式的分析:
    1. 健康分析 (200-300字)
    2. 财运分析 (200-300字)
    3. 事业发展 (200-300字)
    4. 婚姻感情 (200-300字)
    5. 子女缘分 (如有此需求) (200-300字)
    6. 综合建议 (300-400字)
    
    分析应基于传统命理学理论，但请避免迷信色彩，注重实用性建议，帮助当事人发挥优势、克服不足。
    """
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的八字命理分析师，需要基于给定的八字信息提供专业分析。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result['choices'][0]['message']['content']
            
            # 解析AI回复，提取各部分分析
            analysis = {}
            
            # 提取健康分析
            if "健康分析" in ai_text:
                health_start = ai_text.find("健康分析")
                next_section = min(
                    [pos for pos in [ai_text.find("财运分析", health_start), 
                                     ai_text.find("事业发展", health_start),
                                     ai_text.find("婚姻感情", health_start),
                                     ai_text.find("子女缘分", health_start),
                                     ai_text.find("综合建议", health_start)] if pos > 0] or [len(ai_text)]
                )
                analysis['health'] = ai_text[health_start:next_section].replace("健康分析", "").strip()
            
            # 提取财运分析
            if "财运分析" in ai_text:
                wealth_start = ai_text.find("财运分析")
                next_section = min(
                    [pos for pos in [ai_text.find("事业发展", wealth_start), 
                                     ai_text.find("婚姻感情", wealth_start),
                                     ai_text.find("子女缘分", wealth_start),
                                     ai_text.find("综合建议", wealth_start)] if pos > 0] or [len(ai_text)]
                )
                analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析", "").strip()
            
            # 提取事业发展
            if "事业发展" in ai_text:
                career_start = ai_text.find("事业发展")
                next_section = min(
                    [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                     ai_text.find("子女缘分", career_start),
                                     ai_text.find("综合建议", career_start)] if pos > 0] or [len(ai_text)]
                )
                analysis['career'] = ai_text[career_start:next_section].replace("事业发展", "").strip()
            
            # 提取婚姻感情
            if "婚姻感情" in ai_text:
                relationship_start = ai_text.find("婚姻感情")
                next_section = min(
                    [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                     ai_text.find("综合建议", relationship_start)] if pos > 0] or [len(ai_text)]
                )
                analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情", "").strip()
            
            # 提取子女缘分
            if "子女缘分" in ai_text:
                children_start = ai_text.find("子女缘分")
                next_section = min(
                    [pos for pos in [ai_text.find("综合建议", children_start)] if pos > 0] or [len(ai_text)]
                )
                analysis['children'] = ai_text[children_start:next_section].replace("子女缘分", "").strip()
            
            # 提取综合建议
            if "综合建议" in ai_text:
                overall_start = ai_text.find("综合建议")
                analysis['overall'] = ai_text[overall_start:].replace("综合建议", "").strip()
            
            return analysis
        
        else:
            logging.error(f"DeepSeek API调用失败: {response.status_code}, {response.text}")
            # 返回默认分析结果
            return {
                'health': '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
                'wealth': '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
                'career': '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
                'relationship': '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
                'children': '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
                'overall': '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
            }
    
    except Exception as e:
        logging.error(f"调用DeepSeek AI时发生错误: {str(e)}")
        # 返回默认分析结果
        return {
            'health': '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
            'wealth': '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
            'career': '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
            'relationship': '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
            'children': '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
            'overall': '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
        }

@bazi_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_bazi():
    """分析八字命盘"""
    user_id = get_jwt_identity()
    data = request.json
    
    result_id = data.get('resultId')
    
    if not result_id:
        return jsonify(code=400, message="缺少结果ID"), 400
    
    # 查找八字分析结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="分析结果不存在"), 404
    
    if result['userId'] != user_id:
        return jsonify(code=403, message="无权访问此分析结果"), 403
    
    # 如果已经分析过，直接返回结果
    if result.get('analyzed'):
        return jsonify(
            code=200,
            message="成功",
            data={
                "baziChart": result['baziChart'],
                "aiAnalysis": result['aiAnalysis']
            }
        )
    
    # 计算八字
    bazi_chart = calculate_bazi(
        result['birthTime'].split(' ')[0],  # 提取日期部分
        result['birthTime'].split(' ')[1],  # 提取时辰部分
        result['gender']
    )
    
    # 调用AI生成分析
    ai_analysis = generate_ai_analysis(
        bazi_chart,
        result['focusAreas'],
        result['gender']
    )
    
    # 更新数据库
    BaziResultModel.update_analysis(
        result_id,
        bazi_chart,
        ai_analysis
    )
    
    return jsonify(
        code=200,
        message="分析完成",
        data={
            "baziChart": bazi_chart,
            "aiAnalysis": ai_analysis
        }
    )

@bazi_bp.route('/result/<result_id>', methods=['GET'])
@jwt_required()
def get_bazi_result(result_id):
    """获取八字分析结果"""
    user_id = get_jwt_identity()
    
    # 查找八字分析结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="分析结果不存在"), 404
    
    if result['userId'] != user_id:
        return jsonify(code=403, message="无权访问此分析结果"), 403
    
    # 如果尚未分析，返回错误
    if not result.get('analyzed'):
        return jsonify(code=400, message="分析尚未完成"), 400
    
    return jsonify(
        code=200,
        message="成功",
        data={
            "baziChart": result['baziChart'],
            "aiAnalysis": result['aiAnalysis'],
            "focusAreas": result['focusAreas']
        }
    )

@bazi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取历史分析记录"""
    user_id = get_jwt_identity()
    
    # 查找用户的所有结果
    results = BaziResultModel.find_by_user(user_id)
    
    # 简化结果数据
    history = []
    for result in results:
        history.append({
            "resultId": result['_id'],
            "createTime": result['createTime'].isoformat(),
            "focusAreas": result['focusAreas'],
            "pdfUrl": result.get('pdfUrl')
        })
    
    return jsonify(
        code=200,
        message="成功",
        data=history
    )

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
@jwt_required()
def get_pdf(result_id):
    """下载PDF文档"""
    user_id = get_jwt_identity()
    
    # 查找结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="结果不存在"), 404
    
    if result['userId'] != user_id:
        return jsonify(code=403, message="无权访问此结果"), 403
    
    # 查找关联的订单
    order = OrderModel.find_by_id(result['orderId'])
    
    if not order or order['status'] != 'paid':
        return jsonify(code=400, message="订单未支付"), 400
    
    if not result.get('pdfUrl'):
        return jsonify(code=404, message="PDF文档不存在"), 404
    
    # 假设PDF文件存储在本地
    pdf_path = os.path.join(os.getcwd(), 'pdfs', f"{result_id}.pdf")
    
    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"八字命理分析_{result_id}.pdf",
            mimetype='application/pdf'
        )
    
    # 如果文件不存在，重定向到URL
    return jsonify(
        code=302,
        message="重定向到PDF",
        data={"url": result['pdfUrl']}
    ) 