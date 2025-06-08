from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel
from utils.bazi_calculator import calculate_bazi, calculate_flowing_years, get_bazi, format_bazi_analysis
from utils.ai_service import generate_bazi_analysis
# 不直接导入pdf_generator模块，避免WeasyPrint导入错误
import logging
import requests
import json
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
import traceback
import urllib.parse

# 确保DeepSeek API密钥被设置
if not os.environ.get('DEEPSEEK_API_KEY'):
    os.environ['DEEPSEEK_API_KEY'] = 'sk-a70d312fd07b4bce82624bd2373a4db4'
    logging.info("已设置DeepSeek API密钥环境变量")

bazi_bp = Blueprint('bazi', __name__)

# 获取MongoDB客户端和数据库
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-a70d312fd07b4bce82624bd2373a4db4')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

logging.info(f"DeepSeek API密钥前5位: {DEEPSEEK_API_KEY[:5]}...")
logging.info(f"DeepSeek API URL: {DEEPSEEK_API_URL}")

# 存储正在进行分析的结果ID，避免重复分析
analyzing_results = {}

# 基础提示词模板
PROMPT_TEMPLATE = """
你是一位顶尖的传统文化命理大师，你精通周易，能够将国学和卜卦非常完美地结合运用，会六爻起卦，你精通四柱八字，熟读《滴天髓》、《三命通会》、《穷通宝鉴》、《渊海子平》等一系列书，还精通奇门遁甲和风水堪舆等等一系列常见的东方命理玄学技法。

我的出生是（阳历{solar_year}年{solar_month}月{solar_day}日{solar_hour}点），（农历{lunar_year}年{lunar_month}月{lunar_day}日）。性别（{gender}），出生地（{birth_place}），居住地（{living_place}），

我的八字为（{bazi}）
我的八字神煞为： 
{shen_sha}

{qi_yun}
{da_yun}

请按照八字命理的理论和步骤来分析，先帮分析一下我的八字五行旺衰，神煞，大运流年中需要注意的时间和事件，并给我在学业、职场工作、婚姻感情、财富、建康、风水堪舆等方面的人生规划建议。输出结果请用白话文分段论述，既有术语又能让人听懂。
"""

# 追加提示词模板
FOLLOW_UP_TEMPLATES = {
    "婚姻感情": "请你根据该八字情况和流年运势，详细分析一下该八字的婚姻感情情况。",
    "事业财运": "请你根据该八字情况和流年运势，详细分析一下该八字的事业财运情况。",
    "子女情况": "请你根据该八字情况和流年运势，详细分析一下该八字的子女情况。",
    "父母情况": "请你根据该八字情况和流年运势，详细分析一下该八字的父母情况。",
    "身体健康": "请你根据该八字情况和流年运势，详细分析一下该八字的身体健康情况。",
    "学业": "请你根据该八字情况和流年运势，详细分析一下该八字的学业情况。",
    "人际关系": "请你根据该八字情况和流年运势，详细分析一下该八字的人际关系情况。",
    "近五年运势": "请你根据该八字情况和流年运势，详细分析一下该八字的近五年运势情况。"
}

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
    # 准备提示词
    gender_text = "男性" if gender == "male" else "女性"
    birth_year = 2025  # 使用示例年份，实际应从bazi_chart中提取
    
    # 简化的提示词
    prompt = f"""
    请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
    
    八字命盘信息:
    年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
    月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
    日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
    时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}
    
    五行分布:
    金: {bazi_chart['fiveElements']['metal']}
    木: {bazi_chart['fiveElements']['wood']}
    水: {bazi_chart['fiveElements']['water']}
    火: {bazi_chart['fiveElements']['fire']}
    土: {bazi_chart['fiveElements']['earth']}
    
    流年信息(2025-2029):
    {', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in bazi_chart['flowingYears']])}
    
    请按照以下格式提供分析:
    
    健康分析:
    [详细的健康分析，包括体质特点、易发疾病、养生建议等]
    
    财运分析:
    [详细的财运分析，包括财运特点、适合行业、理财建议等]
    
    事业发展:
    [详细的事业分析，包括事业特点、职业方向、发展建议等]
    
    婚姻感情:
    [详细的婚姻感情分析，包括感情特点、相处方式、注意事项等]
    
    子女缘分:
    [详细的子女缘分分析，包括亲子关系、教育方式、注意事项等]
    
    综合建议:
    [综合分析和建议，未来5年的整体运势趋势]
    
    分析应基于传统命理学理论，但请避免迷信色彩，注重实用性建议，帮助当事人发挥优势、克服不足。
    """
    
    try:
        # 检查并记录API密钥情况
        if not DEEPSEEK_API_KEY:
            logging.error("没有找到DeepSeek API密钥，使用默认值")
        else:
            logging.info(f"DeepSeek API密钥前5位: {DEEPSEEK_API_KEY[:5]}...")
        
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
        
        logging.info("准备调用DeepSeek API...")
        logging.info(f"API端点: {DEEPSEEK_API_URL}")
        logging.info(f"请求头: {headers}")
        logging.info(f"请求负载: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        logging.info(f"API响应状态码: {response.status_code}")
        if response.status_code != 200:
            logging.error(f"API错误响应: {response.text[:500]}")
        else:
            logging.info(f"API成功响应(前200字符): {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"成功解析JSON响应: {json.dumps(result, ensure_ascii=False)[:200]}...")
            
            ai_text = result['choices'][0]['message']['content']
            logging.info(f"提取的AI回复(前200字符): {ai_text[:200]}...")
            
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
# 暂时移除JWT验证，用于测试
# @jwt_required()
def analyze_bazi():
    try:
        data = request.json
        
        # 验证必要参数
        required_params = ['solarYear', 'solarMonth', 'solarDay', 'solarHour', 
                          'gender', 'birthPlace', 'livingPlace']
        
        for param in required_params:
            if param not in data:
                return jsonify({'code': 400, 'message': f'缺少参数: {param}'}), 400
        
        # 从请求中获取数据
        solar_year = data['solarYear']
        solar_month = data['solarMonth']
        solar_day = data['solarDay']
        solar_hour = data['solarHour']
        gender = data['gender']
        birth_place = data['birthPlace']
        living_place = data['livingPlace']
        
        # 计算八字
        bazi_data = get_bazi(solar_year, solar_month, solar_day, solar_hour, gender)
        formatted_data = format_bazi_analysis(bazi_data)
        
        # 获取农历日期
        lunar_date = bazi_data.get("lunar_date", {})
        lunar_year = lunar_date.get("year", solar_year)
        lunar_month = lunar_date.get("month", solar_month)
        lunar_day = lunar_date.get("day", solar_day)
        
        # 构建提示词
        prompt = PROMPT_TEMPLATE.format(
            solar_year=solar_year,
            solar_month=solar_month,
            solar_day=solar_day,
            solar_hour=solar_hour,
            lunar_year=lunar_year,
            lunar_month=lunar_month,
            lunar_day=lunar_day,
            gender=gender,
            birth_place=birth_place,
            living_place=living_place,
            bazi=formatted_data['bazi'],
            shen_sha=formatted_data['shen_sha'],
            qi_yun=formatted_data['qi_yun'],
            da_yun=formatted_data['da_yun']
        )
        
        # 调用DeepSeek API进行分析
        analysis = call_deepseek_api(prompt)
        
        # 保存分析结果到数据库
        # 测试模式下使用固定用户ID
        user_id = get_jwt_identity() if request.headers.get('Authorization', '').startswith('Bearer ey') else "test_user_id"
        analysis_id = save_analysis_result(user_id, {
            'basic_info': {
                'solarYear': solar_year,
                'solarMonth': solar_month,
                'solarDay': solar_day,
                'solarHour': solar_hour,
                'gender': gender,
                'birthPlace': birth_place,
                'livingPlace': living_place,
            },
            'bazi_data': bazi_data,
            'formatted_data': formatted_data,
            'analysis': analysis
        })
        
        # 生成PDF
        pdf_path = generate_bazi_pdf(
            analysis_id, 
            formatted_data, 
            analysis, 
            f"{solar_year}年{solar_month}月{solar_day}日 {gender}命 八字分析"
        )
        
        return jsonify({
            'code': 200,
            'message': '分析成功',
            'data': {
                'analysis_id': analysis_id,
                'bazi': formatted_data['bazi'],
                'analysis': analysis,
                'pdf_url': f"/pdfs/{os.path.basename(pdf_path)}" if pdf_path else None
            }
        })
    
    except Exception as e:
        logging.error(f"八字分析错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'分析失败: {str(e)}'}), 500

@bazi_bp.route('/follow-up/<analysis_id>', methods=['POST'])
@jwt_required()
def follow_up_analysis(analysis_id):
    try:
        data = request.json
        topic = data.get('topic')
        
        if not topic or topic not in FOLLOW_UP_TEMPLATES:
            return jsonify({'code': 400, 'message': f'无效的话题: {topic}，可用选项: {", ".join(FOLLOW_UP_TEMPLATES.keys())}'}), 400
        
        # 从数据库获取原始分析
        analysis_doc = db.analyses.find_one({'_id': analysis_id})
        if not analysis_doc:
            return jsonify({'code': 404, 'message': '找不到原始分析记录'}), 404
        
        # 检查权限
        user_id = get_jwt_identity()
        if str(analysis_doc['user_id']) != str(user_id):
            return jsonify({'code': 403, 'message': '无权访问此分析记录'}), 403
        
        # 构建追加提示词
        formatted_data = analysis_doc['formatted_data']
        basic_info = analysis_doc['basic_info']
        
        # 预添加已有的基本信息
        context = f"""
        这是一位出生于阳历{basic_info['solarYear']}年{basic_info['solarMonth']}月{basic_info['solarDay']}日{basic_info['solarHour']}点的{basic_info['gender']}性，
        八字为（{formatted_data['bazi']}）

        {formatted_data['qi_yun']}
        {formatted_data['da_yun']}
        
        前面我们已经进行了基础分析，现在:
        {FOLLOW_UP_TEMPLATES[topic]}
        """
        
        # 调用DeepSeek API进行细化分析
        follow_up_analysis = call_deepseek_api(context)
        
        # 更新数据库中的分析记录
        db.analyses.update_one(
            {'_id': analysis_id},
            {'$set': {f'follow_up.{topic}': follow_up_analysis}}
        )
        
        return jsonify({
            'code': 200,
            'message': '分析成功',
            'data': {
                'analysis_id': analysis_id,
                'topic': topic,
                'analysis': follow_up_analysis
            }
        })
    
    except Exception as e:
        logging.error(f"八字追加分析错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'分析失败: {str(e)}'}), 500

@bazi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    try:
        user_id = get_jwt_identity()
        
        # 从数据库获取用户的分析历史
        analyses = list(db.analyses.find(
            {'user_id': user_id},
            {'basic_info': 1, 'formatted_data': 1, 'created_at': 1}
        ).sort('created_at', -1))
        
        # 格式化输出
        result = []
        for analysis in analyses:
            result.append({
                'analysis_id': str(analysis['_id']),
                'basic_info': analysis['basic_info'],
                'bazi': analysis['formatted_data']['bazi'],
                'created_at': analysis.get('created_at', ''),
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    
    except Exception as e:
        logging.error(f"获取八字分析历史错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500

@bazi_bp.route('/detail/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_detail(analysis_id):
    try:
        # 从数据库获取分析详情
        analysis = db.analyses.find_one({'_id': analysis_id})
        if not analysis:
            return jsonify({'code': 404, 'message': '找不到分析记录'}), 404
        
        # 检查权限
        user_id = get_jwt_identity()
        if str(analysis['user_id']) != str(user_id):
            return jsonify({'code': 403, 'message': '无权访问此分析记录'}), 403
        
        # 格式化输出
        result = {
            'analysis_id': str(analysis['_id']),
            'basic_info': analysis['basic_info'],
            'bazi_data': {
                'bazi': analysis['formatted_data']['bazi'],
                'shen_sha': analysis['formatted_data']['shen_sha'],
                'qi_yun': analysis['formatted_data']['qi_yun'],
                'da_yun': analysis['formatted_data']['da_yun'],
            },
            'analysis': analysis['analysis'],
            'follow_up': analysis.get('follow_up', {}),
            'created_at': analysis.get('created_at', ''),
            'pdf_url': analysis.get('pdf_url')
        }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    
    except Exception as e:
        logging.error(f"获取八字分析详情错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500

def call_deepseek_api(prompt):
    """
    调用DeepSeek API获取八字分析结果
    """
    # 提取出生年份
    birth_year = None
    try:
        if "阳历" in prompt and "年" in prompt:
            year_index = prompt.index("阳历") + 2
            year_end = prompt.index("年", year_index)
            birth_year = int(prompt[year_index:year_end])
    except Exception as e:
        logging.warning(f"无法提取出生年份: {str(e)}")
    
    # 计算当前年龄
    current_year = datetime.now().year
    age = current_year - birth_year if birth_year else None
    
    # 添加年龄相关上下文
    system_content = "你是一位顶尖的传统文化命理大师，精通周易，能够将国学和卜卦非常完美地结合运用。请根据用户提供的八字信息，给出专业、详细、实用的分析和建议。"
    
    if age is not None:
        # 添加年龄相关指导
        system_content += "\n\n重要提示：分析时必须考虑当事人的实际年龄。"
        
        if age < 0:  # 未出生
            system_content += f"\n当事人尚未出生，出生于未来的{birth_year}年。请只分析未来可能的性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。"
        elif age < 6:  # 婴幼儿
            system_content += f"\n当事人目前仅{age}岁，属于婴幼儿阶段。请重点分析性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段（如20岁以后）的预测。"
        elif age < 18:  # 未成年
            system_content += f"\n当事人目前{age}岁，尚未成年。请重点分析性格特点、天赋才能、健康状况和学业发展，避免过多讨论婚姻感情等不适合未成年人的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段的预测。"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # 获取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            analysis = result["choices"][0]["message"]["content"]
            return analysis
        else:
            logging.error(f"DeepSeek API返回格式错误: {result}")
            return "分析生成失败，请稍后再试。"
            
    except requests.exceptions.RequestException as e:
        logging.error(f"DeepSeek API请求失败: {str(e)}")
        return "分析生成失败，API服务暂时不可用。"

def save_analysis_result(user_id, analysis_data):
    """
    保存分析结果到数据库
    """
    from datetime import datetime
    import uuid
    
    # 生成唯一ID
    analysis_id = str(uuid.uuid4())
    
    # 添加创建时间
    analysis_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    analysis_data['user_id'] = user_id
    analysis_data['_id'] = analysis_id
    
    # 保存到数据库
    db.analyses.insert_one(analysis_data)
    
    return analysis_id

@bazi_bp.route('/result/<result_id>', methods=['GET'])
# 暂时移除JWT验证，用于测试
# @jwt_required()
def get_bazi_result(result_id):
    """获取八字分析结果"""
    # 测试环境：不检查用户身份
    # user_id = get_jwt_identity()
    
    logging.info(f"正在获取结果ID: {result_id}")
    
    # 获取URL参数中的出生信息（如果有的话）
    url_birth_date = request.args.get('birthDate')
    url_birth_time = request.args.get('birthTime')
    url_gender = request.args.get('gender')
    
    logging.info(f"URL参数: birthDate={url_birth_date}, birthTime={url_birth_time}, gender={url_gender}")
    
    # 预设AI分析结果（如果API调用失败将使用这个）
    default_ai_analysis = {
        "health": "您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。",
        "wealth": "您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。",
        "career": "您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。",
        "relationship": "您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。",
        "children": "您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。",
        "overall": "综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。",
        "personality": "您性格温和稳重，做事有条理，善于思考和规划。在人际交往中表现得体，能够与各种性格的人相处融洽。",
        "education": "学习能力较强，思维逻辑清晰，适合系统性学习。建议在2025-2026年期间考虑进修或拓展专业技能。",
        "parents": "与父母关系和睦，但可能因工作忙碌而疏于交流。建议定期探望或通话，关注父母健康状况。",
        "social": "社交圈较为稳定，朋友不多但质量高。在2025年有扩展人脉的机会，可能结识对事业有帮助的贵人。",
        "future": "未来五年整体运势向好，2026-2027年是事业和财富积累的关键期，建议把握机会，勇于尝试新的领域。"
    }
    
    # 检查是否正在分析中
    if result_id in analyzing_results:
        logging.info(f"结果ID {result_id} 正在分析中，等待时间：{analyzing_results[result_id]}")
        return jsonify(
            code=202,  # 使用202表示请求已接受但尚未处理完成
            message=f"分析正在进行中，请稍候再试（已等待{analyzing_results[result_id]}秒）",
            data={
                "status": "analyzing",
                "waitTime": analyzing_results[result_id],
                # 正在分析中时，只返回八字命盘数据，不返回完整的默认分析结果
                "baziChart": {},
                "aiAnalysis": {},
                "focusAreas": ["health", "wealth", "career", "relationship"]
            }
        ), 202
    
    # 查找八字分析结果
    try:
        logging.info(f"尝试查找结果ID: {result_id}")
        result = BaziResultModel.find_by_id(result_id)
        
        # 如果找不到结果，返回测试数据
        if not result:
            logging.warning(f"找不到结果ID: {result_id}，返回测试数据")
            
            # 优先使用URL参数中的出生日期，如果没有则使用默认值
            test_date = url_birth_date or "1995-04-01"  # 使用更合理的默认日期，避免使用2025年的日期
            test_time = url_birth_time or "辰时 (07:00-09:00)"
            test_gender = url_gender or "male"
            
            logging.info(f"使用出生信息计算八字: date={test_date}, time={test_time}, gender={test_gender}")
            
            # 调用calculate_bazi函数获取真实计算的八字数据
            from utils.bazi_calculator import calculate_bazi
            test_bazi_chart = calculate_bazi(test_date, test_time, test_gender)
            
            logging.info(f"已计算测试八字数据: {test_bazi_chart}")
            logging.info(f"测试数据年柱: {test_bazi_chart.get('yearPillar', {}).get('heavenlyStem', '无')}+{test_bazi_chart.get('yearPillar', {}).get('earthlyBranch', '无')}")
            
            # 确保测试数据包含出生信息
            test_bazi_chart['birthDate'] = test_date
            test_bazi_chart['birthTime'] = test_time
            test_bazi_chart['gender'] = test_gender
            
            # 返回测试数据时，不返回完整的默认AI分析结果
            # 而是返回空的分析结果，让前端显示"正在分析中"
            empty_analysis = {
                "health": "",
                "wealth": "",
                "career": "",
                "relationship": "",
                "children": "",
                "overall": "",
                "personality": "",
                "education": "",
                "parents": "",
                "social": "",
                "future": ""
            }
            
            response_data = {
                "baziChart": test_bazi_chart,
                "aiAnalysis": empty_analysis,
                "focusAreas": ["health", "wealth", "career", "relationship"]
            }
            
            logging.info(f"返回给前端的测试数据: {json.dumps(response_data, ensure_ascii=False)[:1000]}")
            
            return jsonify(
                code=200,
                message="成功(测试数据)",
                data=response_data
            )
        
        logging.info(f"已找到结果ID: {result_id}")
        
        # 不检查用户权限
        # if result['userId'] != user_id:
        #     return jsonify(code=403, message="无权访问此分析结果"), 403
        
        # 从数据库中获取出生信息
        db_birth_date = result.get('birthDate')
        db_birth_time = result.get('birthTime')
        db_gender = result.get('gender')
        
        logging.info(f"数据库中的出生信息: birth_date={db_birth_date}, birth_time={db_birth_time}, gender={db_gender}")
        
        # 优先使用数据库中的出生信息，其次是URL参数，最后是默认值
        birth_date = db_birth_date or url_birth_date or "1995-04-01"
        birth_time = db_birth_time or url_birth_time or "辰时 (07:00-09:00)"
        gender = db_gender or url_gender or "male"
        
        logging.info(f"最终使用的出生信息: birth_date={birth_date}, birth_time={birth_time}, gender={gender}")
        
        # 如果数据库中的出生信息与URL参数不一致，更新数据库中的出生信息
        if url_birth_date and db_birth_date != url_birth_date or url_birth_time and db_birth_time != url_birth_time or url_gender and db_gender != url_gender:
            logging.info(f"更新数据库中的出生信息: birth_date={url_birth_date}, birth_time={url_birth_time}, gender={url_gender}")
            BaziResultModel.update_birth_info(result_id, url_birth_date, url_birth_time, url_gender)
        
        # 如果已经分析过或有AI分析结果，直接返回
        if result.get('analyzed') or (result.get('aiAnalysis') and any(result.get('aiAnalysis').values())):
            logging.info(f"结果已分析，直接返回: {result_id}")
            
            # 确保八字命盘数据包含神煞、大运和流年信息
            bazi_chart = result.get('baziChart', {})
            
            # 记录年柱信息
            year_pillar = bazi_chart.get('yearPillar', {})
            logging.info(f"数据库中的年柱信息: 天干={year_pillar.get('heavenlyStem', '无')}, 地支={year_pillar.get('earthlyBranch', '无')}")
            
            # 检查是否需要重新计算八字
            need_recalculate = False
            
            # 如果数据库中的八字数据不完整或与实际出生日期不匹配，则需要重新计算
            if not bazi_chart:
                need_recalculate = True
                logging.info(f"需要重新计算八字: 数据库中没有八字数据")
            elif 'birthDate' not in bazi_chart or bazi_chart.get('birthDate') != birth_date:
                need_recalculate = True
                logging.info(f"需要重新计算八字: 数据库中的出生日期({bazi_chart.get('birthDate')})与实际出生日期({birth_date})不匹配")
            elif 'birthTime' not in bazi_chart or bazi_chart.get('birthTime') != birth_time:
                need_recalculate = True
                logging.info(f"需要重新计算八字: 数据库中的出生时间({bazi_chart.get('birthTime')})与实际出生时间({birth_time})不匹配")
            elif 'gender' not in bazi_chart or bazi_chart.get('gender') != gender:
                need_recalculate = True
                logging.info(f"需要重新计算八字: 数据库中的性别({bazi_chart.get('gender')})与实际性别({gender})不匹配")
            
            if need_recalculate:
                logging.info(f"重新计算八字命盘数据: birth_date={birth_date}, birth_time={birth_time}, gender={gender}")
                
                # 使用calculate_bazi计算八字命盘数据
                from utils.bazi_calculator import calculate_bazi
                bazi_chart = calculate_bazi(birth_date, birth_time, gender)
                
                # 确保八字数据包含出生信息
                bazi_chart['birthDate'] = birth_date
                bazi_chart['birthTime'] = birth_time
                bazi_chart['gender'] = gender
                
                # 记录计算出的年柱信息
                year_pillar = bazi_chart.get('yearPillar', {})
                logging.info(f"重新计算的年柱信息: 天干={year_pillar.get('heavenlyStem', '无')}, 地支={year_pillar.get('earthlyBranch', '无')}")
                
                # 更新数据库中的八字数据
                BaziResultModel.update_bazi_data(result_id, bazi_chart)
                logging.info(f"已更新数据库中的八字数据: {result_id}")
            
            # 记录神煞、大运和流年信息是否存在
            logging.info(f"神煞信息是否存在: {'shenSha' in bazi_chart}")
            logging.info(f"大运信息是否存在: {'daYun' in bazi_chart}")
            logging.info(f"流年信息是否存在: {'flowingYears' in bazi_chart}")
            
            # 如果计算结果中没有这些信息，记录警告
            if 'shenSha' not in bazi_chart:
                logging.warning("计算结果中缺少神煞信息")
            
            if 'daYun' not in bazi_chart:
                logging.warning("计算结果中缺少大运信息")
            
            if 'flowingYears' not in bazi_chart or not bazi_chart['flowingYears']:
                logging.warning("计算结果中缺少流年信息")
            
            # 检查大运信息是否与出生日期匹配
            if 'daYun' in bazi_chart and bazi_chart['daYun'] and 'data' in bazi_chart['daYun'] and bazi_chart['daYun']['data']:
                # 获取出生年份
                birth_year = None
                if birth_date:
                    try:
                        birth_year = int(birth_date.split('-')[0])
                        logging.info(f"出生年份: {birth_year}")
                    except Exception as e:
                        logging.warning(f"无法解析出生年份: {birth_date}, 错误: {str(e)}")
                
                # 获取大运起始年龄
                start_age = None
                if 'startAge' in bazi_chart['daYun']:
                    start_age = bazi_chart['daYun']['startAge']
                    logging.info(f"大运起始年龄: {start_age}")
                
                # 如果出生年份和大运起始年龄都存在，检查大运信息是否正确
                if birth_year and start_age is not None:
                    # 计算大运起始年份
                    start_year = birth_year + start_age
                    logging.info(f"大运起始年份: {start_year}")
                    
                    # 检查大运数据是否包含起始年份
                    first_da_yun = bazi_chart['daYun']['data'][0]
                    if 'year' in first_da_yun:
                        first_year = first_da_yun['year']
                        logging.info(f"大运数据中的第一个年份: {first_year}")
                        
                        # 如果大运起始年份与数据中的第一个年份不一致，尝试修正
                        if first_year != start_year:
                            logging.warning(f"大运起始年份({start_year})与数据中的第一个年份({first_year})不一致，尝试修正")
                            
                            # 重新计算八字命盘数据
                            bazi_chart = calculate_bazi(birth_date, birth_time, gender)
                            
                            # 确保八字数据包含出生信息
                            bazi_chart['birthDate'] = birth_date
                            bazi_chart['birthTime'] = birth_time
                            bazi_chart['gender'] = gender
                            
                            # 更新数据库中的八字数据
                            BaziResultModel.update_bazi_data(result_id, bazi_chart)
                            logging.info(f"已更新数据库中的八字数据: {result_id}")
            
            # 检查流年信息是否从当前年份开始
            if 'flowingYears' in bazi_chart and bazi_chart['flowingYears'] and len(bazi_chart['flowingYears']) > 0:
                # 获取当前年份
                current_year = datetime.now().year
                logging.info(f"当前年份: {current_year}")
                
                # 获取流年数据中的第一个年份
                first_flowing_year = bazi_chart['flowingYears'][0]
                if 'year' in first_flowing_year:
                    first_year = first_flowing_year['year']
                    logging.info(f"流年数据中的第一个年份: {first_year}")
                    
                    # 如果流年起始年份与当前年份不一致，尝试修正
                    if first_year != current_year:
                        logging.warning(f"流年起始年份({first_year})与当前年份({current_year})不一致，尝试修正")
                        
                        # 重新计算八字命盘数据
                        bazi_chart = calculate_bazi(birth_date, birth_time, gender)
                        
                        # 确保八字数据包含出生信息
                        bazi_chart['birthDate'] = birth_date
                        bazi_chart['birthTime'] = birth_time
                        bazi_chart['gender'] = gender
                        
                        # 更新数据库中的八字数据
                        BaziResultModel.update_bazi_data(result_id, bazi_chart)
                        logging.info(f"已更新数据库中的八字数据: {result_id}")
            
            # 确保添加出生信息到八字数据中
            bazi_chart['birthDate'] = birth_date
            bazi_chart['birthTime'] = birth_time
            bazi_chart['gender'] = gender
            
            response_data = {
                "baziChart": bazi_chart,
                "aiAnalysis": result.get('aiAnalysis', {}),
                "focusAreas": result.get('focusAreas', [])
            }
            
            logging.info(f"返回给前端的数据: {json.dumps(response_data, ensure_ascii=False)[:1000]}")
            
            # 返回实际的AI分析结果，而不是默认值
            return jsonify(
                code=200,
                message="成功",
                data=response_data
            )
        
        # 如果尚未分析但需要异步分析（测试模式或正常模式）
        logging.info(f"开始计算八字，出生日期: {birth_date}, 时辰: {birth_time}, 性别: {gender}")
        
        # 使用calculate_bazi计算八字命盘数据
        from utils.bazi_calculator import calculate_bazi
        bazi_chart = calculate_bazi(birth_date, birth_time, gender)
        
        # 确保添加出生信息到八字数据中
        bazi_chart['birthDate'] = birth_date
        bazi_chart['birthTime'] = birth_time
        bazi_chart['gender'] = gender
        
        # 记录计算出的年柱信息
        year_pillar = bazi_chart.get('yearPillar', {})
        logging.info(f"计算得到的年柱信息: 天干={year_pillar.get('heavenlyStem', '无')}, 地支={year_pillar.get('earthlyBranch', '无')}")
        logging.info(f"已计算八字数据: {json.dumps(bazi_chart, ensure_ascii=False)[:1000]}")
        
        # 检查DeepSeek API密钥并启动异步分析
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_api_key and result_id not in analyzing_results:
            logging.info(f"开始异步分析结果: {result_id}")
        
        # 记录开始分析的时间
        analyzing_results[result_id] = 0
        
        # 在单独的线程中进行AI分析
        import threading
        def perform_analysis():
            try:
                from time import sleep, time
                start_time = time()
                
                # 更新等待时间
                def update_wait_time():
                    while result_id in analyzing_results:
                        current_time = time()
                        analyzing_results[result_id] = int(current_time - start_time)
                        sleep(1)
                
                # 启动计时线程
                timer_thread = threading.Thread(target=update_wait_time)
                timer_thread.daemon = True
                timer_thread.start()
                
                # 构建性别信息
                gender = result.get('gender', 'male')
                gender_text = "男性" if gender == "male" else "女性"
                
                # 构建提示词
                prompt = f"""
                请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
                
                八字命盘信息:
                年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
                月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
                日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
                时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}
                
                五行分布:
                金: {bazi_chart['fiveElements']['metal']}
                木: {bazi_chart['fiveElements']['wood']}
                水: {bazi_chart['fiveElements']['water']}
                火: {bazi_chart['fiveElements']['fire']}
                土: {bazi_chart['fiveElements']['earth']}
                
                流年信息(2025-2029):
                {', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in bazi_chart['flowingYears']])}
                
                请按照以下格式提供分析:
                
                健康分析:
                [详细的健康分析，包括体质特点、易发疾病、养生建议等]
                
                财运分析:
                [详细的财运分析，包括财运特点、适合行业、理财建议等]
                
                事业发展:
                [详细的事业分析，包括事业特点、职业方向、发展建议等]
                
                婚姻感情:
                [详细的婚姻感情分析，包括感情特点、相处方式、注意事项等]
                
                子女缘分:
                [详细的子女缘分分析，包括亲子关系、教育方式、注意事项等]
                
                综合建议:
                [综合分析和建议，未来5年的整体运势趋势]
                
                性格特点:
                [详细的性格特点分析，包括先天性格、后天影响等]
                
                学业分析:
                [详细的学业分析，包括学习能力、适合学科、学习建议等]
                
                父母情况:
                [详细的父母情况分析，包括与父母关系、孝道建议等]
                
                人际关系:
                [详细的人际关系分析，包括社交特点、人缘情况、交友建议等]
                
                近五年运势:
                [详细的近五年运势分析，包括每年的重点关注事项等]
                """
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {deepseek_api_key}"
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
                
                logging.info("准备调用DeepSeek API...")
                response = requests.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                logging.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result_data = response.json()
                    ai_text = result_data['choices'][0]['message']['content']
                    logging.info(f"成功获取DeepSeek API响应: {ai_text[:100]}...")
                    
                    # 解析AI回复，提取各部分分析
                    new_analysis = {}
                    
                    # 提取健康分析
                    if "健康分析" in ai_text:
                        health_start = ai_text.find("健康分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("财运分析", health_start), 
                                            ai_text.find("事业发展", health_start),
                                            ai_text.find("婚姻感情", health_start),
                                            ai_text.find("子女缘分", health_start),
                                            ai_text.find("综合建议", health_start),
                                            ai_text.find("性格特点", health_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['health'] = ai_text[health_start:next_section].replace("健康分析:", "").replace("健康分析", "").strip()
                    
                    # 提取财运分析
                    if "财运分析" in ai_text:
                        wealth_start = ai_text.find("财运分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("事业发展", wealth_start), 
                                            ai_text.find("婚姻感情", wealth_start),
                                            ai_text.find("子女缘分", wealth_start),
                                            ai_text.find("综合建议", wealth_start),
                                            ai_text.find("性格特点", wealth_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析:", "").replace("财运分析", "").strip()
                    
                    # 提取事业发展
                    if "事业发展" in ai_text:
                        career_start = ai_text.find("事业发展")
                        next_section = min(
                            [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                            ai_text.find("子女缘分", career_start),
                                            ai_text.find("综合建议", career_start),
                                            ai_text.find("性格特点", career_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['career'] = ai_text[career_start:next_section].replace("事业发展:", "").replace("事业发展", "").strip()
                    
                    # 提取婚姻感情
                    if "婚姻感情" in ai_text:
                        relationship_start = ai_text.find("婚姻感情")
                        next_section = min(
                            [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                            ai_text.find("综合建议", relationship_start),
                                            ai_text.find("性格特点", relationship_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情:", "").replace("婚姻感情", "").strip()
                    
                    # 提取子女缘分
                    if "子女缘分" in ai_text:
                        children_start = ai_text.find("子女缘分")
                        next_section = min(
                            [pos for pos in [ai_text.find("综合建议", children_start),
                                            ai_text.find("性格特点", children_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['children'] = ai_text[children_start:next_section].replace("子女缘分:", "").replace("子女缘分", "").strip()
                    
                    # 提取综合建议
                    if "综合建议" in ai_text:
                        overall_start = ai_text.find("综合建议")
                        next_section = min(
                            [pos for pos in [ai_text.find("性格特点", overall_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['overall'] = ai_text[overall_start:next_section].replace("综合建议:", "").replace("综合建议", "").strip()
                    
                    # 提取性格特点
                    if "性格特点" in ai_text:
                        personality_start = ai_text.find("性格特点")
                        next_section = min(
                            [pos for pos in [ai_text.find("学业分析", personality_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['personality'] = ai_text[personality_start:next_section].replace("性格特点:", "").replace("性格特点", "").strip()
                    
                    # 提取学业分析
                    if "学业分析" in ai_text:
                        education_start = ai_text.find("学业分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("父母情况", education_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['education'] = ai_text[education_start:next_section].replace("学业分析:", "").replace("学业分析", "").strip()
                    
                    # 提取父母情况
                    if "父母情况" in ai_text:
                        parents_start = ai_text.find("父母情况")
                        next_section = min(
                            [pos for pos in [ai_text.find("人际关系", parents_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['parents'] = ai_text[parents_start:next_section].replace("父母情况:", "").replace("父母情况", "").strip()
                    
                    # 提取人际关系
                    if "人际关系" in ai_text:
                        social_start = ai_text.find("人际关系")
                        next_section = min(
                            [pos for pos in [ai_text.find("近五年运势", social_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['social'] = ai_text[social_start:next_section].replace("人际关系:", "").replace("人际关系", "").strip()
                    
                    # 提取近五年运势
                    if "近五年运势" in ai_text:
                        future_start = ai_text.find("近五年运势")
                        new_analysis['future'] = ai_text[future_start:].replace("近五年运势:", "").replace("近五年运势", "").strip()
                    
                    logging.info("DeepSeek API调用成功，使用真实分析结果")
                    
                    # 使用真实分析结果更新数据库
                    BaziResultModel.update_analysis(
                        result_id,
                        bazi_chart,
                        new_analysis
                    )
                else:
                    logging.error(f"调用DeepSeek API失败: {response.status_code}, {response.text[:200]}")
                    logging.info("使用默认分析数据更新")
                    # 使用默认分析结果更新数据库
                    BaziResultModel.update_analysis(
                        result_id,
                        bazi_chart,
                        default_ai_analysis
                    )
            
            except Exception as e:
                logging.error(f"调用DeepSeek API出错: {str(e)}")
                logging.info("使用默认分析数据更新")
                # 使用默认分析结果更新数据库
                BaziResultModel.update_analysis(
                    result_id,
                    bazi_chart,
                    default_ai_analysis
                )
            finally:
                # 分析完成，移除记录
                if result_id in analyzing_results:
                    del analyzing_results[result_id]
        
        # 仅启动一次分析线程
        analysis_thread = threading.Thread(target=perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # 返回正在分析的状态和临时数据
        # 不返回完整的默认AI分析结果，而是返回空的分析结果
        empty_analysis = {
            "health": "分析中...",
            "wealth": "分析中...",
            "career": "分析中...",
            "relationship": "分析中...",
            "children": "分析中...",
            "overall": "分析中...",
            "personality": "分析中...",
            "education": "分析中...",
            "parents": "分析中...",
            "social": "分析中...",
            "future": "分析中..."
        }
        
        response_data = {
                "status": "analyzing",
                "waitTime": 0,
                "baziChart": bazi_chart,
            "aiAnalysis": empty_analysis,
                "focusAreas": result.get('focusAreas', ["health", "wealth", "career", "relationship"])
            }
        
        logging.info(f"返回给前端的分析中数据: {json.dumps(response_data, ensure_ascii=False)[:1000]}")
        
        return jsonify(
            code=202,
            message="分析正在进行中，请稍后重试",
            data=response_data
        ), 202
    
    except Exception as e:
        logging.error(f"获取结果时出错: {str(e)}")
        return jsonify(code=500, message=f"服务器内部错误: {str(e)}"), 500

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
# @jwt_required()
def get_pdf(result_id):
    """下载PDF文档 - 始终返回文件流，适应前后端分离部署"""
    logging.info(f"请求下载PDF，结果ID: {result_id}")
    
    # 查找结果
    result = BaziResultModel.find_by_id(result_id)
    
    # 如果找不到结果，且ID以RES开头，尝试查找相关订单ID
    if not result and result_id.startswith('RES'):
        logging.info(f"以RES开头的ID未找到直接匹配，尝试查找相关订单: {result_id}")
        order_id = result_id.replace('RES', '')
        try:
            # 尝试通过订单ID查找分析结果
            from models.order_model import OrderModel
            order = OrderModel.find_by_id(order_id)
            if order and order.get('resultId'):
                logging.info(f"通过订单找到了相关结果ID: {order.get('resultId')}")
                result = BaziResultModel.find_by_id(order.get('resultId'))
            else:
                # 尝试通过订单ID直接查找结果
                result = BaziResultModel.find_by_order_id(order_id)
                if result:
                    logging.info(f"通过订单ID直接查找到了结果")
        except Exception as e:
            logging.error(f"尝试通过订单ID查找结果时出错: {str(e)}")
    
    if not result:
        logging.error(f"找不到结果ID: {result_id}")
        return jsonify(code=404, message="结果不存在"), 404
    
    # 记录找到的结果ID
    actual_result_id = str(result.get('_id'))
    logging.info(f"找到结果，实际ID: {actual_result_id}")
    
    # 检查是否是微信环境
    is_weixin = False
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'micromessenger' in user_agent:
        is_weixin = True
        logging.info("检测到微信环境")
    
    # 检查是否已有PDF URL
    if result.get('pdfUrl'):
        # 检查本地PDF文件是否存在
        pdf_path = os.path.join(os.getcwd(), 'pdfs', f"{result_id}.pdf")
        
        if os.path.exists(pdf_path):
            # 微信环境中，优先返回JSON格式的URL
            if is_weixin:
                # 生成一个临时的可访问URL (在实际部署中，应该使用真实的域名和路径)
                server_url = request.host_url.rstrip('/')
                pdf_url = f"{server_url}/pdfs/{result_id}.pdf"
                
                return jsonify(
                    code=200,
                    message="PDF生成成功",
                    data={"url": pdf_url}
                )
            
            # 非微信环境，直接发送文件
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"八字命理分析_{result_id}.pdf",
                mimetype='application/pdf'
            )
        
        # 如果文件不存在，但有URL，返回URL
        return jsonify(
                code=200,
            message="重定向到PDF",
            data={"url": result['pdfUrl']}
            )
    
    # 如果没有PDF URL，先生成PDF
    try:
        # 安全地导入PDF生成器，放在函数内部而非模块顶部
        from utils.pdf_generator import generate_pdf
        
        # 确保结果中包含必要的数据
        if not result.get('baziChart') or not result.get('aiAnalysis'):
            return jsonify(code=400, message="分析数据不完整，无法生成PDF"), 400
        
        # 生成PDF
        logging.info(f"开始生成PDF: {result_id}")
        pdf_url = generate_pdf(result)
        
        if not pdf_url:
            return jsonify(code=500, message="生成PDF失败"), 500
        
        # 更新数据库记录PDF URL
        BaziResultModel.update_pdf_url(result_id, pdf_url)
        
        # 确定文件路径和类型
        if pdf_url.endswith('.pdf'):
            pdf_path = os.path.join(os.getcwd(), 'static', 'pdfs', f"bazi_analysis_{actual_result_id}.pdf")
            mime_type = 'application/pdf'
            file_ext = 'pdf'
        else:
            pdf_path = os.path.join(os.getcwd(), 'static', 'pdfs', f"bazi_analysis_{actual_result_id}.html")
            mime_type = 'text/html'
            file_ext = 'html'
        
        # 如果文件不存在，尝试使用pdf_url中的路径
        if not os.path.exists(pdf_path) and pdf_url:
            if pdf_url.startswith('/'):
                # 相对路径，转换为绝对路径
                pdf_path = os.path.join(os.getcwd(), pdf_url.lstrip('/'))
            else:
                # 可能是完整路径
                pdf_path = pdf_url
        
        logging.info(f"PDF文件路径: {pdf_path}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            logging.error(f"PDF文件不存在: {pdf_path}")
            return jsonify(code=404, message="PDF文件不存在或生成失败"), 404
        
        # 验证文件是否有效
        try:
            with open(pdf_path, 'rb') as f:
                file_size = os.path.getsize(pdf_path)
                logging.info(f"文件大小: {file_size} 字节")
                
                if file_size == 0:
                    logging.error("文件大小为0，无效文件")
                    return jsonify(code=500, message="生成的文件无效(大小为0)"), 500
                
                # 检查文件头
                if pdf_path.endswith('.pdf'):
                    header = f.read(5)
                    if not header.startswith(b'%PDF-'):
                        logging.error(f"无效的PDF文件头: {header}")
                        return jsonify(code=500, message="生成的PDF文件格式无效"), 500
                    f.seek(0)  # 重置文件指针
        except Exception as e:
            logging.error(f"验证文件时出错: {str(e)}")
            return jsonify(code=500, message=f"验证文件失败: {str(e)}"), 500
        
        # 始终以文件流方式返回，适应前后端分离部署
        try:
            logging.info(f"以文件流方式返回: {pdf_path}")
            response = send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"八字命理分析_{result_id}.{file_ext}",
                mimetype=mime_type
            )
            
            # 添加跨域头，支持前后端分离
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            # 添加缓存控制头，避免浏览器缓存
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            # 确保Content-Disposition头部正确设置，避免多次下载弹窗
            # 使用ASCII文件名，避免Unicode编码错误
            ascii_filename = f"bazi_analysis_{result_id}.{file_ext}"
            # 对中文文件名进行URL编码，以便在header中使用
            encoded_filename = urllib.parse.quote(f"八字命理分析_{result_id}.{file_ext}")
            # 使用RFC 5987编码格式
            response.headers['Content-Disposition'] = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            
            logging.info("成功发送文件流响应")
            return response
        except Exception as e:
            logging.error(f"返回文件流失败: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify(code=500, message=f"文件下载失败: {str(e)}"), 500
    
    except Exception as e:
        logging.error(f"生成PDF时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=f"生成PDF失败: {str(e)}"), 500

# 添加追问分析相关的API
@bazi_bp.route('/followup/<result_id>/<area>', methods=['GET'])
def get_followup_analysis(result_id, area):
    """
    获取追问分析结果
    """
    try:
        current_app.logger.info(f"获取追问分析，结果ID: {result_id}，领域: {area}")
        
        # 验证追问领域
        valid_areas = ["marriage", "career", "children", "parents", "health", 
                      "education", "relationship", "fiveYears"]
        
        if area not in valid_areas:
            return jsonify({
                "code": 400,
                "message": "无效的追问领域"
            }), 400
        
        # 查找结果记录
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            return jsonify({
                "code": 404,
                "message": "找不到对应的结果记录"
            }), 404
        
        # 检查是否已经支付过该领域
        followups = result.get('followups', {})
        if area in followups and followups[area]:
            return jsonify({
                "code": 200,
                "message": "获取追问分析成功",
                "data": {
                    "area": area,
                    "analysis": followups[area]
                }
            })
        
        # 如果没有分析结果，生成新的分析
        # 这里应该调用DeepSeek API生成分析结果
        # 为了演示，我们使用一些示例分析
        analysis = generate_sample_analysis(area, result)
        
        # 更新结果记录，保存分析结果
        BaziResultModel.update_followup(result_id, area, analysis)
        
        return jsonify({
            "code": 200,
            "message": "获取追问分析成功",
            "data": {
                "area": area,
                "analysis": analysis
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取追问分析出错: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

@bazi_bp.route('/followup/list/<result_id>', methods=['GET'])
def list_followups(result_id):
    """
    获取已支付的追问列表
    """
    try:
        current_app.logger.info(f"获取已支付的追问列表，结果ID: {result_id}")
        
        # 查找结果记录
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            return jsonify({
                "code": 404,
                "message": "找不到对应的结果记录"
            }), 404
        
        # 查找该结果关联的所有已支付追问订单
        followup_orders = OrderModel.find_by_result_id_and_type(result_id, "followup")
        
        # 提取已支付的追问领域
        paid_followups = []
        for order in followup_orders:
            if order.get('status') == 'paid':
                paid_followups.append({
                    "area": order.get('area'),
                    "orderId": order.get('_id'),
                    "payTime": order.get('payTime')
                })
        
        return jsonify({
            "code": 200,
            "message": "获取已支付的追问列表成功",
            "data": {
                "followups": paid_followups
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取已支付的追问列表出错: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

def generate_sample_analysis(area, result):
    """
    生成示例分析结果
    实际应用中，这里应该调用DeepSeek API生成分析结果
    """
    # 获取八字和流年信息
    bazi_chart = result.get('baziChart', {})
    birth_date = result.get('birthDate', '')
    birth_time = result.get('birthTime', '')
    gender = result.get('gender', 'male')
    
    # 根据不同领域生成不同的分析
    if area == 'marriage':
        return f"""根据您的八字命盘分析，您的婚姻宫位在{bazi_chart.get('dayPillar', {}).get('earthlyBranch', '未知')}宫，
与{bazi_chart.get('monthPillar', {}).get('earthlyBranch', '未知')}宫形成{get_random_relation()}关系。

从命理角度看，您的感情线较为{get_random_trait()}，在感情中{get_random_role()}。
您适合的伴侣类型是{get_random_partner_type()}的人，最佳婚配年龄在{get_random_age()}岁左右。

未来两年内，您的婚姻运势{get_random_fortune()}，需要注意{get_random_advice()}。"""
    
    elif area == 'career':
        return f"""分析您的八字，事业宫位在{bazi_chart.get('hourPillar', {}).get('earthlyBranch', '未知')}宫，
与财帛宫{bazi_chart.get('yearPillar', {}).get('earthlyBranch', '未知')}形成{get_random_relation()}关系。

您的事业发展方向适合{get_random_career()}行业，具有{get_random_talent()}的天赋。
在工作中，您{get_random_work_style()}，这是您的优势。

近期事业运势{get_random_fortune()}，特别是在{get_random_month()}月有重要机遇。
建议您{get_random_career_advice()}，以提升事业发展。"""
    
    elif area == 'children':
        return f"""根据您的八字，子女宫在{bazi_chart.get('monthPillar', {}).get('earthlyBranch', '未知')}位，
显示您与子女的缘分{get_random_fortune()}。

您适合生育的年龄在{get_random_age()}岁左右，最佳的生育季节是{get_random_season()}。
您的子女未来发展方向可能偏向{get_random_career()}，具有{get_random_talent()}的特质。

在教育子女方面，建议您{get_random_education_advice()}，这样有助于孩子的成长。"""
    
    elif area == 'parents':
        return f"""您的八字中，父母宫在{bazi_chart.get('yearPillar', {}).get('earthlyBranch', '未知')}位，
与您的日柱{bazi_chart.get('dayPillar', {}).get('earthlyBranch', '未知')}形成{get_random_relation()}关系。

您与父亲的关系偏向{get_random_relationship()}，与母亲的关系偏向{get_random_relationship()}。
在家庭中，您扮演着{get_random_role()}的角色。

建议您在与父母相处时{get_random_family_advice()}，这样能够增进彼此感情。"""
    
    elif area == 'health':
        return f"""从您的八字看，健康宫位在{bazi_chart.get('dayPillar', {}).get('earthlyBranch', '未知')}宫，
五行属性为{bazi_chart.get('dayPillar', {}).get('element', '未知')}。

您需要特别注意{get_random_body_part()}的保养，易受{get_random_season()}季节的影响。
建议您平时多{get_random_health_advice()}，避免{get_random_health_warning()}。

在饮食上，宜多食用{get_random_food()}，忌食{get_random_food()}。
定期体检是必要的，特别是{get_random_age()}岁后要更加注重健康管理。"""
    
    elif area == 'education':
        return f"""分析您的八字，学业宫在{bazi_chart.get('hourPillar', {}).get('earthlyBranch', '未知')}位，
与才智宫{bazi_chart.get('monthPillar', {}).get('earthlyBranch', '未知')}形成{get_random_relation()}关系。

您的学习能力偏向{get_random_learning_style()}，在{get_random_subject()}领域有特殊天赋。
学习中的优势是{get_random_talent()}，需要克服的弱点是{get_random_weakness()}。

建议您采用{get_random_study_method()}的学习方法，这样能够取得更好的成绩。
未来适合的发展方向是{get_random_career()}领域。"""
    
    elif area == 'relationship':
        return f"""您的八字中，人际关系宫在{bazi_chart.get('hourPillar', {}).get('earthlyBranch', '未知')}位，
与财帛宫{bazi_chart.get('yearPillar', {}).get('earthlyBranch', '未知')}形成{get_random_relation()}关系。

在人际交往中，您通常表现得{get_random_social_style()}，给人{get_random_impression()}的印象。
您适合与{get_random_friend_type()}类型的人交往，这类人能够与您形成良好的互补关系。

在社交场合，建议您{get_random_social_advice()}，这样能够拓展人脉资源。
工作中的人际关系将对您的事业发展起到{get_random_fortune()}的作用。"""
    
    elif area == 'fiveYears':
        current_year = int(birth_date.split('-')[0])
        years_analysis = ""
        
        for i in range(5):
            year = current_year + i
            years_analysis += f"\n{year}年：整体运势{get_random_fortune()}，"
            years_analysis += f"事业方面{get_random_fortune()}，"
            years_analysis += f"财运{get_random_fortune()}，"
            years_analysis += f"感情方面{get_random_fortune()}。"
            years_analysis += f"建议您{get_random_advice()}。"
        
        return f"""根据您的八字和流年运势，未来五年的总体发展趋势如下：{years_analysis}

特别提醒：在{current_year + 2}年{get_random_month()}月前后，您将面临一个重要的{get_random_event()}，
这可能会对您的{get_random_area()}产生深远影响。

建议您在未来五年中，重点关注{get_random_area()}和{get_random_area()}两个方面，
并且{get_random_advice()}，这样能够趋吉避凶，创造更好的未来。"""
    
    else:
        return "暂无该领域的分析结果。"

# 辅助函数，用于生成随机分析内容
def get_random_relation():
    relations = ["相生", "相克", "比和", "刑冲", "合化", "三合", "六合", "相害"]
    import random
    return random.choice(relations)

def get_random_trait():
    traits = ["温和", "强势", "敏感", "理性", "浪漫", "务实", "多变", "稳定"]
    import random
    return random.choice(traits)

def get_random_role():
    roles = ["扮演主导角色", "倾向于包容对方", "注重平等交流", "善于倾听", "喜欢表达自己", "追求和谐"]
    import random
    return random.choice(roles)

def get_random_partner_type():
    types = ["温柔体贴", "聪明能干", "性格开朗", "稳重可靠", "有创造力", "思想深刻", "善解人意"]
    import random
    return random.choice(types)

def get_random_age():
    import random
    return random.randint(25, 35)

def get_random_fortune():
    fortunes = ["上升", "稳定", "波动", "下降", "先抑后扬", "先扬后抑", "平稳发展", "有重大突破"]
    import random
    return random.choice(fortunes)

def get_random_advice():
    advice = ["调整心态", "加强沟通", "提升专业能力", "拓展人脉", "注重健康", "平衡工作与生活", "增加自信"]
    import random
    return random.choice(advice)

def get_random_career():
    careers = ["金融", "科技", "教育", "医疗", "艺术", "传媒", "服务业", "制造业", "咨询", "法律"]
    import random
    return random.choice(careers)

def get_random_talent():
    talents = ["领导", "创新", "分析", "沟通", "执行", "艺术", "逻辑思维", "语言", "数学", "空间想象"]
    import random
    return random.choice(talents)

def get_random_work_style():
    styles = ["注重细节", "善于全局把握", "高效执行", "创新思考", "团队协作", "独立工作", "善于沟通"]
    import random
    return random.choice(styles)

def get_random_month():
    import random
    return random.randint(1, 12)

def get_random_season():
    seasons = ["春季", "夏季", "秋季", "冬季"]
    import random
    return random.choice(seasons)

def get_random_education_advice():
    advice = ["多鼓励少批评", "注重培养独立思考能力", "关注情商发展", "平衡学习与娱乐", "尊重孩子的兴趣"]
    import random
    return random.choice(advice)

def get_random_relationship():
    relationships = ["融洽", "疏远", "理性", "情感丰富", "互相尊重", "有代沟", "互相支持"]
    import random
    return random.choice(relationships)

def get_random_family_advice():
    advice = ["多表达感谢", "定期团聚", "尊重彼此的隐私", "坦诚沟通", "共同参与活动", "理解包容"]
    import random
    return random.choice(advice)

def get_random_body_part():
    parts = ["心脏", "肺部", "肝脏", "肾脏", "脾胃", "骨骼", "神经系统", "内分泌系统", "免疫系统"]
    import random
    return random.choice(parts)

def get_random_health_advice():
    advice = ["运动", "保持规律作息", "均衡饮食", "减轻压力", "定期体检", "保持良好心态", "充足睡眠"]
    import random
    return random.choice(advice)

def get_random_health_warning():
    warnings = ["熬夜", "过度劳累", "情绪波动", "饮食不规律", "缺乏运动", "过度饮酒", "吸烟"]
    import random
    return random.choice(warnings)

def get_random_food():
    foods = ["绿叶蔬菜", "高蛋白食物", "全谷类", "新鲜水果", "坚果", "海鲜", "红肉", "乳制品", "辛辣食物"]
    import random
    return random.choice(foods)

def get_random_learning_style():
    styles = ["视觉学习", "听觉学习", "实践学习", "逻辑分析", "社交学习", "独立学习", "创造性思考"]
    import random
    return random.choice(styles)

def get_random_subject():
    subjects = ["数学", "语言", "科学", "艺术", "历史", "哲学", "工程", "医学", "法律", "经济"]
    import random
    return random.choice(subjects)

def get_random_weakness():
    weaknesses = ["注意力不集中", "缺乏耐心", "拖延症", "过度完美主义", "缺乏自信", "学习方法不当"]
    import random
    return random.choice(weaknesses)

def get_random_study_method():
    methods = ["番茄工作法", "思维导图", "SQ3R阅读法", "费曼学习法", "间隔重复", "主动回忆", "教学相长"]
    import random
    return random.choice(methods)

def get_random_social_style():
    styles = ["外向活泼", "内敛沉稳", "幽默风趣", "真诚热情", "理性冷静", "敏感体贴", "独立自主"]
    import random
    return random.choice(styles)

def get_random_impression():
    impressions = ["可靠", "聪明", "友善", "神秘", "有趣", "专业", "亲切", "强势", "温和"]
    import random
    return random.choice(impressions)

def get_random_friend_type():
    types = ["思想开放", "性格稳重", "乐观向上", "才华横溢", "踏实可靠", "富有同情心", "有责任感"]
    import random
    return random.choice(types)

def get_random_social_advice():
    advice = ["主动交流", "倾听他人", "展示真实自我", "参加社交活动", "培养共同兴趣", "学会换位思考"]
    import random
    return random.choice(advice)

def get_random_event():
    events = ["职业机会", "感情变化", "财务转机", "健康挑战", "人际关系调整", "居住变动", "学习机会"]
    import random
    return random.choice(events)

def get_random_area():
    areas = ["事业", "财运", "感情", "健康", "家庭", "学业", "人际关系", "心灵成长"]
    import random
    return random.choice(areas)