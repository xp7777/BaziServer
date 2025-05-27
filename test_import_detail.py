#!/usr/bin/env python
# coding: utf-8

import sys
import os
import traceback

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    print("\n步骤1: 尝试导入lunar_python包")
    import lunar_python
    print("成功导入lunar_python包")
    print("lunar_python路径:", lunar_python.__file__)
    print("lunar_python目录内容:", dir(lunar_python))
except Exception as e:
    print("导入lunar_python包失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤2: 尝试从lunar_python导入Solar类")
    from lunar_python import Solar
    print("成功导入Solar类")
    print("Solar类内容:", dir(Solar))
except Exception as e:
    print("导入Solar类失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤3: 尝试从lunar_python导入Lunar类")
    from lunar_python import Lunar
    print("成功导入Lunar类")
    print("Lunar类内容:", dir(Lunar))
except Exception as e:
    print("导入Lunar类失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤4: 尝试创建Solar对象")
    solar = Solar.fromYmd(2025, 5, 21)
    print("成功创建Solar对象:", solar)
    print("公历日期:", solar.toYmd())
except Exception as e:
    print("创建Solar对象失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤5: 尝试获取Lunar对象")
    lunar = solar.getLunar()
    print("成功获取Lunar对象:", lunar)
    print("农历日期:", lunar.toString())
except Exception as e:
    print("获取Lunar对象失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n步骤6: 尝试获取八字")
    print("年干支:", lunar.getYearInGanZhi())
    print("月干支:", lunar.getMonthInGanZhi())
    print("日干支:", lunar.getDayInGanZhi())
    print("时干支:", lunar.getTimeInGanZhi())
except Exception as e:
    print("获取八字失败:", str(e))
    traceback.print_exc()
    sys.exit(1)

print("\n测试完成，所有步骤都成功执行") 