#!/usr/bin/env python
# coding: utf-8

import sys
import os
import traceback

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    from lunar_python import Solar, Lunar
    
    print("lunar-python库已成功导入")
    
    # 创建一个公历日期：2025年5月21日12点
    solar = Solar.fromYmdHms(2025, 5, 21, 12, 0, 0)
    print("公历日期:", solar.toYmd())
    
    # 转换为农历
    lunar = solar.getLunar()
    print("农历日期:", lunar.toString())
    
    # 获取年、月、日、时的天干地支
    print("年干支:", lunar.getYearInGanZhi(), f"({lunar.getYearGan()}{lunar.getYearZhi()})")
    print("月干支:", lunar.getMonthInGanZhi(), f"({lunar.getMonthGan()}{lunar.getMonthZhi()})")
    print("日干支:", lunar.getDayInGanZhi(), f"({lunar.getDayGan()}{lunar.getDayZhi()})")
    print("时干支:", lunar.getTimeInGanZhi(), f"({lunar.getTimeGan()}{lunar.getTimeZhi()})")
    
    # 获取八字
    bazi = lunar.getBaZi()
    print("八字数组:", bazi)
    print("八字:", " ".join(bazi))
    
    # 检查是否和预期相符
    expected_year = "乙巳"
    actual_year = f"{lunar.getYearGan()}{lunar.getYearZhi()}"
    print(f"\n年柱比较:")
    print(f"预期: {expected_year}")
    print(f"实际: {actual_year}")
    print(f"是否匹配: {expected_year == actual_year}")
    
    # 检查立春前后年柱的变化
    print("\n立春前后年柱变化:")
    
    # 立春前
    solar_before = Solar.fromYmd(2025, 2, 3)
    lunar_before = solar_before.getLunar()
    print("立春前(2025-02-03):")
    print("  年干支:", lunar_before.getYearInGanZhi())
    
    # 立春
    solar_lichun = Solar.fromYmd(2025, 2, 4)
    lunar_lichun = solar_lichun.getLunar()
    print("立春(2025-02-04):")
    print("  年干支:", lunar_lichun.getYearInGanZhi())
    
    # 立春后
    solar_after = Solar.fromYmd(2025, 2, 5)
    lunar_after = solar_after.getLunar()
    print("立春后(2025-02-05):")
    print("  年干支:", lunar_after.getYearInGanZhi())
    
    print("\n测试完成")
    
except ImportError as e:
    print("导入lunar-python库失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    traceback.print_exc() 