#!/usr/bin/env python
# coding: utf-8

import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    from lunar_python import Solar, Lunar
    
    print("lunar-python库已成功导入")
    
    # 创建一个公历日期
    solar = Solar.fromYmd(2025, 5, 21)
    print("公历日期:", solar.toYmd())
    
    # 转换为农历
    lunar = solar.getLunar()
    print("农历日期:", lunar.toString())
    
    # 获取年、月、日的天干地支
    print("年干支:", lunar.getYearInGanZhi())
    print("月干支:", lunar.getMonthInGanZhi())
    print("日干支:", lunar.getDayInGanZhi())
    
    # 查看lunar对象的所有方法
    print("\n农历对象的所有方法:")
    methods = [method for method in dir(lunar) if not method.startswith('_')]
    for method in methods:
        print(f"  {method}")
    
    # 检查是否有isLeap相关的方法
    print("\n检查isLeap相关方法:")
    leap_methods = [method for method in methods if "leap" in method.lower()]
    for method in leap_methods:
        print(f"  {method}")
    
    # 尝试获取八字
    print("\n获取八字:")
    bazi = lunar.getBaZi()
    print("八字数组:", bazi)
    
    # 检查八字对象
    print("\n获取八字对象:")
    eight_char = lunar.getEightChar()
    print("八字对象:", eight_char)
    print("八字对象方法:", [m for m in dir(eight_char) if not m.startswith('_')])
    
    # 测试立春前后的年柱变化
    print("\n测试立春前后的年柱变化:")
    
    # 1990年2月3日 (立春前)
    solar_before = Solar.fromYmd(1990, 2, 3)
    lunar_before = solar_before.getLunar()
    print("立春前(1990-02-03):")
    print("  年干支:", lunar_before.getYearInGanZhi())
    
    # 1990年2月4日 (立春)
    solar_lichun = Solar.fromYmd(1990, 2, 4)
    lunar_lichun = solar_lichun.getLunar()
    print("立春(1990-02-04):")
    print("  年干支:", lunar_lichun.getYearInGanZhi())
    
    # 1990年2月5日 (立春后)
    solar_after = Solar.fromYmd(1990, 2, 5)
    lunar_after = solar_after.getLunar()
    print("立春后(1990-02-05):")
    print("  年干支:", lunar_after.getYearInGanZhi())
    
    print("\n测试完成")
    
except ImportError as e:
    print("导入lunar-python库失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    import traceback
    traceback.print_exc() 