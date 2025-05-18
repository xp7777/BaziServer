#!/usr/bin/env python
# coding: utf-8

import sys
import os
import datetime

# 添加项目根目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bazi_calculator import get_bazi, format_bazi_analysis

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
    year = bazi['year']
    month = bazi['month']
    day = bazi['day']
    time = bazi['time']
    
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
    
    # 计算八字
    print(f"\n输入参数: {year}年{month}月{day}日 {hour}点 {gender}")
    bazi_data = get_bazi(year, month, day, hour, gender)
    
    # 打印八字排盘
    print_subheader("八字排盘")
    print_bazi_chart(bazi_data['bazi'])
    
    # 打印神煞
    print_subheader("神煞")
    if bazi_data['shen_sha']:
        for position, values in bazi_data['shen_sha'].items():
            values_str = ', '.join(values) if isinstance(values, list) else values
            print(f"{position}: {values_str}")
    else:
        print("无神煞信息")
    
    # 打印大运
    print_subheader("起运信息")
    qi_yun = bazi_data['da_yun']['qi_yun']
    print(f"起运年龄: {qi_yun['years']}岁")
    print(f"起运日期: {qi_yun['date']}")
    
    print_subheader("大运列表")
    print("┌───────┬───────┬───────┬───────┬───────┬───────┐")
    print("│ 大运  │ 年龄  │ 开始  │ 结束  │ 十神  │ 长生  │")
    print("├───────┼───────┼───────┼───────┼───────┼───────┤")
    for yun in bazi_data['da_yun']['da_yun_list']:
        print(f"│ {yun['da_yun']} │ {yun['start_age']}-{yun['end_age']}岁 │ {yun['start_year']}年 │ {yun['end_year']}年 │ {yun['shi_shen']} │ {yun['chang_sheng']} │")
    print("└───────┴───────┴───────┴───────┴───────┴───────┘")
    
    return bazi_data

def test_formatted_output():
    """测试格式化输出"""
    print_header("测试格式化输出")
    
    bazi_data = get_bazi(1990, 5, 15, 14, '男')  # 直接创建新的对象避免重复输出
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
        {"year": 1990, "month": 5, "day": 15, "hour": 14, "gender": '男', "desc": "1990年5月15日 14点 男"},
        {"year": 1985, "month": 12, "day": 25, "hour": 2, "gender": '女', "desc": "1985年12月25日 2点 女"},
        {"year": 2000, "month": 1, "day": 1, "hour": 0, "gender": '男', "desc": "2000年1月1日 0点 男"},
        {"year": datetime.datetime.now().year, "month": datetime.datetime.now().month, 
         "day": datetime.datetime.now().day, "hour": datetime.datetime.now().hour, 
         "gender": '女', "desc": "今天 现在 女"}
    ]
    
    for case in test_cases:
        print_subheader(f"测试用例: {case['desc']}")
        
        bazi_data = get_bazi(case['year'], case['month'], case['day'], case['hour'], case['gender'])
        
        # 打印八字排盘
        print_bazi_chart(bazi_data['bazi'])
        
        print(f"起运: {bazi_data['da_yun']['qi_yun']['years']}岁 ({bazi_data['da_yun']['qi_yun']['date']})")
        print(f"第一个大运: {bazi_data['da_yun']['da_yun_list'][0]['da_yun']} ({bazi_data['da_yun']['da_yun_list'][0]['start_age']}岁起)")
        
        # 打印神煞
        if bazi_data['shen_sha']:
            print("\n神煞信息:")
            for position, values in bazi_data['shen_sha'].items():
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