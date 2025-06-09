import os
import json
import logging
import requests
import openai
import time
import datetime
import traceback

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

def generate_bazi_analysis(bazi_chart, gender):
    """
    生成八字分析结果
    
    Args:
        bazi_chart: 八字命盘数据
        gender: 性别
        
    Returns:
        dict: 分析结果
    """
    try:
        logger.info("开始生成八字分析")
        
        # 提取八字数据
        year_pillar = bazi_chart['yearPillar']
        month_pillar = bazi_chart['monthPillar']
        day_pillar = bazi_chart['dayPillar']
        hour_pillar = bazi_chart['hourPillar']
        five_elements = bazi_chart['fiveElements']
        
        # 构建提示词
        prompt = f"""
        请作为一名专业的命理师，基于以下八字命盘数据，进行全面的人生分析和指导。
        
        八字信息：
        性别：{gender}
        
        八字命盘：
        年柱：{year_pillar['heavenlyStem']}{year_pillar['earthlyBranch']}
        月柱：{month_pillar['heavenlyStem']}{month_pillar['earthlyBranch']}
        日柱：{day_pillar['heavenlyStem']}{day_pillar['earthlyBranch']}
        时柱：{hour_pillar['heavenlyStem']}{hour_pillar['earthlyBranch']}
        
        五行分布：
        金：{five_elements['metal']}
        木：{five_elements['wood']}
        水：{five_elements['water']}
        火：{five_elements['fire']}
        土：{five_elements['earth']}
        
        请从八字命理的角度进行全面分析，包括：
        1. 性格特点和天赋才能
        2. 健康状况和注意事项
        3. 事业发展和职业选择
        4. 财运分析和理财建议
        5. 感情婚姻和家庭关系
        6. 人际关系和社交特点
        7. 近五年运势变化
        8. 整体人生发展建议
        
        请确保分析专业、全面且易于理解。将分析结果按以下格式返回：
        
        ### 性格特点
        [分析内容]
        
        ### 健康分析
        [分析内容]
        
        ### 事业发展
        [分析内容]
        
        ### 财运分析
        [分析内容]
        
        ### 婚姻感情
        [分析内容]
        
        ### 人际关系
        [分析内容]
        
        ### 近五年运势
        [分析内容]
        
        ### 综合建议
        [分析内容]
        """
        
        # 调用AI接口
        response = call_deepseek_api(prompt)
        
        # 解析返回的文本
        analysis = extract_analysis_from_text(response)
        
        logger.info("八字分析生成完成")
        return analysis
        
    except Exception as e:
        logger.error(f"生成八字分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def generate_followup_analysis(bazi_chart, area, gender):
    """
    生成追问分析结果
    
    Args:
        bazi_chart: 八字命盘数据
        area: 追问领域
        gender: 性别
        
    Returns:
        str: 分析结果
    """
    try:
        logger.info(f"开始生成追问分析: {area}")
        
        # 提取八字数据
        year_pillar = bazi_chart['yearPillar']
        month_pillar = bazi_chart['monthPillar']
        day_pillar = bazi_chart['dayPillar']
        hour_pillar = bazi_chart['hourPillar']
        five_elements = bazi_chart['fiveElements']
        
        # 获取对应领域的提示词模板
        template = get_prompt_template(area)
        
        # 填充提示词
        prompt = template.format(
            gender=gender,
            year_pillar_stem=year_pillar['heavenlyStem'],
            year_pillar_branch=year_pillar['earthlyBranch'],
            month_pillar_stem=month_pillar['heavenlyStem'],
            month_pillar_branch=month_pillar['earthlyBranch'],
            day_pillar_stem=day_pillar['heavenlyStem'],
            day_pillar_branch=day_pillar['earthlyBranch'],
            hour_pillar_stem=hour_pillar['heavenlyStem'],
            hour_pillar_branch=hour_pillar['earthlyBranch'],
            metal=five_elements['metal'],
            wood=five_elements['wood'],
            water=five_elements['water'],
            fire=five_elements['fire'],
            earth=five_elements['earth']
        )
        
        # 调用AI接口
        response = call_deepseek_api(prompt)
        
        logger.info("追问分析生成完成")
        return response
        
    except Exception as e:
        logger.error(f"生成追问分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def analyze_bazi_with_ai(bazi_data):
    """
    使用AI分析八字命盘
    
    Args:
        bazi_data: 八字数据，包含命盘数据
        
    Returns:
        dict: 分析结果
    """
    try:
        logger.info("开始使用AI分析八字命盘")
        
        # 构建提示词
        prompt = f"""
        请你作为一位专业的命理师，为一位客户分析八字命盘。
        
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
        
        神煞信息:
        日冲: {bazi_data['shenSha']['dayChong']}
        值神: {bazi_data['shenSha']['zhiShen']}
        彭祖百忌: {bazi_data['shenSha']['pengZuGan']} {bazi_data['shenSha']['pengZuZhi']}
        喜神: {bazi_data['shenSha']['xiShen']}
        福神: {bazi_data['shenSha']['fuShen']}
        财神: {bazi_data['shenSha']['caiShen']}
        
        大运信息:
        起运年龄: {bazi_data['daYun']['startAge']}岁
        起运年份: {bazi_data['daYun']['startYear']}年
        顺逆: {'顺行' if bazi_data['daYun']['isForward'] else '逆行'}
        
        请按照以下格式提供分析:
        
        总体分析:
        [详细的总体分析，包括命局特点、五行特征、神煞影响等]
        
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
        
        性格特点:
        [详细的性格特点分析，包括先天性格、后天影响等]
        
        学业发展:
        [详细的学业分析，包括学习能力、适合学科、学习建议等]
        
        父母关系:
        [详细的父母关系分析，包括与父母关系、孝道建议等]
        
        人际关系:
        [详细的人际关系分析，包括社交特点、人缘情况、交友建议等]
        
        未来发展:
        [详细的未来发展分析，包括近五年运势、重点关注事项等]
        """
        
        # 调用API
        if DEEPSEEK_API_KEY:
            logger.info("使用DeepSeek API生成分析")
            response = call_deepseek_api(prompt)
        else:
            logger.info("使用OpenAI API生成分析")
            response = call_openai_api(prompt)
            
        if not response:
            logger.error("API调用失败")
            return None
            
        # 解析分析结果
        analysis = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith('分析:') or line.endswith('特点:') or line.endswith('关系:') or line.endswith('发展:'):
                if current_section and current_content:
                    analysis[current_section] = '\n'.join(current_content)
                    current_content = []
                current_section = line[:-1].lower()
                if current_section == '总体':
                    current_section = 'overall'
                elif current_section == '健康':
                    current_section = 'health'
                elif current_section == '财运':
                    current_section = 'wealth'
                elif current_section == '事业':
                    current_section = 'career'
                elif current_section == '婚姻感情':
                    current_section = 'relationship'
                elif current_section == '子女缘分':
                    current_section = 'children'
                elif current_section == '性格特点':
                    current_section = 'personality'
                elif current_section == '学业发展':
                    current_section = 'education'
                elif current_section == '父母关系':
                    current_section = 'parents'
                elif current_section == '人际关系':
                    current_section = 'social'
                elif current_section == '未来发展':
                    current_section = 'future'
            elif current_section:
                if line.startswith('[') and line.endswith(']'):
                    line = line[1:-1]
                current_content.append(line)
        
        # 添加最后一个部分
        if current_section and current_content:
            analysis[current_section] = '\n'.join(current_content)
            
        # 确保所有必要字段都存在
        required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                         'personality', 'education', 'parents', 'social', 'future']
        for field in required_fields:
            if field not in analysis:
                analysis[field] = f"暂无{field}分析数据"
                
        logger.info("AI分析完成")
        return analysis
        
    except Exception as e:
        logger.error(f"AI分析八字命盘失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def extract_analysis_from_text(ai_text):
    """
    从AI生成的文本中提取分析结果
    
    Args:
        ai_text: AI生成的文本
        
    Returns:
        dict: 分析结果
    """
    try:
        logger.info("开始提取分析结果")
        
        # 初始化结果字典
        analysis = {}
        current_section = None
        current_content = []
        
        # 按行处理文本
        for line in ai_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的部分
            if line.endswith('分析:') or line.endswith('特点:') or line.endswith('关系:') or line.endswith('发展:'):
                # 保存上一个部分的内容
                if current_section and current_content:
                    analysis[current_section] = '\n'.join(current_content)
                    current_content = []
                    
                # 设置新的部分
                current_section = line[:-1].lower()
                if current_section == '总体':
                    current_section = 'overall'
                elif current_section == '健康':
                    current_section = 'health'
                elif current_section == '财运':
                    current_section = 'wealth'
                elif current_section == '事业':
                    current_section = 'career'
                elif current_section == '婚姻感情':
                    current_section = 'relationship'
                elif current_section == '子女缘分':
                    current_section = 'children'
                elif current_section == '性格特点':
                    current_section = 'personality'
                elif current_section == '学业发展':
                    current_section = 'education'
                elif current_section == '父母关系':
                    current_section = 'parents'
                elif current_section == '人际关系':
                    current_section = 'social'
                elif current_section == '未来发展':
                    current_section = 'future'
            elif current_section:
                # 去掉方括号
                if line.startswith('[') and line.endswith(']'):
                    line = line[1:-1]
                current_content.append(line)
        
        # 保存最后一个部分的内容
        if current_section and current_content:
            analysis[current_section] = '\n'.join(current_content)
            
        # 确保所有必要字段都存在
        required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                         'personality', 'education', 'parents', 'social', 'future']
        for field in required_fields:
            if field not in analysis:
                analysis[field] = f"暂无{field}分析数据"
                
        logger.info("分析结果提取完成")
        return analysis
        
    except Exception as e:
        logger.error(f"提取分析结果失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None 