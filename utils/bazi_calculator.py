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
    # 计算未来5年的流年信息
    flowing_years = []
    birth_year = bazi_data.get("birthYear", datetime.datetime.now().year)
    
    # 开始年份为今年或出生年份，取较大值
    start_year = max(birth_year, datetime.datetime.now().year)
    
    for i in range(5):
        year = start_year + i
        
        if USING_LUNAR_PYTHON:
            # 使用lunar-python库计算
            solar = Solar.fromYmd(year, 5, 1)  # 使用5月1日作为参考日期
            lunar = solar.getLunar()
            year_gan = lunar.getYearGan()
            year_zhi = lunar.getYearZhi()
            
            logging.info(f"流年计算(lunar-python): {year}年 - {year_gan}{year_zhi}")
            
            flowing_years.append({
                "year": year,
                "heavenlyStem": year_gan,
                "earthlyBranch": year_zhi,
                "element": FIVE_ELEMENTS[year_gan]
            })
        else:
            # 使用传统方法计算
            stem_index = (year - 4) % 10
            branch_index = (year - 4) % 12
            
            stem = HEAVENLY_STEMS[stem_index]
            branch = EARTHLY_BRANCHES[branch_index]
            
            logging.info(f"流年计算(传统): {year}年 - {stem}{branch}")
            
            flowing_years.append({
                "year": year,
                "heavenlyStem": stem,
                "earthlyBranch": branch,
                "element": FIVE_ELEMENTS[stem]
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
        
        # 定义生肖相冲
        SHENGXIAO_CHONG = {
            "鼠": "马", "牛": "羊", "虎": "猴", "兔": "鸡",
            "龙": "狗", "蛇": "猪", "马": "鼠", "羊": "牛",
            "猴": "虎", "鸡": "兔", "狗": "龙", "猪": "蛇"
        }
        
        # 获取基本神煞信息
        day_shengxiao = lunar.getDayShengXiao()
        # 定义建除十二神
        JIAN_CHU = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]
        
        # 获取日支索引
        day_zhi = lunar.getDayZhi()
        day_zhi_index = DI_ZHI.index(day_zhi)
        
        shen_sha = {
            # 日冲（与日支对冲的生肖）
            "dayChong": f"{day_shengxiao}日冲{SHENGXIAO_CHONG.get(day_shengxiao, '')}",
            # 建除十二值神
            "zhiShen": JIAN_CHU[day_zhi_index % 12],
            # 彭祖百忌
            "pengZuGan": f"{lunar.getDayGan()}不开仓",  # 简化的彭祖百忌
            "pengZuZhi": f"{lunar.getDayZhi()}不远行",  # 简化的彭祖百忌
            # 喜神方位
            "xiShen": "东北",  # 简化的喜神方位
            # 福神方位
            "fuShen": "西南",  # 简化的福神方位
            # 财神方位
            "caiShen": "正北",  # 简化的财神方位
            # 本命神煞
            "benMing": []
        }
        
        # 计算本命神煞 (根据性别和八字)
        gan_index = TIAN_GAN.index(bazi.getDayGan())
        zhi_index = DI_ZHI.index(bazi.getDayZhi())
        
        # 天乙贵人
        if gender == 'male':
            # 男命
            if gan_index in [0, 2, 4, 6, 8]:  # 阳干
                if zhi_index in [2, 3]:  # 寅卯
                    shen_sha["benMing"].append("天乙贵人")
            else:  # 阴干
                if zhi_index in [8, 9]:  # 申酉
                    shen_sha["benMing"].append("天乙贵人")
        else:
            # 女命
            if gan_index in [0, 2, 4, 6, 8]:  # 阳干
                if zhi_index in [8, 9]:  # 申酉
                    shen_sha["benMing"].append("天乙贵人")
            else:  # 阴干
                if zhi_index in [2, 3]:  # 寅卯
                    shen_sha["benMing"].append("天乙贵人")
        
        # 文昌
        if (gan_index == 0 and zhi_index == 3) or \
           (gan_index == 1 and zhi_index == 4) or \
           (gan_index == 2 and zhi_index == 5) or \
           (gan_index == 3 and zhi_index == 6) or \
           (gan_index == 4 and zhi_index == 7) or \
           (gan_index == 5 and zhi_index == 8) or \
           (gan_index == 6 and zhi_index == 9) or \
           (gan_index == 7 and zhi_index == 10) or \
           (gan_index == 8 and zhi_index == 11) or \
           (gan_index == 9 and zhi_index == 0):
            shen_sha["benMing"].append("文昌")
        
        # 桃花
        if (zhi_index % 4) == 1:  # 丑、巳、酉、亥
            shen_sha["benMing"].append("桃花")
        
        return shen_sha
    except Exception as e:
        logging.error(f"计算神煞时出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {"shenSha": "计算出错"}

def calculate_da_yun(year, month, day, hour, gender):
    """
    计算大运
    
    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 小时 (0-23)
        gender: 性别 ('male' 或 'female')
        
    Returns:
        dict: 大运信息
    """
    if not USING_LUNAR_PYTHON:
        return {"daYun": "需要lunar-python库支持"}
    
    try:
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        # 转换为农历
        lunar = solar.getLunar()
        # 获取八字对象
        bazi = lunar.getEightChar()
        
        # 计算起运年龄
        # 由于lunar-python库可能没有直接提供起运年龄的方法，我们手动计算
        # 男阳女阴顺排，男阴女阳逆排
        is_yang = (gender == 'male' and lunar.getYearGan() in "甲丙戊庚壬") or \
                  (gender == 'female' and lunar.getYearGan() in "乙丁己辛癸")
        
        # 计算出生月份的节气
        # 简化计算，假设出生在节气之后
        start_age = 0
        if is_yang:
            # 顺排，从出生月份开始计算到下一个节气
            start_age = 1 + (month % 12)  # 简化计算
        else:
            # 逆排，从出生月份开始计算到上一个节气
            start_age = 1 + (12 - month % 12)  # 简化计算
        
        # 获取起运年份
        start_year = year + start_age
        
        # 获取大运干支
        da_yun_list = []
        
        # 计算大运干支
        month_gan_index = TIAN_GAN.index(lunar.getMonthGan())
        month_zhi_index = DI_ZHI.index(lunar.getMonthZhi())
        
        # 计算10个大运
        for i in range(10):
            if is_yang:
                # 顺排
                gan_index = (month_gan_index + i) % 10
                zhi_index = (month_zhi_index + i) % 12
            else:
                # 逆排
                gan_index = (month_gan_index - i + 10) % 10
                zhi_index = (month_zhi_index - i + 12) % 12
            
            heavenly_stem = TIAN_GAN[gan_index]
            earthly_branch = DI_ZHI[zhi_index]
            
            # 获取五行
            element = FIVE_ELEMENTS[heavenly_stem]
            
            start_year_i = start_year + i * 10
            
            da_yun_item = {
                "index": i + 1,
                "ganZhi": f"{heavenly_stem}{earthly_branch}",
                "heavenlyStem": heavenly_stem,
                "earthlyBranch": earthly_branch,
                "startYear": start_year_i,
                "endYear": start_year_i + 9,
                "element": element
            }
            
            da_yun_list.append(da_yun_item)
        
        return {
            "startAge": start_age,
            "startYear": start_year,
            "daYunList": da_yun_list
        }
    except Exception as e:
        logging.error(f"计算大运时出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {"daYun": "计算出错"}

def calculate_bazi(birth_date, birth_time, gender):
    """
    计算八字
    
    Args:
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间，可以是 HH:MM 或者 "子时 (23:00-01:00)" 等中文时辰
        gender: 性别，'male' 或 'female'
        
    Returns:
        dict: 八字数据，如果出错则返回None
    """
    try:
        # 验证日期格式
        if not birth_date or not isinstance(birth_date, str):
            logging.error(f"无效的出生日期: {birth_date}")
            return None
            
        date_parts = birth_date.split('-')
        if len(date_parts) != 3:
            logging.error(f"日期格式错误，应为YYYY-MM-DD: {birth_date}")
            return None
            
        try:
            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
    
            # 验证范围
            if year < 1900 or year > 2100:
                logging.warning(f"出生年份 {year} 超出推荐范围(1900-2100)，计算结果可能不准确")
            if month < 1 or month > 12:
                logging.error(f"无效的月份: {month}")
                return None
            if day < 1 or day > 31:
                logging.error(f"无效的日期: {day}")
                return None
                
        except ValueError:
            logging.error(f"日期格式转换错误: {birth_date}")
            return None
            
        # 解析出生日期和时间
        birth_time_data = parse_birth_date_time(birth_date, birth_time)
        
        # 打印调试信息
        logging.info(f"计算八字: 年={birth_time_data['year']}, 月={birth_time_data['month']}, 日={birth_time_data['day']}, 时={birth_time_data['hour']}")
    
        # 计算四柱
        year_pillar = get_year_pillar(birth_time_data["year"])
        month_pillar = get_month_pillar(birth_time_data["year"], birth_time_data["month"], birth_time_data["day"])
        day_pillar = get_day_pillar(birth_time_data["year"], birth_time_data["month"], birth_time_data["day"])
        hour_pillar = get_hour_pillar(birth_time_data["year"], birth_time_data["month"], birth_time_data["day"], birth_time_data["hour"])
        
        # 打印调试信息
        logging.info(f"四柱计算结果: 年柱={year_pillar['heavenlyStem']}{year_pillar['earthlyBranch']}, 月柱={month_pillar['heavenlyStem']}{month_pillar['earthlyBranch']}, 日柱={day_pillar['heavenlyStem']}{day_pillar['earthlyBranch']}, 时柱={hour_pillar['heavenlyStem']}{hour_pillar['earthlyBranch']}")
    
        # 组装八字数据
        bazi_data = {
            "yearPillar": year_pillar,
            "monthPillar": month_pillar,
            "dayPillar": day_pillar,
            "hourPillar": hour_pillar,
            "birthYear": birth_time_data["year"]
        }
    
        # 计算五行分布
        five_elements = calculate_five_elements(bazi_data)
        bazi_data["fiveElements"] = five_elements
        
        # 计算大运流年
        flowing_years = calculate_flowing_years(gender, bazi_data)
        bazi_data["flowingYears"] = flowing_years
        
        # 计算神煞
        shen_sha = calculate_shen_sha(
            birth_time_data["year"], 
            birth_time_data["month"], 
            birth_time_data["day"], 
            birth_time_data["hour"],
            gender
        )
        bazi_data["shenSha"] = shen_sha
        
        # 计算大运
        da_yun = calculate_da_yun(
            birth_time_data["year"], 
            birth_time_data["month"], 
            birth_time_data["day"], 
            birth_time_data["hour"],
            gender
        )
        bazi_data["daYun"] = da_yun
    
        return bazi_data 
    except Exception as e:
        # 记录异常
        logging.error(f"计算八字时发生错误: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return None

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