"""
修复八字计算器中的问题
"""

import logging

# 1. 修复流年计算问题
# 在utils/bazi_calculator.py的calculate_flowing_years函数中
# 将以下代码:
"""
# 使用传统方法计算
stem_index = (year - 4) % 10
branch_index = (year - 4) % 12

stem = HEAVENLY_STEMS[stem_index]
branch = EARTHLY_BRANCHES[branch_index]
"""

# 修改为:
"""
# 使用正确的传统方法计算
# 1984年是甲子年，以此为基准计算
base_year = 1984
cycle_years = year - base_year
stem_index = cycle_years % 10
branch_index = cycle_years % 12

# 确保索引在正确范围内
if stem_index < 0:
    stem_index += 10
if branch_index < 0:
    branch_index += 12
    
stem = TIAN_GAN[stem_index]
branch = DI_ZHI[branch_index]

logging.info(f"流年干支索引: {stem_index}, {branch_index}")
"""

# 2. 修复大运计算中的生肖问题
# 已经修复，确保SHENG_XIAO字典包含所有可能的键(0-11)

# 3. 修复'EightChar' object has no attribute 'getStartAge'错误
# 在utils/bazi_calculator.py的calculate_da_yun函数中
# 将以下代码:
"""
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
"""

# 修改为:
"""
# 获取起运时间
try:
    # 检查bazi对象是否有getStartAge方法
    if hasattr(bazi, 'getStartAge') and callable(getattr(bazi, 'getStartAge')):
        start_age = bazi.getStartAge()
        start_year = bazi.getStartYear()
        logging.info(f"起运年龄: {start_age}岁, 起运年份: {start_year}年")
    else:
        # lunar-python库可能没有getStartAge方法，使用传统计算方式
        raise AttributeError("EightChar对象没有getStartAge方法")
except Exception as e:
    logging.error(f"获取起运时间出错: {str(e)}")
    
    # 使用传统方法计算起运年龄
    # 根据性别和年干阴阳确定顺逆，并计算起运年龄
    year_gan = lunar.getYearGan()
    year_gan_idx = TIAN_GAN.index(year_gan) if year_gan in TIAN_GAN else 0
    is_yang = year_gan_idx % 2 == 0  # 甲丙戊庚壬为阳，乙丁己辛癸为阴
    
    # 传统规则：阳年生男(或阴年生女)顺行，阴年生男(或阳年生女)逆行
    if (is_yang and gender == 'male') or (not is_yang and gender == 'female'):
        # 阳年生男或阴年生女，起运较早
        start_age = 1 + (year % 6)  # 简化计算，1-6岁之间
    else:
        # 阴年生男或阳年生女，起运较晚
        start_age = 4 + (year % 6)  # 简化计算，4-9岁之间
    
    start_year = year + start_age
    logging.info(f"使用传统方法估算起运年龄: {start_age}岁, 起运年份: {start_year}年")
"""

# 4. 添加打印DeepSeek API请求内容的代码
# 在routes/bazi_routes_fixed_new.py的generate_ai_analysis函数中
# 将以下代码:
"""
logging.info("准备调用DeepSeek API...")
response = requests.post(
    DEEPSEEK_API_URL,
    headers=headers,
    data=json.dumps(payload)
)
"""

# 修改为:
"""
logging.info("准备调用DeepSeek API...")
# 打印请求内容（去除敏感信息）
safe_headers = headers.copy()
if 'Authorization' in safe_headers:
    safe_headers['Authorization'] = safe_headers['Authorization'][:15] + "..." + safe_headers['Authorization'][-5:] if len(safe_headers['Authorization']) > 20 else "***"

# 打印请求详情
logging.info(f"DeepSeek API请求URL: {DEEPSEEK_API_URL}")
logging.info(f"DeepSeek API请求头: {safe_headers}")

# 打印请求体（仅包含关键信息）
safe_payload = {
    "model": payload["model"],
    "temperature": payload["temperature"],
    "max_tokens": payload["max_tokens"],
    "messages": [
        {"role": msg["role"], "content": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]} 
        for msg in payload["messages"]
    ]
}
logging.info(f"DeepSeek API请求体: {json.dumps(safe_payload, ensure_ascii=False)}")

# 打印完整提示词（便于调试）
logging.info(f"DeepSeek API完整提示词: {prompt}")

response = requests.post(
    DEEPSEEK_API_URL,
    headers=headers,
    data=json.dumps(payload)
)
""" 