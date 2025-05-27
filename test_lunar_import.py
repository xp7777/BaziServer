import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

print("测试lunar-python库的导入")

try:
    # 尝试导入lunar_python库
    import lunar_python
    print("成功导入lunar_python库")
    print("lunar_python模块路径:", lunar_python.__file__)
    print("lunar_python模块内容:", dir(lunar_python))
    
    # 尝试导入lunar_python中的各个类
    try:
        from lunar_python import Solar
        print("成功导入Solar类")
    except ImportError as e:
        print(f"导入Solar类失败: {str(e)}")
    
    try:
        from lunar_python import Lunar
        print("成功导入Lunar类")
    except ImportError as e:
        print(f"导入Lunar类失败: {str(e)}")
    
    try:
        from lunar_python.Lunar import Lunar
        print("成功导入lunar_python.Lunar.Lunar类")
    except ImportError as e:
        print("导入lunar_python.Lunar.Lunar类失败:", str(e))
    
    try:
        from lunar_python.Solar import Solar
        print("成功导入lunar_python.Solar.Solar类")
    except ImportError as e:
        print("导入lunar_python.Solar.Solar类失败:", str(e))
    
except ImportError as e:
    print("导入lunar_python库失败:", str(e))
    print("尝试安装lunar_python库...")
    
    try:
        import pip
        print("使用pip安装lunar_python...")
        os.system("pip install lunar_python")
        print("安装完成，请重新运行此脚本")
    except ImportError:
        print("未找到pip，请手动安装lunar_python库")
except Exception as e:
    print("发生其他错误:", str(e))

print("导入测试完成") 