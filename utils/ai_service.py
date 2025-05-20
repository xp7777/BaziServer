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
    metal = five_elements["金"]
    wood = five_elements["木"]
    water = five_elements["水"]
    fire = five_elements["火"]
    earth = five_elements["土"]
    
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
            # 1. 直接从出生日期字段提取
            if "出生日期：" in prompt:
                year_start = prompt.index("出生日期：") + 5
                year_end = prompt.find("年", year_start)
                if year_end > year_start:
                    birth_year = int(prompt[year_start:year_end])
            # 2. 从阳历字段提取
            elif "阳历" in prompt and "年" in prompt:
                year_index = prompt.index("阳历") + 2
                year_end = prompt.index("年", year_index)
                birth_year = int(prompt[year_index:year_end])
            # 3. 使用正则表达式匹配所有年份
            else:
                import re
                # 匹配格式如 birth_year=2025 或 "2025年"
                year_patterns = [
                    r'birth_year=(\d{4})',  # birth_year=2025
                    r'(\d{4})年',           # 2025年
                ]
                
                for pattern in year_patterns:
                    matches = re.findall(pattern, prompt)
                    if matches:
                        # 找到第一个匹配项
                        birth_year = int(matches[0])
                        break
        except Exception as e:
            logger.warning(f"无法提取出生年份: {e}")
        
        # 计算当前年龄
        current_year = datetime.datetime.now().year
        age = current_year - birth_year if birth_year else None
        
        if age is not None:
            logger.info(f"出生年份: {birth_year}, 当前年龄: {age}岁")
        
        # 添加年龄相关上下文
        system_prompt = "你是一位专业的命理分析师，精通八字命理理论。请根据用户提供的八字信息，给出专业、详细、实用的分析和建议。"
        
        if age is not None:
            # 添加年龄相关指导
            system_prompt += "\n\n重要提示：分析时必须考虑当事人的实际年龄。"
            
            if age < 0:  # 未出生
                system_prompt += f"当事人尚未出生，出生于未来的{birth_year}年。请只分析未来可能的性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。"
                logger.info(f"检测到未来出生日期: {birth_year}年，调整分析内容")
            elif age < 6:  # 婴幼儿
                system_prompt += f"当事人目前仅{age}岁，属于婴幼儿阶段。请重点分析性格特点、天赋才能和健康状况，不要分析婚姻感情、学业情况或职业发展等不适合婴幼儿的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段（如20岁以后）的预测。"
                logger.info(f"检测到婴幼儿: {age}岁，调整分析内容")
            elif age < 18:  # 未成年
                system_prompt += f"当事人目前{age}岁，尚未成年。请重点分析性格特点、天赋才能、健康状况和学业发展，避免过多讨论婚姻感情等不适合未成年人的内容。如果需要提到这些方面，请明确指出这是未来特定年龄段的预测。"
                logger.info(f"检测到未成年人: {age}岁，调整分析内容")
        
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
            return result["choices"][0]["message"]["content"]
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
    # 格式化提示词
    prompt = format_prompt(bazi_data, gender, birth_time, focus_area)
    
    # 首先尝试使用DeepSeek API
    if DEEPSEEK_API_KEY:
        logger.info(f"使用DeepSeek API生成分析，领域: {focus_area}")
        response = call_deepseek_api(prompt)
        if response:
            return response
        
        # 如果DeepSeek API失败，等待一段时间后重试
        logger.warning("DeepSeek API调用失败，等待5秒后重试")
        time.sleep(5)
        response = call_deepseek_api(prompt)
        if response:
            return response
    
    # 如果DeepSeek API不可用或失败，使用OpenAI API
    if openai.api_key:
        logger.info(f"使用OpenAI API生成分析，领域: {focus_area}")
        response = call_openai_api(prompt)
        if response:
            return response
        
        # 如果OpenAI API失败，等待一段时间后重试
        logger.warning("OpenAI API调用失败，等待5秒后重试")
        time.sleep(5)
        response = call_openai_api(prompt)
        if response:
            return response
    
    # 如果所有API都失败，返回错误信息
    logger.error("所有AI API调用均失败")
    return "很抱歉，暂时无法生成分析结果，请稍后再试。" 