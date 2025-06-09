#!/usr/bin/env python
# coding: utf-8

import sys
import os
import datetime
import unittest
from lunar_python import Solar, Lunar

# 添加项目根目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bazi_calculator import calculate_bazi

def print_header(text):
    """打印格式化的标题"""
    print("\n" + "=" * 50)
    print(f" {text} ".center(48, "="))
    print("=" * 50)

def print_subheader(text):
    """打印格式化的子标题"""
    print("\n" + "-" * 40)
    print(f" {text} ".center(38, "-"))
    print("-" * 40)

def print_bazi_chart(bazi):
    """打印漂亮的八字排盘"""
    year = bazi['yearPillar']['heavenlyStem'] + bazi['yearPillar']['earthlyBranch']
    month = bazi['monthPillar']['heavenlyStem'] + bazi['monthPillar']['earthlyBranch']
    day = bazi['dayPillar']['heavenlyStem'] + bazi['dayPillar']['earthlyBranch']
    time = bazi['hourPillar']['heavenlyStem'] + bazi['hourPillar']['earthlyBranch']
    
    print("\n┌─────┬─────┬─────┬─────┐")
    print(f"│ 年柱 │ 月柱 │ 日柱 │ 时柱 │")
    print("├─────┼─────┼─────┼─────┤")
    print(f"│ {year[0]} {year[1]} │ {month[0]} {month[1]} │ {day[0]} {day[1]} │ {time[0]} {time[1]} │")
    print("└─────┴─────┴─────┴─────┘")

def test_bazi_calculation():
    """测试八字计算功能"""
    print_header("测试八字计算功能")
    
    # 测试用例：输入阳历日期，计算八字
    year = 1990
    month = 5
    day = 15
    hour = 14  # 14点，对应未时
    gender = '男'
    
    # 构造birth_time字符串
    birth_time = f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
    
    # 计算八字
    print(f"\n输入参数: {birth_time} {gender}")
    bazi_data = calculate_bazi(birth_time, gender)
    
    # 打印八字排盘
    print_subheader("八字排盘")
    print_bazi_chart(bazi_data)
    
    # 打印神煞
    print_subheader("神煞")
    if 'shenSha' in bazi_data:
        for position, values in bazi_data['shenSha'].items():
            values_str = ', '.join(values) if isinstance(values, list) else values
            print(f"{position}: {values_str}")
    else:
        print("无神煞信息")
    
    # 打印大运
    print_subheader("起运信息")
    if 'daYun' in bazi_data:
        qi_yun = bazi_data['daYun']
        print(f"起运年龄: {qi_yun['startAge']}岁")
        print(f"起运年份: {qi_yun['startYear']}年")
    
    print_subheader("大运列表")
    print("┌───────┬───────┬───────┬───────┬───────┬───────┐")
    print("│ 大运  │ 年龄  │ 开始  │ 结束  │ 十神  │ 长生  │")
    print("├───────┼───────┼───────┼───────┼───────┼───────┤")
    if 'daYun' in bazi_data and 'daYunList' in bazi_data['daYun']:
        for yun in bazi_data['daYun']['daYunList']:
            print(f"│ {yun['ganZhi']} │ {yun['startAge']}-{yun['endAge']}岁 │ {yun['startYear']}年 │ {yun['endYear']}年 │ {yun['shiShen']} │ {yun['changSheng']} │")
    print("└───────┴───────┴───────┴───────┴───────┴───────┘")
    
    return bazi_data

def test_formatted_output():
    """测试格式化输出"""
    print_header("测试格式化输出")
    
    birth_time = "1990-05-15 14:00:00"
    bazi_data = calculate_bazi(birth_time, '男')  # 直接创建新的对象避免重复输出
    formatted_data = format_bazi_analysis(bazi_data)
    
    print_subheader("格式化八字")
    print(formatted_data['bazi'])
    
    print_subheader("格式化神煞")
    if formatted_data['shen_sha']:
        print(formatted_data['shen_sha'])
    else:
        print("无神煞信息")
    
    print_subheader("格式化起运信息")
    print(formatted_data['qi_yun'])
    
    print_subheader("格式化大运表")
    print(formatted_data['da_yun'])

def test_multiple_dates():
    """测试多个日期的八字计算"""
    print_header("测试多个日期的八字计算")
    
    test_cases = [
        {"birth_time": "1990-05-15 14:00:00", "gender": '男', "desc": "1990年5月15日 14点 男"},
        {"birth_time": "1985-12-25 02:00:00", "gender": '女', "desc": "1985年12月25日 2点 女"},
        {"birth_time": "2000-01-01 00:00:00", "gender": '男', "desc": "2000年1月1日 0点 男"},
        {"birth_time": datetime.datetime.now().strftime("%Y-%m-%d %H:00:00"), 
         "gender": '女', "desc": "今天 现在 女"}
    ]
    
    for case in test_cases:
        print_subheader(f"测试用例: {case['desc']}")
        
        bazi_data = calculate_bazi(case['birth_time'], case['gender'])
        
        # 打印八字排盘
        print_bazi_chart(bazi_data)
        
        if 'daYun' in bazi_data:
            print(f"起运: {bazi_data['daYun']['startAge']}岁 ({bazi_data['daYun']['startYear']}年)")
            if 'daYunList' in bazi_data['daYun'] and bazi_data['daYun']['daYunList']:
                first_yun = bazi_data['daYun']['daYunList'][0]
                print(f"第一个大运: {first_yun['ganZhi']} ({first_yun['startAge']}岁起)")
        
        # 打印神煞
        if 'shenSha' in bazi_data:
            print("\n神煞信息:")
            for position, values in bazi_data['shenSha'].items():
                values_str = ', '.join(values) if isinstance(values, list) else values
                print(f"  {position}: {values_str}")
        else:
            print("\n无神煞信息")

def main():
    """主函数"""
    # 测试八字计算
    test_bazi_calculation()
    
    # 测试格式化输出
    test_formatted_output()
    
    # 测试多个日期
    test_multiple_dates()

if __name__ == "__main__":
    main() 