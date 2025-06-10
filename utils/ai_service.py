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
        
        # 记录API请求
        logger.info(f"发送请求到DeepSeek API，系统提示长度: {len(system_prompt)} 字符")
        logger.info(f"系统提示前100字符: {system_prompt[:100]}...")
        
        # 发送请求并记录时间
        start_time = datetime.datetime.now()
        logger.info(f"开始API请求时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        
        end_time = datetime.datetime.now()
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
        logger.info(f"输入数据: 性别={gender}, 八字数据=四柱信息+五行分布")
        
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
        性别：{gender}
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
        喜神：{shen_sha.get('xiShen', '无')}
        福神：{shen_sha.get('fuShen', '无')}
        财神：{shen_sha.get('caiShen', '无')}
        本命神煞：{', '.join(shen_sha.get('benMing', [])) or '无'}
        
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
        start_time = datetime.datetime.now()
        response = call_deepseek_api(prompt)
        end_time = datetime.datetime.now()
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

def generate_followup_analysis(bazi_chart, area, gender):
    """
    生成追问分析
    
    Args:
        bazi_chart: 八字图表数据
        area: 分析领域
        gender: 性别
        
    Returns:
        str: 分析结果
    """
    try:
        logger.info(f"开始生成追问分析: {area}")
        
        # 提取四柱信息
        year_pillar = bazi_chart['yearPillar']
        month_pillar = bazi_chart['monthPillar']
        day_pillar = bazi_chart['dayPillar']
        hour_pillar = bazi_chart['hourPillar']
        
        # 提取五行分布
        five_elements = bazi_chart['fiveElements']
        
        # 提取出生年份，默认为当年
        birth_year = datetime.now().year
        if 'birthDate' in bazi_chart and bazi_chart['birthDate']:
            # 尝试从birthDate中提取年份
            try:
                birth_date = bazi_chart['birthDate']
                if isinstance(birth_date, str) and len(birth_date) >= 4:
                    # 假设birthDate格式为"YYYY-MM-DD"或"YYYY/MM/DD"等
                    birth_year = int(birth_date[:4])
                elif hasattr(birth_date, 'year'):
                    # 如果是日期对象
                    birth_year = birth_date.year
            except Exception as e:
                logger.warning(f"从birthDate提取年份失败: {e}, 使用当前年份")
        
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
            earth=five_elements['earth'],
            birth_year=birth_year
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
                'keyPoints': '分析生成失败，请重试'
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
            r'^\s*(.*?)[分析|特点|关系|发展][：:]\s*$'  # xx分析：
        ]
        
        import re
        
        # 判断文本使用了哪种标题格式
        format_type = None
        if re.search(r'###\s*', ai_text):
            format_type = "markdown"
            logger.info("检测到Markdown格式的标题")
        elif re.search(r'^\s*.*?[分析|特点|关系|发展][：:]\s*$', ai_text, re.MULTILINE):
            format_type = "chinese_colon"
            logger.info("检测到中文冒号格式的标题")
        else:
            format_type = "unknown"
            logger.info("未检测到明确的标题格式，尝试多种格式提取")
            
        # 按行处理文本
        lines = ai_text.split('\n')
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
                match = re.search(r'^(.*?)[分析|特点|关系|发展][：:]\s*$', line)
                if match:
                    section_name = match.group(1).strip()
                    is_new_section = True
                    detected_sections.append(f"行 {i+1}: 中文冒号格式标题 - {section_name}")
                    
                # 尝试直接匹配常见标题
                elif line in ["健康分析", "财运分析", "事业发展", "婚姻感情", "子女情况", 
                            "性格特点", "学业分析", "父母关系", "人际关系", "未来发展", 
                            "综合建议", "整体运势", "八字命局核心分析", "五行旺衰与用神", 
                            "神煞解析", "大运与流年关键节点", "事业财运", "人生规划建议"]:
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
            
        # 对于未找到匹配的格式，尝试进行整体分段
        if not analysis and ai_text:
            logger.warning("未能通过标题提取出分段内容，尝试进行整体分段处理")
            
            # 尝试匹配常见的章节标题
            sections = [
                ("八字命局核心分析", "coreAnalysis"),
                ("五行旺衰与用神", "fiveElements"),
                ("神煞解析", "shenShaAnalysis"),
                ("大运与流年关键节点", "keyPoints"),
                ("性格特点", "personality"),
                ("健康分析", "health"),
                ("事业发展", "career"),
                ("事业财运", "career"),
                ("财运分析", "wealth"),
                ("婚姻感情", "relationship"),
                ("子女情况", "children"),
                ("父母情况", "parents"),
                ("人际关系", "social"),
                ("学业", "education"),
                ("近五年运势", "future"),
                ("人生规划建议", "overall"),
                ("综合建议", "overall")
            ]
            
            # 构建匹配模式
            section_titles = '|'.join([re.escape(title) for title, _ in sections])
            pattern = f"(###\\s*({section_titles}).*?)(?=###\\s*({section_titles})|$)"
            
            # 尝试直接定位各个部分
            for zh_title, en_key in sections:
                # 使用更灵活的模式匹配
                section_pattern = f"(?:###\\s*{re.escape(zh_title)}.*?|{re.escape(zh_title)}[：:])(.*?)(?=###\\s*|{section_titles}[：:]|$)"
                matches = re.findall(section_pattern, ai_text, re.DOTALL | re.IGNORECASE)
                
                if matches:
                    # 取最长匹配结果
                    longest_match = max(matches, key=len)
                    content = longest_match.strip()
                    analysis[en_key] = content
                    logger.info(f"通过整体匹配提取到 {en_key} 部分，内容长度: {len(analysis[en_key])} 字符")
        
        # 确保所有必要字段都存在
        required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 
                         'personality', 'education', 'parents', 'social', 'future',
                         'coreAnalysis', 'fiveElements', 'shenShaAnalysis', 'keyPoints']
        for field in required_fields:
            if field not in analysis or not analysis[field]:
                logger.warning(f"缺少必要字段 {field}，添加默认值")
                analysis[field] = f"暂无"
                
        # 记录提取结果
        logger.info(f"最终提取到 {len(analysis)} 个部分: {list(analysis.keys())}")
        for key, value in analysis.items():
            logger.info(f"{key} 部分内容长度: {len(value)} 字符")
            logger.info(f"{key} 部分内容前100字符: {value[:100]}...")
        
        logger.info("分析结果提取完成")
        return analysis
        
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
            'keyPoints': '分析提取过程中出错，请重试'
        }

# 添加辅助函数，映射中文标题到英文键名
def map_section_name(section_name):
    """将中文标题映射到英文键名"""
    section_name = section_name.lower()
    
    # 记录原始标题
    logger.info(f"映射标题: '{section_name}'")
    
    # 新增的映射关系
    # 匹配八字命局核心分析
    if '八字命局' in section_name or '命局核心' in section_name or '核心分析' in section_name:
        return 'coreAnalysis'
    # 匹配五行旺衰与用神
    elif '五行旺衰' in section_name or '用神' in section_name:
        return 'fiveElements'
    # 匹配神煞解析
    elif '神煞' in section_name:
        return 'shenShaAnalysis'
    # 匹配大运与流年关键节点
    elif '大运' in section_name or '流年' in section_name or '关键节点' in section_name:
        return 'keyPoints'
    # 匹配事业财运
    elif '事业财运' in section_name or ('事业' in section_name and '财运' in section_name):
        return 'career'
    # 匹配人生规划建议
    elif '人生规划' in section_name:
        return 'overall'
    
    # 原有的映射关系
    # 匹配总体/综合分析
    elif '总体' in section_name or '综合' in section_name or '整体' in section_name:
        return 'overall'
    # 匹配健康分析
    elif '健康' in section_name:
        return 'health'
    # 匹配财运分析
    elif '财运' in section_name or '财富' in section_name:
        return 'wealth'
    # 匹配事业分析
    elif '事业' in section_name or '职业' in section_name or '工作' in section_name:
        return 'career'
    # 匹配婚姻感情
    elif '婚姻' in section_name or '感情' in section_name or '姻缘' in section_name:
        return 'relationship'
    # 匹配子女分析
    elif '子女' in section_name or '儿女' in section_name:
        return 'children'
    # 匹配性格特点
    elif '性格' in section_name or '个性' in section_name or '品格' in section_name:
        return 'personality'
    # 匹配学业分析
    elif '学业' in section_name or '学习' in section_name or '教育' in section_name:
        return 'education'
    # 匹配父母关系
    elif '父母' in section_name or '双亲' in section_name or '长辈' in section_name:
        return 'parents'
    # 匹配人际关系
    elif '人际' in section_name or '社交' in section_name or '交友' in section_name:
        return 'social'
    # 匹配未来发展/运势
    elif '未来' in section_name or '运势' in section_name or '后运' in section_name or '五年' in section_name:
        return 'future'
    # 默认返回原名
    else:
        logger.warning(f"无法识别的标题: '{section_name}'，使用原名")
        return section_name 