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

# 已知正确的八字数据用于验证
KNOWN_CORRECT_BAZIS = [
    {
        "desc": "武则天 (624年2月17日)",
        "solar": {"year": 624, "month": 2, "day": 17, "hour": 12, "gender": "女"},
        "expected": {
            "year": "甲申",
            "month": "丁卯",
            "day": "庚子",
            "time": "己未"
        }
    },
    {
        "desc": "乾隆皇帝 (1711年9月25日)",
        "solar": {"year": 1711, "month": 9, "day": 25, "hour": 10, "gender": "男"},
        "expected": {
            "year": "辛卯",
            "month": "甲戌",
            "day": "丁丑",
            "time": "丁巳"
        }
    },
    {
        "desc": "李小龙 (1940年11月27日)",
        "solar": {"year": 1940, "month": 11, "day": 27, "hour": 6, "gender": "男"},
        "expected": {
            "year": "庚辰",
            "month": "戊子",
            "day": "壬戌",
            "time": "丁卯"
        }
    }
]

def print_header(text):
    """打印格式化的标题"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(58, "="))
    print("=" * 60)

def print_subheader(text):
    """打印子标题"""
    print("\n" + "-" * 40)
    print(f" {text} ".center(38, "-"))
    print("-" * 40)

def print_bazi_chart(bazi):
    """打印漂亮的八字排盘"""
    try:
        year = bazi['yearPillar']['heavenlyStem'] + bazi['yearPillar']['earthlyBranch']
        month = bazi['monthPillar']['heavenlyStem'] + bazi['monthPillar']['earthlyBranch']
        day = bazi['dayPillar']['heavenlyStem'] + bazi['dayPillar']['earthlyBranch']
        time = bazi['hourPillar']['heavenlyStem'] + bazi['hourPillar']['earthlyBranch']
        
        print("\n┌─────┬─────┬─────┬─────┐")
        print(f"│ 年柱 │ 月柱 │ 日柱 │ 时柱 │")
        print("├─────┼─────┼─────┼─────┤")
        print(f"│ {year[0]} {year[1]} │ {month[0]} {month[1]} │ {day[0]} {day[1]} │ {time[0]} {time[1]} │")
        print("└─────┴─────┴─────┴─────┘")
    except Exception as e:
        print(f"打印八字图表时出错: {e}")
        print(f"原始八字数据: {bazi}")

def validate_bazi(test_case):
    """验证八字计算的正确性"""
    solar = test_case["solar"]
    expected = test_case["expected"]
    
    print_subheader(f"测试用例: {test_case['desc']}")
    print(f"输入数据: {solar['year']}年{solar['month']}月{solar['day']}日 {solar['hour']}时 {solar['gender']}")
    
    # 构造birth_time字符串
    birth_time = f"{solar['year']}-{solar['month']:02d}-{solar['day']:02d} {solar['hour']:02d}:00:00"
    
    # 使用系统计算八字
    bazi_data = calculate_bazi(birth_time, solar['gender'])
    
    # 提取八字
    system_bazi = {
        'year': bazi_data['yearPillar']['heavenlyStem'] + bazi_data['yearPillar']['earthlyBranch'],
        'month': bazi_data['monthPillar']['heavenlyStem'] + bazi_data['monthPillar']['earthlyBranch'],
        'day': bazi_data['dayPillar']['heavenlyStem'] + bazi_data['dayPillar']['earthlyBranch'],
        'time': bazi_data['hourPillar']['heavenlyStem'] + bazi_data['hourPillar']['earthlyBranch']
    }
    
    print("\n计算得到的八字:")
    print_bazi_chart(bazi_data)
    
    # 验证结果
    is_correct = (
        system_bazi['year'] == expected['year'] and
        system_bazi['month'] == expected['month'] and
        system_bazi['day'] == expected['day'] and
        system_bazi['time'] == expected['time']
    )
    
    if is_correct:
        print("\n✓ 八字计算结果正确!")
    else:
        print("\n✗ 八字计算结果不匹配!")
        print("\n期望的八字:")
        print_bazi_chart({
            'yearPillar': {'heavenlyStem': expected['year'][0], 'earthlyBranch': expected['year'][1]},
            'monthPillar': {'heavenlyStem': expected['month'][0], 'earthlyBranch': expected['month'][1]},
            'dayPillar': {'heavenlyStem': expected['day'][0], 'earthlyBranch': expected['day'][1]},
            'hourPillar': {'heavenlyStem': expected['time'][0], 'earthlyBranch': expected['time'][1]}
        })
        
        print("\n差异:")
        for pillar in ['year', 'month', 'day', 'time']:
            if system_bazi[pillar] != expected[pillar]:
                print(f"{pillar}柱不匹配: 计算得 {system_bazi[pillar]}, 期望 {expected[pillar]}")
    
    return is_correct

def test_real_cases():
    """测试真实历史人物的八字数据"""
    print_header("八字计算正确性验证")
    
    print("\n使用历史上有记载的真实出生时间进行验证，检查八字计算的准确性。")
    
    results = []
    for test_case in KNOWN_CORRECT_BAZIS:
        result = validate_bazi(test_case)
        results.append(result)
    
    # 总结
    success_count = results.count(True)
    total_count = len(results)
    
    print("\n" + "-" * 60)
    print(f"验证结果总结: {success_count}/{total_count} 测试通过")
    if success_count == total_count:
        print("✓ 所有八字计算结果正确!")
    else:
        print("✗ 部分八字计算结果不正确，请检查计算逻辑!")

def test_current_date_functions():
    """测试当前日期的各项功能"""
    print_header("当前日期功能测试")
    
    # 获取当前日期时间
    now = datetime.datetime.now()
    birth_time = now.strftime("%Y-%m-%d %H:00:00")
    gender = '男'  # 可以根据需要修改
    
    print(f"\n当前日期时间: {birth_time}")
    print(f"性别: {gender}")
    
    # 计算八字
    bazi_data = calculate_bazi(birth_time, gender)
    
    # 打印八字
    print_subheader("八字排盘")
    print_bazi_chart(bazi_data)
    
    # 打印神煞
    print_subheader("神煞信息")
    if 'shenSha' in bazi_data:
        for position, values in bazi_data['shenSha'].items():
            values_str = ', '.join(values) if isinstance(values, list) else values
            print(f"{position}: {values_str}")
    else:
        print("无神煞信息")
    
    # 打印大运
    print_subheader("大运信息")
    if 'daYun' in bazi_data:
        qi_yun = bazi_data['daYun']
        print(f"起运年龄: {qi_yun['startAge']}岁")
        print(f"起运年份: {qi_yun['startYear']}年")
    
    # 格式化输出
    print_subheader("格式化输出")
    formatted_data = format_bazi_analysis(bazi_data)
    print(f"八字: {formatted_data['bazi']}")
    print(f"起运: {formatted_data['qi_yun']}")
    
    # 显示大运列表
    print_subheader("大运列表")
    print("┌───────┬───────┬───────┬───────┬───────┐")
    print("│ 大运  │ 年龄  │ 开始  │ 结束  │ 十神  │")
    print("├───────┼───────┼───────┼───────┼───────┤")
    if 'daYun' in bazi_data and 'daYunList' in bazi_data['daYun']:
        for yun in bazi_data['daYun']['daYunList'][:5]:  # 只显示前5个大运
            print(f"│ {yun['ganZhi']} │ {yun['startAge']}-{yun['endAge']}岁 │ {yun['startYear']}年 │ {yun['endYear']}年 │ {yun['shiShen']} │")
    print("└───────┴───────┴───────┴───────┴───────┘")

def main():
    """主函数"""
    # 测试真实案例
    test_real_cases()
    
    # 测试当前日期功能
    test_current_date_functions()

if __name__ == "__main__":
    main()