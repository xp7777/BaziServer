import os
import json
import logging
import requests
import openai
import time
import datetime

logger = logging.getLogger(__name__)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_prompt_template(focus_area):
    """
    根据关注领域获取提示词模板
    
    Args:
        focus_area: 关注领域
        
    Returns:
        str: 提示词模板
    """
    templates = {
        "health": """
        请作为一名专业的命理师，基于下面的八字命盘数据，分析此人的健康状况和潜在健康风险。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从五行平衡的角度分析其健康状况，包括：
        1. 整体健康状况评估
        2. 潜在的健康风险点
        3. 容易出现的健康问题
        4. 对应的养生建议和预防措施
        5. 大运流年中需要特别注意的健康变化
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的健康建议。
        """,
        
        "wealth": """
        请作为一名专业的命理师，基于下面的八字命盘数据，分析此人的财运和发财机遇。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从八字命理的角度分析其财运状况，包括：
        1. 整体财运评估
        2. 财富来源和积累方式
        3. 适合从事的财富相关行业
        4. 大运流年中的财运高峰期
        5. 提升财运的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的财富建议。
        """,
        
        "career": """
        请作为一名专业的命理师，基于下面的八字命盘数据，分析此人的事业发展和职业选择。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从八字命理的角度分析其事业状况，包括：
        1. 事业发展总体趋势
        2. 适合从事的行业和职业
        3. 事业发展中的优势和障碍
        4. 大运流年中的事业机遇期
        5. 提升事业运势的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的事业发展建议。
        """,
        
        "relationship": """
        请作为一名专业的命理师，基于下面的八字命盘数据，分析此人的婚姻感情状况。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从八字命理的角度分析其婚姻感情状况，包括：
        1. 感情和婚姻总体运势
        2. 适合的伴侣类型和特征
        3. 婚姻中可能面临的挑战
        4. 大运流年中的婚恋机遇期
        5. 提升感情运势的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的感情婚姻建议。
        """,
        
        "children": """
        请作为一名专业的命理师，基于下面的八字命盘数据，分析此人的子女缘分和家庭关系。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从八字命理的角度分析其子女缘分，包括：
        1. 子女缘分总体评估
        2. 可能的子女数量和性别
        3. 与子女的关系特点
        4. 教育子女的适合方式
        5. 提升家庭和谐的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的家庭关系建议。
        """,
        
        "overall": """
        请作为一名专业的命理师，基于下面的八字命盘数据，进行全面的人生分析和指导。
        
        八字信息：
        性别：{gender}
        出生日期：{birth_year}年{birth_month}月{birth_day}日{birth_hour}时
        
        八字命盘：
        年柱：{year_pillar_stem}{year_pillar_branch}
        月柱：{month_pillar_stem}{month_pillar_branch}
        日柱：{day_pillar_stem}{day_pillar_branch}
        时柱：{hour_pillar_stem}{hour_pillar_branch}
        
        五行分布：
        金：{metal}
        木：{wood}
        水：{water}
        火：{fire}
        土：{earth}
        
        请从八字命理的角度进行全面分析，包括：
        1. 性格特点和天赋才能
        2. 人生总体运势和发展方向
        3. 健康、财富、事业、婚姻的整体评估
        4. 大运流年中的关键转折点
        5. 提升整体运势的综合建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的人生指导建议。
        """
    }
    
    return templates.get(focus_area, templates["overall"])

def format_prompt(bazi_data, gender, birth_time, focus_area):
    """
    格式化提示词
    
    Args:
        bazi_data: 八字数据
        gender: 性别
        birth_time: 出生时间
        focus_area: 关注领域
        
    Returns:
        str: 格式化后的提示词
    """
    # 获取提示词模板
    template = get_prompt_template(focus_area)
    
    # 格式化性别
    gender_text = "男" if gender == "male" else "女"
    
    # 格式化生日
    birth_year = birth_time["year"]
    birth_month = birth_time["month"]
    birth_day = birth_time["day"]
    birth_hour = birth_time["hour"]
    
    # 格式化八字
    year_pillar_stem = bazi_data["yearPillar"]["heavenlyStem"]
    year_pillar_branch = bazi_data["yearPillar"]["earthlyBranch"]
    month_pillar_stem = bazi_data["monthPillar"]["heavenlyStem"]
    month_pillar_branch = bazi_data["monthPillar"]["earthlyBranch"]
    day_pillar_stem = bazi_data["dayPillar"]["heavenlyStem"]
    day_pillar_branch = bazi_data["dayPillar"]["earthlyBranch"]
    hour_pillar_stem = bazi_data["hourPillar"]["heavenlyStem"]
    hour_pillar_branch = bazi_data["hourPillar"]["earthlyBranch"]
    
    # 格式化五行
    five_elements = bazi_data["fiveElements"]
    metal = five_elements.get("金", five_elements.get("metal", 0))
    wood = five_elements.get("木", five_elements.get("wood", 0))
    water = five_elements.get("水", five_elements.get("water", 0))
    fire = five_elements.get("火", five_elements.get("fire", 0))
    earth = five_elements.get("土", five_elements.get("earth", 0))
    
    # 生成流年信息
    flowing_years_text = ""
    if "flowingYears" in bazi_data and bazi_data["flowingYears"]:
        flowing_years_list = []
        for year_data in bazi_data["flowingYears"]:
            year = year_data.get("year", "")
            stem = year_data.get("heavenlyStem", "")
            branch = year_data.get("earthlyBranch", "")
            flowing_years_list.append(f"{year}年: {stem}{branch}")
        flowing_years_text = "流年信息：\n" + "\n".join(flowing_years_list)
    
    # 填充模板
    prompt = template.format(
        gender=gender_text,
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        year_pillar_stem=year_pillar_stem,
        year_pillar_branch=year_pillar_branch,
        month_pillar_stem=month_pillar_stem,
        month_pillar_branch=month_pillar_branch,
        day_pillar_stem=day_pillar_stem,
        day_pillar_branch=day_pillar_branch,
        hour_pillar_stem=hour_pillar_stem,
        hour_pillar_branch=hour_pillar_branch,
        metal=metal,
        wood=wood,
        water=water,
        fire=fire,
        earth=earth
    )
    
    # 添加流年信息
    if flowing_years_text:
        prompt += "\n\n" + flowing_years_text
    
    # 添加当前年份提示，确保AI使用正确的信息
    current_year = datetime.datetime.now().year
    prompt += f"\n\n重要说明：当前年份是{current_year}年。请使用上述提供的流年信息进行分析，不要自行计算流年。"
    
    return prompt

def call_openai_api(prompt):
    """
    调用OpenAI API
    
    Args:
        prompt: 提示词
        
    Returns:
        str: AI响应
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位专业的命理分析师，精通八字命理理论。请根据用户提供的八字信息，给出专业、详细、实用的分析和建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.exception(f"调用OpenAI API异常: {str(e)}")
        return None

def call_deepseek_api(prompt):
    """
    调用DeepSeek API
    
    Args:
        prompt: 提示词
        
    Returns:
        str: AI响应
    """
    try:
        # 提取出生年份
        birth_year = None
        try:
            # 尝试多种方式提取出生年份
            # 使用正则表达式提取出生年份，更加可靠
            import re
            # 首先尝试匹配"阳历xxxx年"格式
            year_match = re.search(r'阳历(\d{4})年', prompt)
            if year_match:
                birth_year = int(year_match.group(1))
                logging.info(f"从'阳历xxxx年'格式提取出生年份: {birth_year}")
            # 尝试匹配{birth_year}年或{solar_year}年格式
            elif re.search(r'出生日期：(\d{4})年', prompt):
                year_match = re.search(r'出生日期：(\d{4})年', prompt)
                birth_year = int(year_match.group(1))
                logging.info(f"从'出生日期：xxxx年'格式提取出生年份: {birth_year}")
            # 尝试匹配其他格式的年份
            elif "solar_year=" in prompt or "birth_year=" in prompt:
                # 处理格式化字符串中的占位符
                for prefix in ["solar_year=", "birth_year="]:
                    if prefix in prompt:
                        start_index = prompt.index(prefix) + len(prefix)
                        end_index = prompt.find(",", start_index)
                        if end_index == -1:
                            end_index = prompt.find("}", start_index)
                        if end_index > start_index:
                            birth_year = int(prompt[start_index:end_index])
                            logging.info(f"从'{prefix}'格式提取出生年份: {birth_year}")
                            break
            # 最后尝试匹配任何4位数年份
            elif re.search(r'\d{4}年', prompt):
                year_matches = re.findall(r'(\d{4})年', prompt)
                if year_matches:
                    # 假设第一个出现的年份是出生年份
                    birth_year = int(year_matches[0])
                    logging.info(f"从正则匹配提取可能的出生年份: {birth_year}")
        except Exception as e:
            logging.warning(f"无法提取出生年份: {e}")
        
        # 计算当前年龄
        current_year = datetime.datetime.now().year
        age = current_year - birth_year if birth_year else None
        
        # 记录年龄信息
        if age is not None:
            if birth_year > current_year:
                logging.info(f"检测到未来出生年份: {birth_year}，当前年龄将为负数: {age}")
            else:
                logging.info(f"出生年份: {birth_year}, 当前年龄: {age}岁")
        
        # 提取流年信息
        flowing_years = []
        try:
            if "流年信息：" in prompt:
                import re
                # 匹配格式如 "2025年: 乙巳"
                flowing_year_pattern = r'(\d{4})年: ([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])'
                flowing_years = re.findall(flowing_year_pattern, prompt)
                logging.info(f"提取到流年信息: {flowing_years}")
        except Exception as e:
            logging.warning(f"提取流年信息失败: {e}")
        
        # 添加年龄相关上下文
        system_prompt = "你是一位专业的命理分析师，精通八字命理理论。请根据用户提供的八字信息，给出专业、详细、实用的分析和建议。"
        
        # 添加当前年份信息
        system_prompt += f"\n\n重要说明：当前年份是{current_year}年，请确保在分析中使用正确的年份信息。"
        
        # 添加明确的年份干支对照表
        system_prompt += "\n\n年份与天干地支对照表（2020-2030）："
        system_prompt += "\n2020年 - 庚子年"
        system_prompt += "\n2021年 - 辛丑年"
        system_prompt += "\n2022年 - 壬寅年"
        system_prompt += "\n2023年 - 癸卯年"
        system_prompt += "\n2024年 - 甲辰年"
        system_prompt += "\n2025年 - 乙巳年（注意：2025年是乙巳年，不是乙丑年）"
        system_prompt += "\n2026年 - 丙午年"
        system_prompt += "\n2027年 - 丁未年"
        system_prompt += "\n2028年 - 戊申年"
        system_prompt += "\n2029年 - 己酉年"
        system_prompt += "\n2030年 - 庚戌年"
        system_prompt += "\n请在分析中严格遵循上述对照表。"
        
        # 添加流年提示
        if flowing_years:
            system_prompt += f"\n\n在分析中，请严格使用提示中提供的流年信息，不要自行计算流年。特别注意{current_year}年的天干地支。"
        
        # 明确添加年龄信息
        if age is not None:
            age_str = f"{age}岁" if age >= 0 else f"未出生，将于{birth_year}年出生"
            system_prompt += f"\n\n重要提示：当事人当前年龄为{age_str}（出生年份{birth_year}年），请在分析时明确考虑这一点。"
            
            # 添加年龄相关指导
            system_prompt += "\n\n分析时必须考虑当事人的实际年龄。"
            
            if birth_year > current_year:  # 未出生（未来出生日期）
                system_prompt += f"当事人尚未出生，出生于未来的{birth_year}年。请只分析未来可能的性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。"
                logging.info(f"检测到未来出生日期: {birth_year}年，调整分析内容")
            elif age < 6:  # 婴幼儿
                system_prompt += f"当事人目前仅{age}岁，属于婴幼儿阶段。请重点分析性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段（如20岁以后）的预测。"
                logging.info(f"检测到婴幼儿: {age}岁，调整分析内容")
            elif age < 18:  # 未成年
                system_prompt += f"当事人目前{age}岁，尚未成年。请重点分析性格特点、天赋才能、健康状况和学业发展，避免过多讨论婚姻感情等不适合未成年人的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段的预测。"
                logging.info(f"检测到未成年人: {age}岁，调整分析内容")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # 检查内容中是否有错误的流年信息，如果有则修正
            if flowing_years and current_year:
                for year_str, stem, branch in flowing_years:
                    year = int(year_str)
                    if year == current_year:
                        correct_ganzhi = f"{stem}{branch}"
                        wrong_patterns = [
                            rf"{year}年[^{stem}{branch}]{{2}}",  # 2025年乙丑
                            rf"{year}.*?[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥](?!{stem}{branch})"  # 2025...乙丑
                        ]
                        import re
                        for pattern in wrong_patterns:
                            content = re.sub(pattern, f"{year}年{correct_ganzhi}", content)
            
            return content
        else:
            logger.error(f"DeepSeek API响应异常: {result}")
            return None
    
    except Exception as e:
        logger.exception(f"调用DeepSeek API异常: {str(e)}")
        return None

def generate_bazi_analysis(bazi_data, gender, birth_time, focus_area):
    """
    生成八字分析
    
    Args:
        bazi_data: 八字数据
        gender: 性别
        birth_time: 出生时间
        focus_area: 关注领域
        
    Returns:
        str: 分析结果
    """
    try:
        # 格式化提示词
        prompt = format_prompt(bazi_data, gender, birth_time, focus_area)
        
        # 调用API
        if DEEPSEEK_API_KEY:
            logger.info("使用DeepSeek API生成分析")
            analysis = call_deepseek_api(prompt)
        else:
            logger.info("使用OpenAI API生成分析")
            analysis = call_openai_api(prompt)
            
        return analysis
    except Exception as e:
        logger.error(f"生成八字分析失败: {str(e)}")
        return "分析生成失败，请稍后再试。"

def analyze_bazi_with_ai(bazi_data):
    """
    使用AI分析八字命盘
    
    Args:
        bazi_data: 八字数据，包含出生信息和命盘数据
        
    Returns:
        str: 分析结果文本
    """
    try:
        logger.info("开始使用AI分析八字命盘")
        
        # 提取必要信息
        gender = bazi_data.get('gender', 'male')
        birth_date = bazi_data.get('birthDate', '')
        birth_time = bazi_data.get('birthTime', '')
        
        # 记录分析的基本信息
        logger.info(f"分析信息: 性别={gender}, 出生日期={birth_date}, 出生时间={birth_time}")
        
        # 构建性别信息
        gender_text = "男性" if gender == "male" else "女性"
        
        # 构建提示词
        prompt = f"""
        请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
        
        八字命盘信息:
        年柱: {bazi_data['yearPillar']['heavenlyStem']}{bazi_data['yearPillar']['earthlyBranch']}
        月柱: {bazi_data['monthPillar']['heavenlyStem']}{bazi_data['monthPillar']['earthlyBranch']}
        日柱: {bazi_data['dayPillar']['heavenlyStem']}{bazi_data['dayPillar']['earthlyBranch']}
        时柱: {bazi_data['hourPillar']['heavenlyStem']}{bazi_data['hourPillar']['earthlyBranch']}
        
        五行分布:
        金: {bazi_data['fiveElements']['metal']}
        木: {bazi_data['fiveElements']['wood']}
        水: {bazi_data['fiveElements']['water']}
        火: {bazi_data['fiveElements']['fire']}
        土: {bazi_data['fiveElements']['earth']}
        
        流年信息:
        {', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in bazi_data.get('flowingYears', [])])}
        
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
        
        # 调用API
        if DEEPSEEK_API_KEY:
            logger.info("使用DeepSeek API生成分析")
            analysis = call_deepseek_api(prompt)
        else:
            logger.info("使用OpenAI API生成分析")
            analysis = call_openai_api(prompt)
            
        logger.info(f"AI分析完成，结果长度: {len(analysis) if analysis else 0}")
        return analysis
    except Exception as e:
        logger.error(f"AI分析八字命盘失败: {str(e)}")
        return "分析生成失败，请稍后再试。"

def extract_analysis_from_text(ai_text):
    """
    从AI分析文本中提取各部分分析
    
    Args:
        ai_text: AI生成的分析文本
        
    Returns:
        dict: 各部分分析结果
    """
    try:
        logger.info("开始从AI文本中提取分析结果")
        
        # 初始化分析结果字典
        analysis = {
            "health": "暂无健康分析数据",
            "wealth": "暂无财运分析数据",
            "career": "暂无事业分析数据",
            "relationship": "暂无婚姻感情分析数据",
            "children": "暂无子女分析数据",
            "overall": "暂无综合分析数据",
            "personality": "暂无性格分析数据",
            "education": "暂无学业分析数据",
            "parents": "暂无父母分析数据",
            "social": "暂无人际关系分析数据",
            "future": "暂无未来分析数据"
        }
        
        if not ai_text:
            logger.warning("AI文本为空，返回默认分析结果")
            return analysis
            
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
            analysis['health'] = ai_text[health_start:next_section].replace("健康分析:", "").replace("健康分析", "").strip()
        
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
            analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析:", "").replace("财运分析", "").strip()
        
        # 提取事业发展
        if "事业发展" in ai_text:
            career_start = ai_text.find("事业发展")
            next_section = min(
                [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                ai_text.find("子女缘分", career_start),
                                ai_text.find("综合建议", career_start),
                                ai_text.find("性格特点", career_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['career'] = ai_text[career_start:next_section].replace("事业发展:", "").replace("事业发展", "").strip()
        
        # 提取婚姻感情
        if "婚姻感情" in ai_text:
            relationship_start = ai_text.find("婚姻感情")
            next_section = min(
                [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                ai_text.find("综合建议", relationship_start),
                                ai_text.find("性格特点", relationship_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情:", "").replace("婚姻感情", "").strip()
        
        # 提取子女缘分
        if "子女缘分" in ai_text:
            children_start = ai_text.find("子女缘分")
            next_section = min(
                [pos for pos in [ai_text.find("综合建议", children_start),
                                ai_text.find("性格特点", children_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['children'] = ai_text[children_start:next_section].replace("子女缘分:", "").replace("子女缘分", "").strip()
        
        # 提取综合建议
        if "综合建议" in ai_text:
            overall_start = ai_text.find("综合建议")
            next_section = min(
                [pos for pos in [ai_text.find("性格特点", overall_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['overall'] = ai_text[overall_start:next_section].replace("综合建议:", "").replace("综合建议", "").strip()
        
        # 提取性格特点
        if "性格特点" in ai_text:
            personality_start = ai_text.find("性格特点")
            next_section = min(
                [pos for pos in [ai_text.find("学业分析", personality_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['personality'] = ai_text[personality_start:next_section].replace("性格特点:", "").replace("性格特点", "").strip()
        
        # 提取学业分析
        if "学业分析" in ai_text:
            education_start = ai_text.find("学业分析")
            next_section = min(
                [pos for pos in [ai_text.find("父母情况", education_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['education'] = ai_text[education_start:next_section].replace("学业分析:", "").replace("学业分析", "").strip()
        
        # 提取父母情况
        if "父母情况" in ai_text:
            parents_start = ai_text.find("父母情况")
            next_section = min(
                [pos for pos in [ai_text.find("人际关系", parents_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['parents'] = ai_text[parents_start:next_section].replace("父母情况:", "").replace("父母情况", "").strip()
        
        # 提取人际关系
        if "人际关系" in ai_text:
            social_start = ai_text.find("人际关系")
            next_section = min(
                [pos for pos in [ai_text.find("近五年运势", social_start)] if pos > 0] or [len(ai_text)]
            )
            analysis['social'] = ai_text[social_start:next_section].replace("人际关系:", "").replace("人际关系", "").strip()
        
        # 提取近五年运势
        if "近五年运势" in ai_text:
            future_start = ai_text.find("近五年运势")
            analysis['future'] = ai_text[future_start:].replace("近五年运势:", "").replace("近五年运势", "").strip()
        
        # 如果没有提取到任何内容，将整个分析文本作为overall
        if all(value.startswith("暂无") for value in analysis.values()):
            analysis['overall'] = ai_text.strip()
        
        logger.info("成功从AI文本中提取分析结果")
        return analysis
    except Exception as e:
        logger.error(f"从AI文本中提取分析结果失败: {str(e)}")
        return {
            "health": "暂无健康分析数据",
            "wealth": "暂无财运分析数据",
            "career": "暂无事业分析数据",
            "relationship": "暂无婚姻感情分析数据",
            "children": "暂无子女分析数据",
            "overall": "分析提取失败，请稍后再试。",
            "personality": "暂无性格分析数据",
            "education": "暂无学业分析数据",
            "parents": "暂无父母分析数据",
            "social": "暂无人际关系分析数据",
            "future": "暂无未来分析数据"
        } 