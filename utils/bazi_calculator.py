import os
import json
import logging
import traceback
from datetime import datetime, timedelta
import math
import re
import sxtwl
from lunar_python import Solar, Lunar

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 五行
FIVE_ELEMENTS = {
    # 天干五行
    "甲": "wood", "乙": "wood",
    "丙": "fire", "丁": "fire",
    "戊": "earth", "己": "earth",
    "庚": "metal", "辛": "metal",
    "壬": "water", "癸": "water",
    # 地支五行
    "子": "water", "丑": "earth",
    "寅": "wood", "卯": "wood",
    "辰": "earth", "巳": "fire",
    "午": "fire", "未": "earth",
    "申": "metal", "酉": "metal",
    "戌": "earth", "亥": "water"
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
WU_XING = {
    "甲": "wood", "乙": "wood",
    "丙": "fire", "丁": "fire",
    "戊": "earth", "己": "earth",
    "庚": "metal", "辛": "metal",
    "壬": "water", "癸": "water"
}

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

# 五行生克关系
SHENG_KE = {
    "wood": {"生": "fire", "克": "earth", "被生": "water", "被克": "metal"},
    "fire": {"生": "earth", "克": "metal", "被生": "wood", "被克": "water"},
    "earth": {"生": "metal", "克": "water", "被生": "fire", "被克": "wood"},
    "metal": {"生": "water", "克": "wood", "被生": "earth", "被克": "fire"},
    "water": {"生": "wood", "克": "fire", "被生": "metal", "被克": "earth"}
}

# 在文件开头添加配置
import traceback
import logging

# 配置lunar-python支持
USING_LUNAR_PYTHON = True  # 由于代码中已经使用了lunar库的功能，所以这里设置为True

# 天干地支常量定义
TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"

# 五行属性
FIVE_ELEMENTS = {
    "甲": "wood", "乙": "wood",
    "丙": "fire", "丁": "fire",
    "戊": "earth", "己": "earth",
    "庚": "metal", "辛": "metal",
    "壬": "water", "癸": "water"
}

# 纳音五行对照表
NA_YIN = {
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
    "壬辰": "长流水", "癸巳": "长流水"
}

def get_na_yin(gan_zhi):
    """获取纳音五行"""
    return NA_YIN.get(gan_zhi, "未知")

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
        if not birth_date:
            raise ValueError("出生日期不能为空")
            
        # 验证日期格式
        if not isinstance(birth_date, str) or not birth_date.count('-') == 2:
            raise ValueError(f"日期格式错误: {birth_date}，应为 YYYY-MM-DD 格式")
            
        year, month, day = map(int, birth_date.split('-'))
        
        # 验证日期范围
        if not (1900 <= year <= 2100):
            raise ValueError(f"年份 {year} 超出范围 (1900-2100)")
        if not (1 <= month <= 12):
            raise ValueError(f"月份 {month} 超出范围 (1-12)")
        if not (1 <= day <= 31):
            raise ValueError(f"日期 {day} 超出范围 (1-31)")
            
        # 验证日期是否有效
        try:
            datetime(year, month, day)
        except ValueError as e:
            raise ValueError(f"无效的日期: {birth_date}, {str(e)}")
            
    except Exception as e:
        logging.error(f"解析日期出错: {str(e)}")
        raise ValueError(f"日期解析失败: {str(e)}")
    
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
        if not birth_time:
            raise ValueError("出生时辰不能为空")
            
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
            else:
                raise ValueError(f"无法识别的时辰格式: {birth_time}")
        # 尝试解析 HH:MM 格式
        elif ':' in birth_time:
            parts = birth_time.split(':')
            if len(parts) >= 1:
                hour = int(parts[0])
                if not (0 <= hour <= 23):
                    raise ValueError(f"小时数 {hour} 超出范围 (0-23)")
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
                raise ValueError(f"无法识别的时辰格式: {birth_time}")
    except Exception as e:
        logging.error(f"解析时间出错: {str(e)}")
        raise ValueError(f"时间解析失败: {str(e)}")
    
    return {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour
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
        day_stem_index = TIAN_GAN.index(day_stem)
        
        # 计算时干索引
        base_stem_index = (day_stem_index % 5) * 2
        hour_stem_index = (base_stem_index + branch_index // 2) % 10
        
        # 获取天干和地支
        heavenly_stem = TIAN_GAN[hour_stem_index]
        earthly_branch = DI_ZHI[branch_index]
    
    return {
        "heavenlyStem": heavenly_stem,
        "earthlyBranch": earthly_branch,
        "element": FIVE_ELEMENTS[heavenly_stem]
    }

def get_element(gan):
    """获取天干的五行属性"""
    return WU_XING.get(gan, "unknown")

def calculate_five_elements(year_stem_index, year_branch_index,
                          month_stem_index, month_branch_index,
                          day_stem_index, day_branch_index,
                          hour_stem_index, hour_branch_index):
    """
    计算五行分布
    
    Args:
        year_stem_index: 年干索引
        year_branch_index: 年支索引
        month_stem_index: 月干索引
        month_branch_index: 月支索引
        day_stem_index: 日干索引
        day_branch_index: 日支索引
        hour_stem_index: 时干索引
        hour_branch_index: 时支索引
        
    Returns:
        dict: 五行分布
    """
    try:
        # 初始化五行计数
        five_elements = {
            'metal': 0,
            'wood': 0,
            'water': 0,
            'fire': 0,
            'earth': 0
        }
        
        # 获取天干地支
        year_stem = TIAN_GAN[year_stem_index]
        year_branch = DI_ZHI[year_branch_index]
        month_stem = TIAN_GAN[month_stem_index]
        month_branch = DI_ZHI[month_branch_index]
        day_stem = TIAN_GAN[day_stem_index]
        day_branch = DI_ZHI[day_branch_index]
        hour_stem = TIAN_GAN[hour_stem_index]
        hour_branch = DI_ZHI[hour_branch_index]
    
    # 统计天干五行
        stems = [year_stem, month_stem, day_stem, hour_stem]
        for stem in stems:
            element = FIVE_ELEMENTS[stem]
            if element == '金':
                five_elements['metal'] += 1
            elif element == '木':
                five_elements['wood'] += 1
            elif element == '水':
                five_elements['water'] += 1
            elif element == '火':
                five_elements['fire'] += 1
            elif element == '土':
                five_elements['earth'] += 1
                
        # 统计地支五行
        branches = [year_branch, month_branch, day_branch, hour_branch]
        for branch in branches:
            element = FIVE_ELEMENTS[branch]
            if element == '金':
                five_elements['metal'] += 1
            elif element == '木':
                five_elements['wood'] += 1
            elif element == '水':
                five_elements['water'] += 1
            elif element == '火':
                five_elements['fire'] += 1
            elif element == '土':
                five_elements['earth'] += 1
                
        return five_elements
        
    except Exception as e:
        logger.error(f"计算五行分布失败: {str(e)}")
        logger.error(traceback.format_exc())
    return {
            'metal': 0,
            'wood': 0,
            'water': 0,
            'fire': 0,
            'earth': 0
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
    birth_year = bazi_data.get("birthYear", datetime.now().year)
    
    # 获取日干信息，用于计算十神
    day_gan = bazi_data.get("dayHeavenlyStem", "")
    day_gan_index = TIAN_GAN.index(day_gan) if day_gan in TIAN_GAN else 0
    
    # 获取日支信息，用于计算旺衰
    day_zhi = bazi_data.get("dayEarthlyBranch", "")
    
    # 开始年份为今年或出生年份，取较大值
    start_year = max(birth_year, datetime.now().year)
    
    try:
        for i in range(10):  # 计算未来10年
            year = start_year + i
            
            if USING_LUNAR_PYTHON:
                # 使用lunar-python库计算
                solar = Solar.fromYmd(year, 5, 1)  # 使用5月1日作为参考日期
                lunar = solar.getLunar()
                year_gan = lunar.getYearGan()
                year_zhi = lunar.getYearZhi()
                
                logging.info(f"流年计算(lunar-python): {year}年 - {year_gan}{year_zhi}")
                
                # 天干地支五行映射字典
                element_map = {
                    # 天干五行
                    "甲": "wood", "乙": "wood", 
                    "丙": "fire", "丁": "fire",
                    "戊": "earth", "己": "earth",
                    "庚": "metal", "辛": "metal",
                    "壬": "water", "癸": "water",
                    # 地支五行
                    "子": "water", "丑": "earth",
                    "寅": "wood", "卯": "wood",
                    "辰": "earth", "巳": "fire",
                    "午": "fire", "未": "earth",
                    "申": "metal", "酉": "metal",
                    "戌": "earth", "亥": "water"
                }
                
                # 计算流年五行
                gan_element = element_map.get(year_gan, "unknown")
                zhi_element = element_map.get(year_zhi, "unknown")
                
                # 计算流年十神
                gan_index = TIAN_GAN.index(year_gan) if year_gan in TIAN_GAN else 0
                shi_shen = get_shi_shen_name(day_gan, year_gan)
                
                # 计算旺衰
                wang_shuai = calculate_wang_shuai(year_zhi)
                
                # 计算纳音
                na_yin = get_na_yin(year_gan + year_zhi)
                
                # 计算流年神煞
                liu_nian_shen_sha = []
                
                # 计算流年吉凶 - 使用适当的函数版本
                ji_xiong = calculate_ji_xiong(year_gan + year_zhi)  # 使用接受单个gan_zhi参数的版本
                
                # 计算与出生年的年龄差
                age = year - birth_year + 1  # 虚岁
                
                # 添加流年信息
                flowing_years.append({
                    "year": year,
                    "age": age,
                    "heavenlyStem": year_gan,
                    "earthlyBranch": year_zhi,
                    "ganElement": gan_element,
                    "zhiElement": zhi_element,
                    "shiShen": shi_shen,
                    "wangShuai": wang_shuai,
                    "naYin": na_yin,
                    "shenSha": liu_nian_shen_sha,
                    "jiXiong": ji_xiong
                })
            else:
                # 如果没有lunar-python库，返回基本信息
                flowing_years.append({
                    "year": year,
                    "age": year - birth_year + 1,
                    "heavenlyStem": "",
                    "earthlyBranch": "",
                    "ganElement": "",
                    "zhiElement": "",
                    "shiShen": "",
                    "wangShuai": "",
                    "naYin": "",
                    "shenSha": [],
                    "jiXiong": ""
                })
    except Exception as e:
        logging.error(f"计算流年出错: {str(e)}")
        logging.error(traceback.format_exc())
    
    return flowing_years

def calculate_ji_xiong(gan, zhi, day_gan, day_zhi):
    """
    计算干支组合的吉凶
    
    Args:
        gan: 天干
        zhi: 地支
        day_gan: 日干
        day_zhi: 日支
        
    Returns:
        str: 吉/凶/平
    """
    score = 0
    
    # 天干合化
    if (gan + day_gan) in ["甲己", "乙庚", "丙辛", "丁壬", "戊癸"]:
        score += 2
    
    # 地支三合
    SAN_HE = {
        "寅": ["寅", "午", "戌"],
        "巳": ["巳", "酉", "丑"],
        "申": ["申", "子", "辰"],
        "亥": ["亥", "卯", "未"]
    }
    for key, value in SAN_HE.items():
        if zhi in value and day_zhi in value:
            score += 2
            break
    
    # 地支六合
    LIU_HE = {
        "子": "丑", "丑": "子",
        "寅": "亥", "亥": "寅",
        "卯": "戌", "戌": "卯",
        "辰": "酉", "酉": "辰",
        "巳": "申", "申": "巳",
        "午": "未", "未": "午"
    }
    if LIU_HE.get(zhi) == day_zhi:
        score += 1
    
    # 判断吉凶
    if score >= 3:
        return "上吉"
    elif score == 2:
        return "吉"
    elif score == 1:
        return "平"
    else:
        return "凶"

def get_hour_gan_zhi(hour, day_gan):
    """
    根据时辰和日干计算时柱
    
    Args:
        hour: 小时 (0-23)
        day_gan: 日干
        
    Returns:
        tuple: (时干, 时支)
    """
    # 将小时转换为时辰索引
    hour_branch_index = (hour + 1) // 2 % 12
    
    # 子时前和子时后的分界点是23点，而不是0点
    if hour == 23:
        hour_branch_index = 0
    
    # 时支
    DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"
    hour_zhi = DI_ZHI[hour_branch_index]
    
    # 根据日干确定时干
    TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
    day_gan_index = TIAN_GAN.index(day_gan)
    
    # 计算时干的起始位置
    hour_gan_base = (day_gan_index * 2) % 10
    
    # 计算最终的时干索引
    hour_gan_index = (hour_gan_base + hour_branch_index) % 10
    hour_gan = TIAN_GAN[hour_gan_index]
    
    return hour_gan, hour_zhi

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
    try:
        # 创建农历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        # 获取天干地支
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        
        # 计算日冲
        hour_gan, hour_zhi = get_hour_gan_zhi(hour, day_gan)
        
        # 计算神煞
        shen_sha = calculate_shen_sha(year, month, day, hour, gender)
        
        # 计算大运
        da_yun = calculate_da_yun(year, month, day, hour, gender)
        
        # 计算流年
        # 生成从今年开始的未来5年流年
        current_year = datetime.now().year
        flowing_years = []
        
        for i in range(5):  # 计算5个流年
            liu_nian_year = current_year + i
            age = liu_nian_year - year
            
            # 获取流年天干地支
            # 干支从出生年开始推算
            years_from_birth = liu_nian_year - year
            gan_index = (TIAN_GAN.index(year_gan) + years_from_birth) % 10
            zhi_index = (DI_ZHI.index(year_zhi) + years_from_birth) % 12
            
            liu_nian_gan = TIAN_GAN[gan_index]
            liu_nian_zhi = DI_ZHI[zhi_index]
            
            # 计算流年五行
            gan_element = get_five_element(liu_nian_gan)
            zhi_element = get_five_element(liu_nian_zhi)
            
            # 计算流年十神
            shi_shen = calculate_shi_shen(liu_nian_gan)
            
            # 计算流年旺衰
            wang_shuai = calculate_wang_shuai(liu_nian_zhi)
            
            # 计算流年纳音
            na_yin = calculate_na_yin(liu_nian_gan + liu_nian_zhi)
            
            # 计算流年神煞
            liu_nian_shen_sha = calculate_liu_nian_shen_sha(liu_nian_gan, liu_nian_zhi)
            
            # 计算流年吉凶
            ji_xiong = calculate_ji_xiong(liu_nian_gan + liu_nian_zhi)
            
            flowing_years.append({
                "year": liu_nian_year,
                "age": age,
                "heavenlyStem": liu_nian_gan,
                "earthlyBranch": liu_nian_zhi,
                "ganElement": gan_element,
                "zhiElement": zhi_element,
                "shiShen": shi_shen,
                "wangShuai": wang_shuai,
                "naYin": na_yin,
                "shenSha": liu_nian_shen_sha,
                "jiXiong": ji_xiong
            })
        
        return {
            "yearPillar": {
                "heavenlyStem": year_gan,
                "earthlyBranch": year_zhi
            },
            "monthPillar": {
                "heavenlyStem": month_gan,
                "earthlyBranch": month_zhi
            },
            "dayPillar": {
                "heavenlyStem": day_gan,
                "earthlyBranch": day_zhi
            },
            "hourPillar": {
                "heavenlyStem": hour_gan,
                "earthlyBranch": hour_zhi
            },
            "shenSha": shen_sha,
            "daYun": da_yun,
            "flowingYears": flowing_years,
            "birthDate": solar_date.strftime("%Y-%m-%d"),
            "birthTime": f"{hour:02d}:00",
            "gender": gender
        }
        
    except Exception as e:
        logging.error(f"计算八字出错: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def get_five_element(gan_or_zhi):
    """根据天干或地支获取五行属性"""
    FIVE_ELEMENTS = {
        # 天干五行
        "甲": "wood", "乙": "wood",
        "丙": "fire", "丁": "fire",
        "戊": "earth", "己": "earth",
        "庚": "metal", "辛": "metal",
        "壬": "water", "癸": "water",
        # 地支五行
        "子": "water", "丑": "earth",
        "寅": "wood", "卯": "wood",
        "辰": "earth", "巳": "fire",
        "午": "fire", "未": "earth",
        "申": "metal", "酉": "metal",
        "戌": "earth", "亥": "water"
    }
    return FIVE_ELEMENTS.get(gan_or_zhi, "未知")

# 方位定义
POSITIONS = {
    'XI': {
        '甲': '亥', '乙': '子', '丙': '寅', '丁': '卯',
        '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    },
    'FU': {
        '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
        '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    },
    'CAI': {
        '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
        '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
        '壬': '寅', '癸': '卯'
    }
}

def get_chong(zhi):
    """获取地支相冲"""
    chong_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
    }
    return chong_map.get(zhi, '未知')

def get_zhi_shen(gan):
    """获取值神"""
    zhi_shen_map = {
        '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
        '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    }
    return zhi_shen_map.get(gan, '未知')

def get_peng_zu_gan(gan):
    """获取彭祖干忌"""
    peng_zu_gan_map = {
        '甲': '沐浴',
        '乙': '冠带',
        '丙': '修造',
        '丁': '斋醮',
        '戊': '经络',
        '己': '开光',
        '庚': '出行',
        '辛': '疗病',
        '壬': '祈福',
        '癸': '求嗣'
    }
    return peng_zu_gan_map.get(gan, '未知')

def get_peng_zu_zhi(zhi):
    """获取彭祖支忌"""
    peng_zu_zhi_map = {
        '子': '祭祀',
        '丑': '会客',
        '寅': '安葬',
        '卯': '求财',
        '辰': '启钻',
        '巳': '赴任',
        '午': '修造',
        '未': '开市',
        '申': '安床',
        '酉': '入宅',
        '戌': '破土',
        '亥': '嫁娶'
    }
    return peng_zu_zhi_map.get(zhi, '未知')

def calculate_ben_ming_shen_sha(year_gan, year_zhi, day_gan, day_zhi):
    """计算本命神煞"""
    try:
        shen_sha = []
        
        # 天乙贵人
        if year_gan in ["甲", "戊", "庚"] and year_zhi in ["子", "寅", "辰", "午", "申", "戌"]:
            shen_sha.append("天乙贵人")
        
        # 文昌贵人
        if day_gan in ["乙", "丙"] and day_zhi in ["巳", "午"]:
            shen_sha.append("文昌贵人")
        
        # 金舆
        if year_gan in ["丁", "己"] and year_zhi in ["丑", "未"]:
            shen_sha.append("金舆")
        
        # 天德
        if year_gan in ["丙", "丁"] and year_zhi in ["寅", "卯"]:
            shen_sha.append("天德")
            
        return shen_sha
    except Exception as e:
        logging.error(f"计算本命神煞失败: {str(e)}")
        return []

def calculate_year_gan_shen_sha(gan):
    """计算年干神煞"""
    try:
        shen_sha = []
        
        # 天乙贵人
        if gan in ["甲", "戊", "庚"]:
            shen_sha.append("天乙贵人")
        
        # 文昌贵人
        if gan in ["乙", "丙"]:
            shen_sha.append("文昌贵人")
        
        # 金舆
        if gan in ["丁", "己"]:
            shen_sha.append("金舆")
        
        # 天德
        if gan in ["丙", "丁"]:
            shen_sha.append("天德")
            
        return shen_sha
    except Exception as e:
        logging.error(f"计算年干神煞失败: {str(e)}")
        return []

def calculate_year_zhi_shen_sha(zhi):
    """计算年支神煞"""
    try:
        shen_sha = []
        
        # 华盖
        if zhi in ["辰", "戌", "丑", "未"]:
            shen_sha.append("华盖")
        
        # 驿马
        if zhi in ["寅", "巳", "申", "亥"]:
            shen_sha.append("驿马")
        
        # 劫煞
        if zhi in ["巳", "酉", "丑"]:
            shen_sha.append("劫煞")
            
        # 灾煞
        if zhi in ["午", "子", "卯", "酉"]:
            shen_sha.append("灾煞")
            
        return shen_sha
    except Exception as e:
        logging.error(f"计算年支神煞失败: {str(e)}")
        return []

def calculate_day_gan_shen_sha(gan):
    """计算日干神煞"""
    try:
        shen_sha = []
        
        # 日贵
        if gan in ["甲", "丙", "戊", "庚", "壬"]:
            shen_sha.append("日贵")
        
        # 天喜
        if gan in ["乙", "丁"]:
            shen_sha.append("天喜")
        
        # 天医
        if gan in ["甲", "丙"]:
            shen_sha.append("天医")
            
        return shen_sha
    except Exception as e:
        logging.error(f"计算日干神煞失败: {str(e)}")
        return []

def calculate_day_zhi_shen_sha(zhi):
    """计算日支神煞"""
    try:
        shen_sha = []
        
        # 青龙
        if zhi in ["寅", "卯"]:
            shen_sha.append("青龙")
        
        # 朱雀
        if zhi in ["巳", "午"]:
            shen_sha.append("朱雀")
        
        # 白虎
        if zhi in ["申", "酉"]:
            shen_sha.append("白虎")
        
        # 玄武
        if zhi in ["子", "亥"]:
            shen_sha.append("玄武")
            
        return shen_sha
    except Exception as e:
        logging.error(f"计算日支神煞失败: {str(e)}")
        return []

def calculate_da_yun(year, month, day, hour, gender):
    """计算大运"""
    try:
        # 转换性别为中文
        gender_cn = '男' if gender == 'male' else '女'
        
        # 创建农历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        # 获取下一个节气日期
        next_jie_qi = lunar.getNextJieQi()
        next_jie_qi_solar = next_jie_qi.getSolar()
        next_jie_qi_date = datetime(
            next_jie_qi_solar.getYear(),
            next_jie_qi_solar.getMonth(),
            next_jie_qi_solar.getDay()
        )
        
        # 计算起运年龄
        birth_date = datetime(year, month, day)
        days_diff = (next_jie_qi_date - birth_date).days
        start_age = max(1, days_diff // 3)  # 每3天为1岁
        
        # 确定大运顺序（阳男阴女顺行，阴男阳女逆行）
        year_gan = lunar.getYearGan()
        is_yang = year_gan in ['甲', '丙', '戊', '庚', '壬']
        is_forward = (is_yang and gender_cn == '男') or (not is_yang and gender_cn == '女')
        
        # 生成大运列表
        da_yun_list = []
        current_month_gan_index = TIAN_GAN.index(lunar.getMonthGan())
        current_month_zhi_index = DI_ZHI.index(lunar.getMonthZhi())
        
        for i in range(8):  # 计算8个大运
            age_start = start_age + i * 10
            age_end = age_start + 9
            year_start = year + age_start
            year_end = year_start + 9
            
            # 计算大运干支
            if is_forward:
                gan_index = (current_month_gan_index + i) % 10
                zhi_index = (current_month_zhi_index + i) % 12
            else:
                gan_index = (current_month_gan_index - i) % 10
                zhi_index = (current_month_zhi_index - i) % 12
            
            gan = TIAN_GAN[gan_index]
            zhi = DI_ZHI[zhi_index]
            
            # 组装大运信息
            da_yun_list.append({
                'index': i + 1,
                'startAge': age_start,
                'endAge': age_end,
                'startYear': year_start,
                'endYear': year_end,
                'heavenlyStem': gan,
                'earthlyBranch': zhi,
                'naYin': get_na_yin(gan + zhi),
                'jiXiong': calculate_ji_xiong(gan + zhi)
            })
        
        return {
            'startAge': start_age,
            'startYear': year + start_age,
            'isForward': is_forward,
            'daYunList': da_yun_list
        }
    except Exception as e:
        logging.error(f"计算大运时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return {
            'startAge': 1,
            'startYear': year + 1,
            'isForward': True,
            'daYunList': []
        }

def calculate_liu_nian_shen_sha(gan, zhi):
    """计算流年神煞（简化版）"""
    try:
        shen_sha = []
        
        # 太岁合
        if gan + zhi == "甲子" or gan + zhi == "乙丑" or gan + zhi == "丙寅":
            shen_sha.append("太岁合")
            
        # 驿马
        if zhi in ["寅", "巳", "申", "亥"]:
            shen_sha.append("驿马")
            
        # 华盖
        if zhi in ["辰", "戌", "丑", "未"]:
            shen_sha.append("华盖")
            
        # 金神
        if gan in ["庚", "辛"] and zhi in ["申", "酉"]:
            shen_sha.append("金神")
            
        # 天德
        if gan in ["丙", "丁"] and zhi in ["巳", "午"]:
            shen_sha.append("天德")
        
        return shen_sha
    except Exception as e:
        logging.error(f"计算流年神煞失败: {str(e)}")
        return []

def calculate_ji_xiong(gan_zhi):
    """计算吉凶（简化版）"""
    try:
        # 这里只是一个简单的判断示例，实际情况会更复杂
        if not gan_zhi or len(gan_zhi) != 2:
            return "中平"
        
        gan = gan_zhi[0]
        zhi = gan_zhi[1]
        
        # 简单的吉凶判断规则
        if gan in ["甲", "丙", "戊", "庚", "壬"] and zhi in ["寅", "午", "戌"]:
            return "大吉"
        elif gan in ["乙", "丁", "己", "辛", "癸"] and zhi in ["巳", "酉", "丑"]:
            return "吉"
        elif gan in ["乙", "丁", "己", "辛", "癸"] and zhi in ["寅", "午", "戌"]:
            return "小吉"
        elif gan in ["甲", "丙", "戊", "庚", "壬"] and zhi in ["巳", "酉", "丑"]:
            return "小凶"
        elif zhi in ["子", "卯", "未"]:
            return "凶"
        else:
            return "中平"
    except Exception as e:
        logging.error(f"计算吉凶失败: {str(e)}")
        return "中平"

def get_hour_gan(day_gan, hour_zhi):
    """根据日干和时支计算时干"""
    try:
        # 甲己还有甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸壬为首
        day_gan_start_map = {
            "甲": "甲", "己": "甲",
            "乙": "丙", "庚": "丙",
            "丙": "戊", "辛": "戊",
            "丁": "庚", "壬": "庚",
            "戊": "壬", "癸": "壬"
        }
        
        # 子时开始的干序
        start_gan = day_gan_start_map.get(day_gan)
        if not start_gan:
            raise ValueError(f"无效的日干: {day_gan}")
            
        # 从起始干开始推算
        gan_index = TIAN_GAN.index(start_gan)
        zhi_index = DI_ZHI.index(hour_zhi)
        
        # 每个时辰对应的干位移
        hour_gan_index = (gan_index + zhi_index) % 10
        return TIAN_GAN[hour_gan_index]
    except Exception as e:
        logging.error(f"计算时干失败: {str(e)}")
        return "未知"

def calculate_bazi(birth_datetime, gender):
    """
    计算八字
    
    Args:
        birth_datetime: 出生日期时间字符串，格式为"YYYY-MM-DD HH:mm"或"YYYY-MM-DD 时辰 (HH:mm-HH:mm)"
        gender: 性别（'male'或'female'）
        
    Returns:
        dict: 八字信息
    """
    try:
        logging.info(f"计算八字，输入参数: birth_datetime={birth_datetime}, gender={gender}")
        
        # 转换性别为中文
        gender_cn = '男' if gender == 'male' else '女'
        
        # 解析日期时间
        if "时" in birth_datetime:
            # 处理带时辰格式的日期时间
            # 首先提取日期部分 (YYYY-MM-DD)
            date_pattern = r"(\d{4}-\d{1,2}-\d{1,2})"
            date_match = re.search(date_pattern, birth_datetime)
            if not date_match:
                raise ValueError(f"无法从字符串中提取日期: {birth_datetime}")
                
            date_str = date_match.group(1)
            
            # 提取时辰部分
            time_pattern = r"([子丑寅卯辰巳午未申酉戌亥]时)"
            time_match = re.search(time_pattern, birth_datetime)
            if not time_match:
                raise ValueError(f"无法从字符串中提取时辰: {birth_datetime}")
                
            time_str = time_match.group(1)
            
            year, month, day = map(int, date_str.split("-"))
            
            # 将时辰转换为小时
            HOUR_MAPPING = {
                "子时": 0, "丑时": 2, "寅时": 4, "卯时": 6,
                "辰时": 8, "巳时": 10, "午时": 12, "未时": 14,
                "申时": 16, "酉时": 18, "戌时": 20, "亥时": 22
            }
            hour = HOUR_MAPPING.get(time_str, 0)
            logging.info(f"解析时辰: {time_str} -> {hour}点")
        else:
            # 处理标准时间格式
            parts = birth_datetime.split(" ")
            if len(parts) < 2:
                raise ValueError(f"时间格式错误: {birth_datetime}，应为 'YYYY-MM-DD HH:mm' 格式")
                
            date_str = parts[0]
            time_str = parts[1]
            year, month, day = map(int, date_str.split("-"))
            hour, minute = map(int, time_str.split(":"))
            
        logging.info(f"解析后的时间: {year}年{month}月{day}日 {hour}时")
        
        # 创建农历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        # 获取四柱干支
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        
        # 获取时辰地支 - 修复方法
        # lunar-python库没有getHourZhi方法，我们使用hour_zhi = DI_ZHI[hour // 2 % 12]
        hour_index = hour // 2 % 12
        hour_zhi = DI_ZHI[hour_index]
        
        # 使用自定义函数计算时干
        hour_gan = get_hour_gan(day_gan, hour_zhi)
        
        # 计算年柱信息
        year_pillar = {
            "heavenlyStem": year_gan,
            "earthlyBranch": year_zhi,
            "naYin": get_na_yin(year_gan + year_zhi),
            "shiShen": get_shi_shen_name(day_gan, year_gan),
            "wangShuai": calculate_wang_shuai(year_zhi)
        }
        
        # 计算月柱信息
        month_pillar = {
            "heavenlyStem": month_gan,
            "earthlyBranch": month_zhi,
            "naYin": get_na_yin(month_gan + month_zhi),
            "shiShen": get_shi_shen_name(day_gan, month_gan),
            "wangShuai": calculate_wang_shuai(month_zhi)
        }
        
        # 计算日柱信息
        day_pillar = {
            "heavenlyStem": day_gan,
            "earthlyBranch": day_zhi,
            "naYin": get_na_yin(day_gan + day_zhi),
            "shiShen": "日主",
            "wangShuai": calculate_wang_shuai(day_zhi)
        }
        
        # 计算时柱信息
        hour_pillar = {
            "heavenlyStem": hour_gan,
            "earthlyBranch": hour_zhi,
            "naYin": get_na_yin(hour_gan + hour_zhi),
            "shiShen": get_shi_shen_name(day_gan, hour_gan),
            "wangShuai": calculate_wang_shuai(hour_zhi)
        }
        
        # 组装结果
        result = {
            "yearPillar": year_pillar,
            "monthPillar": month_pillar,
            "dayPillar": day_pillar,
            "hourPillar": hour_pillar,
            "shenSha": {
                "dayChong": get_chong(day_zhi),
                "zhiShen": get_zhi_shen(day_gan),
                "xiShen": calculate_xi_shen(day_gan),
                "fuShen": calculate_fu_shen(day_gan),
                "caiShen": calculate_cai_shen(day_gan),
                "benMing": calculate_ben_ming_shen_sha(year_gan, year_zhi, day_gan, day_zhi),
                "yearGan": calculate_year_gan_shen_sha(year_gan),
                "yearZhi": calculate_year_zhi_shen_sha(year_zhi),
                "dayGan": calculate_day_gan_shen_sha(day_gan),
                "dayZhi": calculate_day_zhi_shen_sha(day_zhi)
            },
            "daYun": calculate_da_yun(year, month, day, hour, gender_cn),
            "flowingYears": []
        }
        
        # 计算流年
        current_year = datetime.now().year
        start_year = year + 1
        end_year = current_year + 10  # 往后推算10年
        
        for y in range(start_year, end_year + 1):
            liu_nian = get_liu_nian(y, start_year)
            if liu_nian:
                liu_nian_info = {
                    "year": y,
                    "age": y - year,
                    "heavenlyStem": liu_nian["gan"],
                    "earthlyBranch": liu_nian["zhi"],
                    "ganElement": liu_nian["ganElement"],
                    "zhiElement": liu_nian["zhiElement"],
                    "shenSha": calculate_liu_nian_shen_sha(liu_nian["gan"], liu_nian["zhi"]),
                    "jiXiong": calculate_ji_xiong(liu_nian["gan"] + liu_nian["zhi"])
                }
                result["flowingYears"].append(liu_nian_info)
        
        # 添加五行分布统计
        result["fiveElements"] = {
            "wood": 0,
            "fire": 0,
            "earth": 0,
            "metal": 0,
            "water": 0
        }
        
        # 统计天干五行
        for gan in [year_gan, month_gan, day_gan, hour_gan]:
            element = WU_XING.get(gan)
            if element:
                result["fiveElements"][element] += 1
        
        # 统计地支五行
        for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
            element_map = {
                "子": "water", "丑": "earth",
                "寅": "wood", "卯": "wood",
                "辰": "earth", "巳": "fire",
                "午": "fire", "未": "earth",
                "申": "metal", "酉": "metal",
                "戌": "earth", "亥": "water"
            }
            element = element_map.get(zhi)
            if element:
                result["fiveElements"][element] += 1
        
        logging.info("八字计算完成")
        return result
        
    except Exception as e:
        logging.error(f"计算八字失败: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def calculate_xi_shen(gan):
    """计算喜神方位"""
    try:
        XI_SHEN_MAP = {
            "甲": "艮", "乙": "艮",
            "丙": "离", "丁": "离",
            "戊": "坤", "己": "坤",
            "庚": "兑", "辛": "兑",
            "壬": "坎", "癸": "坎"
        }
        return XI_SHEN_MAP.get(gan, "未知")
    except Exception as e:
        logging.error(f"计算喜神失败: {str(e)}")
        return "未知"

def calculate_fu_shen(gan):
    """计算福神方位"""
    try:
        FU_SHEN_MAP = {
            "甲": "坤", "乙": "坤",
            "丙": "艮", "丁": "艮",
            "戊": "巽", "己": "巽",
            "庚": "乾", "辛": "乾",
            "壬": "坤", "癸": "坤"
        }
        return FU_SHEN_MAP.get(gan, "未知")
    except Exception as e:
        logging.error(f"计算福神失败: {str(e)}")
        return "未知"

def calculate_cai_shen(gan):
    """计算财神方位"""
    try:
        CAI_SHEN_MAP = {
            "甲": "艮", "乙": "巽",
            "丙": "坤", "丁": "乾",
            "戊": "坎", "己": "离",
            "庚": "艮", "辛": "巽",
            "壬": "坤", "癸": "乾"
        }
        return CAI_SHEN_MAP.get(gan, "未知")
    except Exception as e:
        logging.error(f"计算财神失败: {str(e)}")
        return "未知"

def calculate_wang_shuai(zhi):
    """计算旺衰"""
    try:
        # 简化版旺衰判断
        WANG = ["寅", "卯", "辰"]  # 春季旺
        XIANG = ["巳", "午", "未"]  # 夏季旺
        PING = ["申", "酉", "戌"]  # 秋季旺
        SHUAI = ["亥", "子", "丑"]  # 冬季旺
        
        if zhi in WANG:
            return "旺"
        elif zhi in XIANG:
            return "相"
        elif zhi in PING:
            return "平"
        elif zhi in SHUAI:
            return "衰"
        else:
            return "未知"
    except Exception as e:
        logging.error(f"计算旺衰失败: {str(e)}")
        return "未知"

def get_shi_shen_name(day_gan, target_gan):
    """计算十神名称"""
    try:
        # 十神: 比肩、劫财、食神、伤官、偏财、正财、七杀、正官、偏印、正印
        if not day_gan or not target_gan:
            return "未知"
            
        day_index = TIAN_GAN.index(day_gan)
        target_index = TIAN_GAN.index(target_gan)
        
        # 计算五行生克关系的索引
        diff = (target_index - day_index) % 10
        
        SHI_SHEN_NAMES = [
            "比肩", "劫财", "食神", "伤官", "偏财", 
            "正财", "七杀", "正官", "偏印", "正印"
        ]
        
        return SHI_SHEN_NAMES[diff]
    except Exception as e:
        logging.error(f"计算十神名称失败: {str(e)}")
        return "未知"

def get_liu_nian(year, birth_year):
    """
    获取流年信息
    
    Args:
        year: 要计算的年份
        birth_year: 出生年份
        
    Returns:
        dict: 流年信息 
    """
    try:
        # 创建公历对象
        solar = Solar.fromYmd(year, 5, 1)  # 使用5月1日作为参考日期
        lunar = solar.getLunar()
        
        # 获取干支
        gan = lunar.getYearGan()
        zhi = lunar.getYearZhi()
        
        # 天干五行对应
        gan_wu_xing = {
            "甲": "wood", "乙": "wood",
            "丙": "fire", "丁": "fire",
            "戊": "earth", "己": "earth",
            "庚": "metal", "辛": "metal",
            "壬": "water", "癸": "water"
        }
        
        # 地支五行对应
        zhi_wu_xing = {
            "子": "water", "丑": "earth",
            "寅": "wood", "卯": "wood",
            "辰": "earth", "巳": "fire",
            "午": "fire", "未": "earth",
            "申": "metal", "酉": "metal",
            "戌": "earth", "亥": "water"
        }
        
        # 计算五行
        gan_element = gan_wu_xing.get(gan, "unknown")
        zhi_element = zhi_wu_xing.get(zhi, "unknown")
        
        return {
            "year": year,
            "age": year - birth_year + 1,  # 虚岁
            "gan": gan,
            "zhi": zhi,
            "ganElement": gan_element,
            "zhiElement": zhi_element
        }
    except Exception as e:
        logging.error(f"获取流年信息失败: {str(e)}")
        return None

# 使用示例
if __name__ == "__main__":
    # 测试
    test_date = "2025-05-27"
    test_time = "12:00"
    test_gender = "male"
    
    result = calculate_bazi(test_date, test_gender)
    print(f"年柱: {result['yearPillar']['heavenlyStem']}{result['yearPillar']['earthlyBranch']}")
    print(f"月柱: {result['monthPillar']['heavenlyStem']}{result['monthPillar']['earthlyBranch']}")
    print(f"日柱: {result['dayPillar']['heavenlyStem']}{result['dayPillar']['earthlyBranch']}")
    print(f"时柱: {result['hourPillar']['heavenlyStem']}{result['hourPillar']['earthlyBranch']}")
    print(f"五行: {result['fiveElements']}")
    print(f"流年: {[(y['year'], y['heavenlyStem'] + y['earthlyBranch']) for y in result['flowingYears']]}") 