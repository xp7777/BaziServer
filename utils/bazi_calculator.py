import os
import json
import logging
import datetime
from datetime import timedelta
import math
import sxtwl  # 导入四柱万年历库

# 注意: 现在使用的是PyPI上的真实sxtwl包(https://pypi.org/project/sxtwl/)
# 不再使用模拟的sxtwl.py文件


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

# 天干列表
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支列表
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 十神列表
SHI_SHEN = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"]
# 十二长生
CHANG_SHENG = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]
# 五行
WU_XING = ["木", "火", "土", "金", "水"]

# 神煞对应表（简化版，实际可能需要更复杂的规则）
SHEN_SHA = {
    "年干": {
        0: ["金舆", "福星贵人"], # 甲
        1: ["金舆", "福星贵人", "流霞"], # 乙
        2: ["驿马"], # 丙
        3: ["驿马"], # 丁
        # 其他天干对应的神煞...
    },
    "年支": {
        0: ["将星"], # 子
        5: ["寡宿", "华盖", "元辰"], # 巳
        # 其他地支对应的神煞...
    },
    "月支": {
        2: ["月德贵人"], # 寅
        4: ["月德贵人", "天德贵人"], # 辰
        # 其他月支对应的神煞...
    }
    # 其他位置的神煞...
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

def get_lunar_date(year, month, day, hour=12):
    """
    将公历日期转换为农历日期
    """
    day_obj = sxtwl.fromSolar(year, month, day)
    
    lunar_year = day_obj.getLunarYear()
    lunar_month = day_obj.getLunarMonth()
    lunar_day = day_obj.getLunarDay()
    
    # 月份可能有闰月，需要特殊处理
    is_leap = day_obj.isLunarLeap()
    
    return {
        "year": lunar_year,
        "month": lunar_month,
        "day": lunar_day,
        "is_leap": is_leap
    }

def get_bazi(year, month, day, hour, gender='男'):
    """
    计算八字和神煞
    year, month, day: 阳历年月日
    hour: 小时（0-23）
    gender: '男' 或 '女'
    """
    day_obj = sxtwl.fromSolar(year, month, day)
    
    # 计算八字
    gz_year = day_obj.getYearGZ()
    gz_month = day_obj.getMonthGZ()
    gz_day = day_obj.getDayGZ()
    
    # 计算时辰干支
    # 时辰对应：子时(0,1), 丑时(2,3), ..., 亥时(22,23)
    time_zhi = hour // 2
    time_gan = (gz_day.tg * 2 + time_zhi) % 10
    gz_time = {"tg": time_gan, "dz": time_zhi}
    
    # 天干
    year_tg = TIAN_GAN[gz_year.tg]
    month_tg = TIAN_GAN[gz_month.tg]
    day_tg = TIAN_GAN[gz_day.tg]
    time_tg = TIAN_GAN[gz_time["tg"]]
    
    # 地支
    year_dz = DI_ZHI[gz_year.dz]
    month_dz = DI_ZHI[gz_month.dz]
    day_dz = DI_ZHI[gz_day.dz]
    time_dz = DI_ZHI[gz_time["dz"]]
    
    # 组合八字
    bazi = {
        "year": f"{year_tg}{year_dz}",
        "month": f"{month_tg}{month_dz}",
        "day": f"{day_tg}{day_dz}",
        "time": f"{time_tg}{time_dz}"
    }
    
    # 获取神煞（简化示例）
    shen_sha = {}
    
    # 年干神煞
    if gz_year.tg in SHEN_SHA.get("年干", {}):
        shen_sha["年干"] = SHEN_SHA["年干"][gz_year.tg]
    
    # 年支神煞
    if gz_year.dz in SHEN_SHA.get("年支", {}):
        shen_sha["年支"] = SHEN_SHA["年支"][gz_year.dz]
    
    # 月支神煞
    if gz_month.dz in SHEN_SHA.get("月支", {}):
        shen_sha["月支"] = SHEN_SHA["月支"][gz_month.dz]
    
    # 计算大运
    da_yun = calculate_da_yun(year, month, day, hour, bazi, gender)
    
    return {
        "bazi": bazi,
        "shen_sha": shen_sha,
        "da_yun": da_yun
    }

def calculate_da_yun(year, month, day, hour, bazi, gender):
    """
    计算大运信息
    """
    day_obj = sxtwl.fromSolar(year, month, day)
    
    # 性别和月令确定大运顺序
    month_tg_idx = day_obj.getMonthGZ().tg
    month_dz_idx = day_obj.getMonthGZ().dz
    
    # 阳年男命、阴年女命顺行；阴年男命、阳年女命逆行
    year_tg_idx = day_obj.getYearGZ().tg
    is_yang_year = year_tg_idx % 2 == 0  # 甲、丙、戊、庚、壬为阳
    is_male = gender == '男'
    
    forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)
    
    # 计算起运时间
    # 注意：实际八字起运时间计算复杂，这里仅为简化示例
    birth_date = datetime.datetime(year, month, day, hour)
    
    # 简化：男孩3天，女孩100天（实际应基于出生断节气计算）
    if is_male:
        qi_yun_days = 3 * 365.25  # 约3年
    else:
        qi_yun_days = 3 * 365.25 + 3 * 30 + 24  # 约3年3个月24天
    
    qi_yun_date = birth_date + datetime.timedelta(days=qi_yun_days)
    
    # 大运干支
    da_yun_list = []
    
    # 计算8个大运
    for i in range(8):
        if forward:
            new_dz_idx = (month_dz_idx + i + 1) % 12
            new_tg_idx = (month_tg_idx + i + 1) % 10
        else:
            new_dz_idx = (month_dz_idx - i - 1) % 12
            new_tg_idx = (month_tg_idx - i - 1) % 10
        
        # 计算当前大运对应的十神
        shi_shen_idx = (new_tg_idx - day_obj.getDayGZ().tg) % 10
        shi_shen = SHI_SHEN[shi_shen_idx]
        
        # 计算长生十二宫位置（简化）
        chang_sheng_idx = i % 12
        chang_sheng_name = CHANG_SHENG[chang_sheng_idx]
        
        # 计算大运交接时间
        jiao_yun_date = qi_yun_date + datetime.timedelta(days=i * 10 * 365.25)  # 每个大运10年
        
        # 岁数范围
        start_age = i * 10 + int(qi_yun_days / 365.25)
        end_age = start_age + 9
        
        da_yun_list.append({
            "da_yun": f"{TIAN_GAN[new_tg_idx]}{DI_ZHI[new_dz_idx]}",
            "shi_shen": shi_shen,
            "chang_sheng": chang_sheng_name,
            "start_age": start_age,
            "end_age": end_age,
            "start_year": jiao_yun_date.year,
            "end_year": jiao_yun_date.year + 9
        })
    
    # 返回起运信息和大运列表
    return {
        "qi_yun": {
            "days": int(qi_yun_days),
            "years": round(qi_yun_days / 365.25, 1),
            "date": qi_yun_date.strftime("%Y-%m-%d")
        },
        "da_yun_list": da_yun_list
    }

def format_bazi_analysis(bazi_data):
    """
    格式化八字分析数据，生成DeepSeek API需要的提示内容
    """
    bazi = bazi_data["bazi"]
    shen_sha = bazi_data["shen_sha"]
    da_yun = bazi_data["da_yun"]
    
    # 格式化八字
    bazi_str = f"{bazi['year']}，{bazi['month']}，{bazi['day']}，{bazi['time']}"
    
    # 格式化神煞
    shen_sha_str = ""
    for position, sha_list in shen_sha.items():
        if sha_list:
            shen_sha_str += f"[{position}]  {' '.join(sha_list)}    \n"
    
    # 格式化大运
    qi_yun_info = da_yun["qi_yun"]
    qi_yun_str = f"起运：我于出生后{int(qi_yun_info['years'])}年{qi_yun_info['days'] % 365 // 30}个月{qi_yun_info['days'] % 30}天开始起运，在公历{qi_yun_info['date']}交运"
    
    da_yun_table = "旺衰\t大运\t十神\t年龄\t开始时间\t结束时间\n"
    for yun in da_yun["da_yun_list"]:
        da_yun_table += f"{yun['chang_sheng']}\t{yun['da_yun']}\t{yun['shi_shen']}\t{yun['start_age']}\t{yun['start_year']}\t{yun['end_year']}\n"
    
    return {
        "bazi": bazi_str,
        "shen_sha": shen_sha_str,
        "qi_yun": qi_yun_str,
        "da_yun": da_yun_table
    }

# 使用示例
if __name__ == "__main__":
    # 测试用例：1986年4月23日17点出生的女性
    bazi_data = get_bazi(1986, 4, 23, 17, '女')
    formatted = format_bazi_analysis(bazi_data)
    
    print(f"八字：{formatted['bazi']}")
    print(f"神煞：\n{formatted['shen_sha']}")
    print(f"{formatted['qi_yun']}")
    print(f"大运：\n{formatted['da_yun']}") 