import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    import lunar_python
    print("成功导入lunar_python库")
    print("lunar_python路径:", lunar_python.__file__ if hasattr(lunar_python, "__file__") else "无路径信息")
    
    # 尝试使用基本功能
    try:
        from lunar_python.Solar import Solar
        solar = Solar.fromYmd(2023, 1, 1)
        print("创建Solar对象成功:", solar.toYmd())
    except Exception as e:
        print("使用Solar类失败:", str(e))
    
except ImportError as e:
    print("导入lunar_python库失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))

print("测试完成") 