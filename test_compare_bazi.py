#!/usr/bin/env python
# coding: utf-8

import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    # 导入两个库的八字计算模块
    from utils.bazi_calculator import calculate_bazi as calculate_bazi_sxtwl
    from utils.lunar_bazi_calculator import calculate_bazi as calculate_bazi_lunar
    
    # 测试不同年份的八字计算
    test_cases = [
        {"birth_time": "2025-05-21 12:00:00", "gender": "男", "desc": "2025年5月21日12点 男"},
        {"birth_time": "1986-04-23 17:00:00", "gender": "女", "desc": "1986年4月23日17点 女"},
        {"birth_time": "1990-01-15 12:00:00", "gender": "男", "desc": "1990年1月15日12点 男"},
        {"birth_time": "1989-12-31 23:00:00", "gender": "女", "desc": "1989年12月31日23点 女"},
        {"birth_time": "1990-01-01 00:00:00", "gender": "男", "desc": "1990年1月1日0点 男"},
        {"birth_time": "1990-02-03 12:00:00", "gender": "女", "desc": "1990年2月3日12点 女"}, # 立春前
        {"birth_time": "1990-02-04 12:00:00", "gender": "男", "desc": "1990年2月4日12点 男"}, # 立春
        {"birth_time": "1990-02-05 12:00:00", "gender": "女", "desc": "1990年2月5日12点 女"}, # 立春后
    ]
    
    print("\n=== 比较sxtwl和lunar-python计算的八字结果 ===\n")
    
    for case in test_cases:
        print(f"\n测试用例: {case['desc']}")
        print("-" * 50)
        
        # 使用sxtwl计算
        try:
            bazi_sxtwl = calculate_bazi_sxtwl(case["birth_time"], case["gender"])
            print(f"sxtwl计算结果:")
            print(f"  年柱: {bazi_sxtwl['yearPillar']['heavenlyStem']}{bazi_sxtwl['yearPillar']['earthlyBranch']}")
            print(f"  月柱: {bazi_sxtwl['monthPillar']['heavenlyStem']}{bazi_sxtwl['monthPillar']['earthlyBranch']}")
            print(f"  日柱: {bazi_sxtwl['dayPillar']['heavenlyStem']}{bazi_sxtwl['dayPillar']['earthlyBranch']}")
            print(f"  时柱: {bazi_sxtwl['hourPillar']['heavenlyStem']}{bazi_sxtwl['hourPillar']['earthlyBranch']}")
        except Exception as e:
            print(f"sxtwl计算出错: {str(e)}")
        
        # 使用lunar-python计算
        try:
            bazi_lunar = calculate_bazi_lunar(case["birth_time"], case["gender"])
            print(f"lunar-python计算结果:")
            print(f"  年柱: {bazi_lunar['yearPillar']['heavenlyStem']}{bazi_lunar['yearPillar']['earthlyBranch']}")
            print(f"  月柱: {bazi_lunar['monthPillar']['heavenlyStem']}{bazi_lunar['monthPillar']['earthlyBranch']}")
            print(f"  日柱: {bazi_lunar['dayPillar']['heavenlyStem']}{bazi_lunar['dayPillar']['earthlyBranch']}")
            print(f"  时柱: {bazi_lunar['hourPillar']['heavenlyStem']}{bazi_lunar['hourPillar']['earthlyBranch']}")
            
            # 显示农历日期
            lunar_date = bazi_lunar.get("lunarDate", {})
            print(f"  农历: {lunar_date.get('year')}年{lunar_date.get('month')}月{lunar_date.get('day')}日 {'闰' if lunar_date.get('isLeap') else ''}月")
        except Exception as e:
            print(f"lunar-python计算出错: {str(e)}")
        
        # 比较结果
        try:
            year_sxtwl = bazi_sxtwl['yearPillar']['heavenlyStem'] + bazi_sxtwl['yearPillar']['earthlyBranch']
            month_sxtwl = bazi_sxtwl['monthPillar']['heavenlyStem'] + bazi_sxtwl['monthPillar']['earthlyBranch']
            day_sxtwl = bazi_sxtwl['dayPillar']['heavenlyStem'] + bazi_sxtwl['dayPillar']['earthlyBranch']
            time_sxtwl = bazi_sxtwl['hourPillar']['heavenlyStem'] + bazi_sxtwl['hourPillar']['earthlyBranch']
            
            year_lunar = bazi_lunar['yearPillar']['heavenlyStem'] + bazi_lunar['yearPillar']['earthlyBranch']
            month_lunar = bazi_lunar['monthPillar']['heavenlyStem'] + bazi_lunar['monthPillar']['earthlyBranch']
            day_lunar = bazi_lunar['dayPillar']['heavenlyStem'] + bazi_lunar['dayPillar']['earthlyBranch']
            time_lunar = bazi_lunar['hourPillar']['heavenlyStem'] + bazi_lunar['hourPillar']['earthlyBranch']
            
            if year_sxtwl != year_lunar:
                print(f"年柱不同: sxtwl={year_sxtwl}, lunar-python={year_lunar}")
            if month_sxtwl != month_lunar:
                print(f"月柱不同: sxtwl={month_sxtwl}, lunar-python={month_lunar}")
            if day_sxtwl != day_lunar:
                print(f"日柱不同: sxtwl={day_sxtwl}, lunar-python={day_lunar}")
            if time_sxtwl != time_lunar:
                print(f"时柱不同: sxtwl={time_sxtwl}, lunar-python={time_lunar}")
        except:
            print("无法比较结果")
    
except ImportError as e:
    print("导入模块失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    import traceback
    traceback.print_exc() 