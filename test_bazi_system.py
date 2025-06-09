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
from utils.bazi_calculator import calculate_bazi

def test_bazi_system():
    """测试八字命理系统"""
    # 测试用例：2008年1月1日12时出生的男性
    birth_date = "2008-01-01"
    birth_time = "午时 (11:00-13:00)"
    gender = "male"
    
    logging.info(f"测试八字命理系统: {birth_date}, {birth_time}, {gender}")
    
    # 计算八字
    bazi_data = calculate_bazi(birth_date, birth_time, gender)
    assert bazi_data is not None, "八字计算失败"
    
    # 打印四柱
    logging.info(f"四柱:")
    logging.info(f"  年柱: {bazi_data['yearPillar']['heavenlyStem']}{bazi_data['yearPillar']['earthlyBranch']} ({bazi_data['yearPillar']['element']})")
    logging.info(f"  月柱: {bazi_data['monthPillar']['heavenlyStem']}{bazi_data['monthPillar']['earthlyBranch']} ({bazi_data['monthPillar']['element']})")
    logging.info(f"  日柱: {bazi_data['dayPillar']['heavenlyStem']}{bazi_data['dayPillar']['earthlyBranch']} ({bazi_data['dayPillar']['element']})")
    logging.info(f"  时柱: {bazi_data['hourPillar']['heavenlyStem']}{bazi_data['hourPillar']['earthlyBranch']} ({bazi_data['hourPillar']['element']})")
    
    # 验证四柱
    assert 'yearPillar' in bazi_data, "缺少年柱信息"
    assert 'monthPillar' in bazi_data, "缺少月柱信息"
    assert 'dayPillar' in bazi_data, "缺少日柱信息"
    assert 'hourPillar' in bazi_data, "缺少时柱信息"
    
    # 打印神煞信息
    shen_sha = bazi_data.get('shenSha', {})
    logging.info(f"神煞信息:")
    logging.info(f"  日冲: {shen_sha.get('dayChong', '计算失败')}")
    logging.info(f"  值神: {shen_sha.get('zhiShen', '计算失败')}")
    logging.info(f"  彭祖百忌: 干-{shen_sha.get('pengZuGan', '计算失败')}, 支-{shen_sha.get('pengZuZhi', '计算失败')}")
    logging.info(f"  喜神方位: {shen_sha.get('xiShen', '计算失败')}")
    logging.info(f"  福神方位: {shen_sha.get('fuShen', '计算失败')}")
    logging.info(f"  财神方位: {shen_sha.get('caiShen', '计算失败')}")
    
    # 验证神煞信息
    assert shen_sha, "缺少神煞信息"
    assert 'dayChong' in shen_sha, "缺少日冲信息"
    assert 'zhiShen' in shen_sha, "缺少值神信息"
    assert 'benMing' in shen_sha, "缺少本命神煞信息"
    
    # 打印大运信息
    da_yun = bazi_data.get('daYun', {})
    logging.info(f"大运信息:")
    logging.info(f"  起运年龄: {da_yun.get('startAge', '计算失败')}岁")
    logging.info(f"  起运年份: {da_yun.get('startYear', '计算失败')}年")
    logging.info(f"  排法: {'顺排' if da_yun.get('isForward') else '逆排'}")
    
    # 验证大运信息
    assert da_yun, "缺少大运信息"
    assert 'startAge' in da_yun, "缺少起运年龄"
    assert 'startYear' in da_yun, "缺少起运年份"
    assert 'daYunList' in da_yun, "缺少大运列表"
    
    # 打印大运列表
    da_yun_list = da_yun.get('daYunList', [])
    if da_yun_list:
        logging.info(f"  大运列表:")
        for yun in da_yun_list[:5]:  # 只显示前5个大运
            logging.info(f"    第{yun['index']}运: {yun['ganZhi']} ({yun['element']})")
            logging.info(f"      {yun['startYear']}-{yun['endYear']}年 ({yun['startAge']}-{yun['endAge']}岁)")
            logging.info(f"      十神: {yun['shiShen']}")
            logging.info(f"      旺衰: {yun['wangShuai']}")
            logging.info(f"      纳音: {yun['naYin']}")
    else:
        logging.info("  大运列表: 暂无数据")
    
    # 打印测试结果
    logging.info("测试通过！")

if __name__ == "__main__":
    test_bazi_system() 