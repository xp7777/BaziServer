import os
import json
import logging
import requests
import openai
import time
from datetime import datetime
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
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的健康状况和潜在健康风险。
        
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
        
        请从五行平衡的角度专门分析其健康状况，包括：
        1. 整体健康状况评估
        2. 潜在的健康风险点
        3. 容易出现的健康问题
        4. 对应的养生建议和预防措施
        5. 大运流年中需要特别注意的健康变化
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的健康建议。
        """,
        
        "wealth": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的财运和发财机遇。
        
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
        
        请从八字命理的角度专门分析其财运状况，包括：
        1. 整体财运评估
        2. 财富来源和积累方式
        3. 适合从事的财富相关行业
        4. 大运流年中的财运高峰期
        5. 提升财运的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的财富建议。
        """,
        
        "career": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的事业发展和职业选择。
        
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
        
        请从八字命理的角度专门分析其事业状况，包括：
        1. 事业发展总体趋势
        2. 适合从事的行业和职业
        3. 事业发展中的优势和障碍
        4. 大运流年中的事业机遇期
        5. 提升事业运势的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的事业发展建议。
        """,
        
        "relationship": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的婚姻感情状况。
        
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
        
        请从八字命理的角度专门分析其婚姻感情状况，包括：
        1. 感情和婚姻总体运势
        2. 适合的伴侣类型和特征
        3. 婚姻中可能面临的挑战
        4. 大运流年中的婚恋机遇期
        5. 提升感情运势的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的感情婚姻建议。
        """,
        
        "children": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的子女缘分和家庭关系。
        
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
        
        请从八字命理的角度专门分析其子女缘分，包括：
        1. 子女缘分总体评估
        2. 可能的子女数量和性别
        3. 与子女的关系特点
        4. 教育子女的适合方式
        5. 提升家庭和谐的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的家庭关系建议。
        """,

        "parents": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人与父母的关系和孝道情况。
        
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
        
        请从八字命理的角度专门分析其与父母的关系，包括：
        1. 与父母关系的总体状况
        2. 与父亲的关系特点和发展
        3. 与母亲的关系特点和发展
        4. 如何改善与父母的关系
        5. 孝道方面的建议和注意事项
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的亲子关系建议。
        """,

        "education": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的学业发展和学习能力。
        
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
        
        请从八字命理的角度专门分析其学业情况，包括：
        1. 学习能力和思维方式
        2. 适合的学习领域和学科
        3. 学业中的优势和挑战
        4. 大运流年中的关键学习阶段
        5. 提升学业成绩的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的学业发展建议。
        """,

        "social": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人的人际关系和社交能力。
        
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
        
        请从八字命理的角度专门分析其人际关系状况，包括：
        1. 社交能力和人际交往特点
        2. 朋友关系和人脉资源
        3. 人际关系中的优势和挑战
        4. 大运流年中的社交发展阶段
        5. 提升人际关系的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的社交能力提升建议。
        """,

        "future": """
        请作为一名专业的命理师，基于下面的八字命盘数据，专门分析此人未来五年的运势发展。
        
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
        
        请从八字命理的角度专门分析其未来五年运势，包括：
        1. 未来五年总体运势
        2. 每年的具体运势变化
        3. 事业、财运、感情、健康等方面的发展
        4. 未来五年中的关键时间点
        5. 把握机遇和规避风险的具体建议
        
        请在回答中使用专业的五行理论，同时确保答案通俗易懂，给予实用的未来规划建议。
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
    
    # 如果找不到特定领域的模板，返回最接近的领域模板
    if focus_area not in templates:
        # 映射别名
        aliases = {
            "marriage": "relationship",
            "work": "career",
            "money": "wealth",
            "family": "children",
            "study": "education",
            "friends": "social",
            "fiveYears": "future"  # 保持这个映射，因为模板名叫future
        }
        # 使用映射的键名查找模板
        template_key = aliases.get(focus_area, "overall")
        
        # 如果用的是fiveYears，记录映射关系
        if focus_area == "fiveYears":
            logger.info(f"将fiveYears映射到future模板")
        
        return templates.get(template_key, templates["overall"])
    
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
    current_year = datetime.now().year
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

def clean_markdown_symbols(text):
    """
    清理文本中的Markdown符号（* 和 #），但保留内容
    
    Args:
        text: 需要清理的文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return text
        
    # 移除文本中的 * 符号（保留加粗和斜体的效果，但去除符号）
    text = text.replace('**', '').replace('*', '')
    
    # 移除文本中的 # 符号（保留标题效果但去除符号）
    import re
    text = re.sub(r'^###\s+', '', text, flags=re.MULTILINE)  # 移除三级标题的 ###
    text = re.sub(r'^##\s+', '', text, flags=re.MULTILINE)   # 移除二级标题的 ##
    text = re.sub(r'^#\s+', '', text, flags=re.MULTILINE)    # 移除一级标题的 #
    
    # 移除 Markdown 列表标记
    text = re.sub(r'^\s*-\s+', '• ', text, flags=re.MULTILINE)  # 将 Markdown 列表转为实心圆点
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # 移除数字列表标记
    
    return text

def call_deepseek_api(prompt):
    """
    调用DeepSeek API
    
    Args:
        prompt: 提示词
        
    Returns:
        str: AI响应
    """
    try:
        # 记录提示词
        logger.info("开始调用DeepSeek API进行八字分析")
        logger.info(f"请求提示词长度: {len(prompt)} 字符")
        logger.info(f"提示词前100字符: {prompt[:100]}...")
        
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
        current_year = datetime.now().year
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
        
        # 记录API请求
        logger.info(f"发送请求到DeepSeek API，系统提示长度: {len(system_prompt)} 字符")
        logger.info(f"系统提示前100字符: {system_prompt[:100]}...")
        
        # 发送请求并记录时间
        start_time = datetime.now()
        logger.info(f"开始API请求时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"API请求完成，耗时: {duration:.2f}秒")
        
        result = response.json()
        
        # 记录API响应
        logger.info(f"收到DeepSeek API响应: {result}")
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # 记录返回内容
            logger.info(f"DeepSeek返回内容长度: {len(content)} 字符")
            logger.info(f"返回内容前500字符: {content[:500]}...")
            logger.info(f"返回内容后500字符: {content[-500:] if len(content) > 500 else content}")
            
            # 分段记录内容（每1000字一段）
            if len(content) > 1000:
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                for i, chunk in enumerate(chunks):
                    logger.info(f"内容片段 {i+1}/{len(chunks)}: {chunk}")
            
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
            
            # 保留原始Markdown格式，不在此处清理，以便提取函数能正确识别标题
            logger.info("保留内容中的Markdown格式，用于后续分析提取")
            
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
        
        # 转换性别为中文
        if gender == 'male' or gender == '男':
            gender_cn = '男'
        elif gender == 'female' or gender == '女':
            gender_cn = '女'
        else:
            gender_cn = '男'  # 默认值
            
        logger.info(f"性别转换: {gender} -> {gender_cn}")
        logger.info(f"输入数据: 性别={gender_cn}, 八字数据=四柱信息+五行分布")
        
        # 提取八字数据
        year_pillar = bazi_chart['yearPillar']
        month_pillar = bazi_chart['monthPillar']
        day_pillar = bazi_chart['dayPillar']
        hour_pillar = bazi_chart['hourPillar']
        five_elements = bazi_chart['fiveElements']
        
        # 记录八字数据
        logger.info(f"八字四柱: 年柱={year_pillar['heavenlyStem']}{year_pillar['earthlyBranch']}, "
                  f"月柱={month_pillar['heavenlyStem']}{month_pillar['earthlyBranch']}, "
                  f"日柱={day_pillar['heavenlyStem']}{day_pillar['earthlyBranch']}, "
                  f"时柱={hour_pillar['heavenlyStem']}{hour_pillar['earthlyBranch']}")
        logger.info(f"五行分布: 金={five_elements['metal']}, 木={five_elements['wood']}, "
                  f"水={five_elements['water']}, 火={five_elements['fire']}, 土={five_elements['earth']}")
        
        # 获取神煞、大运、流年信息
        shen_sha = bazi_chart.get('shenSha', {})
        da_yun = bazi_chart.get('daYun', {})
        flowing_years = bazi_chart.get('flowingYears', [])
        
        # 获取出生日期信息
        birth_date = bazi_chart.get('birthDate', '')
        birth_time = bazi_chart.get('birthTime', '')
        
        # 计算年龄
        current_year = 2025  # 当前年份
        birth_year = int(birth_date.split('-')[0]) if birth_date and '-' in birth_date else 0
        age = current_year - birth_year if birth_year > 0 else 0
        
        # 构建提示词
        prompt = f"""
        请作为一名专业的命理师，基于以下八字命盘数据，进行全面的人生分析和指导。
        
        八字基本信息：
        性别：{gender_cn}
        出生日期：{birth_date}
        出生时间：{birth_time}
        当前年龄：{age}岁
        
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
        
        神煞信息：
        日冲：{shen_sha.get('dayChong', '无')}
        值神：{shen_sha.get('zhiShen', '无')}
        彭祖百忌: {shen_sha.get('pengZuGan', '')} {shen_sha.get('pengZuZhi', '')}
        喜神：{shen_sha.get('xiShen', '无')}
        福神：{shen_sha.get('fuShen', '无')}
        财神：{shen_sha.get('caiShen', '无')}
        
        大运信息：
        起运年龄：{da_yun.get('startAge', '无')}岁
        起运年份：{da_yun.get('startYear', '无')}年
        大运顺序：{'顺行' if da_yun.get('isForward', True) else '逆行'}
        大运列表：{', '.join([f"{yun.get('startAge', '')}-{yun.get('endAge', '')}岁 {yun.get('heavenlyStem', '')}{yun.get('earthlyBranch', '')}" for yun in da_yun.get('daYunList', [])[:5]]) if da_yun.get('daYunList') else '无'}
        
        流年信息：
        {', '.join([f"{year.get('year', '')}年({year.get('age', '')}岁) {year.get('heavenlyStem', '')}{year.get('earthlyBranch', '')}" for year in flowing_years[:5]]) if flowing_years else '无'}
        
        请从八字命理的角度进行全面专业的分析，包括以下内容：
        
        一、八字命局核心分析
        分析八字四柱的组合特点、日主旺衰、格局类型、命局核心特征，以及对人生的整体影响。
        
        二、五行旺衰与用神
        详细分析五行的旺衰状态，确定用神、忌神，并解释它们对人生各方面的影响。
        
        三、神煞解析
        解读命盘中的重要神煞，分析其对命主各方面运势的具体影响。
        
        四、大运与流年关键节点
        分析当前及未来大运、流年的特点，指出人生关键转折点和需要注意的时期。
        
        五、人生规划建议
        结合以上分析，为命主提供具体的人生规划建议。
        
        六、八个核心领域分析
        1. 婚姻感情：分析感情特点、婚姻状况、配偶特征，以及相关吉凶。
        2. 事业财运：分析适合的事业方向、财富来源、发展机遇与挑战。
        3. 子女情况：分析子女缘分、教育方式、亲子关系等。
        4. 父母情况：分析与父母的关系、对父母的影响等。
        5. 身体健康：分析体质特点、易患疾病、保健养生建议。
        6. 学业：分析学习能力、适合的学习领域、学业发展建议。
        7. 人际关系：分析社交特点、人际关系模式、贵人特征等。
        8. 近五年运势：详细分析未来五年的运势变化、机遇与挑战。
        
        请确保分析专业、全面且易于理解。将分析结果按以下格式返回：
        
        ### 八字命局核心分析
        [分析内容]
        
        ### 五行旺衰与用神
        [分析内容]
        
        ### 神煞解析
        [分析内容]
        
        ### 大运与流年关键节点
        [分析内容]
        
        ### 婚姻感情
        [分析内容]
        
        ### 事业财运
        [分析内容]
        
        ### 子女情况
        [分析内容]
        
        ### 父母情况
        [分析内容]
        
        ### 身体健康
        [分析内容]
        
        ### 学业
        [分析内容]
        
        ### 人际关系
        [分析内容]
        
        ### 近五年运势
        [分析内容]
        
        ### 人生规划建议
        [分析内容]
        """
        
        # 记录完整提示词
        logger.info(f"生成八字分析的完整提示词:\n{prompt}")
        
        # 调用AI接口
        logger.info("开始调用DeepSeek API生成分析...")
        start_time = datetime.now()
        response = call_deepseek_api(prompt)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 记录API调用时间
        logger.info(f"DeepSeek API调用完成，总耗时: {duration:.2f}秒")
        
        # 记录原始响应内容
        logger.info("开始提取分析结果")
        if response:
            logger.info(f"原始响应内容长度: {len(response)} 字符")
            logger.info(f"原始响应内容前500字符: \n{response[:500]}...")
            logger.info(f"原始响应内容后500字符: \n{response[-500:] if len(response) > 500 else response}")
        else:
            logger.warning("API返回内容为空")
        
        # 解析返回的文本
        analysis = extract_analysis_from_text(response)
        
        # 记录提取结果
        logger.info("分析结果提取完成")
        logger.info(f"提取的分析结果包含字段: {list(analysis.keys())}")
        
        logger.info("八字分析生成完成")
        return analysis
        
    except Exception as e:
        logger.error(f"生成八字分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def generate_followup_analysis(bazi_chart, area, gender, previous_analysis=None):
    """
    生成追问分析
    
    Args:
        bazi_chart: 八字图表数据
        area: 分析领域
        gender: 性别
        previous_analysis: 之前的整体分析结果(可选)
        
    Returns:
        str: 分析结果
    """
    try:
        logger.info(f"开始生成追问分析: {area}")
        
        # 转换性别为中文
        if gender == 'male' or gender == '男':
            gender_cn = '男'
        elif gender == 'female' or gender == '女':
            gender_cn = '女'
        else:
            gender_cn = '男'  # 默认值
            
        logger.info(f"性别转换: {gender} -> {gender_cn}")
        
        # 提取四柱信息
        year_pillar = bazi_chart['yearPillar']
        month_pillar = bazi_chart['monthPillar']
        day_pillar = bazi_chart['dayPillar']
        hour_pillar = bazi_chart['hourPillar']
        
        # 提取五行分布
        five_elements = bazi_chart['fiveElements']
        
        # 提取出生信息
        birth_year = None
        birth_month = None
        birth_day = None
        birth_hour = None
        
        # 从birthDate中提取年月日
        if 'birthDate' in bazi_chart and bazi_chart['birthDate']:
            try:
                birth_date = bazi_chart['birthDate']
                if isinstance(birth_date, str):
                    # 尝试解析不同的日期格式
                    if "-" in birth_date:
                        parts = birth_date.split("-")
                        if len(parts) >= 3:
                            birth_year = int(parts[0])
                            birth_month = int(parts[1])
                            birth_day = int(parts[2])
                    elif "/" in birth_date:
                        parts = birth_date.split("/")
                        if len(parts) >= 3:
                            birth_year = int(parts[0])
                            birth_month = int(parts[1])
                            birth_day = int(parts[2])
                    elif len(birth_date) >= 8:  # 可能是YYYYMMDD格式
                        birth_year = int(birth_date[:4])
                        birth_month = int(birth_date[4:6])
                        birth_day = int(birth_date[6:8])
            except Exception as e:
                logger.warning(f"从birthDate提取日期失败: {e}")
        
        # 从birthTime中提取时辰
        if 'birthTime' in bazi_chart and bazi_chart['birthTime']:
            birth_hour = bazi_chart['birthTime']
        
        # 如果没有获取到年月日，使用当前日期
        current_date = datetime.now()
        if not birth_year:
            birth_year = current_date.year
        if not birth_month:
            birth_month = current_date.month
        if not birth_day:
            birth_day = current_date.day
        if not birth_hour:
            birth_hour = "未知时辰"
            
        logger.info(f"解析的出生信息: 年={birth_year}, 月={birth_month}, 日={birth_day}, 时={birth_hour}")
        
        # 获取对应领域的提示词模板
        template = get_prompt_template(area)
        
        # 调整提示词，添加之前的分析信息作为参考
        context = ""
        if 'aiAnalysis' in bazi_chart and bazi_chart['aiAnalysis']:
            # 如果有之前的分析，添加与当前追问领域相关的内容
            ai_analysis = bazi_chart['aiAnalysis']
            
            # 获取领域映射
            related_fields = {
                "health": ["health", "coreAnalysis", "fiveElements"],
                "wealth": ["wealth", "career", "fiveElements"],
                "career": ["career", "wealth", "fiveElements"],
                "relationship": ["relationship", "coreAnalysis"],
                "children": ["children", "relationship"],
                "parents": ["parents", "coreAnalysis"],
                "education": ["education", "coreAnalysis"],
                "social": ["social", "coreAnalysis"],
                "future": ["future", "keyPoints"]
            }
            
            # 默认相关字段
            related = related_fields.get(area, [area, "coreAnalysis"])
            
            # 添加相关的分析内容作为上下文
            context += "\n\n之前的分析概要（仅供参考）：\n"
            for field in related:
                if field in ai_analysis and ai_analysis[field]:
                    context += f"\n{field}分析：{ai_analysis[field][:300]}...\n"
        
        # 添加神煞和大运信息
        shen_sha_info = ""
        if 'shenSha' in bazi_chart and bazi_chart['shenSha']:
            shen_sha = bazi_chart['shenSha']
            shen_sha_info = "\n\n神煞信息：\n"
            if 'benMing' in shen_sha and shen_sha['benMing']:
                shen_sha_info += f"本命神煞：{', '.join(shen_sha['benMing']) or '无'}\n"
            
        da_yun_info = ""
        if 'daYun' in bazi_chart and bazi_chart['daYun']:
            da_yun = bazi_chart['daYun']
            da_yun_info = "\n\n大运信息：\n"
            da_yun_info += f"起运年龄：{da_yun.get('startAge', 0)}岁\n"
            da_yun_info += f"起运年份：{da_yun.get('startYear', birth_year)}年\n"
            da_yun_info += f"大运顺序：{'顺行' if da_yun.get('isForward', True) else '逆行'}\n"
        
        # 添加流年信息
        liu_nian_info = ""
        if 'flowingYears' in bazi_chart and bazi_chart['flowingYears']:
            liu_nian = bazi_chart['flowingYears']
            current_year = datetime.now().year
            liu_nian_info = "\n\n流年信息：\n"
            
            # 只显示当前年份和未来4年的流年
            relevant_years = [year for year in liu_nian if isinstance(year, dict) and year.get('year', 0) >= current_year]
            relevant_years = sorted(relevant_years, key=lambda x: x.get('year', 0))[:5]
            
            for year_data in relevant_years:
                year = year_data.get('year', '')
                age = year_data.get('age', '')
                heavenly_stem = year_data.get('heavenlyStem', '')
                earthly_branch = year_data.get('earthlyBranch', '')
                liu_nian_info += f"{year}年({age}岁): {heavenly_stem}{earthly_branch}\n"
        
        # 填充最终的提示词
        prompt = template.format(
            gender=gender_cn,
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
            earth=five_elements['earth'],
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            birth_hour=birth_hour
        )
        
        # 添加上下文信息
        prompt += context + shen_sha_info + da_yun_info + liu_nian_info
        
        # 添加追问的明确目的
        prompt += f"\n\n请专注于{area}领域的深入分析，提供更具体、实用的建议。请确保分析内容符合被测人的年龄和实际情况。"
        
        # 调用AI接口
        response = call_deepseek_api(prompt)
        
        # 检查并格式化返回结果
        if response:
            logger.info("追问分析生成完成")
            return response
        else:
            logger.error("追问分析生成失败，API返回为空")
            return f"很抱歉，{area}分析生成失败，请稍后重试。"
        
    except Exception as e:
        logger.error(f"生成追问分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 返回默认错误信息而不是None，确保用户得到反馈
        return f"很抱歉，生成{area}分析时遇到了技术问题，请稍后重试。错误信息：{str(e)}"

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
    """从AI返回的文本中提取分析结果
    
    Args:
        ai_text: AI返回的文本
        
    Returns:
        dict: 提取的分析结果
    """
    try:
        if not ai_text:
            logger.warning("AI返回的文本为空")
            return {
                'overall': '分析生成失败，请重试',
                'health': '分析生成失败，请重试',
                'wealth': '分析生成失败，请重试',
                'career': '分析生成失败，请重试',
                'relationship': '分析生成失败，请重试',
                'children': '分析生成失败，请重试',
                'personality': '分析生成失败，请重试',
                'education': '分析生成失败，请重试',
                'parents': '分析生成失败，请重试',
                'social': '分析生成失败，请重试',
                'future': '分析生成失败，请重试',
                'coreAnalysis': '分析生成失败，请重试',
                'fiveElements': '分析生成失败，请重试',
                'shenShaAnalysis': '分析生成失败，请重试',
                'keyPoints': '分析生成失败，请重试',
                'lifePlan': '分析生成失败，请重试'  # 添加人生规划建议字段
            }
        
        logger.info("开始提取分析结果")
        logger.info(f"待提取的文本长度: {len(ai_text)} 字符")
        logger.info(f"文本前300字符: {ai_text[:300]}...")
        
        analysis = {}
        current_section = None
        current_content = []
        
        # 标题模式匹配，支持多种格式
        section_patterns = [
            r'###\s*(.*?)\s*$',  # ### 标题
            r'^\s*(.*?)[：:]\s*$',  # 标题：
            r'^\s*(.*?)[分析|特点|关系|发展|建议][：:]\s*$'  # xx分析：
        ]
        
        import re
        
        # 判断文本使用了哪种标题格式
        format_type = None
        if re.search(r'###\s*', ai_text):
            format_type = "markdown"
            logger.info("检测到Markdown格式的标题")
        elif re.search(r'^\s*.*?[分析|特点|关系|发展|建议][：:]\s*$', ai_text, re.MULTILINE):
            format_type = "chinese_colon"
            logger.info("检测到中文冒号格式的标题")
        else:
            format_type = "unknown"
            logger.info("未检测到明确的标题格式，尝试多种格式提取")
            
        # 预处理文本，保留Markdown标记格式进行提取，但不清理
        processing_text = ai_text
        
        # 按行处理文本
        lines = processing_text.split('\n')
        logger.info(f"文本共有 {len(lines)} 行")
        
        detected_sections = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的部分
            is_new_section = False
            section_name = None
            
            # 尝试多种格式匹配
            if format_type == "markdown" or format_type == "unknown":
                match = re.search(r'###\s*(.*?)\s*$', line)
                if match:
                    section_name = match.group(1).strip()
                    is_new_section = True
                    detected_sections.append(f"行 {i+1}: Markdown格式标题 - {section_name}")
                    
            if (format_type == "chinese_colon" or format_type == "unknown") and not is_new_section:
                # 尝试匹配"xxx分析:"或"xxx特点:"等格式
                match = re.search(r'^(.*?)[分析|特点|关系|发展|建议][：:]\s*$', line)
                if match:
                    section_name = match.group(1).strip()
                    is_new_section = True
                    detected_sections.append(f"行 {i+1}: 中文冒号格式标题 - {section_name}")
                    
                # 尝试直接匹配常见标题
                elif line in ["健康分析", "财运分析", "事业发展", "婚姻感情", "子女情况", 
                            "性格特点", "学业分析", "父母关系", "人际关系", "未来发展", 
                            "综合建议", "整体运势", "八字命局核心分析", "五行旺衰与用神", 
                            "神煞解析", "大运与流年关键节点", "事业财运", "人生规划建议",
                            "父母情况", "身体健康", "学业", "近五年运势", "未来感情发展",
                            "未来事业财运", "未来子女缘分"]:
                    section_name = line
                    is_new_section = True
                    detected_sections.append(f"行 {i+1}: 直接匹配标题 - {section_name}")
            
            if is_new_section and section_name:
                # 保存上一个部分的内容
                if current_section and current_content:
                    analysis[current_section] = '\n'.join(current_content)
                    logger.info(f"提取到 {current_section} 部分，内容长度: {len(analysis[current_section])} 字符")
                    current_content = []
                    
                # 设置新的部分
                current_section = map_section_name(section_name)
            elif current_section:
                # 去掉方括号
                if line.startswith('[') and line.endswith(']'):
                    line = line[1:-1]
                current_content.append(line)
        
        # 记录检测到的所有标题
        logger.info(f"检测到的所有标题 ({len(detected_sections)}):")
        for section_info in detected_sections:
            logger.info(section_info)
        
        # 保存最后一个部分的内容
        if current_section and current_content:
            analysis[current_section] = '\n'.join(current_content)
            logger.info(f"提取到最后一部分 {current_section}，内容长度: {len(analysis[current_section])} 字符")
        
        # 如果使用的是Markdown格式但提取结果很少，尝试直接使用正则表达式提取
        if format_type == "markdown" and len(analysis) < 5:
            logger.info("提取结果不足，尝试使用正则表达式从原始文本直接提取所有章节")
            sections = re.findall(r'###\s*(.*?)\s*\n(.*?)(?=\n###|$)', ai_text, re.DOTALL)
            for title, content in sections:
                section_name = map_section_name(title.strip())
                analysis[section_name] = content.strip()
                logger.info(f"正则提取到Markdown标题 '{title.strip()}' -> {section_name}，内容长度: {len(content.strip())} 字符")
        
        # 直接从原始文本中提取特定段落
        # 1. 提取父母情况
        parents_matches = re.findall(r'###\s*父母情况\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                         re.findall(r'父母情况(.*?)(?=身体健康|学业|人际关系|近五年运势|-|\Z)', ai_text, re.DOTALL)
        if parents_matches:
            parents_content = max(parents_matches, key=len).strip()
            analysis["parents"] = parents_content
            logger.info(f"直接从原文提取到父母情况，内容长度: {len(parents_content)} 字符")
            
        # 2. 提取身体健康
        health_matches = re.findall(r'###\s*身体健康\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                        re.findall(r'身体健康(.*?)(?=学业|人际关系|近五年运势|-|\Z)', ai_text, re.DOTALL)
        if health_matches:
            health_content = max(health_matches, key=len).strip()
            analysis["health"] = health_content
            logger.info(f"直接从原文提取到身体健康，内容长度: {len(health_content)} 字符")
            
        # 3. 提取学业
        education_matches = re.findall(r'###\s*学业\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                           re.findall(r'学业(.*?)(?=人际关系|近五年运势|-|\Z)', ai_text, re.DOTALL)
        if education_matches:
            education_content = max(education_matches, key=len).strip()
            analysis["education"] = education_content
            logger.info(f"直接从原文提取到学业，内容长度: {len(education_content)} 字符")
            
        # 4. 提取近五年运势
        future_matches = re.findall(r'###\s*近五年运势\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                        re.findall(r'近五年运势(?:\s*\([^)]*\))?(.*?)(?=人生规划|人生规划建议|-|\Z)', ai_text, re.DOTALL)
        if future_matches:
            future_content = max(future_matches, key=len).strip()
            analysis["future"] = future_content
            logger.info(f"直接从原文提取到近五年运势，内容长度: {len(future_content)} 字符")
            
        # 5. 提取人生规划建议
        lifePlan_matches = re.findall(r'###\s*人生规划建议\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                          re.findall(r'人生规划建议(.*?)(?=-|\Z)', ai_text, re.DOTALL)
        if lifePlan_matches:
            lifePlan_content = max(lifePlan_matches, key=len).strip()
            analysis["lifePlan"] = lifePlan_content
            logger.info(f"直接从原文提取到人生规划建议，内容长度: {len(lifePlan_content)} 字符")
        
        # 6. 提取婚姻感情
        relationship_matches = re.findall(r'###\s*婚姻感情\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                              re.findall(r'婚姻感情(.*?)(?=事业财运|子女情况|-|\Z)', ai_text, re.DOTALL)
        if relationship_matches:
            relationship_content = max(relationship_matches, key=len).strip()
            analysis["relationship"] = relationship_content
            logger.info(f"直接从原文提取到婚姻感情，内容长度: {len(relationship_content)} 字符")
            
        # 7. 提取事业财运
        career_matches = re.findall(r'###\s*事业财运\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                        re.findall(r'事业财运(.*?)(?=子女情况|父母情况|-|\Z)', ai_text, re.DOTALL)
        if career_matches:
            career_content = max(career_matches, key=len).strip()
            analysis["career"] = career_content
            logger.info(f"直接从原文提取到事业财运，内容长度: {len(career_content)} 字符")
            
        # 8. 提取子女情况
        children_matches = re.findall(r'###\s*子女情况\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                          re.findall(r'子女情况(.*?)(?=父母情况|身体健康|-|\Z)', ai_text, re.DOTALL)
        if children_matches:
            children_content = max(children_matches, key=len).strip()
            analysis["children"] = children_content
            logger.info(f"直接从原文提取到子女情况，内容长度: {len(children_content)} 字符")
            
        # 9. 提取八字命局核心分析
        core_matches = re.findall(r'###\s*八字命局核心分析\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL)
        if core_matches:
            core_content = max(core_matches, key=len).strip()
            analysis["coreAnalysis"] = core_content
            logger.info(f"直接从原文提取到八字命局核心分析，内容长度: {len(core_content)} 字符")
        
        # 10. 提取五行旺衰与用神
        five_matches = re.findall(r'###\s*五行旺衰与用神\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL)
        if five_matches:
            five_content = max(five_matches, key=len).strip()
            analysis["fiveElements"] = five_content
            logger.info(f"直接从原文提取到五行旺衰与用神，内容长度: {len(five_content)} 字符")
            
        # 11. 提取神煞解析
        shen_sha_matches = re.findall(r'###\s*神煞解析\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL)
        if shen_sha_matches:
            shen_sha_content = max(shen_sha_matches, key=len).strip()
            analysis["shenShaAnalysis"] = shen_sha_content
            logger.info(f"直接从原文提取到神煞解析，内容长度: {len(shen_sha_content)} 字符")
            
        # 12. 提取人际关系
        social_matches = re.findall(r'###\s*人际关系\s*\n(.*?)(?=###|$)', ai_text, re.DOTALL) or \
                        re.findall(r'人际关系(.*?)(?=近五年运势|人生规划|-|\Z)', ai_text, re.DOTALL)
        if social_matches:
            social_content = max(social_matches, key=len).strip()
            analysis["social"] = social_content
            logger.info(f"直接从原文提取到人际关系，内容长度: {len(social_content)} 字符")
        
        # 确保所有必要字段都存在
        required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                         'personality', 'education', 'parents', 'social', 'future',
                         'coreAnalysis', 'fiveElements', 'shenShaAnalysis', 'keyPoints', 'lifePlan']
        for field in required_fields:
            if field not in analysis or not analysis[field]:
                logger.warning(f"缺少必要字段 {field}，添加默认值")
                analysis[field] = f"分析生成中..."
                
        # 记录提取结果
        logger.info(f"最终提取到 {len(analysis)} 个部分: {list(analysis.keys())}")
        for key, value in analysis.items():
            logger.info(f"{key} 部分内容长度: {len(value)} 字符")
            logger.info(f"{key} 部分内容前100字符: {value[:100]}...")
            
        # 再次清理每个部分的Markdown符号
        cleaned_analysis = {}
        for key, value in analysis.items():
            cleaned_analysis[key] = clean_markdown_symbols(value)
            logger.info(f"清理后 {key} 部分内容长度: {len(cleaned_analysis[key])} 字符")
        
        logger.info("分析结果提取完成")
        return cleaned_analysis
        
    except Exception as e:
        logger.error(f"提取分析结果失败: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'overall': '分析提取过程中出错，请重试',
            'health': '分析提取过程中出错，请重试',
            'wealth': '分析提取过程中出错，请重试',
            'career': '分析提取过程中出错，请重试',
            'relationship': '分析提取过程中出错，请重试',
            'children': '分析提取过程中出错，请重试',
            'personality': '分析提取过程中出错，请重试',
            'education': '分析提取过程中出错，请重试',
            'parents': '分析提取过程中出错，请重试',
            'social': '分析提取过程中出错，请重试',
            'future': '分析提取过程中出错，请重试',
            'coreAnalysis': '分析提取过程中出错，请重试',
            'fiveElements': '分析提取过程中出错，请重试',
            'shenShaAnalysis': '分析提取过程中出错，请重试',
            'keyPoints': '分析提取过程中出错，请重试',
            'lifePlan': '分析提取过程中出错，请重试'
        }

# 添加辅助函数，映射中文标题到英文键名
def map_section_name(section_name):
    """映射章节名称到标准字段名
    
    Args:
        section_name: 章节名称
        
    Returns:
        str: 标准字段名
    """
    # 去除前后空格
    section_name = section_name.strip()
    
    # 映射表
    mapping = {
        # 核心分析
        "八字命局核心分析": "coreAnalysis",
        "命局核心分析": "coreAnalysis",
        "八字核心": "coreAnalysis",
        
        # 五行分析
        "五行旺衰与用神": "fiveElements",
        "五行分析": "fiveElements",
        "五行": "fiveElements",
        "用神分析": "fiveElements",
        
        # 神煞分析
        "神煞解析": "shenShaAnalysis",
        "神煞分析": "shenShaAnalysis",
        
        # 大运流年
        "大运与流年关键节点": "keyPoints",
        "大运流年": "keyPoints",
        "流年大运": "keyPoints",
        "大运分析": "keyPoints",
        "流年分析": "keyPoints",
        
        # 婚姻感情
        "婚姻感情": "relationship",
        "婚姻": "relationship",
        "感情": "relationship",
        "婚恋": "relationship",
        "未来感情发展": "relationship",
        
        # 事业财运
        "事业财运": "career",
        "事业": "career",
        "事业发展": "career",
        "未来事业财运": "career",
        
        # 财运
        "财运": "wealth",
        "财运分析": "wealth",
        "财富": "wealth",
        
        # 子女
        "子女情况": "children",
        "子女": "children",
        "未来子女缘分": "children",
        
        # 父母
        "父母情况": "parents",
        "父母关系": "parents",
        "父母": "parents",
        
        # 健康
        "身体健康": "health",
        "健康": "health",
        "健康分析": "health",
        
        # 学业
        "学业": "education",
        "学业分析": "education",
        "教育": "education",
        
        # 人际关系
        "人际关系": "social",
        "社交": "social",
        "人际": "social",
        
        # 未来运势
        "近五年运势": "future",
        "未来运势": "future",
        "运势": "future",
        "未来发展": "future",
        "未来五年": "future",
        
        # 综合建议
        "综合建议": "overall",
        "整体运势": "overall",
        "总结建议": "overall",
        
        # 人生规划建议 - 修正映射到lifePlan而非overall
        "人生规划建议": "lifePlan",
        "人生规划": "lifePlan",
        "规划建议": "lifePlan",
        "1. 养育重": "lifePlan",  # 添加特殊情况匹配
        
        # 性格特点
        "性格特点": "personality",
        "性格": "personality",
        "个性": "personality"
    }
    
    # 尝试直接匹配
    if section_name in mapping:
        return mapping[section_name]
    
    # 尝试部分匹配
    for key, value in mapping.items():
        if key in section_name or section_name in key:
            logger.info(f"映射标题: '{section_name}' -> '{value}'")
            return value
    
    # 如果没有匹配项，使用原名
    logger.warning(f"无法识别的标题: '{section_name}'，使用原名")
    return section_name