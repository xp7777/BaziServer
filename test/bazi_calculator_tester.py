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
        year = bazi['year']
        month = bazi['month']
        day = bazi['day']
        time = bazi['time']
        
        print("\n┌─────┬─────┬─────┬─────┐")
        print(f"│ 年柱 │ 月柱 │ 日柱 │ 时柱 │")
        print("├─────┼─────┼─────┼─────┤")
        print(f"│ {year[0]} {year[1]} │ {month[0]} {month[1]} │ {day[0]} {day[1]} │ {time[0]} {time[1]} │")
        print("└─────┴─────┴─────┴─────┘")
    except Exception as e:
        print(f"打印八字图表时出错: {e}")
        print(f"原始八字数据: {bazi}")

def show_analysis_results(bazi_data):
    """显示八字分析结果"""
    # 打印八字
    print_subheader("八字排盘")
    print_bazi_chart(bazi_data['bazi'])
    
    # 打印神煞
    print_subheader("神煞信息")
    if bazi_data['shen_sha']:
        for position, values in bazi_data['shen_sha'].items():
            values_str = ', '.join(values) if isinstance(values, list) else values
            print(f"{position}: {values_str}")
    else:
        print("无神煞信息")
    
    # 打印大运
    print_subheader("大运信息")
    qi_yun = bazi_data['da_yun']['qi_yun']
    print(f"起运年龄: {qi_yun['years']}岁")
    print(f"起运日期: {qi_yun['date']}")
    
    # 显示大运列表
    print_subheader("大运列表")
    print("┌───────┬───────┬───────┬───────┬───────┬───────┐")
    print("│ 大运  │ 年龄  │ 开始  │ 结束  │ 十神  │ 旺衰  │")
    print("├───────┼───────┼───────┼───────┼───────┼───────┤")
    for yun in bazi_data['da_yun']['da_yun_list'][:8]:  # 显示8个大运
        print(f"│ {yun['da_yun']} │ {yun['start_age']}-{yun['end_age']}岁 │ {yun['start_year']}年 │ {yun['end_year']}年 │ {yun['shi_shen']} │ {yun['chang_sheng']} │")
    print("└───────┴───────┴───────┴───────┴───────┴───────┘")
    
    # 格式化输出
    formatted_data = format_bazi_analysis(bazi_data)
    print_subheader("格式化输出 (适用于AI分析)")
    print(f"八字: {formatted_data['bazi']}")
    if formatted_data['shen_sha']:
        print(f"\n神煞: \n{formatted_data['shen_sha']}")
    print(f"\n起运: {formatted_data['qi_yun']}")

def get_user_input():
    """获取用户输入的出生信息"""
    print_header("八字命理计算测试")
    print("\n请输入出生信息(阳历):")
    
    # 设置默认值，方便测试
    default_year = datetime.datetime.now().year
    default_month = datetime.datetime.now().month
    default_day = datetime.datetime.now().day
    default_hour = datetime.datetime.now().hour
    default_gender = '男'
    
    try:
        year_input = input(f"年份 (默认: {default_year}): ").strip()
        year = int(year_input) if year_input else default_year
        
        month_input = input(f"月份 (默认: {default_month}): ").strip()
        month = int(month_input) if month_input else default_month
        
        day_input = input(f"日期 (默认: {default_day}): ").strip()
        day = int(day_input) if day_input else default_day
        
        hour_input = input(f"小时(0-23) (默认: {default_hour}): ").strip()
        hour = int(hour_input) if hour_input else default_hour
        
        gender_input = input(f"性别('男'/'女') (默认: {default_gender}): ").strip()
        gender = gender_input if gender_input else default_gender
        
        return {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'gender': gender
        }
    except ValueError as e:
        print(f"输入格式错误: {e}")
        print("将使用默认值继续...")
        return {
            'year': default_year,
            'month': default_month,
            'day': default_day,
            'hour': default_hour,
            'gender': default_gender
        }

def test_predefined_dates():
    """测试预定义的日期"""
    print_header("测试预定义的著名日期")
    
    test_cases = [
        {"desc": "乔布斯 (1955年2月24日)", "year": 1955, "month": 2, "day": 24, "hour": 19, "gender": "男"},
        {"desc": "比尔·盖茨 (1955年10月28日)", "year": 1955, "month": 10, "day": 28, "hour": 21, "gender": "男"},
        {"desc": "马云 (1964年9月10日)", "year": 1964, "month": 9, "day": 10, "hour": 12, "gender": "男"},
    ]
    
    for case in test_cases:
        print_subheader(case["desc"])
        print(f"出生信息: {case['year']}年{case['month']}月{case['day']}日 {case['hour']}时 {case['gender']}")
        
        bazi_data = get_bazi(
            case['year'], 
            case['month'], 
            case['day'], 
            case['hour'], 
            case['gender']
        )
        
        # 打印八字排盘
        print_bazi_chart(bazi_data['bazi'])
        
        # 打印起运信息
        qi_yun = bazi_data['da_yun']['qi_yun']
        print(f"\n起运年龄: {qi_yun['years']}岁")
        print(f"起运日期: {qi_yun['date']}")
        
        # 打印神煞
        if bazi_data['shen_sha']:
            print("\n神煞信息:")
            for position, values in bazi_data['shen_sha'].items():
                values_str = ', '.join(values) if isinstance(values, list) else values
                print(f"  {position}: {values_str}")

def main():
    """主函数"""
    while True:
        print_header("八字命理计算测试工具")
        print("\n1. 输入出生信息计算八字")
        print("2. 测试预定义的著名人物")
        print("3. 使用当前时间进行测试")
        print("0. 退出")
        
        choice = input("\n请选择功能: ").strip()
        
        if choice == '1':
            birth_info = get_user_input()
            bazi_data = get_bazi(
                birth_info['year'],
                birth_info['month'],
                birth_info['day'],
                birth_info['hour'],
                birth_info['gender']
            )
            show_analysis_results(bazi_data)
        
        elif choice == '2':
            test_predefined_dates()
        
        elif choice == '3':
            now = datetime.datetime.now()
            print_subheader("当前日期时间")
            print(f"时间: {now.year}年{now.month}月{now.day}日 {now.hour}时")
            
            bazi_data = get_bazi(now.year, now.month, now.day, now.hour, '男')
            show_analysis_results(bazi_data)
        
        elif choice == '0':
            print("\n谢谢使用，再见!")
            break
        
        else:
            print("\n无效选择，请重新输入!")
        
        input("\n按Enter键继续...")

if __name__ == "__main__":
    main() 