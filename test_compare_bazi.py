#!/usr/bin/env python
# coding: utf-8

import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    # 导入两个库的八字计算模块
    from utils.bazi_calculator import get_bazi as get_bazi_sxtwl
    from utils.lunar_bazi_calculator import get_bazi as get_bazi_lunar
    
    # 测试不同年份的八字计算
    test_cases = [
        {"year": 2025, "month": 5, "day": 21, "hour": 12, "gender": "男", "desc": "2025年5月21日12点 男"},
        {"year": 1986, "month": 4, "day": 23, "hour": 17, "gender": "女", "desc": "1986年4月23日17点 女"},
        {"year": 1990, "month": 1, "day": 15, "hour": 12, "gender": "男", "desc": "1990年1月15日12点 男"},
        {"year": 1989, "month": 12, "day": 31, "hour": 23, "gender": "女", "desc": "1989年12月31日23点 女"},
        {"year": 1990, "month": 1, "day": 1, "hour": 0, "gender": "男", "desc": "1990年1月1日0点 男"},
        {"year": 1990, "month": 2, "day": 3, "hour": 12, "gender": "女", "desc": "1990年2月3日12点 女"}, # 立春前
        {"year": 1990, "month": 2, "day": 4, "hour": 12, "gender": "男", "desc": "1990年2月4日12点 男"}, # 立春
        {"year": 1990, "month": 2, "day": 5, "hour": 12, "gender": "女", "desc": "1990年2月5日12点 女"}, # 立春后
    ]
    
    print("\n=== 比较sxtwl和lunar-python计算的八字结果 ===\n")
    
    for case in test_cases:
        print(f"\n测试用例: {case['desc']}")
        print("-" * 50)
        
        # 使用sxtwl计算
        try:
            bazi_sxtwl = get_bazi_sxtwl(case["year"], case["month"], case["day"], case["hour"], case["gender"])
            print(f"sxtwl计算结果:")
            print(f"  年柱: {bazi_sxtwl['bazi']['year']}")
            print(f"  月柱: {bazi_sxtwl['bazi']['month']}")
            print(f"  日柱: {bazi_sxtwl['bazi']['day']}")
            print(f"  时柱: {bazi_sxtwl['bazi']['time']}")
        except Exception as e:
            print(f"sxtwl计算出错: {str(e)}")
        
        # 使用lunar-python计算
        try:
            bazi_lunar = get_bazi_lunar(case["year"], case["month"], case["day"], case["hour"], case["gender"])
            print(f"lunar-python计算结果:")
            print(f"  年柱: {bazi_lunar['bazi']['year']}")
            print(f"  月柱: {bazi_lunar['bazi']['month']}")
            print(f"  日柱: {bazi_lunar['bazi']['day']}")
            print(f"  时柱: {bazi_lunar['bazi']['time']}")
            
            # 显示农历日期
            lunar_date = bazi_lunar.get("lunar_date", {})
            print(f"  农历: {lunar_date.get('year')}年{lunar_date.get('month')}月{lunar_date.get('day')}日 {'闰' if lunar_date.get('isLeap') else ''}月")
        except Exception as e:
            print(f"lunar-python计算出错: {str(e)}")
        
        # 比较结果
        try:
            if bazi_sxtwl['bazi']['year'] != bazi_lunar['bazi']['year']:
                print(f"年柱不同: sxtwl={bazi_sxtwl['bazi']['year']}, lunar-python={bazi_lunar['bazi']['year']}")
            if bazi_sxtwl['bazi']['month'] != bazi_lunar['bazi']['month']:
                print(f"月柱不同: sxtwl={bazi_sxtwl['bazi']['month']}, lunar-python={bazi_lunar['bazi']['month']}")
            if bazi_sxtwl['bazi']['day'] != bazi_lunar['bazi']['day']:
                print(f"日柱不同: sxtwl={bazi_sxtwl['bazi']['day']}, lunar-python={bazi_lunar['bazi']['day']}")
            if bazi_sxtwl['bazi']['time'] != bazi_lunar['bazi']['time']:
                print(f"时柱不同: sxtwl={bazi_sxtwl['bazi']['time']}, lunar-python={bazi_lunar['bazi']['time']}")
        except:
            print("无法比较结果")
    
except ImportError as e:
    print("导入模块失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    import traceback
    traceback.print_exc() 