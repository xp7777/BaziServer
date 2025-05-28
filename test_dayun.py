#!/usr/bin/env python
# coding: utf-8

import sys
import os
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入八字计算模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.bazi_calculator import calculate_bazi, calculate_da_yun

def test_da_yun(birth_date, birth_time, gender):
    """测试大运计算"""
    logging.info(f"测试大运计算: {birth_date}, {birth_time}, {gender}")
    
    # 解析出生日期
    year, month, day = map(int, birth_date.split('-'))
    
    # 解析出生时间
    hour = int(birth_time.split(':')[0])
    
    # 计算大运
    da_yun = calculate_da_yun(year, month, day, hour, gender)
    
    # 打印大运基本信息
    logging.info(f"大运起运年龄: {da_yun.get('startAge')}岁，起运年份: {da_yun.get('startYear')}年")
    
    # 打印大运列表
    da_yun_list = da_yun.get('daYunList', [])
    if da_yun_list:
        logging.info(f"大运列表(前5项):")
        for i, yun in enumerate(da_yun_list[:5]):
            logging.info(f"  第{i+1}运: {yun.get('ganZhi')}，{yun.get('startYear')}-{yun.get('endYear')}年，{yun.get('startAge')}-{yun.get('endAge')}岁")
    else:
        logging.warning("大运列表为空")
    
    # 打印小运列表
    xiao_yun_list = da_yun.get('xiaoYunList', [])
    if xiao_yun_list:
        logging.info(f"小运列表(前5项):")
        for i, yun in enumerate(xiao_yun_list[:5]):
            logging.info(f"  {yun.get('year')}年: {yun.get('ganZhi')}，{yun.get('age')}岁")
    else:
        logging.warning("小运列表为空")
    
    return da_yun

if __name__ == "__main__":
    # 测试示例1: 1970年10月10日出生
    test_da_yun("1970-10-10", "3:46", "female")
    
    # 测试示例2: 2008年5月15日出生
    test_da_yun("2008-05-15", "12:00", "male") 