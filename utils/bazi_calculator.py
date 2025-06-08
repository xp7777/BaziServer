import os
import json
import logging
import datetime
from datetime import timedelta
import math

# 导入lunar-python库代替sxtwl
try:
    import lunar_python
    from lunar_python import Solar, Lunar
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
    day_gan = bazi_data.get("dayPillar", {}).get("heavenlyStem", "")
    day_gan_index = TIAN_GAN.index(day_gan) if day_gan in TIAN_GAN else 0
    
    # 开始年份为今年或出生年份，取较大值
    current_year = datetime.datetime.now().year
    start_year = max(birth_year, current_year)
    
    logging.info(f"流年计算 - 出生年份: {birth_year}, 当前年份: {current_year}, 开始年份: {start_year}")
    
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
            
            # 计算流年神煞
            stem_index = TIAN_GAN.index(year_gan)
            branch_index = DI_ZHI.index(year_zhi)
            shen_sha = calculate_flowing_year_shen_sha(stem_index, branch_index)
            
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
                "age": age,
                "shenSha": shen_sha
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
            
            # 计算流年神煞
            shen_sha = calculate_flowing_year_shen_sha(stem_index, branch_index)
            
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
                "age": age,
                "shenSha": shen_sha
            })
    
    return flowing_years

def calculate_shen_sha(year_stem_index, year_branch_index, 
                      month_stem_index, month_branch_index, 
                      day_stem_index, day_branch_index, 
                      hour_stem_index, hour_branch_index):
    """
    计算神煞
    
    参数:
        year_stem_index: 年干索引
        year_branch_index: 年支索引
        month_stem_index: 月干索引
        month_branch_index: 月支索引
        day_stem_index: 日干索引
        day_branch_index: 日支索引
        hour_stem_index: 时干索引
        hour_branch_index: 时支索引
    
    返回:
        dict: 神煞信息
    """
    # 天干地支映射
    heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 日冲
    day_chong_index = (day_branch_index + 6) % 12
    day_chong = earthly_branches[day_chong_index]
    
    # 值神
    zhi_shen_map = ['贵人', '腾蛇', '朱雀', '六合', '勾陈', '青龙', '天空', '白虎', '太常', '玄武', '太阴', '天后']
    zhi_shen = zhi_shen_map[day_branch_index]
    
    # 彭祖百忌
    peng_zu_gan_map = [
        '甲不开仓', '乙不栽植', '丙不修灶', '丁不剃头', '戊不受田',
        '己不破券', '庚不经络', '辛不合酱', '壬不泱水', '癸不词讼'
    ]
    peng_zu_zhi_map = [
        '子不问卜', '丑不冠带', '寅不祭祀', '卯不穿井', '辰不哭泣',
        '巳不远行', '午不苫盖', '未不服药', '申不安床', '酉不会客',
        '戌不吃犬', '亥不嫁娶'
    ]
    peng_zu_gan = peng_zu_gan_map[day_stem_index]
    peng_zu_zhi = peng_zu_zhi_map[day_branch_index]
    
    # 喜神、福神、财神方位
    xi_shen_map = ['东北', '东北', '西南', '西南', '东北', '东北', '西南', '西南', '东北', '东北']
    fu_shen_map = ['东南', '东南', '西北', '西北', '东南', '东南', '西北', '西北', '东南', '东南']
    cai_shen_map = ['正东', '正东', '正南', '正南', '中央', '中央', '正西', '正西', '正北', '正北']
    xi_shen = xi_shen_map[day_stem_index]
    fu_shen = fu_shen_map[day_stem_index]
    cai_shen = cai_shen_map[day_stem_index]
    
    # 本命神煞
    ben_ming_shen_sha = []
    
    # 年干神煞
    year_gan_shen_sha = []
    if year_stem_index in [0, 5]:  # 甲己
        year_gan_shen_sha.append('金舆')
    if year_stem_index in [2, 7]:  # 丙辛
        year_gan_shen_sha.append('福星贵人')
    
    # 年支神煞
    year_zhi_shen_sha = []
    if year_branch_index in [2, 6, 10]:  # 寅午戌
        year_zhi_shen_sha.append('将星')
    
    # 日干神煞
    day_gan_shen_sha = []
    if day_stem_index in [4, 5]:  # 戊己
        day_gan_shen_sha.append('天德')
    if day_stem_index in [6, 7]:  # 庚辛
        day_gan_shen_sha.append('月德')
    
    # 日支神煞
    day_zhi_shen_sha = []
    if day_branch_index in [1, 4, 7, 10]:  # 丑辰未戌
        day_zhi_shen_sha.append('天乙贵人')
    
    # 合并本命神煞
    ben_ming_shen_sha.extend(['将星', '文昌'])  # 简化示例
    
    return {
        "dayChong": day_chong,
        "zhiShen": zhi_shen,
        "pengZuGan": peng_zu_gan,
        "pengZuZhi": peng_zu_zhi,
        "xiShen": xi_shen,
        "fuShen": fu_shen,
        "caiShen": cai_shen,
        "benMing": ben_ming_shen_sha,
        "yearGan": year_gan_shen_sha,
        "yearZhi": year_zhi_shen_sha,
        "dayGan": day_gan_shen_sha,
        "dayZhi": day_zhi_shen_sha
    }

def calculate_flowing_year_shen_sha(stem_index, branch_index):
    """
    计算流年神煞
    
    参数:
        stem_index: 天干索引
        branch_index: 地支索引
    
    返回:
        list: 神煞列表
    """
    shen_sha = []
    
    # 简化的流年神煞计算
    if stem_index in [4, 5]:  # 戊己
        shen_sha.append('天德')
    if stem_index in [6, 7]:  # 庚辛
        shen_sha.append('月德')
    if branch_index in [2, 6, 10]:  # 寅午戌
        shen_sha.append('将星')
    if branch_index in [1, 4, 7, 10]:  # 丑辰未戌
        shen_sha.append('天乙贵人')
    if branch_index in [2, 3]:  # 寅卯
        shen_sha.append('文昌')
    if stem_index in [0, 5]:  # 甲己
        shen_sha.append('金舆')
    
    return shen_sha

def calculate_da_yun(birth_year, birth_month, birth_day, 
                   year_stem_index, year_branch_index, 
                   month_stem_index, month_branch_index, 
                   gender):
    """
    计算大运
    
    参数:
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        year_stem_index: 年干索引
        year_branch_index: 年支索引
        month_stem_index: 月干索引
        month_branch_index: 月支索引
        gender: 性别 ('male'/'female')
    
    返回:
        dict: 大运信息
    """
    # 天干地支映射
    heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    elements = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水']
    
    # 尝试使用lunar-python库计算大运
    try:
        if USING_LUNAR_PYTHON:
            logging.info(f"使用lunar-python库计算大运 - 出生年月日: {birth_year}-{birth_month}-{birth_day}, 性别: {gender}")
            
            # 创建公历对象
            try:
                # 解析出生年月日
                birth_year = int(birth_year)
                birth_month = int(birth_month)
                birth_day = int(birth_day)
                
                # 获取出生时的小时（简化处理，使用中午12点）
                birth_hour = 12
                
                # 创建公历对象
                solar = Solar.fromYmdHms(birth_year, birth_month, birth_day, birth_hour, 0, 0)
                
                # 转换为农历
                lunar = solar.getLunar()
                
                # 获取八字对象
                eight_char = lunar.getEightChar()
                
                # 获取大运信息
                yun = eight_char.getYun(1 if gender == 'male' else 0)
                
                # 获取起运年龄和起运年份
                start_age = yun.getStartAge()
                start_year = birth_year + start_age
                
                # 确定大运顺序
                is_forward = yun.isForward()
                
                logging.info(f"lunar-python计算结果 - 起运年龄: {start_age}, 起运年份: {start_year}, 顺行: {is_forward}")
                
                # 生成大运列表
                da_yun_list = []
                
                # 获取月干支索引
                month_gan = lunar.getMonthGan()
                month_zhi = lunar.getMonthZhi()
                month_stem_index = heavenly_stems.index(month_gan)
                month_branch_index = earthly_branches.index(month_zhi)
                
                for i in range(8):  # 计算8个大运
                    if is_forward:
                        # 顺行
                        current_stem_index = (month_stem_index + i + 1) % 10
                        current_branch_index = (month_branch_index + i + 1) % 12
                    else:
                        # 逆行
                        current_stem_index = (month_stem_index - i - 1) % 10
                        current_branch_index = (month_branch_index - i - 1) % 12
                    
                    # 大运开始年份和结束年份
                    start_year_i = start_year + i * 10
                    end_year_i = start_year_i + 9
                    
                    da_yun_list.append({
                        "index": i + 1,
                        "ganZhi": heavenly_stems[current_stem_index] + earthly_branches[current_branch_index],
                        "heavenlyStem": heavenly_stems[current_stem_index],
                        "earthlyBranch": earthly_branches[current_branch_index],
                        "element": elements[current_stem_index],
                        "startYear": start_year_i,
                        "endYear": end_year_i
                    })
                
                return {
                    "startAge": start_age,
                    "startYear": start_year,
                    "daYun": da_yun_list
                }
                
            except Exception as e:
                logging.error(f"使用lunar-python计算大运出错: {str(e)}")
                # 出错时使用备用算法
                logging.info("使用备用算法计算大运")
    except Exception as e:
        logging.error(f"lunar-python库调用出错: {str(e)}")
    
    # 备用算法：使用简化的大运计算方法
    logging.info("使用简化算法计算大运")
    
    # 确定大运顺序
    # 阳年生男、阴年生女顺行；阳年生女、阴年生男逆行
    is_yang_year = year_stem_index % 2 == 0  # 甲丙戊庚壬为阳干
    is_male = gender == 'male'
    
    is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)
    
    # 起运年龄（简化处理，男孩8岁起运，女孩7岁起运）
    start_age = 8 if is_male else 7
    
    # 使用实际出生年份计算起运年份
    start_year = int(birth_year) + start_age
    
    logging.info(f"简化算法 - 出生年份: {birth_year}, 性别: {gender}, 起运年龄: {start_age}, 起运年份: {start_year}")
    
    # 生成大运列表
    da_yun_list = []
    
    for i in range(8):  # 计算8个大运
        if is_forward:
            # 顺行
            current_stem_index = (month_stem_index + i + 1) % 10
            current_branch_index = (month_branch_index + i + 1) % 12
        else:
            # 逆行
            current_stem_index = (month_stem_index - i - 1) % 10
            current_branch_index = (month_branch_index - i - 1) % 12
        
        # 大运开始年份和结束年份
        start_year_i = start_year + i * 10
        end_year_i = start_year_i + 9
        
        da_yun_list.append({
            "index": i + 1,
            "ganZhi": heavenly_stems[current_stem_index] + earthly_branches[current_branch_index],
            "heavenlyStem": heavenly_stems[current_stem_index],
            "earthlyBranch": earthly_branches[current_branch_index],
            "element": elements[current_stem_index],
            "startYear": start_year_i,
            "endYear": end_year_i
        })
    
    return {
        "startAge": start_age,
        "startYear": start_year,
        "daYun": da_yun_list
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
        # 解析出生日期和时间
        birth_info = parse_birth_date_time(birth_date, birth_time)
        
        # 获取年、月、日、时
        year = birth_info["year"]
        month = birth_info["month"]
        day = birth_info["day"]
        hour = birth_info["hour"]
        
        # 记录出生年份，确保后续计算正确使用
        logging.info(f"计算八字 - 出生年份: {year}, 月: {month}, 日: {day}, 时: {hour}")
        
        # 计算年柱
        year_pillar = get_year_pillar(year)
        
        # 计算月柱
        month_pillar = get_month_pillar(year, month, day)
        
        # 计算日柱
        day_pillar = get_day_pillar(year, month, day)
        
        # 计算时柱
        hour_pillar = get_hour_pillar(year, month, day, hour)
        
        # 获取出生年份
        birth_year = year
        
        # 合并八字信息
        bazi_data = {
            "yearPillar": year_pillar,
            "monthPillar": month_pillar,
            "dayPillar": day_pillar,
            "hourPillar": hour_pillar,
            "birthYear": birth_year  # 确保保存出生年份
        }
        
        # 计算五行
        five_elements = calculate_five_elements(bazi_data)
        
        # 计算神煞
        shen_sha = calculate_shen_sha(year, month, day, hour, gender)
        
        # 计算大运
        # 获取天干地支索引
        year_stem_index = HEAVENLY_STEMS.index(year_pillar["heavenlyStem"]) if year_pillar["heavenlyStem"] in HEAVENLY_STEMS else 0
        year_branch_index = EARTHLY_BRANCHES.index(year_pillar["earthlyBranch"]) if year_pillar["earthlyBranch"] in EARTHLY_BRANCHES else 0
        month_stem_index = HEAVENLY_STEMS.index(month_pillar["heavenlyStem"]) if month_pillar["heavenlyStem"] in HEAVENLY_STEMS else 0
        month_branch_index = EARTHLY_BRANCHES.index(month_pillar["earthlyBranch"]) if month_pillar["earthlyBranch"] in EARTHLY_BRANCHES else 0
        
        # 计算大运，传递实际出生年份
        da_yun = calculate_da_yun(birth_year, month, day, 
                                 year_stem_index, year_branch_index,
                                 month_stem_index, month_branch_index,
                                 gender)
        
        # 计算流年
        flowing_years = calculate_flowing_years(gender, bazi_data)
        
        # 计算十神
        ten_gods = calculate_ten_gods(bazi_data)
        
        # 计算纳音
        na_yin = calculate_na_yin(bazi_data)
        
        # 返回完整的八字信息
        return {
            "yearPillar": year_pillar,
            "monthPillar": month_pillar,
            "dayPillar": day_pillar,
            "hourPillar": hour_pillar,
            "fiveElements": five_elements,
            "shenSha": shen_sha,
            "daYun": da_yun,
            "tenGods": ten_gods,
            "naYin": na_yin,
            'flowingYears': flowing_years,
            'birthDate': birth_date,
            'birthTime': birth_time,
            'gender': gender,
            'birthYear': birth_year  # 确保包含出生年份
        }
    except Exception as e:
        import traceback
        logging.error(f"计算八字出错: {str(e)}")
        logging.error(traceback.format_exc())
        
        # 返回默认值
        return {
            'yearPillar': {
                'heavenlyStem': '甲',
                'earthlyBranch': '子',
                'element': '水'
            },
            'monthPillar': {
                'heavenlyStem': '丙',
                'earthlyBranch': '寅',
                'element': '木'
            },
            'dayPillar': {
                'heavenlyStem': '戊',
                'earthlyBranch': '午',
                'element': '火'
            },
            'hourPillar': {
                'heavenlyStem': '庚',
                'earthlyBranch': '申',
                'element': '金'
            },
            'fiveElements': {
                'wood': 2,
                'fire': 2,
                'earth': 1,
                'metal': 2,
                'water': 1
            },
            'flowingYears': [
                {
                    'year': 2025,
                    'heavenlyStem': '乙',
                    'earthlyBranch': '丑',
                    'element': '土'
                },
                {
                    'year': 2026,
                    'heavenlyStem': '丙',
                    'earthlyBranch': '寅',
                    'element': '木'
                },
                {
                    'year': 2027,
                    'heavenlyStem': '丁',
                    'earthlyBranch': '卯',
                    'element': '木'
                },
                {
                    'year': 2028,
                    'heavenlyStem': '戊',
                    'earthlyBranch': '辰',
                    'element': '土'
                },
                {
                    'year': 2029,
                    'heavenlyStem': '己',
                    'earthlyBranch': '巳',
                    'element': '火'
                }
            ],
            'birthDate': birth_date,
            'birthTime': birth_time,
            'gender': gender
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