#!/usr/bin/env python
# coding: utf-8

import sys
import os
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入八字计算模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.bazi_calculator import calculate_bazi, calculate_shen_sha, calculate_da_yun

def test_example():
    """测试示例八字"""
    logging.info("测试示例八字计算...")
    
    # 使用示例数据：女性 出生时间 公历：1970年10月10日3时46分
    birth_date = "1970-10-10"
    birth_time = "3:46"
    gender = "female"
    
    # 计算八字
    bazi_data = calculate_bazi(birth_date, birth_time, gender)
    
    # 提取四柱
    year_pillar = f"{bazi_data['yearPillar']['heavenlyStem']}{bazi_data['yearPillar']['earthlyBranch']}"
    month_pillar = f"{bazi_data['monthPillar']['heavenlyStem']}{bazi_data['monthPillar']['earthlyBranch']}"
    day_pillar = f"{bazi_data['dayPillar']['heavenlyStem']}{bazi_data['dayPillar']['earthlyBranch']}"
    hour_pillar = f"{bazi_data['hourPillar']['heavenlyStem']}{bazi_data['hourPillar']['earthlyBranch']}"
    
    logging.info(f"四柱: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
    
    # 检查是否与预期结果一致：庚戌 丙戌 癸亥 甲寅
    expected = ["庚戌", "丙戌", "癸亥", "甲寅"]
    actual = [year_pillar, month_pillar, day_pillar, hour_pillar]
    
    for i, (exp, act) in enumerate(zip(expected, actual)):
        if exp != act:
            logging.warning(f"第{i+1}柱不匹配: 预期={exp}, 实际={act}")
        else:
            logging.info(f"第{i+1}柱匹配: {exp}")
    
    # 测试神煞计算
    year, month, day = map(int, birth_date.split('-'))
    hour = int(birth_time.split(':')[0])
    
    shen_sha = calculate_shen_sha(year, month, day, hour, gender)
    logging.info(f"神煞计算结果: {json.dumps(shen_sha, ensure_ascii=False, indent=2)}")
    
    # 测试大运计算
    da_yun = calculate_da_yun(year, month, day, hour, gender)
    logging.info(f"大运起运年龄: {da_yun.get('startAge')}岁，起运年份: {da_yun.get('startYear')}年")
    
    # 检查大运列表
    da_yun_list = da_yun.get('daYunList', [])
    if da_yun_list:
        logging.info(f"大运列表(前3项): {da_yun_list[:3]}")
    else:
        logging.warning("大运列表为空")

def test_2008_case():
    """测试2008年出生的情况"""
    logging.info("\n测试2008年出生的八字计算...")
    
    birth_date = "2008-05-15"
    birth_time = "12:00"
    gender = "male"
    
    # 计算八字
    bazi_data = calculate_bazi(birth_date, birth_time, gender)
    
    # 提取四柱
    year_pillar = f"{bazi_data['yearPillar']['heavenlyStem']}{bazi_data['yearPillar']['earthlyBranch']}"
    month_pillar = f"{bazi_data['monthPillar']['heavenlyStem']}{bazi_data['monthPillar']['earthlyBranch']}"
    day_pillar = f"{bazi_data['dayPillar']['heavenlyStem']}{bazi_data['dayPillar']['earthlyBranch']}"
    hour_pillar = f"{bazi_data['hourPillar']['heavenlyStem']}{bazi_data['hourPillar']['earthlyBranch']}"
    
    logging.info(f"四柱: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
    
    # 测试神煞计算
    year, month, day = map(int, birth_date.split('-'))
    hour = int(birth_time.split(':')[0])
    
    shen_sha = calculate_shen_sha(year, month, day, hour, gender)
    logging.info(f"神煞计算结果: {json.dumps(shen_sha, ensure_ascii=False, indent=2)}")
    
    # 测试大运计算
    da_yun = calculate_da_yun(year, month, day, hour, gender)
    logging.info(f"大运起运年龄: {da_yun.get('startAge')}岁，起运年份: {da_yun.get('startYear')}年")
    
    # 检查大运列表
    da_yun_list = da_yun.get('daYunList', [])
    if da_yun_list:
        logging.info(f"大运列表(前3项): {da_yun_list[:3]}")
    else:
        logging.warning("大运列表为空")

if __name__ == "__main__":
    test_example()
    test_2008_case() 