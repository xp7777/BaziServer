import sys
import os

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    
    print("lunar-python库已成功导入")
    
    # 测试大运
    print("\n=== 大运和流年测试 ===")
    
    # 创建公历对象
    solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
    lunar = solar.getLunar()
    
    print(f"公历: {solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日 {solar.getHour()}时")
    print(f"农历: {lunar.toString()}")
    print(f"八字: {' '.join(lunar.getBaZi())}")
    
    # 获取八字对象
    eight_char = lunar.getEightChar()
    
    # 男性大运
    yun_male = eight_char.getYun(1)  # 1表示男性
    print("\n男性大运:")
    print(f"起运年份: {yun_male.getStartYear()}")
    print(f"起运月份: {yun_male.getStartMonth()}")
    print(f"起运日: {yun_male.getStartDay()}")
    print(f"起运时: {yun_male.getStartHour()}")
    print(f"起运公历: {yun_male.getStartSolar().toYmd()}")
    print(f"大运方向: {'顺' if yun_male.isForward() else '逆'}")
    
    # 获取大运列表
    da_yun_list = yun_male.getDaYun()
    print(f"\n大运数量: {len(da_yun_list)}")
    
    # 遍历大运
    for i, da_yun in enumerate(da_yun_list):
        if i >= 8:  # 只显示前8个大运
            break
            
        print(f"\n第{i+1}步大运:")
        print(f"大运对象类型: {type(da_yun)}")
        print(f"大运对象方法: {[method for method in dir(da_yun) if not method.startswith('_')]}")
        
        # 测试各种方法
        try:
            print(f"索引: {da_yun.getIndex()}")
        except:
            print("无法获取索引")
            
        try:
            print(f"年龄: {da_yun.getStartAge()} - {da_yun.getEndAge()}")
        except:
            # 尝试根据起运年份和索引计算年龄
            start_age = yun_male.getStartYear() + i * 10
            end_age = start_age + 9
            print(f"推算年龄范围: {start_age} - {end_age}")
            
        try:
            print(f"天干地支: {da_yun.getGanZhi()}")
        except:
            print("无法获取干支")
        
        # 尝试获取干支
        try:
            print(f"当前大运干: {da_yun.getGan()}")
            print(f"当前大运支: {da_yun.getZhi()}")
        except:
            pass
            
        # 直接查看对象的字符串表示
        print(f"大运对象: {da_yun}")
    
    # 测试流年
    print("\n=== 流年测试 ===")
    
    # 测试一个流年的计算（以2025年为例）
    test_year = 2025
    try:
        liu_nian = eight_char.getYearXun(test_year)
        print(f"{test_year}年流年: {liu_nian}")
    except:
        print(f"无法获取{test_year}年流年")
        
    try:
        # 尝试获取2025年的天干地支
        birth_year = solar.getYear()
        year_offset = test_year - birth_year
        gan_index = (year_offset + lunar.getYearGanIndex()) % 10
        zhi_index = (year_offset + lunar.getYearZhiIndex()) % 12
        
        from lunar_python.util.LunarUtil import LunarUtil
        gan = LunarUtil.GAN[gan_index]
        zhi = LunarUtil.ZHI[zhi_index]
        
        print(f"{test_year}年干支: {gan}{zhi}")
    except Exception as e:
        print(f"计算{test_year}年干支出错: {e}")
        
    # 尝试直接使用Solar获取2025年的对象
    try:
        solar_2025 = Solar.fromYmd(2025, 1, 1)
        lunar_2025 = solar_2025.getLunar()
        print(f"2025年正月初一干支: {lunar_2025.getYearInGanZhi()}")
    except Exception as e:
        print(f"获取2025年干支出错: {e}")
    
except ImportError as e:
    print("导入lunar-python库失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    import traceback
    traceback.print_exc() 