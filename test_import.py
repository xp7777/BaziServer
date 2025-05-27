#!/usr/bin/env python
# coding: utf-8

import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)

try:
    print("\n尝试导入sxtwl库...")
    import sxtwl
    print("导入sxtwl成功")
    print("sxtwl版本:", getattr(sxtwl, "__version__", "未知"))
    print("sxtwl模块路径:", sxtwl.__file__)
except ImportError as e:
    print("导入sxtwl失败:", str(e))
except Exception as e:
    print("导入sxtwl时发生其他错误:", str(e))

try:
    print("\n尝试导入lunar_python库...")
    import lunar_python
    print("导入lunar_python成功")
    print("lunar_python版本:", getattr(lunar_python, "__version__", "未知"))
    print("lunar_python模块路径:", lunar_python.__file__)
    
    print("\n检查lunar_python子模块...")
    print("lunar_python内容:", dir(lunar_python))
    
    from lunar_python import Solar, Lunar
    print("导入Solar和Lunar成功")
except ImportError as e:
    print("导入lunar_python失败:", str(e))
except Exception as e:
    print("导入lunar_python时发生其他错误:", str(e))

print("\n所有测试完成") 