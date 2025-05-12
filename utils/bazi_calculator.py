import os
import json
import logging
import datetime
from datetime import timedelta
import math

logger = logging.getLogger(__name__)

# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 五行
FIVE_ELEMENTS = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "丑": "土",
    "寅": "木", "卯": "木",
    "辰": "土", "巳": "火",
    "午": "火", "未": "土",
    "申": "金", "酉": "金",
    "戌": "土", "亥": "水"
}

# 阴阳
YIN_YANG = {
    "甲": "阳", "乙": "阴",
    "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴",
    "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴",
    "子": "阳", "丑": "阴",
    "寅": "阳", "卯": "阴",
    "辰": "阳", "巳": "阴",
    "午": "阳", "未": "阴",
    "申": "阳", "酉": "阴",
    "戌": "阳", "亥": "阴"
}

# 月支和节气对应表
SOLAR_TERMS = {
    1: {"name": "立春", "day": 4},
    2: {"name": "惊蛰", "day": 6},
    3: {"name": "清明", "day": 5},
    4: {"name": "立夏", "day": 6},
    5: {"name": "芒种", "day": 6},
    6: {"name": "小暑", "day": 7},
    7: {"name": "立秋", "day": 8},
    8: {"name": "白露", "day": 8},
    9: {"name": "寒露", "day": 8},
    10: {"name": "立冬", "day": 7},
    11: {"name": "大雪", "day": 7},
    12: {"name": "小寒", "day": 6}
}

def convert_lunar_to_solar(year, month, day):
    """
    将农历日期转换为公历日期
    
    这里使用一个简化的转换方法，实际项目中应该使用完整的万年历数据
    
    Args:
        year: 农历年
        month: 农历月
        day: 农历日
        
    Returns:
        tuple: (公历年, 公历月, 公历日)
    """
    # 这里应该根据万年历数据进行转换
    # 由于这是一个复杂的计算，这里只做一个简单的模拟
    # 实际项目中应该使用专业的万年历库或API
    
    # 以下是模拟代码，实际项目中请替换
    # 假设农历日期比公历日期晚一个月左右
    solar_date = datetime.datetime(year, month, day) - timedelta(days=30)
    return (solar_date.year, solar_date.month, solar_date.day)

def get_year_pillar(year):
    """
    计算年柱
    
    Args:
        year: 公历年份
        
    Returns:
        dict: 年柱信息
    """
    # 计算天干索引
    stem_index = (year - 4) % 10
    # 计算地支索引
    branch_index = (year - 4) % 12
    
    # 获取天干和地支
    heavenly_stem = HEAVENLY_STEMS[stem_index]
    earthly_branch = EARTHLY_BRANCHES[branch_index]
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem]
    }

def get_month_pillar(year, month, day):
    """
    计算月柱
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        
    Returns:
        dict: 月柱信息
    """
    # 获取节气日期
    solar_term = SOLAR_TERMS.get(month, {"day": 15})
    
    # 如果当前日期在节气日期之前，月份减1
    if day < solar_term["day"]:
        month = month - 1
        if month == 0:
            month = 12
            year -= 1
    
    # 计算月干索引
    year_stem_index = (year - 4) % 10
    base_stem_index = (year_stem_index % 5) * 2
    month_stem_index = (base_stem_index + month - 1) % 10
    
    # 计算月支索引
    month_branch_index = (month + 1) % 12
    
    # 获取天干和地支
    heavenly_stem = HEAVENLY_STEMS[month_stem_index]
    earthly_branch = EARTHLY_BRANCHES[month_branch_index]
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem]
    }

def get_day_pillar(year, month, day):
    """
    计算日柱
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        
    Returns:
        dict: 日柱信息
    """
    # 计算基准日期到当前日期的天数
    base_date = datetime.datetime(1900, 1, 1)
    current_date = datetime.datetime(year, month, day)
    days = (current_date - base_date).days
    
    # 计算日干索引
    day_stem_index = (days + 10) % 10
    # 计算日支索引
    day_branch_index = (days + 12) % 12
    
    # 获取天干和地支
    heavenly_stem = HEAVENLY_STEMS[day_stem_index]
    earthly_branch = EARTHLY_BRANCHES[day_branch_index]
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem]
    }

def get_hour_pillar(year, month, day, hour):
    """
    计算时柱
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰 (0-23)
        
    Returns:
        dict: 时柱信息
    """
    # 计算时辰地支索引
    branch_index = hour // 2
    if branch_index == 12:
        branch_index = 0
    
    # 获取日干索引
    day_pillar = get_day_pillar(year, month, day)
    day_stem = day_pillar["heavenlyStem"]
    day_stem_index = HEAVENLY_STEMS.index(day_stem)
    
    # 计算时干索引
    base_stem_index = (day_stem_index % 5) * 2
    hour_stem_index = (base_stem_index + branch_index // 2) % 10
    
    # 获取天干和地支
    heavenly_stem = HEAVENLY_STEMS[hour_stem_index]
    earthly_branch = EARTHLY_BRANCHES[branch_index]
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem]
    }

def calculate_five_elements(bazi_data):
    """
    计算八字中五行的分布情况
    
    Args:
        bazi_data: 八字数据
        
    Returns:
        dict: 五行分布
    """
    elements_count = {
        "木": 0,
        "火": 0,
        "土": 0,
        "金": 0,
        "水": 0
    }
    
    # 统计天干五行
    for pillar in [bazi_data["yearPillar"], bazi_data["monthPillar"], bazi_data["dayPillar"], bazi_data["hourPillar"]]:
        stem = pillar["heavenlyStem"]
        branch = pillar["earthlyBranch"]
        
        stem_element = FIVE_ELEMENTS[stem]
        branch_element = FIVE_ELEMENTS[branch]
        
        elements_count[stem_element] += 1
        elements_count[branch_element] += 1
    
    return elements_count

def calculate_flowing_years(gender, bazi_data):
    """
    计算大运流年
    
    Args:
        gender: 性别 ("male" 或 "female")
        bazi_data: 八字数据
        
    Returns:
        list: 大运流年数据
    """
    # 这里应该根据八字和性别计算大运流年
    # 由于这是一个复杂的计算，这里只做一个简单的模拟
    
    # 获取月干支
    month_stem = bazi_data["monthPillar"]["heavenlyStem"]
    month_branch = bazi_data["monthPillar"]["earthlyBranch"]
    
    # 确定大运方向
    month_stem_yin_yang = YIN_YANG[month_stem]
    is_forward = (gender == "male" and month_stem_yin_yang == "阳") or (gender == "female" and month_stem_yin_yang == "阴")
    
    # 计算起运年龄
    start_age = 1  # 简化处理，实际应根据出生月日计算
    
    # 计算大运
    flowing_years = []
    
    # 天干地支索引
    stem_index = HEAVENLY_STEMS.index(month_stem)
    branch_index = EARTHLY_BRANCHES.index(month_branch)
    
    for i in range(8):
        if is_forward:
            new_stem_index = (stem_index + i + 1) % 10
            new_branch_index = (branch_index + i + 1) % 12
        else:
            new_stem_index = (stem_index - i - 1) % 10
            new_branch_index = (branch_index - i - 1) % 12
        
        new_stem = HEAVENLY_STEMS[new_stem_index]
        new_branch = EARTHLY_BRANCHES[new_branch_index]
        
        flowing_years.append({
            "year": start_age + i * 10,
            "heavenlyStem": new_stem,
            "earthlyBranch": new_branch,
            "element": FIVE_ELEMENTS[new_stem]
        })
    
    return flowing_years

def calculate_bazi(gender, birth_time):
    """
    计算八字
    
    Args:
        gender: 性别 ("male" 或 "female")
        birth_time: 出生时间
        
    Returns:
        dict: 八字数据
    """
    year = birth_time["year"]
    month = birth_time["month"]
    day = birth_time["day"]
    hour = birth_time["hour"]
    is_lunar = birth_time.get("isLunar", False)
    
    # 如果是农历，转换为公历
    if is_lunar:
        year, month, day = convert_lunar_to_solar(year, month, day)
    
    # 计算四柱
    year_pillar = get_year_pillar(year)
    month_pillar = get_month_pillar(year, month, day)
    day_pillar = get_day_pillar(year, month, day)
    hour_pillar = get_hour_pillar(year, month, day, hour)
    
    # 组装八字数据
    bazi_data = {
        "yearPillar": year_pillar,
        "monthPillar": month_pillar,
        "dayPillar": day_pillar,
        "hourPillar": hour_pillar
    }
    
    # 计算五行分布
    five_elements = calculate_five_elements(bazi_data)
    bazi_data["fiveElements"] = five_elements
    
    return bazi_data 