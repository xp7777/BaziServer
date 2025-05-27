import sys
import os
import datetime
import inspect

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    import lunar_python
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    
    print("lunar-python库已成功导入")
    print("lunar-python路径:", lunar_python.__file__)
    print("lunar-python内容:", dir(lunar_python))
    
    print("\n=== 基本测试 ===")
    
    # 创建公历对象
    solar = Solar.fromYmd(1990, 1, 15)
    print("公历:", solar.toYmd())
    
    # 转换为农历
    lunar = solar.getLunar()
    print("农历:", lunar.toString())
    
    # 获取八字
    bazi = lunar.getBaZi()
    print("八字数组:", bazi)
    
    if len(bazi) >= 8:
        print("八字:", bazi[0] + bazi[1], bazi[2] + bazi[3], bazi[4] + bazi[5], bazi[6] + bazi[7])
    else:
        print("警告: getBaZi()返回的数组长度小于8", len(bazi))
        
    # 尝试直接获取干支
    print("\n=== 干支获取方法 ===")
    print("年柱:", lunar.getYearInGanZhi())
    print("月柱:", lunar.getMonthInGanZhi())
    print("日柱:", lunar.getDayInGanZhi())
    print("时柱:", lunar.getTimeInGanZhi())
    
    # 单独获取天干地支
    print("\n=== 单独获取天干地支 ===")
    print("年干:", lunar.getYearGan())
    print("年支:", lunar.getYearZhi())
    print("月干:", lunar.getMonthGan())
    print("月支:", lunar.getMonthZhi())
    print("日干:", lunar.getDayGan())
    print("日支:", lunar.getDayZhi())
    print("时干:", lunar.getTimeGan())
    print("时支:", lunar.getTimeZhi())
    
    # 获取八字对象
    print("\n=== 八字对象测试 ===")
    eight_char = lunar.getEightChar()
    print("八字对象:", eight_char)
    print("八字对象方法:", [method for method in dir(eight_char) if not method.startswith('_')])
    
    # 测试大运
    print("\n=== 大运测试 ===")
    yun_male = eight_char.getYun(1)  # 1表示男性
    print("大运对象:", yun_male)
    print("大运对象方法:", [method for method in dir(yun_male) if not method.startswith('_')])
    
    # 查看大运对象的具体属性和方法
    print("\n大运对象详细信息:")
    for attr in dir(yun_male):
        if not attr.startswith('_'):
            try:
                value = getattr(yun_male, attr)
                if callable(value):
                    print(f"{attr}(): {value()}")
                else:
                    print(f"{attr}: {value}")
            except Exception as e:
                print(f"{attr}: 无法访问 - {str(e)}")
    
    # 获取大运信息
    print("\n=== 获取大运信息 ===")
    da_yun = yun_male.getDaYun()
    print("大运列表:", da_yun)
    print("大运类型:", type(da_yun))
    if len(da_yun) > 0:
        print("第一个大运:", da_yun[0])
    
    # 检查五行关系
    print("\n=== 五行关系 ===")
    try:
        from lunar_python import LunarUtil
        print("五行天干:", LunarUtil.WU_XING_GAN)
        print("五行地支:", LunarUtil.WU_XING_ZHI)
        
        # 测试天干五行
        for gan in "甲乙丙丁戊己庚辛壬癸":
            print(f"{gan}的五行: {LunarUtil.WU_XING_GAN.get(gan)}")
        
        # 测试地支五行
        for zhi in "子丑寅卯辰巳午未申酉戌亥":
            print(f"{zhi}的五行: {LunarUtil.WU_XING_ZHI.get(zhi)}")
    except Exception as e:
        print("五行关系测试失败:", str(e))
    
    print("测试完成")
    
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
    import traceback
    traceback.print_exc() 