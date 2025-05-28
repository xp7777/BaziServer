#!/usr/bin/env python
# coding: utf-8

import sys
import os
import json
import logging
import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入八字计算模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.bazi_calculator import calculate_bazi, calculate_shen_sha, calculate_da_yun

def test_bazi_system(birth_date, birth_time, gender):
    """测试八字命理系统"""
    logging.info(f"测试八字命理系统: {birth_date}, {birth_time}, {gender}")
    
    # 解析出生日期
    year, month, day = map(int, birth_date.split('-'))
    
    # 解析出生时间
    hour = int(birth_time.split(':')[0])
    
    # 计算年龄
    current_year = datetime.datetime.now().year
    age = current_year - year
    
    logging.info(f"年龄: {age}岁")
    
    # 计算八字
    bazi_data = calculate_bazi(birth_date, birth_time, gender)
    
    # 打印四柱
    logging.info(f"四柱: {bazi_data.get('yearPillar', {}).get('text', '')} {bazi_data.get('monthPillar', {}).get('text', '')} {bazi_data.get('dayPillar', {}).get('text', '')} {bazi_data.get('hourPillar', {}).get('text', '')}")
    
    # 打印学业发展和性格分析
    analysis = bazi_data.get('analysis', {})
    career = analysis.get('career', {})
    personality = analysis.get('personality', '')
    
    logging.info(f"学业发展: {career.get('education', '未提供')[:100]}...")
    logging.info(f"性格分析: {personality[:100]}...")
    
    # 计算神煞
    shen_sha = calculate_shen_sha(year, month, day, hour, gender)
    
    # 打印神煞信息
    logging.info(f"神煞信息:")
    logging.info(f"  日冲: {shen_sha.get('dayChong', '计算失败')}")
    logging.info(f"  彭祖百忌: {shen_sha.get('pengZuGan', '计算失败')} {shen_sha.get('pengZuZhi', '计算失败')}")
    logging.info(f"  喜神方位: {shen_sha.get('xiShen', '计算失败')}")
    logging.info(f"  福神方位: {shen_sha.get('fuShen', '计算失败')}")
    logging.info(f"  财神方位: {shen_sha.get('caiShen', '计算失败')}")
    
    # 计算大运
    da_yun = calculate_da_yun(year, month, day, hour, gender)
    
    # 打印大运信息
    logging.info(f"大运信息:")
    logging.info(f"  起运年龄: {da_yun.get('startAge', '计算失败')}岁，起运年份: {da_yun.get('startYear', '计算失败')}年")
    
    # 打印大运列表
    da_yun_list = da_yun.get('daYunList', [])
    if da_yun_list:
        logging.info(f"  大运列表(前5项):")
        for i, yun in enumerate(da_yun_list[:5]):
            logging.info(f"    第{i+1}运: {yun.get('ganZhi', '计算失败')}，{yun.get('startYear', '?')}-{yun.get('endYear', '?')}年，{yun.get('startAge', '?')}-{yun.get('endAge', '?')}岁")
    else:
        logging.warning("  大运列表为空")
    
    return {
        "bazi": bazi_data,
        "shenSha": shen_sha,
        "daYun": da_yun
    }

if __name__ == "__main__":
    # 测试2008年出生的用户
    test_bazi_system("2008-01-01", "12:00", "male")
    
    # 分隔线
    logging.info("-" * 50)
    
    # 测试示例: 1970年10月10日出生的用户
    test_bazi_system("1970-10-10", "3:46", "female") 