import os
import json
import logging
import datetime
from datetime import timedelta
import math

# 导入lunar-python库代替sxtwl
try:
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    from lunar_python.util import LunarUtil
    USING_LUNAR_PYTHON = True
    logging.info("成功导入lunar-python库")
except ImportError:
    import sxtwl  # 导入四柱万年历库作为备选
    USING_LUNAR_PYTHON = False
    logging.warning("未能导入lunar-python库，使用sxtwl作为备选")

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

def parse_birth_date_time(birth_date, birth_time):
    """
    解析出生日期和时间
    
    Args:
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间，可以是 HH:MM 或者 "子时 (23:00-01:00)" 等中文时辰
        
    Returns:
        dict: 包含年、月、日、时的字典
    """
    logging.info(f"解析日期和时间: {birth_date}, {birth_time}")
    
    # 解析日期
    try:
        year, month, day = map(int, birth_date.split('-'))
    except Exception as e:
        logging.error(f"解析日期出错: {str(e)}")
        # 默认使用当前日期
        now = datetime.datetime.now()
        year, month, day = now.year, now.month, now.day
    
    # 解析时间
    hour = 0
    
    # 时辰映射表
    hour_map = {
        '子时': 0, '丑时': 2, '寅时': 4, '卯时': 6,
        '辰时': 8, '巳时': 10, '午时': 12, '未时': 14,
        '申时': 16, '酉时': 18, '戌时': 20, '亥时': 22,
        '子': 0, '丑': 2, '寅': 4, '卯': 6, 
        '辰': 8, '巳': 10, '午': 12, '未': 14, 
        '申': 16, '酉': 18, '戌': 20, '亥': 22
    }
    
    try:
        # 先检查是否是带括号的中文时辰格式
        if '(' in birth_time and ')' in birth_time:
            # 获取括号前的部分
            time_name = birth_time.split('(')[0].strip()
            logging.info(f"提取时辰名称: {time_name}")
            
            # 查找对应的时辰
            for key, value in hour_map.items():
                if key in time_name:
                    hour = value
                    logging.info(f"识别到带括号的时辰: {key}, 对应小时: {hour}")
                    break
        # 尝试解析 HH:MM 格式
        elif ':' in birth_time:
            parts = birth_time.split(':')
            if len(parts) >= 1:
                hour = int(parts[0])
                logging.info(f"识别到时分格式，小时: {hour}")
        # 尝试解析纯中文时辰格式
        else:
            # 查找中文时辰
            for key, value in hour_map.items():
                if key in birth_time:
                    hour = value
                    logging.info(f"识别到中文时辰: {key}, 对应小时: {hour}")
                    break
            else:
                logging.warning(f"未识别的时辰格式: {birth_time}，使用默认子时")
    except Exception as e:
        logging.error(f"解析时间出错: {str(e)}")
        # 默认使用子时(0点)
        hour = 0
    
    logging.info(f"解析结果: 年={year}, 月={month}, 日={day}, 时={hour}")
    
    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "isLunar": False  # 默认为阳历
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
    if USING_LUNAR_PYTHON:
        # 使用lunar-python库转换
        lunar = Lunar.fromYmd(year, month, day)
        solar = lunar.getSolar()
        return (solar.getYear(), solar.getMonth(), solar.getDay())
    else:
        # 使用sxtwl库转换
        lunar = sxtwl.Lunar()
        day_obj = lunar.getDayBySolar(year, month, day)
        return (day_obj.y, day_obj.m, day_obj.d)

def get_year_pillar(year):
    """
    计算年柱
    
    Args:
        year: 公历年份
        
    Returns:
        dict: 年柱信息
    """
    if USING_LUNAR_PYTHON:
        # 使用lunar-python库计算
        solar = Solar.fromYmd(year, 5, 1)  # 使用5月1日作为参考日期
        lunar = solar.getLunar()
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        
        logging.info(f"使用lunar-python计算{year}年的年柱: {year_gan}{year_zhi}")
        
        heavenly_stem = year_gan
        earthly_branch = year_zhi
    else:
        # 使用传统方法计算
        stem_index = (year - 4) % 10
        branch_index = (year - 4) % 12
        
        heavenly_stem = HEAVENLY_STEMS[stem_index]
        earthly_branch = EARTHLY_BRANCHES[branch_index]
        
        logging.info(f"使用传统方法计算{year}年的年柱: {heavenly_stem}{earthly_branch}")
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem],
        "birthYear": year
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
    if USING_LUNAR_PYTHON:
        # 使用lunar-python库计算
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        
        heavenly_stem = month_gan
        earthly_branch = month_zhi
    else:
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
    if USING_LUNAR_PYTHON:
        # 使用lunar-python库计算
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        
        heavenly_stem = day_gan
        earthly_branch = day_zhi
    else:
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
    if USING_LUNAR_PYTHON:
        # 使用lunar-python库计算
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        hour_gan = lunar.getTimeGan()
        hour_zhi = lunar.getTimeZhi()
        
        heavenly_stem = hour_gan
        earthly_branch = hour_zhi
    else:
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
    
    # 转换为英文键名用于前端显示
    return {
        "wood": elements_count["木"],
        "fire": elements_count["火"],
        "earth": elements_count["土"],
        "metal": elements_count["金"],
        "water": elements_count["水"]
    }

def calculate_flowing_years(gender, bazi_data):
    """
    计算大运流年
    
    Args:
        gender: 性别 ("male" 或 "female")
        bazi_data: 八字数据
        
    Returns:
        list: 大运流年数据
    """
    # 计算未来10年的流年信息
    flowing_years = []
    birth_year = bazi_data.get("birthYear", datetime.datetime.now().year)
    
    # 获取日干信息，用于计算十神
    day_gan = bazi_data.get("dayHeavenlyStem", "")
    day_gan_index = TIAN_GAN.index(day_gan) if day_gan in TIAN_GAN else 0
    
    # 开始年份为今年或出生年份，取较大值
    start_year = max(birth_year, datetime.datetime.now().year)
    
    for i in range(10):  # 增加到10年
        year = start_year + i
        
        if USING_LUNAR_PYTHON:
            # 使用lunar-python库计算
            solar = Solar.fromYmd(year, 5, 1)  # 使用5月1日作为参考日期
            lunar = solar.getLunar()
            year_gan = lunar.getYearGan()
            year_zhi = lunar.getYearZhi()
            
            logging.info(f"流年计算(lunar-python): {year}年 - {year_gan}{year_zhi}")
            
            # 计算流年五行
            gan_element = FIVE_ELEMENTS[year_gan]
            zhi_element = FIVE_ELEMENTS[year_zhi]
            
            # 计算流年十神
            gan_index = TIAN_GAN.index(year_gan)
            shi_shen = calculate_shi_shen(day_gan_index, gan_index)
            
            # 计算旺衰
            wang_shuai = calculate_wang_shuai(day_gan, year_zhi)
            
            # 计算纳音
            na_yin = get_na_yin(year_gan + year_zhi)
            
            # 计算与出生年的年龄差
            age = year - birth_year + 1  # 虚岁
            
            flowing_years.append({
                "year": year,
                "heavenlyStem": year_gan,
                "earthlyBranch": year_zhi,
                "ganZhi": f"{year_gan}{year_zhi}",
                "element": gan_element,
                "zhiElement": zhi_element,
                "shiShen": shi_shen,
                "wangShuai": wang_shuai,
                "naYin": na_yin,
                "age": age
            })
        else:
            # 使用传统方法计算
            stem_index = (year - 4) % 10
            branch_index = (year - 4) % 12
            
            stem = HEAVENLY_STEMS[stem_index]
            branch = EARTHLY_BRANCHES[branch_index]
            
            logging.info(f"流年计算(传统): {year}年 - {stem}{branch}")
            
            # 计算流年五行
            gan_element = FIVE_ELEMENTS[stem]
            zhi_element = FIVE_ELEMENTS[branch]
            
            # 计算流年十神
            shi_shen = "未知"  # 默认值
            if day_gan in TIAN_GAN:
                shi_shen = calculate_shi_shen(day_gan_index, stem_index)
            
            # 计算旺衰
            wang_shuai = "未知"  # 默认值
            if day_gan in TIAN_GAN:
                wang_shuai = calculate_wang_shuai(day_gan, branch)
            
            # 计算纳音
            na_yin = get_na_yin(stem + branch)
            
            # 计算与出生年的年龄差
            age = year - birth_year + 1  # 虚岁
            
            flowing_years.append({
                "year": year,
                "heavenlyStem": stem,
                "earthlyBranch": branch,
                "ganZhi": f"{stem}{branch}",
                "element": gan_element,
                "zhiElement": zhi_element,
                "shiShen": shi_shen,
                "wangShuai": wang_shuai,
                "naYin": na_yin,
                "age": age
            })
    
    return flowing_years

def calculate_shen_sha(year, month, day, hour, gender):
    """
    计算神煞
    
    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 小时 (0-23)
        gender: 性别 ('male' 或 'female')
        
    Returns:
        dict: 神煞信息
    """
    if not USING_LUNAR_PYTHON:
        return {"shenSha": "需要lunar-python库支持"}
    
    try:
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        # 转换为农历
        lunar = solar.getLunar()
        # 获取八字对象
        bazi = lunar.getEightChar()
        
        # 获取四柱天干地支
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        hour_gan = lunar.getTimeGan()
        hour_zhi = lunar.getTimeZhi()
        
        logging.info(f"四柱: {year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}")
        
        # 获取索引
        year_gan_index = TIAN_GAN.index(year_gan)
        year_zhi_index = DI_ZHI.index(year_zhi)
        month_gan_index = TIAN_GAN.index(month_gan)
        month_zhi_index = DI_ZHI.index(month_zhi)
        day_gan_index = TIAN_GAN.index(day_gan)
        day_zhi_index = DI_ZHI.index(day_zhi)
        hour_gan_index = TIAN_GAN.index(hour_gan)
        hour_zhi_index = DI_ZHI.index(hour_zhi)
        
        # 定义生肖相冲
        SHENGXIAO_CHONG = {
            "鼠": "马", "牛": "羊", "虎": "猴", "兔": "鸡",
            "龙": "狗", "蛇": "猪", "马": "鼠", "羊": "牛",
            "猴": "虎", "鸡": "兔", "狗": "龙", "猪": "蛇"
        }
        
        # 定义建除十二神 (依据月支查询)
        JIAN_CHU = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]
        
        # 计算日冲
        day_chong_zhi = DI_ZHI[(day_zhi_index + 6) % 12]
        
        # 计算值神(建除十二神)
        # 值神的计算方法：以月支索引作为起点，然后按日支索引查询
        zhi_shen_index = (month_zhi_index + day_zhi_index) % 12
        zhi_shen = JIAN_CHU[zhi_shen_index]
        
        # 定义神煞对应表
        # 年干神煞
        YEAR_GAN_SHEN_SHA = {
            "甲": ["国印贵人", "太极贵人"],
            "乙": ["金舆", "金舆", "流霞"],
            "丙": ["驿马"],
            "丁": ["驿马", "流霞"],
            "戊": ["羊刃", "劫煞"],
            "己": ["天德贵人"],
            "庚": ["金舆", "羊刃"],
            "辛": ["天德贵人", "太极贵人"],
            "壬": ["羊刃", "金舆"],
            "癸": ["国印贵人", "太极贵人"]
        }
        
        # 年支神煞
        YEAR_ZHI_SHEN_SHA = {
            "子": ["将星", "劫煞"],
            "丑": ["灾煞", "华盖"],
            "寅": ["天德贵人", "福星贵人"],
            "卯": ["福星贵人", "天德贵人"],
            "辰": ["灾煞", "六害"],
            "巳": ["灾煞", "劫煞"],
            "午": ["将星", "灾煞"],
            "未": ["灾煞", "孤辰"],
            "申": ["天德贵人", "福星贵人"],
            "酉": ["福星贵人", "天德贵人"],
            "戌": ["华盖", "孤辰"],
            "亥": ["劫煞", "将星"]
        }
        
        # 日干神煞
        DAY_GAN_SHEN_SHA = {
            "甲": ["金舆", "太极贵人", "天乙贵人"],
            "乙": ["金舆", "天厨贵人", "太极贵人"],
            "丙": ["文昌贵人", "驿马"],
            "丁": ["驿马", "流霞"],
            "戊": ["羊刃", "天厨贵人"],
            "己": ["天德贵人", "天乙贵人"],
            "庚": ["金舆", "羊刃", "太极贵人"],
            "辛": ["天德贵人", "天厨贵人"],
            "壬": ["羊刃", "金舆", "太极贵人"],
            "癸": ["文昌贵人", "国印贵人"]
        }
        
        # 日支神煞
        DAY_ZHI_SHEN_SHA = {
            "子": ["将星", "天德贵人"],
            "丑": ["空亡", "华盖"],
            "寅": ["天德贵人", "福星贵人"],
            "卯": ["福星贵人", "天德贵人"],
            "辰": ["空亡", "六害"],
            "巳": ["亡神", "劫煞"],
            "午": ["将星", "亡神"],
            "未": ["空亡", "亡神"],
            "申": ["天德贵人", "福星贵人"],
            "酉": ["福星贵人", "天德贵人"],
            "戌": ["空亡", "孤辰"],
            "亥": ["将星", "亡神"]
        }
        
        # 收集神煞信息
        year_gan_shen_sha = YEAR_GAN_SHEN_SHA.get(year_gan, [])
        year_zhi_shen_sha = YEAR_ZHI_SHEN_SHA.get(year_zhi, [])
        day_gan_shen_sha = DAY_GAN_SHEN_SHA.get(day_gan, [])
        day_zhi_shen_sha = DAY_ZHI_SHEN_SHA.get(day_zhi, [])
        
        # 合并本命神煞
        ben_ming = []
        for shen_sha_list in [year_gan_shen_sha, year_zhi_shen_sha, day_gan_shen_sha, day_zhi_shen_sha]:
            for item in shen_sha_list:
                if item not in ben_ming:
                    ben_ming.append(item)
        
        # 获取方位信息
        try:
            xi_shen = lunar.getDayPositionXiDesc()
            fu_shen = lunar.getDayPositionFuDesc()
            cai_shen = lunar.getDayPositionCaiDesc()
            peng_zu_gan = lunar.getPengZuGan()
            peng_zu_zhi = lunar.getPengZuZhi()
        except Exception as e:
            logging.error(f"获取方位信息出错: {str(e)}")
            xi_shen = "未知"
            fu_shen = "未知"
            cai_shen = "未知"
            peng_zu_gan = "未知"
            peng_zu_zhi = "未知"
        
        # 确保所有神煞列表都有值
        if not year_gan_shen_sha:
            year_gan_shen_sha = ["无特殊神煞"]
        if not year_zhi_shen_sha:
            year_zhi_shen_sha = ["无特殊神煞"]
        if not day_gan_shen_sha:
            day_gan_shen_sha = ["无特殊神煞"]
        if not day_zhi_shen_sha:
            day_zhi_shen_sha = ["无特殊神煞"]
        if not ben_ming:
            ben_ming = ["无特殊神煞"]
        
        shen_sha = {
            # 日冲（与日支对冲的生肖）
            "dayChong": f"{day_zhi}日冲{day_chong_zhi}",
            # 值神（建除十二神）
            "zhiShen": zhi_shen,
            # 喜神方位
            "xiShen": xi_shen,
            # 福神方位
            "fuShen": fu_shen,
            # 财神方位
            "caiShen": cai_shen,
            # 彭祖百忌
            "pengZuGan": peng_zu_gan,
            "pengZuZhi": peng_zu_zhi,
            # 本命神煞
            "benMing": ben_ming,
            # 分类存储神煞信息
            "yearGan": year_gan_shen_sha,  # 年干神煞
            "yearZhi": year_zhi_shen_sha,  # 年支神煞
            "monthGan": [],  # 月干神煞
            "monthZhi": [],  # 月支神煞
            "dayGan": day_gan_shen_sha,   # 日干神煞
            "dayZhi": day_zhi_shen_sha,   # 日支神煞
            "hourGan": [],  # 时干神煞
            "hourZhi": []   # 时支神煞
        }
        
        logging.info(f"神煞计算结果: 值神={zhi_shen}, 日冲={day_chong_zhi}, 本命神煞数量={len(ben_ming)}")
        return shen_sha
    except Exception as e:
        logging.error(f"计算神煞时出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {
            "dayChong": "计算失败",
            "zhiShen": "计算失败",
            "pengZuGan": "计算失败",
            "pengZuZhi": "计算失败",
            "xiShen": "计算失败",
            "fuShen": "计算失败",
            "caiShen": "计算失败",
            "benMing": ["计算失败"],
            "yearGan": ["计算失败"],
            "yearZhi": ["计算失败"],
            "dayGan": ["计算失败"],
            "dayZhi": ["计算失败"]
        }

def calculate_da_yun(year, month, day, hour, gender):
    """
    计算大运和流年
    
    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 小时 (0-23)
        gender: 性别 ('male' 或 'female')
        
    Returns:
        dict: 大运和流年信息
    """
    if not USING_LUNAR_PYTHON:
        return {"daYun": [], "liuNian": []}
    
    try:
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        # 转换为农历
        lunar = solar.getLunar()
        # 获取八字对象
        bazi = lunar.getEightChar()
        
        # 获取性别
        if gender == 'male':
            gender_code = 1
        else:
            gender_code = 0
            
        # 获取起运时间
        try:
            start_age = bazi.getStartAge()
            start_year = bazi.getStartYear()
            logging.info(f"起运年龄: {start_age}岁, 起运年份: {start_year}年")
        except Exception as e:
            logging.error(f"获取起运时间出错: {str(e)}")
            # 估算起运时间 (传统方法：男阳女阴顺行，男阴女阳逆行，从出生后100天左右起运)
            birth_date = datetime.date(year, month, day)
            today = datetime.date.today()
            days_diff = (today - birth_date).days
            months_diff = days_diff // 30
            start_age = max(0, months_diff // 12)  # 确保不为负数
            start_year = year + start_age
            logging.info(f"估算起运年龄: {start_age}岁, 起运年份: {start_year}年")
        
        # 如果起运年龄为0，重新计算
        if start_age == 0 or start_year == 0:
            # 根据性别和月柱阴阳判断是否逆行
            # 估算起运时间 (传统方法：男阳女阴顺行，男阴女阳逆行，起运时间在3-30岁之间)
            year_gan = lunar.getYearGan()
            year_gan_idx = TIAN_GAN.index(year_gan)
            is_yang = year_gan_idx % 2 == 0  # 甲丙戊庚壬为阳，乙丁己辛癸为阴
            
            # 计算起运时间
            if (is_yang and gender == 'male') or (not is_yang and gender == 'female'):
                # 男阳女阴起运早
                start_age = 1 + year % 6  # 简化起运计算
            else:
                # 男阴女阳起运晚
                start_age = 4 + year % 6  # 简化起运计算
                
            start_year = year + start_age
            logging.info(f"重新计算起运年龄: {start_age}岁, 起运年份: {start_year}年")
        
        # 获取当前年份
        current_year = datetime.datetime.now().year
        
        # 计算大运数组
        da_yun_count = 10  # 显示10个大运
        da_yun_list = []
        
        # 获取月柱
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        
        logging.info(f"月柱: {month_gan}{month_zhi}")
        
        # 获取起始干支索引
        gan_index = TIAN_GAN.index(month_gan)
        zhi_index = DI_ZHI.index(month_zhi)
        
        # 阴阳顺逆行
        # 阳男阴女顺行，阴男阳女逆行
        is_forward = ((TIAN_GAN.index(lunar.getYearGan()) % 2 == 0) and gender_code == 1) or \
                     ((TIAN_GAN.index(lunar.getYearGan()) % 2 == 1) and gender_code == 0)
        
        logging.info(f"大运行进方向: {'顺行' if is_forward else '逆行'}")
        
        # 初始化生肖查询表
        SHENG_XIAO = LunarUtil.ANIMAL
        
        for i in range(da_yun_count):
            # 计算当前大运干支索引
            if is_forward:
                current_gan_index = (gan_index + i) % 10
                current_zhi_index = (zhi_index + i) % 12
            else:
                current_gan_index = (gan_index - i) % 10
                current_zhi_index = (zhi_index - i) % 12
                if current_gan_index < 0:
                    current_gan_index += 10
                if current_zhi_index < 0:
                    current_zhi_index += 12
            
            # 获取大运干支
            da_yun_gan = TIAN_GAN[current_gan_index]
            da_yun_zhi = DI_ZHI[current_zhi_index]
            
            # 计算大运开始年龄和年份
            start_age_current = start_age + 10 * i
            start_year_current = start_year + 10 * i
            end_age_current = start_age_current + 9
            end_year_current = start_year_current + 9
            
            # 计算大运五行
            da_yun_gan_wuxing = get_wuxing(da_yun_gan)
            da_yun_zhi_wuxing = get_wuxing(da_yun_zhi)
            
            # 计算流年信息（只显示大运范围内的流年）
            liu_nian_list = []
            
            # 判断是否显示流年（只显示当前大运和下一个大运的流年）
            show_liu_nian = (current_year >= start_year_current and current_year <= end_year_current) or \
                            (current_year >= start_year_current - 10 and current_year <= end_year_current - 10)
            
            if show_liu_nian:
                # 显示10年流年
                for j in range(10):
                    liu_nian_year = start_year_current + j
                    liu_nian_age = start_age_current + j
                    
                    # 计算流年干支
                    base_year = 1984  # 甲子年
                    offset = (liu_nian_year - base_year) % 60
                    liu_nian_gan = TIAN_GAN[offset % 10]
                    liu_nian_zhi = DI_ZHI[offset % 12]
                    
                    # 获取流年生肖
                    liu_nian_shengxiao = SHENG_XIAO[offset % 12]
                    
                    # 计算流年五行
                    liu_nian_gan_wuxing = get_wuxing(liu_nian_gan)
                    liu_nian_zhi_wuxing = get_wuxing(liu_nian_zhi)
                    
                    # 计算流年与大运天干地支的关系
                    liu_nian_relations = {
                        "ganRelation": get_gan_relation(da_yun_gan, liu_nian_gan),
                        "zhiRelation": get_zhi_relation(da_yun_zhi, liu_nian_zhi)
                    }
                    
                    # 计算流年神煞
                    try:
                        liu_nian_shen_sha = calculate_liu_nian_shen_sha(liu_nian_gan, liu_nian_zhi)
                    except Exception as e:
                        logging.error(f"计算流年神煞出错: {str(e)}")
                        liu_nian_shen_sha = ["计算失败"]
                    
                    # 计算岁运（太岁、太阴、太阳）
                    try:
                        tai_yin = calculate_tai_yin(liu_nian_zhi)
                        tai_yang = calculate_tai_yang(liu_nian_zhi)
                    except Exception as e:
                        logging.error(f"计算太阴太阳出错: {str(e)}")
                        tai_yin = "计算失败"
                        tai_yang = "计算失败"
                        
                    sui_yun = {
                        "taiSui": f"太岁{liu_nian_gan}{liu_nian_zhi}",
                        "taiYin": tai_yin,
                        "taiYang": tai_yang
                    }
                    
                    # 当前是否为今年
                    is_current = liu_nian_year == current_year
                    
                    liu_nian_list.append({
                        "year": liu_nian_year,
                        "age": liu_nian_age,
                        "gan": liu_nian_gan,
                        "zhi": liu_nian_zhi,
                        "ganZhi": f"{liu_nian_gan}{liu_nian_zhi}",
                        "ganWuxing": liu_nian_gan_wuxing,
                        "zhiWuxing": liu_nian_zhi_wuxing,
                        "shengXiao": liu_nian_shengxiao,
                        "relations": liu_nian_relations,
                        "shenSha": liu_nian_shen_sha,
                        "suiYun": sui_yun,
                        "isCurrent": is_current
                    })
            
            # 当前是否为当前大运
            is_current_da_yun = (current_year >= start_year_current and current_year <= end_year_current)
            
            da_yun_list.append({
                "index": i + 1,
                "startAge": start_age_current,
                "endAge": end_age_current,
                "startYear": start_year_current,
                "endYear": end_year_current,
                "gan": da_yun_gan,
                "zhi": da_yun_zhi,
                "ganZhi": f"{da_yun_gan}{da_yun_zhi}",
                "ganWuxing": da_yun_gan_wuxing,
                "zhiWuxing": da_yun_zhi_wuxing,
                "isCurrent": is_current_da_yun,
                "liuNian": liu_nian_list
            })
        
        result = {
            "startAge": start_age,
            "startYear": start_year,
            "daYun": da_yun_list
        }
        
        logging.info(f"大运计算完成，共{len(da_yun_list)}个大运，起运年龄: {start_age}岁")
        return result
    except Exception as e:
        logging.error(f"计算大运时出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {
            "startAge": 1,
            "startYear": year + 1,
            "daYun": [],
            "error": str(e)
        }

def calculate_liu_nian_shen_sha(liu_nian_gan, liu_nian_zhi):
    """
    计算流年神煞
    
    Args:
        liu_nian_gan: 流年天干
        liu_nian_zhi: 流年地支
        
    Returns:
        dict: 流年神煞信息
    """
    # 流年神煞表（简化版）
    LIU_NIAN_GAN_SHEN_SHA = {
        "甲": ["天德贵人", "太极贵人"],
        "乙": ["金舆", "流霞"],
        "丙": ["驿马", "文昌贵人"],
        "丁": ["驿马", "流霞"],
        "戊": ["羊刃", "劫煞"],
        "己": ["天德贵人", "天乙贵人"],
        "庚": ["金舆", "羊刃"],
        "辛": ["天德贵人", "太极贵人"],
        "壬": ["羊刃", "金舆"],
        "癸": ["国印贵人", "太极贵人"]
    }
    
    LIU_NIAN_ZHI_SHEN_SHA = {
        "子": ["将星", "劫煞"],
        "丑": ["灾煞", "华盖"],
        "寅": ["天德贵人", "福星贵人"],
        "卯": ["福星贵人", "天德贵人"],
        "辰": ["灾煞", "六害"],
        "巳": ["灾煞", "劫煞"],
        "午": ["将星", "灾煞"],
        "未": ["灾煞", "孤辰"],
        "申": ["天德贵人", "福星贵人"],
        "酉": ["福星贵人", "天德贵人"],
        "戌": ["华盖", "孤辰"],
        "亥": ["劫煞", "将星"]
    }
    
    # 获取流年神煞
    gan_shen_sha = LIU_NIAN_GAN_SHEN_SHA.get(liu_nian_gan, [])
    zhi_shen_sha = LIU_NIAN_ZHI_SHEN_SHA.get(liu_nian_zhi, [])
    
    # 合并神煞
    all_shen_sha = []
    for shen_sha_list in [gan_shen_sha, zhi_shen_sha]:
        for item in shen_sha_list:
            if item not in all_shen_sha:
                all_shen_sha.append(item)
    
    return all_shen_sha

def calculate_tai_yin(liu_nian_zhi):
    """
    计算太阴位置
    
    Args:
        liu_nian_zhi: 流年地支
        
    Returns:
        str: 太阴位置
    """
    tai_yin_map = {
        "子": "亥",
        "丑": "戌",
        "寅": "酉",
        "卯": "申",
        "辰": "未",
        "巳": "午",
        "午": "巳",
        "未": "辰",
        "申": "卯",
        "酉": "寅",
        "戌": "丑",
        "亥": "子"
    }
    
    return f"太阴{tai_yin_map.get(liu_nian_zhi, '')}"

def calculate_tai_yang(liu_nian_zhi):
    """
    计算太阳位置
    
    Args:
        liu_nian_zhi: 流年地支
        
    Returns:
        str: 太阳位置
    """
    tai_yang_map = {
        "子": "巳",
        "丑": "午",
        "寅": "未",
        "卯": "申",
        "辰": "酉",
        "巳": "戌",
        "午": "亥",
        "未": "子",
        "申": "丑",
        "酉": "寅",
        "戌": "卯",
        "亥": "辰"
    }
    
    return f"太阳{tai_yang_map.get(liu_nian_zhi, '')}"

def calculate_bazi(birth_date, birth_time, gender):
    """
    计算八字命盘信息
    
    Args:
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间，格式为 HH:MM 或 "子时 (23:00-01:00)" 等
        gender: 性别，'male' 或 'female'
        
    Returns:
        dict: 八字命盘信息
    """
    try:
        logging.info(f"开始计算八字: {birth_date}, {birth_time}, {gender}")
        
        # 解析出生日期和时间
        birth_info = parse_birth_date_time(birth_date, birth_time)
        
        # 获取年、月、日、时
        year = birth_info["year"]
        month = birth_info["month"]
        day = birth_info["day"]
        hour = birth_info["hour"]
        
        logging.info(f"解析出生信息: 年={year}, 月={month}, 日={day}, 时={hour}")
        
        # 计算年柱
        year_pillar = get_year_pillar(year)
        logging.info(f"年柱: {year_pillar}")
        
        # 计算月柱
        month_pillar = get_month_pillar(year, month, day)
        logging.info(f"月柱: {month_pillar}")
        
        # 计算日柱
        day_pillar = get_day_pillar(year, month, day)
        logging.info(f"日柱: {day_pillar}")
        
        # 计算时柱
        hour_pillar = get_hour_pillar(year, month, day, hour)
        logging.info(f"时柱: {hour_pillar}")
        
        # 获取出生年份
        birth_year = year
        
        # 合并八字信息
        bazi_data = {
            "yearPillar": year_pillar,
            "monthPillar": month_pillar,
            "dayPillar": day_pillar,
            "hourPillar": hour_pillar,
            "birthYear": birth_year,
            "yearHeavenlyStem": year_pillar.get("heavenlyStem", "未知"),
            "yearEarthlyBranch": year_pillar.get("earthlyBranch", "未知"),
            "monthHeavenlyStem": month_pillar.get("heavenlyStem", "未知"),
            "monthEarthlyBranch": month_pillar.get("earthlyBranch", "未知"),
            "dayHeavenlyStem": day_pillar.get("heavenlyStem", "未知"),
            "dayEarthlyBranch": day_pillar.get("earthlyBranch", "未知"),
            "hourHeavenlyStem": hour_pillar.get("heavenlyStem", "未知"),
            "hourEarthlyBranch": hour_pillar.get("earthlyBranch", "未知"),
            "eightChar": {
                "year": f"{year_pillar.get('heavenlyStem', '未知')}{year_pillar.get('earthlyBranch', '未知')}",
                "month": f"{month_pillar.get('heavenlyStem', '未知')}{month_pillar.get('earthlyBranch', '未知')}",
                "day": f"{day_pillar.get('heavenlyStem', '未知')}{day_pillar.get('earthlyBranch', '未知')}",
                "hour": f"{hour_pillar.get('heavenlyStem', '未知')}{hour_pillar.get('earthlyBranch', '未知')}"
            }
        }
        
        logging.info("计算五行分布")
        # 计算五行分布
        try:
            five_elements = calculate_five_elements(bazi_data)
            bazi_data["fiveElements"] = five_elements
            logging.info(f"五行分布: {five_elements}")
        except Exception as e:
            logging.error(f"计算五行分布时出错: {str(e)}")
            bazi_data["fiveElements"] = {"metal": 0, "wood": 0, "water": 0, "fire": 0, "earth": 0}
        
        logging.info("计算神煞")
        # 计算神煞
        try:
            shen_sha = calculate_shen_sha(year, month, day, hour, gender)
            bazi_data["shenSha"] = shen_sha
            logging.info(f"神煞: {shen_sha}")
        except Exception as e:
            logging.error(f"计算神煞时出错: {str(e)}")
            bazi_data["shenSha"] = {
                "dayChong": "未知",
                "zhiShen": "未知",
                "pengZuGan": "未知",
                "pengZuZhi": "未知",
                "xiShen": "未知",
                "fuShen": "未知",
                "caiShen": "未知",
                "benMing": [],
                "yearGan": [],
                "yearZhi": [],
                "dayGan": [],
                "dayZhi": []
            }
        
        logging.info("计算大运")
        # 计算大运
        try:
            da_yun = calculate_da_yun(year, month, day, hour, gender)
            bazi_data["daYun"] = da_yun
            logging.info(f"大运起运年龄: {da_yun.get('startAge', 0)}岁, 起运年份: {da_yun.get('startYear', 0)}年")
        except Exception as e:
            logging.error(f"计算大运时出错: {str(e)}")
            bazi_data["daYun"] = {"startAge": 0, "startYear": 0, "daYun": []}
        
        logging.info("计算流年")
        # 计算流年
        try:
            flowing_years = calculate_flowing_years(gender, bazi_data)
            bazi_data["flowingYears"] = flowing_years
            logging.info(f"流年数量: {len(flowing_years)}")
        except Exception as e:
            logging.error(f"计算流年时出错: {str(e)}")
            bazi_data["flowingYears"] = []
        
        # 计算各柱十神
        try:
            bazi_data["shiShen"] = {}
            day_gan_index = TIAN_GAN.index(day_pillar.get("heavenlyStem", "甲"))
            
            # 年干十神
            year_gan_index = TIAN_GAN.index(year_pillar.get("heavenlyStem", "甲"))
            bazi_data["shiShen"]["year"] = calculate_shi_shen(day_gan_index, year_gan_index)
            
            # 月干十神
            month_gan_index = TIAN_GAN.index(month_pillar.get("heavenlyStem", "甲"))
            bazi_data["shiShen"]["month"] = calculate_shi_shen(day_gan_index, month_gan_index)
            
            # 时干十神
            hour_gan_index = TIAN_GAN.index(hour_pillar.get("heavenlyStem", "甲"))
            bazi_data["shiShen"]["hour"] = calculate_shi_shen(day_gan_index, hour_gan_index)
            logging.info("计算十神完成")
        except Exception as e:
            logging.error(f"计算十神时出错: {str(e)}")
            bazi_data["shiShen"] = {"year": "未知", "month": "未知", "hour": "未知"}
        
        # 各柱旺衰
        try:
            bazi_data["wangShuai"] = {}
            bazi_data["wangShuai"]["year"] = calculate_wang_shuai(day_pillar.get("heavenlyStem", "甲"), year_pillar.get("earthlyBranch", "子"))
            bazi_data["wangShuai"]["month"] = calculate_wang_shuai(day_pillar.get("heavenlyStem", "甲"), month_pillar.get("earthlyBranch", "子"))
            bazi_data["wangShuai"]["day"] = calculate_wang_shuai(day_pillar.get("heavenlyStem", "甲"), day_pillar.get("earthlyBranch", "子"))
            bazi_data["wangShuai"]["hour"] = calculate_wang_shuai(day_pillar.get("heavenlyStem", "甲"), hour_pillar.get("earthlyBranch", "子"))
            logging.info("计算旺衰完成")
        except Exception as e:
            logging.error(f"计算旺衰时出错: {str(e)}")
            bazi_data["wangShuai"] = {"year": "未知", "month": "未知", "day": "未知", "hour": "未知"}
        
        # 纳音五行
        try:
            bazi_data["naYin"] = {}
            bazi_data["naYin"]["year"] = get_na_yin(year_pillar.get("heavenlyStem", "甲") + year_pillar.get("earthlyBranch", "子"))
            bazi_data["naYin"]["month"] = get_na_yin(month_pillar.get("heavenlyStem", "甲") + month_pillar.get("earthlyBranch", "子"))
            bazi_data["naYin"]["day"] = get_na_yin(day_pillar.get("heavenlyStem", "甲") + day_pillar.get("earthlyBranch", "子"))
            bazi_data["naYin"]["hour"] = get_na_yin(hour_pillar.get("heavenlyStem", "甲") + hour_pillar.get("earthlyBranch", "子"))
            logging.info("计算纳音五行完成")
        except Exception as e:
            logging.error(f"计算纳音五行时出错: {str(e)}")
            bazi_data["naYin"] = {"year": "未知", "month": "未知", "day": "未知", "hour": "未知"}
        
        logging.info("八字计算完成")
        return bazi_data
    
    except Exception as e:
        logging.error(f"计算八字出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        # 返回空数据以避免程序崩溃
        return {
            "yearPillar": {"heavenlyStem": "未知", "earthlyBranch": "未知", "element": "未知"},
            "monthPillar": {"heavenlyStem": "未知", "earthlyBranch": "未知", "element": "未知"},
            "dayPillar": {"heavenlyStem": "未知", "earthlyBranch": "未知", "element": "未知"},
            "hourPillar": {"heavenlyStem": "未知", "earthlyBranch": "未知", "element": "未知"},
            "fiveElements": {"metal": 0, "wood": 0, "water": 0, "fire": 0, "earth": 0},
            "shenSha": {"dayChong": "未知", "zhiShen": "未知", "benMing": [], "yearGan": [], "yearZhi": [], "dayGan": [], "dayZhi": []},
            "daYun": {"startAge": 0, "startYear": 0, "daYun": []},
            "flowingYears": []
        }

# 添加兼容性函数，为了解决导入错误
def get_bazi(birth_date, birth_time, gender):
    """
    计算八字（兼容性函数）
    
    Args:
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间，可以是 HH:MM 或者 "子时 (23:00-01:00)" 等中文时辰
        gender: 性别，'male' 或 'female'
        
    Returns:
        dict: 八字数据
    """
    logging.info(f"调用get_bazi兼容函数: {birth_date}, {birth_time}, {gender}")
    return calculate_bazi(birth_date, birth_time, gender)

# 添加格式化函数，为了兼容之前的代码
def format_bazi_analysis(bazi_data):
    """
    格式化八字分析数据，生成DeepSeek API需要的提示内容
    
    Args:
        bazi_data: 由calculate_bazi或get_bazi返回的八字数据
        
    Returns:
        dict: 格式化后的八字数据，包含bazi, shen_sha, qi_yun, da_yun等字段
    """
    logging.info("格式化八字数据")
    
    # 从新版bazi_data中提取信息
    year_pillar = bazi_data.get("yearPillar", {})
    month_pillar = bazi_data.get("monthPillar", {})
    day_pillar = bazi_data.get("dayPillar", {})
    hour_pillar = bazi_data.get("hourPillar", {})
    five_elements = bazi_data.get("fiveElements", {})
    flowing_years = bazi_data.get("flowingYears", [])
    
    # 格式化八字
    bazi_str = f"{year_pillar.get('heavenlyStem', '')}{year_pillar.get('earthlyBranch', '')}，"
    bazi_str += f"{month_pillar.get('heavenlyStem', '')}{month_pillar.get('earthlyBranch', '')}，"
    bazi_str += f"{day_pillar.get('heavenlyStem', '')}{day_pillar.get('earthlyBranch', '')}，"
    bazi_str += f"{hour_pillar.get('heavenlyStem', '')}{hour_pillar.get('earthlyBranch', '')}"
    
    # 格式化神煞（简化版本）
    shen_sha_str = "此版本暂无神煞信息\n"
    
    # 格式化大运（简化版本）
    qi_yun_str = "起运：根据八字推算，命主将于近期交运"
    
    # 格式化流年信息
    da_yun_table = "五行\t流年\t干支\t年份\n"
    for yun in flowing_years:
        da_yun_table += f"{yun.get('element', '')}\t流年\t{yun.get('heavenlyStem', '')}{yun.get('earthlyBranch', '')}\t{yun.get('year', '')}\n"
    
    # 格式化五行信息
    wu_xing_info = f"五行统计：金 {five_elements.get('metal', 0)}，木 {five_elements.get('wood', 0)}，"
    wu_xing_info += f"水 {five_elements.get('water', 0)}，火 {five_elements.get('fire', 0)}，土 {five_elements.get('earth', 0)}"
    
    return {
        "bazi": bazi_str,
        "shen_sha": shen_sha_str,
        "qi_yun": qi_yun_str,
        "da_yun": da_yun_table,
        "wu_xing": wu_xing_info
    }

def get_wuxing(character):
    """
    获取天干或地支的五行属性
    
    Args:
        character: 天干或地支字符
        
    Returns:
        str: 五行属性
    """
    wu_xing_map = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水",
        "寅": "木", "卯": "木",
        "巳": "火", "午": "火",
        "丑": "土", "辰": "土", "未": "土", "戌": "土",
        "申": "金", "酉": "金",
        "子": "水", "亥": "水"
    }
    
    return wu_xing_map.get(character, "未知")

def get_gan_relation(gan1, gan2):
    """
    计算两个天干之间的关系
    
    Args:
        gan1: 第一个天干
        gan2: 第二个天干
        
    Returns:
        str: 关系名称
    """
    # 获取天干的五行
    wu_xing1 = get_wuxing(gan1)
    wu_xing2 = get_wuxing(gan2)
    
    # 确定阴阳
    is_yang1 = TIAN_GAN.index(gan1) % 2 == 0
    is_yang2 = TIAN_GAN.index(gan2) % 2 == 0
    
    # 相同五行
    if wu_xing1 == wu_xing2:
        if is_yang1 == is_yang2:
            return "比肩"
        else:
            return "劫财"
    
    # 五行生克关系
    wu_xing_sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    wu_xing_ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    if wu_xing_sheng.get(wu_xing1) == wu_xing2:
        return "食神" if is_yang1 == is_yang2 else "伤官"
    elif wu_xing_sheng.get(wu_xing2) == wu_xing1:
        return "正印" if is_yang1 == is_yang2 else "偏印"
    elif wu_xing_ke.get(wu_xing1) == wu_xing2:
        return "正财" if is_yang1 == is_yang2 else "偏财"
    elif wu_xing_ke.get(wu_xing2) == wu_xing1:
        return "正官" if is_yang1 == is_yang2 else "七杀"
    
    return "未知"

def get_zhi_relation(zhi1, zhi2):
    """
    计算两个地支之间的关系
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
        
    Returns:
        str: 关系名称
    """
    # 地支索引
    index1 = DI_ZHI.index(zhi1)
    index2 = DI_ZHI.index(zhi2)
    
    # 六冲
    if abs(index1 - index2) == 6:
        return "六冲"
    
    # 三合
    san_he = [
        ["寅", "午", "戌"],  # 火局三合
        ["亥", "卯", "未"],  # 木局三合
        ["申", "子", "辰"],  # 水局三合
        ["巳", "酉", "丑"]   # 金局三合
    ]
    
    for he in san_he:
        if zhi1 in he and zhi2 in he:
            return "三合"
    
    # 六合
    liu_he = [
        ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
        ("辰", "酉"), ("巳", "申"), ("午", "未")
    ]
    
    for he in liu_he:
        if (zhi1 == he[0] and zhi2 == he[1]) or (zhi1 == he[1] and zhi2 == he[0]):
            return "六合"
    
    # 三会
    san_hui = [
        ["寅", "卯", "辰"],  # 东方三会
        ["巳", "午", "未"],  # 南方三会
        ["申", "酉", "戌"],  # 西方三会
        ["亥", "子", "丑"]   # 北方三会
    ]
    
    for hui in san_hui:
        if zhi1 in hui and zhi2 in hui:
            return "三会"
    
    # 相刑
    xiang_xing = [
        ("子", "卯"), ("卯", "子"), ("丑", "戌"), ("戌", "丑"), 
        ("寅", "巳"), ("巳", "申"), ("申", "寅"),
        ("辰", "辰"), ("午", "午"), ("酉", "酉"), ("亥", "亥")
    ]
    
    for xing in xiang_xing:
        if (zhi1 == xing[0] and zhi2 == xing[1]):
            return "相刑"
    
    # 相害
    xiang_hai = [
        ("子", "未"), ("丑", "午"), ("寅", "巳"),
        ("卯", "辰"), ("申", "亥"), ("酉", "戌")
    ]
    
    for hai in xiang_hai:
        if (zhi1 == hai[0] and zhi2 == hai[1]) or (zhi1 == hai[1] and zhi2 == hai[0]):
            return "相害"
    
    return "无关系"

# 添加缺失的函数
def calculate_shi_shen(day_gan_index, target_gan_index):
    """
    计算十神
    
    Args:
        day_gan_index: 日干索引
        target_gan_index: 目标天干索引
        
    Returns:
        str: 十神名称
    """
    try:
        # 十神计算规则
        diff = (target_gan_index - day_gan_index) % 10
        
        if day_gan_index % 2 == 0:  # 阳干日主
            shi_shen_map = {
                0: "比肩", 1: "劫财", 
                2: "食神", 3: "伤官", 
                4: "偏财", 5: "正财", 
                6: "七杀", 7: "正官", 
                8: "偏印", 9: "正印"
            }
        else:  # 阴干日主
            shi_shen_map = {
                0: "比肩", 9: "劫财", 
                8: "食神", 7: "伤官", 
                6: "偏财", 5: "正财", 
                4: "七杀", 3: "正官", 
                2: "偏印", 1: "正印"
            }
        
        return shi_shen_map.get(diff, "未知")
    except Exception as e:
        logging.error(f"计算十神出错: {str(e)}")
        return "未知"

def calculate_wang_shuai(day_gan, target_zhi):
    """
    计算各柱旺衰
    
    Args:
        day_gan: 日干
        target_zhi: 目标地支
        
    Returns:
        str: 旺衰状态
    """
    try:
        # 获取日干五行
        day_gan_wuxing = get_wuxing(day_gan)
        # 获取目标地支五行
        target_zhi_wuxing = get_wuxing(target_zhi)
        
        # 五行生克关系
        sheng_ke = {
            "木": {"生": "火", "克": "土", "被生": "水", "被克": "金"},
            "火": {"生": "土", "克": "金", "被生": "木", "被克": "水"},
            "土": {"生": "金", "克": "水", "被生": "火", "被克": "木"},
            "金": {"生": "水", "克": "木", "被生": "土", "被克": "火"},
            "水": {"生": "木", "克": "火", "被生": "金", "被克": "土"}
        }
        
        relation = "平"
        
        # 判断关系
        if target_zhi_wuxing == day_gan_wuxing:
            relation = "旺"
        elif sheng_ke[day_gan_wuxing]["生"] == target_zhi_wuxing:
            relation = "相"
        elif sheng_ke[day_gan_wuxing]["克"] == target_zhi_wuxing:
            relation = "休"
        elif sheng_ke[day_gan_wuxing]["被生"] == target_zhi_wuxing:
            relation = "死"
        elif sheng_ke[day_gan_wuxing]["被克"] == target_zhi_wuxing:
            relation = "囚"
        
        return relation
    except Exception as e:
        logging.error(f"计算旺衰出错: {str(e)}")
        return "未知"

def get_na_yin(gan_zhi):
    """
    计算纳音五行
    
    Args:
        gan_zhi: 干支组合，如"甲子"
        
    Returns:
        str: 纳音五行
    """
    try:
        # 纳音五行对照表
        na_yin_map = {
            "甲子": "海中金", "乙丑": "海中金",
            "丙寅": "炉中火", "丁卯": "炉中火",
            "戊辰": "大林木", "己巳": "大林木",
            "庚午": "路旁土", "辛未": "路旁土",
            "壬申": "剑锋金", "癸酉": "剑锋金",
            "甲戌": "山头火", "乙亥": "山头火",
            "丙子": "涧下水", "丁丑": "涧下水",
            "戊寅": "城头土", "己卯": "城头土",
            "庚辰": "白蜡金", "辛巳": "白蜡金",
            "壬午": "杨柳木", "癸未": "杨柳木",
            "甲申": "泉中水", "乙酉": "泉中水",
            "丙戌": "屋上土", "丁亥": "屋上土",
            "戊子": "霹雳火", "己丑": "霹雳火",
            "庚寅": "松柏木", "辛卯": "松柏木",
            "壬辰": "长流水", "癸巳": "长流水",
            "甲午": "砂石金", "乙未": "砂石金",
            "丙申": "山下火", "丁酉": "山下火",
            "戊戌": "平地木", "己亥": "平地木",
            "庚子": "壁上土", "辛丑": "壁上土",
            "壬寅": "金薄金", "癸卯": "金薄金",
            "甲辰": "覆灯火", "乙巳": "覆灯火",
            "丙午": "天河水", "丁未": "天河水",
            "戊申": "大驿土", "己酉": "大驿土",
            "庚戌": "钗钏金", "辛亥": "钗钏金",
            "壬子": "桑柘木", "癸丑": "桑柘木",
            "甲寅": "大溪水", "乙卯": "大溪水",
            "丙辰": "沙中土", "丁巳": "沙中土",
            "戊午": "天上火", "己未": "天上火",
            "庚申": "石榴木", "辛酉": "石榴木",
            "壬戌": "大海水", "癸亥": "大海水"
        }
        
        return na_yin_map.get(gan_zhi, "未知")
    except Exception as e:
        logging.error(f"计算纳音五行出错: {str(e)}")
        return "未知"

# 使用示例
if __name__ == "__main__":
    # 测试
    test_date = "2025-05-27"
    test_time = "12:00"
    test_gender = "male"
    
    result = calculate_bazi(test_date, test_time, test_gender)
    print(f"年柱: {result['yearPillar']['heavenlyStem']}{result['yearPillar']['earthlyBranch']}")
    print(f"月柱: {result['monthPillar']['heavenlyStem']}{result['monthPillar']['earthlyBranch']}")
    print(f"日柱: {result['dayPillar']['heavenlyStem']}{result['dayPillar']['earthlyBranch']}")
    print(f"时柱: {result['hourPillar']['heavenlyStem']}{result['hourPillar']['earthlyBranch']}")
    print(f"五行: {result['fiveElements']}")
    print(f"流年: {[(y['year'], y['heavenlyStem'] + y['earthlyBranch']) for y in result['flowingYears']]}") 