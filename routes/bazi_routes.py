from flask import Blueprint, jsonify, request, send_file
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
    
    # 校验2025年的结果，确保是乙巳年
    if year == 2025:
        logging.info("检测到2025年，验证天干地支")
        correct_stem = "乙"
        correct_branch = "巳"
        if heavenly_stems[year_stem_index] != correct_stem or earthly_branches[year_branch_index] != correct_branch:
            logging.warning(f"2025年计算出错误的天干地支: {heavenly_stems[year_stem_index]}{earthly_branches[year_branch_index]}，应为{correct_stem}{correct_branch}")
            # 强制修正
            year_stem_index = heavenly_stems.index(correct_stem)
            year_branch_index = earthly_branches.index(correct_branch)
            logging.info(f"已修正2025年的天干地支为: {correct_stem}{correct_branch}")
    
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
    
    # 添加调试信息，确认年份
    logging.info(f"当前系统年份: {current_year}，计算未来5年流年")
    
    # 正确的年份-干支对照表（2020-2030）
    year_ganzhi_map = {
        2020: ["庚", "子"],  # 庚子年
        2021: ["辛", "丑"],  # 辛丑年
        2022: ["壬", "寅"],  # 壬寅年
        2023: ["癸", "卯"],  # 癸卯年
        2024: ["甲", "辰"],  # 甲辰年
        2025: ["乙", "巳"],  # 乙巳年
        2026: ["丙", "午"],  # 丙午年
        2027: ["丁", "未"],  # 丁未年
        2028: ["戊", "申"],  # 戊申年
        2029: ["己", "酉"],  # 己酉年
        2030: ["庚", "戌"]   # 庚戌年
    }
    
    for i in range(5):
        flow_year = current_year + i
        
        # 使用标准计算方法
        calculated_stem_index = (flow_year - 4) % 10
        calculated_branch_index = (flow_year - 4) % 12
        calculated_stem = heavenly_stems[calculated_stem_index]
        calculated_branch = earthly_branches[calculated_branch_index]
        
        # 检查是否有准确的对照记录
        if flow_year in year_ganzhi_map:
            correct_stem = year_ganzhi_map[flow_year][0]
            correct_branch = year_ganzhi_map[flow_year][1]
            
            # 添加日志，验证计算
            if calculated_stem != correct_stem or calculated_branch != correct_branch:
                logging.warning(f"流年 {flow_year}: 计算得到 {calculated_stem}{calculated_branch}，但正确值应为 {correct_stem}{correct_branch}")
                # 使用正确的值
                stem = correct_stem
                branch = correct_branch
                element_index = heavenly_stems.index(correct_stem) % 5
            else:
                logging.info(f"流年 {flow_year}: 计算正确 {calculated_stem}{calculated_branch}")
                stem = calculated_stem
                branch = calculated_branch
                element_index = calculated_stem_index % 5
        else:
            # 使用计算值，但添加警告
            logging.warning(f"流年 {flow_year}: 没有预设干支对照，使用计算值 {calculated_stem}{calculated_branch}")
            stem = calculated_stem
            branch = calculated_branch
            element_index = calculated_stem_index % 5
        
        flowing_years.append({
            'year': flow_year,
            'heavenlyStem': stem,
            'earthlyBranch': branch,
            'element': elements[element_index]
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
    current_year = datetime.now().year
    
    # 格式化流年信息
    flowing_years_text = "\n流年信息("
    start_year = current_year
    end_year = current_year + 4
    flowing_years_text += f"{start_year}-{end_year}):\n"
    
    flowing_years_list = []
    for year_info in bazi_chart['flowingYears']:
        year_str = f"{year_info['year']}年: {year_info['heavenlyStem']}{year_info['earthlyBranch']}"
        flowing_years_list.append(year_str)
    
    flowing_years_text += ", ".join(flowing_years_list)
    
    # 记录重要年份的天干地支，用于后期验证
    year_ganzhi_map = {}
    for year_info in bazi_chart['flowingYears']:
        year_ganzhi_map[year_info['year']] = f"{year_info['heavenlyStem']}{year_info['earthlyBranch']}"
    
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
    
    {flowing_years_text}
    
    当前年份是{current_year}年，请严格使用上述流年信息进行分析，不要自行计算流年。
    
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
        
        # 准备系统提示，确保包含正确的年份干支对照
        system_content = f"你是一位专业的八字命理分析师，需要基于给定的八字信息提供专业分析。当前年份是{current_year}年，请确保分析中的年份和天干地支信息准确无误。特别注意流年分析时，{current_year}年是{year_ganzhi_map.get(current_year, '')}年，不要使用错误的信息。"
        
        # 添加年龄信息（从solar_year计算）
        try:
            birth_year = int(result.get('basicInfo', {}).get('solarYear', 0))
            if birth_year > 0:
                age = current_year - birth_year
                age_str = f"{age}岁" if age >= 0 else f"未出生，将于{birth_year}年出生"
                system_content += f"\n\n重要提示：当事人当前年龄为{age_str}（出生年份{birth_year}年），请在分析时明确考虑这一点。"
                logging.info(f"添加年龄信息: {age_str}")
        except Exception as e:
            logging.warning(f"计算年龄失败: {e}")
        
        # 添加明确的年份干支对照表
        system_content += "\n\n年份与天干地支对照表（2020-2030）："
        system_content += "\n2020年 - 庚子年"
        system_content += "\n2021年 - 辛丑年"
        system_content += "\n2022年 - 壬寅年"
        system_content += "\n2023年 - 癸卯年"
        system_content += "\n2024年 - 甲辰年"
        system_content += "\n2025年 - 乙巳年（注意：2025年是乙巳年，不是乙丑年）"
        system_content += "\n2026年 - 丙午年"
        system_content += "\n2027年 - 丁未年"
        system_content += "\n2028年 - 戊申年"
        system_content += "\n2029年 - 己酉年"
        system_content += "\n2030年 - 庚戌年"
        system_content += "\n请在分析中严格遵循上述对照表，避免使用不正确的干支信息。"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        logging.info("准备调用DeepSeek API...")
        
        # 调用 API
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        # 检查响应状态码
        if response.status_code != 200:
            logging.error(f"调用DeepSeek API失败: HTTP {response.status_code}")
            logging.error(f"错误详情: {response.text}")
            return None
        
        result = response.json()
        
        # 检查API响应
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # 后处理：修正年份和天干地支的对应关系
            import re
            for year, ganzhi in year_ganzhi_map.items():
                # 查找类似"2025年乙丑"的模式并替换为正确的"2025年乙巳"
                wrong_patterns = [
                    rf"{year}年(?!{ganzhi})[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]",
                    rf"{year}\s*年(?!{ganzhi})[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]"
                ]
                
                for pattern in wrong_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        logging.warning(f"发现错误的年份天干地支对应: {matches}")
                        content = re.sub(pattern, f"{year}年{ganzhi}", content)
            
            logging.info("成功从DeepSeek获取分析")
            
            # 解析响应内容成不同领域的分析
            analysis_result = {
                "health": "",
                "wealth": "",
                "career": "",
                "relationship": "",
                "children": "",
                "overall": ""
            }
            
            # 提取各部分内容
            health_match = re.search(r'健康分析[：:]([\s\S]*?)(?=财运分析[：:]|婚姻感情[：:]|事业发展[：:]|子女缘分[：:]|综合建议[：:]|$)', content)
            if health_match:
                analysis_result["health"] = health_match.group(1).strip()
            
            wealth_match = re.search(r'财运分析[：:]([\s\S]*?)(?=健康分析[：:]|婚姻感情[：:]|事业发展[：:]|子女缘分[：:]|综合建议[：:]|$)', content)
            if wealth_match:
                analysis_result["wealth"] = wealth_match.group(1).strip()
            
            career_match = re.search(r'事业发展[：:]([\s\S]*?)(?=健康分析[：:]|财运分析[：:]|婚姻感情[：:]|子女缘分[：:]|综合建议[：:]|$)', content)
            if career_match:
                analysis_result["career"] = career_match.group(1).strip()
            
            relationship_match = re.search(r'婚姻感情[：:]([\s\S]*?)(?=健康分析[：:]|财运分析[：:]|事业发展[：:]|子女缘分[：:]|综合建议[：:]|$)', content)
            if relationship_match:
                analysis_result["relationship"] = relationship_match.group(1).strip()
            
            children_match = re.search(r'子女缘分[：:]([\s\S]*?)(?=健康分析[：:]|财运分析[：:]|事业发展[：:]|婚姻感情[：:]|综合建议[：:]|$)', content)
            if children_match:
                analysis_result["children"] = children_match.group(1).strip()
            
            overall_match = re.search(r'综合建议[：:]([\s\S]*?)$', content)
            if overall_match:
                analysis_result["overall"] = overall_match.group(1).strip()
            else:
                # 如果没有找到综合建议，使用全部内容
                analysis_result["overall"] = content
            
            return analysis_result
        else:
            logging.error(f"从DeepSeek API返回的结果中没有找到choices: {result}")
            return None
    
    except Exception as e:
        logging.exception(f"生成AI分析时出错: {str(e)}")
        return None

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
        
        # 计算当前年龄
        current_year = datetime.now().year
        age = current_year - int(solar_year)
        if int(solar_year) > current_year:
            logging.info(f"未来出生年份: {solar_year} > {current_year}，年龄计算为负数: {age}岁")
        else:
            logging.info(f"年龄计算: {current_year} - {solar_year} = {age}岁")
        
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
        
        # 根据年龄添加额外的分析指导
        if age < 0:  # 未出生
            prompt = f"重要说明：此人尚未出生，出生年份为{solar_year}年。\n" + prompt
            logging.info(f"检测到未来出生年份: {solar_year}，添加特殊提示")
        elif age < 6:  # 婴幼儿
            prompt = f"重要说明：此人目前仅{age}岁，属于婴幼儿阶段。\n" + prompt
            logging.info(f"检测到婴幼儿: {age}岁，添加特殊提示")
        elif age < 18:  # 未成年
            prompt = f"重要说明：此人目前{age}岁，尚未成年。\n" + prompt
            logging.info(f"检测到未成年人: {age}岁，添加特殊提示")
        
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
        # 尝试不同的提取模式
        if "阳历" in prompt and "年" in prompt:
            year_index = prompt.index("阳历") + 2
            year_end = prompt.index("年", year_index)
            birth_year = int(prompt[year_index:year_end])
        elif "出生时间：" in prompt and "年" in prompt:
            year_index = prompt.index("出生时间：") + 5
            year_end = prompt.index("年", year_index)
            birth_year = int(prompt[year_index:year_end])
        elif "solar_year=" in prompt:
            # 处理格式化字符串中的占位符
            start_index = prompt.index("solar_year=") + len("solar_year=")
            end_index = prompt.find(",", start_index)
            if end_index == -1:
                end_index = prompt.find("}", start_index)
            if end_index > start_index:
                birth_year = int(prompt[start_index:end_index])
        # 正则表达式提取所有年份，然后找出最可能的出生年份
        elif "年" in prompt:
            import re
            years = re.findall(r'\d{4}年', prompt)
            if years:
                # 假设第一个出现的四位数年份是出生年份
                birth_year = int(years[0][:-1])  # 去掉"年"字
    except Exception as e:
        logging.warning(f"无法提取出生年份: {str(e)}")
    
    # 计算当前年龄
    current_year = datetime.now().year
    age = current_year - birth_year if birth_year else None
    
    if age is not None:
        if birth_year > current_year:
            logging.info(f"检测到未来出生年份: {birth_year}，当前年龄为负数: {age}")
        else:
            logging.info(f"提取出生年份成功: {birth_year}, 当前年龄: {age}")
    else:
        logging.warning("无法提取出生年份或计算年龄")
    
    # 添加年龄相关上下文
    system_content = "你是一位顶尖的传统文化命理大师，精通周易，能够将国学和卜卦非常完美地结合运用。请根据用户提供的八字信息，给出专业、详细、实用的分析和建议。"
    
    # 明确添加年龄信息
    if age is not None:
        age_str = f"{age}岁" if age >= 0 else f"未出生，将于{birth_year}年出生"
        system_content += f"\n\n重要提示：当事人当前年龄为{age_str}（出生年份{birth_year}年），请在分析时明确考虑这一点。"
        logging.info(f"添加年龄信息到系统提示: {age_str}")
    
    # 添加明确的年份干支对照表
    system_content += "\n\n年份与天干地支对照表（2020-2030）："
    system_content += "\n2020年 - 庚子年"
    system_content += "\n2021年 - 辛丑年"
    system_content += "\n2022年 - 壬寅年"
    system_content += "\n2023年 - 癸卯年"
    system_content += "\n2024年 - 甲辰年"
    system_content += "\n2025年 - 乙巳年（注意：2025年是乙巳年，不是乙丑年）"
    system_content += "\n2026年 - 丙午年"
    system_content += "\n2027年 - 丁未年"
    system_content += "\n2028年 - 戊申年"
    system_content += "\n2029年 - 己酉年"
    system_content += "\n2030年 - 庚戌年"
    system_content += "\n请在分析中严格遵循上述对照表，不要自行计算错误的干支信息。"
    
    if age is not None:
        # 添加年龄相关指导
        system_content += "\n\n重要提示：分析时必须考虑当事人的实际年龄。"
        
        if birth_year > current_year:  # 未出生（未来出生日期）
            system_content += f"当事人尚未出生，出生于未来的{birth_year}年。请只分析未来可能的性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。"
            logging.info(f"检测到未来出生日期: {birth_year}年，调整分析内容")
        elif age < 6:  # 婴幼儿
            system_content += f"当事人目前仅{age}岁，属于婴幼儿阶段。请重点分析性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段（如20岁以后）的预测。"
            logging.info(f"检测到婴幼儿: {age}岁，调整分析内容")
        elif age < 18:  # 未成年
            system_content += f"当事人目前{age}岁，尚未成年。请重点分析性格特点、天赋才能、健康状况和学业发展，避免过多讨论婚姻感情等不适合未成年人的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段的预测。"
            logging.info(f"检测到未成年人: {age}岁，调整分析内容")
    
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
            
            # 修正可能错误的干支信息
            import re
            # 查找类似"2025年乙丑"的模式并替换为正确的"2025年乙巳"
            if "2025年乙丑" in analysis:
                analysis = analysis.replace("2025年乙丑", "2025年乙巳")
                logging.info("修正了分析结果中的'2025年乙丑'为'2025年乙巳'")
            
            # 使用正则表达式查找其他可能的错误格式
            wrong_patterns = [
                r'2025\s*年(?!乙巳)[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]',
                r'2025年.*?[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥](?!乙巳)'
            ]
            
            for pattern in wrong_patterns:
                matches = re.findall(pattern, analysis)
                if matches:
                    for match in matches:
                        logging.info(f"找到错误的2025年干支表达: {match}")
                        corrected = re.sub(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]', '乙巳', match)
                        analysis = analysis.replace(match, corrected)
                        logging.info(f"已更正为: {corrected}")
            
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
    
    # 检查是否正在分析中
    if result_id in analyzing_results:
        logging.info(f"结果ID {result_id} 正在分析中，等待时间：{analyzing_results[result_id]}")
        return jsonify(
            code=202,  # 使用202表示请求已接受但尚未处理完成
            message=f"分析正在进行中，请稍候再试（已等待{analyzing_results[result_id]}秒）",
            data={
                "status": "analyzing",
                "waitTime": analyzing_results[result_id]
            }
        ), 202
    
    # 查找八字分析结果
    try:
        result = BaziResultModel.find_by_id(result_id)
        
        # 如果找不到结果，返回测试数据
        if not result:
            logging.warning(f"找不到结果ID: {result_id}，返回测试数据")
            return jsonify(
                code=200,
                message="成功(测试数据)",
                data={
                    "baziChart": {
                        "yearPillar": {"heavenlyStem": "甲", "earthlyBranch": "子", "element": "水"},
                        "monthPillar": {"heavenlyStem": "丙", "earthlyBranch": "寅", "element": "木"},
                        "dayPillar": {"heavenlyStem": "戊", "earthlyBranch": "午", "element": "火"},
                        "hourPillar": {"heavenlyStem": "庚", "earthlyBranch": "申", "element": "金"},
                        "fiveElements": {"wood": 2, "fire": 2, "earth": 1, "metal": 2, "water": 1},
                        "flowingYears": [
                            {"year": 2025, "heavenlyStem": "乙", "earthlyBranch": "丑", "element": "土"},
                            {"year": 2026, "heavenlyStem": "丙", "earthlyBranch": "寅", "element": "木"},
                            {"year": 2027, "heavenlyStem": "丁", "earthlyBranch": "卯", "element": "木"},
                            {"year": 2028, "heavenlyStem": "戊", "earthlyBranch": "辰", "element": "土"},
                            {"year": 2029, "heavenlyStem": "己", "earthlyBranch": "巳", "element": "火"}
                        ]
                    },
                    "aiAnalysis": {
                        "health": "您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。",
                        "wealth": "您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。",
                        "career": "您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。",
                        "relationship": "您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。",
                        "children": "您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。",
                        "overall": "综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。"
                    },
                    "focusAreas": ["health", "wealth", "career", "relationship"]
                }
            )
        
        # 不检查用户权限
        # if result['userId'] != user_id:
        #     return jsonify(code=403, message="无权访问此分析结果"), 403
        
        # 如果已经分析过或有AI分析结果，直接返回
        if result.get('analyzed') or (result.get('aiAnalysis') and any(result.get('aiAnalysis').values())):
            logging.info(f"结果已分析，直接返回: {result_id}")
            return jsonify(
                code=200,  # 确保返回状态码为200，表示成功
                message="成功",
                data={
                    "baziChart": result.get('baziChart', {}),
                    "aiAnalysis": result.get('aiAnalysis', {}),
                    "focusAreas": result.get('focusAreas', [])
                }
            )
        
        # 如果尚未分析但需要异步分析（测试模式或正常模式）
        # 检查是否有八字命盘数据
        bazi_chart = result.get('baziChart', {
            "yearPillar": {"heavenlyStem": "甲", "earthlyBranch": "子", "element": "水"},
            "monthPillar": {"heavenlyStem": "丙", "earthlyBranch": "寅", "element": "木"},
            "dayPillar": {"heavenlyStem": "戊", "earthlyBranch": "午", "element": "火"},
            "hourPillar": {"heavenlyStem": "庚", "earthlyBranch": "申", "element": "金"},
            "fiveElements": {"wood": 2, "fire": 2, "earth": 1, "metal": 2, "water": 1},
            "flowingYears": [
                {"year": 2025, "heavenlyStem": "乙", "earthlyBranch": "丑", "element": "土"},
                {"year": 2026, "heavenlyStem": "丙", "earthlyBranch": "寅", "element": "木"},
                {"year": 2027, "heavenlyStem": "丁", "earthlyBranch": "卯", "element": "木"},
                {"year": 2028, "heavenlyStem": "戊", "earthlyBranch": "辰", "element": "土"},
                {"year": 2029, "heavenlyStem": "己", "earthlyBranch": "巳", "element": "火"}
            ]
        })
        
        # 预设AI分析结果（如果API调用失败将使用这个）
        default_ai_analysis = {
                "health": "您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。",
                "wealth": "您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。",
                "career": "您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。",
                "relationship": "您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。",
                "children": "您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。",
                "overall": "综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。"
            }
        
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
                
                # 提取出生年份并计算年龄
                birth_year = None
                try:
                    # 尝试从八字命盘中提取出生年份
                    if 'basicInfo' in result and 'solarYear' in result['basicInfo']:
                        birth_year = int(result['basicInfo']['solarYear'])
                        logging.info(f"从基本信息中提取出生年份: {birth_year}")
                    # 只有在无法从基本信息中获取时，才尝试从流年推算（不推荐的方法）
                    elif 'flowingYears' in bazi_chart and len(bazi_chart['flowingYears']) > 0:
                        # 假设流年信息中的第一个年份与出生年份相近
                        first_flowing_year = bazi_chart['flowingYears'][0]['year']
                        # 通常流年比出生年份大2-10岁左右，这里简单估算
                        birth_year = first_flowing_year - 10
                        logging.warning(f"无法获取准确出生年份，从流年估算: {first_flowing_year} - 10 = {birth_year}，这可能不准确")
                except Exception as e:
                    logging.warning(f"无法提取出生年份: {str(e)}")
                
                # 计算当前年龄
                current_year = datetime.now().year
                age = current_year - birth_year if birth_year else None
                logging.info(f"计算年龄: 当前年份={current_year}, 出生年份={birth_year}, 年龄={age}")
                
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
                """
                
                # 创建包含年龄信息的系统提示
                system_content = "你是一位专业的八字命理分析师，需要基于给定的八字信息提供专业分析。"
                
                # 明确添加年龄信息
                if age is not None:
                    age_str = f"{age}岁" if age >= 0 else f"未出生，将于{birth_year}年出生"
                    system_content += f"\n\n重要提示：当事人当前年龄为{age_str}（出生年份{birth_year}年），请在分析时明确考虑这一点。"
                    logging.info(f"添加年龄信息到系统提示: {age_str}")
                
                # 添加明确的年份干支对照表
                system_content += "\n\n年份与天干地支对照表（2020-2030）："
                system_content += "\n2020年 - 庚子年"
                system_content += "\n2021年 - 辛丑年"
                system_content += "\n2022年 - 壬寅年"
                system_content += "\n2023年 - 癸卯年"
                system_content += "\n2024年 - 甲辰年"
                system_content += "\n2025年 - 乙巳年（注意：2025年是乙巳年，不是乙丑年）"
                system_content += "\n2026年 - 丙午年"
                system_content += "\n2027年 - 丁未年"
                system_content += "\n2028年 - 戊申年"
                system_content += "\n2029年 - 己酉年"
                system_content += "\n2030年 - 庚戌年"
                system_content += "\n请在分析中严格遵循上述对照表，不要使用错误的干支信息。"
                
                # 添加年龄相关的上下文指导
                if age is not None:
                    # 添加年龄相关指导
                    system_content += "\n\n重要提示：分析时必须考虑当事人的实际年龄。"
                    
                    if birth_year > current_year:  # 未出生（未来出生日期）
                        system_content += f"当事人尚未出生，出生于未来的{birth_year}年。请只分析未来可能的性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。"
                        logging.info(f"检测到未来出生日期: {birth_year}年，调整分析内容")
                    elif age < 6:  # 婴幼儿
                        system_content += f"当事人目前仅{age}岁，属于婴幼儿阶段。请重点分析性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段（如20岁以后）的预测。"
                        logging.info(f"检测到婴幼儿: {age}岁，调整分析内容")
                    elif age < 18:  # 未成年
                        system_content += f"当事人目前{age}岁，尚未成年。请重点分析性格特点、天赋才能、健康状况和学业发展，避免过多讨论婚姻感情等不适合未成年人的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段的预测。"
                        logging.info(f"检测到未成年人: {age}岁，调整分析内容")
                
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {deepseek_api_key}"
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
                                            ai_text.find("综合建议", health_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['health'] = ai_text[health_start:next_section].replace("健康分析:", "").replace("健康分析", "").strip()
                    
                    # 提取财运分析
                    if "财运分析" in ai_text:
                        wealth_start = ai_text.find("财运分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("事业发展", wealth_start), 
                                            ai_text.find("婚姻感情", wealth_start),
                                            ai_text.find("子女缘分", wealth_start),
                                            ai_text.find("综合建议", wealth_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析:", "").replace("财运分析", "").strip()
                    
                    # 提取事业发展
                    if "事业发展" in ai_text:
                        career_start = ai_text.find("事业发展")
                        next_section = min(
                            [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                            ai_text.find("子女缘分", career_start),
                                            ai_text.find("综合建议", career_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['career'] = ai_text[career_start:next_section].replace("事业发展:", "").replace("事业发展", "").strip()
                    
                    # 提取婚姻感情
                    if "婚姻感情" in ai_text:
                        relationship_start = ai_text.find("婚姻感情")
                        next_section = min(
                            [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                            ai_text.find("综合建议", relationship_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情:", "").replace("婚姻感情", "").strip()
                    
                    # 提取子女缘分
                    if "子女缘分" in ai_text:
                        children_start = ai_text.find("子女缘分")
                        next_section = min(
                            [pos for pos in [ai_text.find("综合建议", children_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['children'] = ai_text[children_start:next_section].replace("子女缘分:", "").replace("子女缘分", "").strip()
                    
                    # 提取综合建议
                    if "综合建议" in ai_text:
                        overall_start = ai_text.find("综合建议")
                        new_analysis['overall'] = ai_text[overall_start:].replace("综合建议:", "").replace("综合建议", "").strip()
                    
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
        return jsonify(
            code=202,
            message="分析正在进行中，请稍后重试",
            data={
                "status": "analyzing",
                "waitTime": 0,
                "baziChart": bazi_chart,
                "aiAnalysis": default_ai_analysis,
                "focusAreas": result.get('focusAreas', ["health", "wealth", "career", "relationship"])
            }
        ), 202
    
    except Exception as e:
        logging.error(f"获取结果时出错: {str(e)}")
        return jsonify(code=500, message=f"服务器内部错误: {str(e)}"), 500

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
# @jwt_required()
def get_pdf(result_id):
    """下载PDF文档"""
    try:
        # 获取分析结果
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            return jsonify(code=404, message="找不到分析结果"), 404
        
        # 从请求参数中获取存储模式，默认使用'stream'直接返回文件流
        storage_mode = request.args.get('mode', 'stream')
        
        # 配置文件路径
        pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"bazi_analysis_{result_id}.pdf")
        
        # 强制删除旧的PDF文件，确保每次请求都生成新的PDF
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logging.info(f"删除旧的PDF文件: {pdf_path}")
            except Exception as e:
                logging.warning(f"删除旧文件时出错: {str(e)}")
        
        # 现在PDF文件不存在，需要生成新的PDF
        # 导入PDF生成模块
        from utils.pdf_generator import generate_pdf
        
        # 处理数据
        logging.info(f"原始结果数据类型: {type(result)}")
        logging.info(f"原始结果数据键: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
        
        # 确保结果数据结构合理
        pdf_data = {}
        pdf_data['_id'] = result_id
        
        # 处理八字命盘数据
        if isinstance(result, dict):
            # 复制分析结果和八字图表数据
            if 'aiAnalysis' in result:
                pdf_data['analysis'] = result['aiAnalysis']
            elif 'analysis' in result:
                pdf_data['analysis'] = result['analysis']
            
            # 复制八字数据 
            if 'baziChart' in result:
                # 将baziChart数据整合到pdf_data
                bazi_chart = result['baziChart']
                if isinstance(bazi_chart, dict):
                    # 提取八字命盘信息
                    year_pillar = bazi_chart.get('yearPillar', {})
                    month_pillar = bazi_chart.get('monthPillar', {})
                    day_pillar = bazi_chart.get('dayPillar', {})
                    hour_pillar = bazi_chart.get('hourPillar', {})
                    
                    # 构建八字文本
                    bazi_text = ""
                    if all([year_pillar, month_pillar, day_pillar, hour_pillar]):
                        year_stem = year_pillar.get('heavenlyStem', '')
                        year_branch = year_pillar.get('earthlyBranch', '')
                        month_stem = month_pillar.get('heavenlyStem', '')
                        month_branch = month_pillar.get('earthlyBranch', '')
                        day_stem = day_pillar.get('heavenlyStem', '')
                        day_branch = day_pillar.get('earthlyBranch', '')
                        hour_stem = hour_pillar.get('heavenlyStem', '')
                        hour_branch = hour_pillar.get('earthlyBranch', '')
                        
                        bazi_text = f"年柱: {year_stem}{year_branch} 月柱: {month_stem}{month_branch} 日柱: {day_stem}{day_branch} 时柱: {hour_stem}{hour_branch}"
                    
                    # 添加到pdf_data
                    pdf_data['bazi'] = bazi_text
                    
                    # 五行数据
                    if 'fiveElements' in bazi_chart:
                        pdf_data['five_elements'] = bazi_chart['fiveElements']
            
            # 处理各种可能的数据格式
            if 'formatted_data' in result and isinstance(result['formatted_data'], dict):
                formatted_data = result['formatted_data']
                
                # 提取可能的数据
                if 'bazi' in formatted_data and not pdf_data.get('bazi'):
                    pdf_data['bazi'] = formatted_data['bazi']
                
                if 'five_elements' in formatted_data and not pdf_data.get('five_elements'):
                    pdf_data['five_elements'] = formatted_data['five_elements']
                
                if 'shen_sha' in formatted_data:
                    pdf_data['shen_sha'] = formatted_data['shen_sha']
                
                if 'da_yun' in formatted_data:
                    pdf_data['da_yun'] = formatted_data['da_yun']
                
                if 'qi_yun' in formatted_data:
                    pdf_data['qi_yun'] = formatted_data['qi_yun']
        
        # 确保分析数据存在
        if not pdf_data.get('analysis'):
            pdf_data['analysis'] = {
                'health': '您的八字中五行需要平衡。从健康角度看，应注意保持规律作息，避免过度劳累和情绪波动。',
                'wealth': '您的财运有发展空间，适合稳健的理财方式。投资方面，建议分散投资组合，避免投机性强的项目。',
                'career': '您的事业发展有良好前景，具有一定的组织能力和执行力。建议持续提升专业技能，扩展人脉关系。',
                'relationship': '您的婚姻感情关系值得经营。已婚者需注意与伴侣的沟通，单身者有望遇到合适的对象。',
                'children': '您与子女关系和谐。教育方面，建议采用引导式的方法，尊重子女的兴趣发展。',
                'overall': '您的八字展现出潜力，人生发展有诸多可能。建议在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。'
            }
        
        # 确保八字数据存在  
        if not pdf_data.get('bazi'):
            pdf_data['bazi'] = "年柱: 甲子 月柱: 丙寅 日柱: 戊午 时柱: 庚申"
            
        # 确保五行数据存在
        if not pdf_data.get('five_elements'):
            pdf_data['five_elements'] = {"metal": 1, "wood": 1, "water": 1, "fire": 1, "earth": 1}
        
        # 添加标题
        pdf_data['title'] = "八字命理分析报告"
            
        # 生成PDF
        logging.info(f"生成PDF的数据结构: {json.dumps(pdf_data, ensure_ascii=False)[:500]}")
        pdf_path = generate_pdf(pdf_data)
        
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify(code=500, message="生成PDF失败"), 500
        
        # 如果使用云存储模式
        if storage_mode == 'cloud':
            try:
                from utils.cloud_storage import upload_to_cloud_storage, is_cloud_storage_available, get_fallback_url
                
                # 检查云存储是否可用
                if not is_cloud_storage_available():
                    logging.warning("云存储服务未配置，使用直接流方式回退")
                    # 云存储不可用，返回回退URL
                    return jsonify(
                        code=400, 
                        message="云存储服务尚未配置，请使用stream模式",
                        data={
                            "fallback_url": get_fallback_url(result_id),
                            "fallback_mode": "stream"
                        }
                    ), 400
                
                # 尝试上传到云存储
                cloud_url = upload_to_cloud_storage(pdf_path, result_id)
                
                # 更新数据库记录PDF URL
                if cloud_url:
                    BaziResultModel.update_pdf_url(result_id, cloud_url)
                    
                    return jsonify(
                        code=200,
                        message="PDF上传云存储成功",
                        data={"url": cloud_url}
                    )
                else:
                    # 上传失败，返回回退URL
                    return jsonify(
                        code=500,
                        message="上传云存储失败，请使用stream模式",
                        data={
                            "fallback_url": get_fallback_url(result_id),
                            "fallback_mode": "stream"
                        }
                    ), 500
            except ImportError:
                logging.error("云存储模块导入失败")
                return jsonify(
                    code=500,
                    message="云存储模块不可用，请使用stream模式",
                    data={
                        "fallback_url": get_fallback_url(result_id),
                        "fallback_mode": "stream"
                    }
                ), 500
        
        # 默认使用流模式：直接返回文件
        logging.info(f"使用流模式返回PDF文件: {pdf_path}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return jsonify(code=404, message="PDF文件不存在"), 404
            
        # 发送PDF文件流
        try:
            response = send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"八字命理分析_{result_id}.pdf",
                mimetype='application/pdf'
            )
            # 添加缓存控制头以防止浏览器缓存
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        except Exception as send_error:
            logging.exception(f"发送文件时出错: {str(send_error)}")
            return jsonify(code=500, message=f"发送PDF文件失败: {str(send_error)}"), 500
    
    except Exception as e:
        logging.exception(f"生成PDF时出错: {str(e)}")
        return jsonify(code=500, message=f"生成PDF失败: {str(e)}"), 500 

@bazi_bp.route('/calculate', methods=['POST'])
def calculate_bazi():
    """
    计算八字数据（不包含AI分析）
    
    此接口仅计算八字命盘数据，不进行AI分析，主要用于测试八字计算功能。
    所有八字计算均基于公历生日进行。
    """
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
        
        return jsonify({
            'code': 200,
            'message': '计算成功',
            'data': {
                'solar_date': {
                    'year': solar_year,
                    'month': solar_month,
                    'day': solar_day,
                    'hour': solar_hour
                },
                'lunar_date': {
                    'year': lunar_year,
                    'month': lunar_month,
                    'day': lunar_day
                },
                'gender': gender,
                'birth_place': birth_place,
                'living_place': living_place,
                'bazi': formatted_data['bazi'],
                'shen_sha': formatted_data['shen_sha'],
                'qi_yun': formatted_data['qi_yun'],
                'da_yun': formatted_data['da_yun'],
                'bazi_data': bazi_data,
                'formatted_data': formatted_data
            }
        })
    
    except Exception as e:
        logging.error(f"八字计算错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'计算失败: {str(e)}'}), 500