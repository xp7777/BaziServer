import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    import lunar_python
    print("lunar_python库版本:", lunar_python.__version__ if hasattr(lunar_python, "__version__") else "无版本信息")
    print("lunar_python路径:", lunar_python.__file__ if hasattr(lunar_python, "__file__") else "无路径信息")
    
    # 导入关键类
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    print("成功导入Solar和Lunar类")
    
    # 显示lunar_python模块内容
    print("\nlunar_python模块内容:")
    print(sorted([item for item in dir(lunar_python) if not item.startswith('__')]))
    
    # 测试基本功能
    solar = Solar.fromYmd(1970, 10, 10)  # 示例日期
    lunar = solar.getLunar()
    print("\n公历:", solar.toYmd())
    print("农历:", lunar.toString())
    
    # 显示Solar类的方法
    print("\nSolar类的方法:")
    print(sorted([method for method in dir(Solar) if not method.startswith('__')]))
    
    # 显示Lunar类的方法
    print("\nLunar类的方法:")
    print(sorted([method for method in dir(Lunar) if not method.startswith('__')]))
    
    # 显示lunar对象的方法
    print("\n具体lunar对象的方法:")
    print(sorted([method for method in dir(lunar) if not method.startswith('__')]))
    
    # 测试八字相关方法
    print("\n八字相关测试:")
    
    if hasattr(lunar, 'getBaZi'):
        print("八字:", " ".join(lunar.getBaZi()))
    else:
        print("lunar对象没有getBaZi方法")
    
    if hasattr(lunar, 'getEightChar'):
        bazi = lunar.getEightChar()
        print("八字对象:", bazi)
        print("八字对象方法:", sorted([method for method in dir(bazi) if not method.startswith('__')]))
    else:
        print("lunar对象没有getEightChar方法")
    
    # 检查getYearGan等方法
    for method_name in ['getYearGan', 'getYearZhi', 'getMonthGan', 'getMonthZhi', 'getDayGan', 'getDayZhi', 'getTimeGan', 'getTimeZhi']:
        if hasattr(lunar, method_name):
            try:
                value = getattr(lunar, method_name)()
                print(f"{method_name}(): {value}")
            except Exception as e:
                print(f"{method_name}() 调用失败: {str(e)}")
        else:
            print(f"lunar对象没有{method_name}方法")
    
except ImportError as e:
    print("导入lunar_python库失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    import traceback
    traceback.print_exc()

print("\n测试完成") 