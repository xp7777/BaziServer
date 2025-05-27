#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试神煞和大运流年的计算功能
"""

import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入八字计算模块
from utils.bazi_calculator import calculate_bazi, calculate_shen_sha, calculate_da_yun

def test_shen_sha_calculation():
    """测试神煞计算功能"""
    logging.info("===== 测试神煞计算功能 =====")
    
    test_cases = [
        {"date": "2006-10-15", "time": "午时 (11:00-13:00)", "gender": "male", "name": "2006年男命"},
        {"date": "1995-10-08", "time": "辰时 (07:00-09:00)", "gender": "male", "name": "1995年男命"},
        {"date": "1990-06-21", "time": "子时 (23:00-01:00)", "gender": "female", "name": "1990年女命"},
    ]
    
    for case in test_cases:
        logging.info(f"----------- 测试案例: {case['name']} -----------")
        
        # 解析日期和时间
        date_parts = case['date'].split('-')
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        
        # 解析时辰
        hour = 12  # 默认中午
        if "子时" in case['time']:
            hour = 0
        elif "丑时" in case['time']:
            hour = 2
        elif "寅时" in case['time']:
            hour = 4
        elif "卯时" in case['time']:
            hour = 6
        elif "辰时" in case['time']:
            hour = 8
        elif "巳时" in case['time']:
            hour = 10
        elif "午时" in case['time']:
            hour = 12
        elif "未时" in case['time']:
            hour = 14
        elif "申时" in case['time']:
            hour = 16
        elif "酉时" in case['time']:
            hour = 18
        elif "戌时" in case['time']:
            hour = 20
        elif "亥时" in case['time']:
            hour = 22
        
        # 计算神煞
        shen_sha = calculate_shen_sha(year, month, day, hour, case['gender'])
        
        # 打印结果
        logging.info(f"日冲: {shen_sha.get('dayChong', '无')}")
        logging.info(f"值神: {shen_sha.get('zhiShen', '无')}")
        logging.info(f"彭祖百忌: {shen_sha.get('pengZuGan', '无')} {shen_sha.get('pengZuZhi', '无')}")
        logging.info(f"喜神方位: {shen_sha.get('xiShen', '无')}")
        logging.info(f"福神方位: {shen_sha.get('fuShen', '无')}")
        logging.info(f"财神方位: {shen_sha.get('caiShen', '无')}")
        logging.info(f"本命神煞: {', '.join(shen_sha.get('benMing', ['无']))}")
        
        # 计算完整八字
        bazi = calculate_bazi(case['date'], case['time'], case['gender'])
        if bazi and 'shenSha' in bazi:
            logging.info("八字计算中的神煞信息已包含")

def test_da_yun_calculation():
    """测试大运计算功能"""
    logging.info("===== 测试大运计算功能 =====")
    
    test_cases = [
        {"date": "2006-10-15", "time": "午时 (11:00-13:00)", "gender": "male", "name": "2006年男命"},
        {"date": "1995-10-08", "time": "辰时 (07:00-09:00)", "gender": "male", "name": "1995年男命"},
        {"date": "1990-06-21", "time": "子时 (23:00-01:00)", "gender": "female", "name": "1990年女命"},
    ]
    
    for case in test_cases:
        logging.info(f"----------- 测试案例: {case['name']} -----------")
        
        # 解析日期和时间
        date_parts = case['date'].split('-')
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        
        # 解析时辰
        hour = 12  # 默认中午
        if "子时" in case['time']:
            hour = 0
        elif "丑时" in case['time']:
            hour = 2
        elif "寅时" in case['time']:
            hour = 4
        elif "卯时" in case['time']:
            hour = 6
        elif "辰时" in case['time']:
            hour = 8
        elif "巳时" in case['time']:
            hour = 10
        elif "午时" in case['time']:
            hour = 12
        elif "未时" in case['time']:
            hour = 14
        elif "申时" in case['time']:
            hour = 16
        elif "酉时" in case['time']:
            hour = 18
        elif "戌时" in case['time']:
            hour = 20
        elif "亥时" in case['time']:
            hour = 22
        
        # 计算大运
        da_yun = calculate_da_yun(year, month, day, hour, case['gender'])
        
        # 打印结果
        logging.info(f"起运年龄: {da_yun.get('startAge', '无')}岁")
        logging.info(f"起运年份: {da_yun.get('startYear', '无')}年")
        
        # 打印大运列表
        if 'daYunList' in da_yun:
            logging.info("大运列表:")
            for item in da_yun['daYunList']:
                logging.info(f"{item['index']}. {item['heavenlyStem']}{item['earthlyBranch']} ({item['element']}) {item['startYear']}-{item['endYear']}年")
        
        # 计算完整八字
        bazi = calculate_bazi(case['date'], case['time'], case['gender'])
        if bazi and 'daYun' in bazi:
            logging.info("八字计算中的大运信息已包含")

if __name__ == "__main__":
    logging.info("开始测试神煞和大运流年计算功能...")
    
    # 测试神煞计算
    test_shen_sha_calculation()
    
    # 测试大运计算
    test_da_yun_calculation()
    
    logging.info("测试完成!") 