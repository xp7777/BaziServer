import sys
import os
import datetime

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    from lunar_python import Solar, Lunar
    print("lunar-python库已成功导入")
    
    # 测试基本功能
    solar = Solar.fromYmd(1990, 1, 15)
    lunar = solar.getLunar()
    print("公历:", solar.toYmd())
    print("农历:", lunar.toString())
    print("八字:", " ".join(lunar.getBaZi()))
    
except ImportError as e:
    print("导入lunar-python库失败:", str(e))
    print("尝试安装lunar-python库...")
    
    try:
        import pip
        print("使用pip安装lunar-python...")
        os.system("pip install lunar-python")
        print("安装完成，请重新运行此脚本")
    except ImportError:
        print("未找到pip，请手动安装lunar-python库")
except Exception as e:
    print("发生其他错误:", str(e)) 