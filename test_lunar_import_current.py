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
    
    print("\n步骤2: 尝试从lunar_python导入Solar和Lunar类")
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    print("成功导入Solar和Lunar类")
    
    print("\n步骤3: 测试基本功能")
    solar = Solar.fromYmd(1970, 10, 10)  # 使用您示例中的日期
    lunar = solar.getLunar()
    print("公历:", solar.toYmd())
    print("农历:", lunar.toString())
    print("八字:", " ".join(lunar.getBaZi()))
    
    print("\n步骤4: 测试神煞计算")
    bazi = lunar.getEightChar()
    print("日主:", lunar.getDayGan())
    print("年干:", lunar.getYearGan())
    print("年支:", lunar.getYearZhi())
    
    # 测试一些可能会出问题的方法
    try:
        solar_terms = lunar.getTerm()
        print("节气信息:", solar_terms.getName())
    except Exception as e:
        print("获取节气信息失败:", str(e))
        traceback.print_exc()
    
except ImportError as e:
    print("导入模块失败:", str(e))
    traceback.print_exc()
except Exception as e:
    print("发生其他错误:", str(e))
    traceback.print_exc()

print("\n测试完成") 